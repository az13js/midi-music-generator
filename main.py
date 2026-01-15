import argparse
import json
import sys
import os
import itertools
import logging
from typing import List, Tuple, Union

from core.theory import Chord, Key, get_scale_notes, get_diatonic_chord, ChordQuality, get_chord_intervals
from generators import MelodyGenerator, HarmonyGenerator, RhythmGenerator, RhythmPattern
from composers import SimpleArranger

# ==================== 日志配置 ====================

class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)

def setup_logging(verbose: int = 0, quiet: bool = False, log_file: str = None):
    """
    设置日志系统

    Args:
        verbose: 详细级别 (0=WARNING, 1=INFO, 2=DEBUG)
        quiet: 安静模式，只显示错误
        log_file: 日志文件路径（可选）
    """
    # 确定日志级别
    if quiet:
        level = logging.ERROR
    elif verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    else:  # verbose >= 2
        level = logging.DEBUG

    # 创建日志格式
    if verbose >= 2:
        # DEBUG 模式：显示详细的时间和函数信息
        fmt = '%(asctime)s [%(levelname)s] %(name)s.%(funcName)s(): %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
    elif verbose == 1:
        # INFO 模式：简洁格式
        fmt = '[%(levelname)s] %(message)s'
        datefmt = None
    else:
        # WARNING/ERROR 模式：极简格式
        fmt = '%(levelname)s: %(message)s'
        datefmt = None

    # 配置控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(fmt, datefmt))

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = []  # 清除现有的处理器
    root_logger.addHandler(console_handler)

    # 如果指定了日志文件，添加文件处理器
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(fmt, datefmt))
            root_logger.addHandler(file_handler)
            print(f"日志文件: {log_file}")
        except Exception as e:
            print(f"警告：无法创建日志文件 {log_file}: {e}", file=sys.stderr)

    return logging.getLogger(__name__)

# ==================== 工具函数 ====================

def load_preset(name: str, logger: logging.Logger) -> dict:
    """加载预设配置文件"""
    preset_path = f"presets/{name}.json"

    if not os.path.exists(preset_path):
        logger.error(f"Preset file '{preset_path}' not found")
        logger.info(f"Available presets: {get_available_presets()}")
        sys.exit(1)

    try:
        with open(preset_path, 'r', encoding='utf-8') as f:
            preset = json.load(f)
        logger.debug(f"Loaded preset from: {preset_path}")
        logger.debug(f"Preset content: {json.dumps(preset, indent=2, ensure_ascii=False)}")
        return preset
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in preset file '{preset_path}': {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading preset '{preset_path}': {e}")
        sys.exit(1)

def get_available_presets() -> List[str]:
    """获取可用的预设列表"""
    presets_dir = "presets"
    if not os.path.exists(presets_dir):
        return []

    presets = []
    for filename in os.listdir(presets_dir):
        if filename.endswith('.json'):
            presets.append(filename[:-5])  # 移除 .json 扩展名
    return sorted(presets)

def display_preset_info(preset: dict, logger: logging.Logger):
    """显示预设配置信息"""
    logger.info("="*60)
    logger.info("预设配置信息 (Preset Configuration)")
    logger.info("="*60)
    logger.info(f"调性 (Key): {preset.get('key', 'C_MAJOR')}")
    logger.info(f"速度 (Tempo): {preset.get('tempo', 120)} BPM")
    logger.info(f"小节数 (Bars): {preset.get('structure', {}).get('bars', 16)}")

    if 'melody' in preset:
        melody = preset['melody']
        logger.info(f"旋律策略 (Melody Strategy): {melody.get('strategy', 'structured')}")
        logger.info(f"力度曲线 (Velocity Curve): {melody.get('velocity_curve', 'flat')}")

    if 'harmony' in preset:
        harmony = preset['harmony']
        logger.info(f"和弦进行 (Harmony Progression): {harmony.get('progression', 'pop_basic')}")
        logger.info(f"和弦类型 (Voicing): {harmony.get('voicing', 'close')}")

    if 'rhythm' in preset:
        rhythm = preset['rhythm']
        logger.info(f"节奏模式 (Rhythm Pattern): {rhythm.get('pattern', 'steady')}")

    logger.info("="*60)

def display_generation_stats(stats: dict, logger: logging.Logger):
    """显示生成统计信息"""
    logger.info("="*60)
    logger.info("生成统计 (Generation Statistics)")
    logger.info("="*60)

    for key, value in stats.items():
        if isinstance(value, list):
            logger.info(f"{key}: {len(value)} items")
        elif isinstance(value, dict):
            logger.info(f"{key}:")
            for k, v in value.items():
                logger.info(f"  - {k}: {v}")
        else:
            logger.info(f"{key}: {value}")

    logger.info("="*60)

# ==================== 生成器适配器 ====================

class PrecomputedGenerator:
    """适配器类：包装预计算好的数据传递给 SimpleArranger"""
    def __init__(self, data: List[Union[int, Tuple[int, float], Tuple[int, float, int]]], track_name: str = "Unknown"):
        self.data = data
        self.track_name = track_name

    def generate(self, key: Key):
        return self.data

# ==================== 主函数 ====================

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="MIDI Music Generator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python main.py --preset pop --output output.mid

  # 显示详细生成过程信息
  python main.py --preset jazz --output jazz.mid -v

  # 显示调试信息（最详细）
  python main.py --preset classical --output classical.mid -vv

  # 安静模式（仅错误）
  python main.py --preset rock --output rock.mid -q

  # 将日志保存到文件
  python main.py --preset pop --output pop.mid --log-file generation.log

  # 列出可用预设
  python main.py --list-presets
        """
    )

    parser.add_argument("--preset", default="pop", help="预设名称 (默认: pop)")
    parser.add_argument("--output", default="output.mid", help="输出 MIDI 文件路径")
    parser.add_argument("--bars", type=int, default=None, help="生成的小节数量")

    # 日志相关参数
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="增加输出详细程度 (-v=INFO, -vv=DEBUG)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="安静模式，仅显示错误信息")
    parser.add_argument("--log-file", type=str, default=None,
                        help="将日志保存到指定文件")
    parser.add_argument("--list-presets", action="store_true",
                        help="列出所有可用的预设并退出")
    parser.add_argument("--show-info", action="store_true",
                        help="显示预设详细信息")

    args = parser.parse_args()

    # 设置日志
    logger = setup_logging(verbose=args.verbose, quiet=args.quiet, log_file=args.log_file)

    # 列出可用预设
    if args.list_presets:
        presets = get_available_presets()
        print("\n可用的预设 (Available Presets):")
        print("-" * 40)
        for preset in presets:
            print(f"  - {preset}")
        print(f"\n共 {len(presets)} 个预设\n")
        sys.exit(0)

    logger.info(f"MIDI Music Generator 开始运行")
    logger.debug(f"命令行参数: {vars(args)}")

    # 加载预设
    logger.info(f"加载预设: {args.preset}")
    preset = load_preset(args.preset, logger)

    # 显示预设信息
    if args.show_info or args.verbose >= 1:
        display_preset_info(preset, logger)

    # 解析配置
    try:
        key = Key[preset.get("key", "C_MAJOR")]
    except KeyError:
        logger.warning(f"Unknown key '{preset.get('key')}', using C_MAJOR")
        key = Key.C_MAJOR

    tempo = preset.get("tempo", 120)
    bars = args.bars if args.bars is not None else preset.get("structure", {}).get("bars", 16)

    logger.info(f"基本参数: Key={key.value}, Tempo={tempo} BPM, Bars={bars}")
    logger.debug(f"预设详细内容:\n{json.dumps(preset, indent=2, ensure_ascii=False)}")

    # 初始化编曲器
    logger.info("初始化编曲器...")
    arranger = SimpleArranger(tempo=tempo, key=key)
    logger.debug(f"编曲器参数: ticks_per_beat={arranger.ticks_per_beat}")

    # 统计信息
    generation_stats = {
        "tracks": [],
        "total_notes": 0,
        "duration_beats": 0
    }

    # ==================== 旋律轨道 ====================
    if "melody" in preset:
        logger.info("\n[1/3] 生成旋律轨道...")
        melody_cfg = preset["melody"]
        strategy_name = melody_cfg.get("strategy", "structured")

        logger.debug(f"旋律策略: {strategy_name}")
        logger.debug(f"旋律配置: {json.dumps(melody_cfg, indent=2)}")

        # 创建旋律生成器
        melody_gen = MelodyGenerator(strategy_name=strategy_name, key=key)
        logger.debug(f"可用旋律策略: {MelodyGenerator.get_available_strategies()}")

        # 生成旋律
        length = bars * 4 * 2  # 估算长度
        logger.debug(f"生成旋律长度: {length} 音符")
        melody_pitches = melody_gen.generate(length=length)
        logger.debug(f"实际生成旋律音符数: {len(melody_pitches)}")

        # 生成节奏
        logger.info("  - 生成节奏模式...")
        rhythm_cfg = preset.get("rhythm", {})
        pattern_map = {
            "steady": RhythmPattern.STEADY_QUARTERS,
            "rock_beat": RhythmPattern.ROCK_BEAT,
            "swing_eighths": RhythmPattern.SWING_EIGHTHS,
            "syncopated_16": RhythmPattern.SYNCOPATED_16,
            "techno": RhythmPattern.TECHNO,
            "bossa_nova": RhythmPattern.BOSSA_NOVA,
            "steady_eighths": RhythmPattern.STEADY_EIGHTHS,
            "steady_quarters": RhythmPattern.STEADY_QUARTERS,
        }
        target_pattern = pattern_map.get(rhythm_cfg.get("pattern", "steady"), RhythmPattern.STEADY_QUARTERS)

        if rhythm_cfg.get("style"):
            rhythm_gen = RhythmGenerator("groove", style=rhythm_cfg.get("style"))
            logger.debug(f"使用风格节奏: {rhythm_cfg.get('style')}")
        else:
            rhythm_gen = RhythmGenerator("pattern", pattern=target_pattern)
            logger.debug(f"使用模式节奏: {target_pattern.value}")

        durations = rhythm_gen.generate(num_bars=bars)
        logger.debug(f"生成的节奏时长列表: {len(durations)} 项")

        # 应用力度曲线
        curve_type = melody_cfg.get("velocity_curve", "flat")
        logger.debug(f"应用力度曲线: {curve_type}")
        base_velocities = melody_gen.strategy.apply_velocity_curve(melody_pitches, curve_type=curve_type)

        # 组合旋律数据
        logger.debug("组合旋律音高、节奏和力度...")
        melody_data = []
        pitch_iter = itertools.cycle(melody_pitches)
        vel_iter = itertools.cycle(base_velocities)

        for i, dur in enumerate(durations):
            note = next(pitch_iter)
            vel = next(vel_iter)
            melody_data.append((note, dur, vel))

        # 记录统计
        track_stats = {
            "name": "Melody",
            "channel": 0,
            "note_count": len(melody_data),
            "strategy": strategy_name,
            "velocity_curve": curve_type
        }
        generation_stats["tracks"].append(track_stats)
        generation_stats["total_notes"] += len(melody_data)
        generation_stats["duration_beats"] += sum(d for _, d, _ in melody_data)

        logger.info(f"  ✓ 旋律生成完成: {len(melody_data)} 音符")
        logger.debug(f"  旋律音域: {min(m[0] for m in melody_data)} - {max(m[0] for m in melody_data)}")
        logger.debug(f"  力度范围: {min(m[2] for m in melody_data)} - {max(m[2] for m in melody_data)}")

        # 音色读取，默认为 0 (钢琴)
        melody_program = melody_cfg.get("program", 0)
        logger.debug(f"  旋律音色 (Program): {melody_program}")

        # 添加到编曲器
        arranger.add_track(
            name="Melody", 
            generator=PrecomputedGenerator(melody_data, "Melody"), 
            channel=0, 
            program=melody_program
        )

    # ==================== 和声轨道 ====================
    if "harmony" in preset:
        logger.info("\n[2/3] 生成和声轨道...")
        harmony_cfg = preset["harmony"]
        progression_name = harmony_cfg.get("progression", "pop_basic")
        voicing_type = harmony_cfg.get("voicing", "close")

        logger.debug(f"和弦进行: {progression_name}")
        logger.debug(f"和弦类型: {voicing_type}")

        # 实例化和声生成器
        harmony_gen = HarmonyGenerator(
            strategy_name="progression",
            key=key,
            progression_name=progression_name,
            beats_per_bar=4
        )

        # 生成基础根音和时值
        roots_durations = harmony_gen.generate(num_bars=bars)
        logger.debug(f"生成的和弦数量: {len(roots_durations)}")

        # 生成琶音
        logger.info("  - 生成和弦琶音...")
        arpeggio_data = []

        if hasattr(harmony_gen.strategy, 'progression') and harmony_gen.strategy.progression:
            prog_chords = harmony_gen.strategy.progression.chords
            prog_len = len(prog_chords)

            # 显示和弦进行
            chord_names = []
            for degree, quality in prog_chords:
                chord = Chord(root=degree-1, quality=quality)
                chord_names.append(chord.get_chord_name(key))
            logger.debug(f"和弦进行: {' - '.join(chord_names)}")

            for i, (root_note, duration) in enumerate(roots_durations):
                degree, quality = prog_chords[i % prog_len]

                # 处理 voicing
                final_quality = quality
                if voicing_type == "open":
                    if quality == ChordQuality.MAJOR:
                        final_quality = ChordQuality.MAJOR_SEVENTH
                    elif quality == ChordQuality.MINOR:
                        final_quality = ChordQuality.MINOR_SEVENTH
                    elif quality == ChordQuality.DOMINANT_SEVENTH:
                        final_quality = ChordQuality.DOMINANT_NINTH

                # 获取音程
                intervals = get_chord_intervals(final_quality)
                logger.debug(f"和弦 {i+1}: degree={degree}, quality={final_quality.value}, intervals={intervals}")

                # 生成琶音音符
                for interval in intervals:
                    arpeggio_data.append((root_note + interval, duration, 80))
        else:
            # 降级处理
            logger.warning("无法获取和弦进行信息，使用简单三和弦")
            for root_note, duration in roots_durations:
                for interval in [0, 4, 7]:
                    arpeggio_data.append((root_note + interval, duration, 80))

        # 记录统计
        track_stats = {
            "name": "Harmony",
            "channel": 1,
            "note_count": len(arpeggio_data),
            "progression": progression_name,
            "voicing": voicing_type
        }
        generation_stats["tracks"].append(track_stats)
        generation_stats["total_notes"] += len(arpeggio_data)
        generation_stats["duration_beats"] += sum(d for _, d, _ in arpeggio_data)

        logger.info(f"  ✓ 和声生成完成: {len(arpeggio_data)} 音符")
        logger.debug(f"  和弦音域: {min(m[0] for m in arpeggio_data)} - {max(m[0] for m in arpeggio_data)}")

        # 音色读取，默认为 0 (钢琴)
        harmony_program = harmony_cfg.get("program", 0)
        logger.debug(f"  和声音色 (Program): {harmony_program}")

        # 添加到编曲器
        arranger.add_track(
            name="Harmony", 
            generator=PrecomputedGenerator(arpeggio_data, "Harmony"), 
            channel=1, 
            program=harmony_program
        )

    # ==================== 低音轨道 ====================
    if "harmony" in preset:
        logger.info("\n[3/3] 生成低音轨道...")
        harmony_cfg = preset["harmony"]

        bass_gen = HarmonyGenerator(
            strategy_name="progression",
            key=key,
            progression_name=preset["harmony"].get("progression"),
            beats_per_bar=4
        )
        bass_roots = bass_gen.generate(num_bars=bars)

        # 低音低一个八度
        bass_data = [(note - 12, dur, 100) for note, dur in bass_roots]

        # 记录统计
        track_stats = {
            "name": "Bass",
            "channel": 2,
            "note_count": len(bass_data),
            "octave_shift": -12
        }
        generation_stats["tracks"].append(track_stats)
        generation_stats["total_notes"] += len(bass_data)
        generation_stats["duration_beats"] += sum(d for _, d, _ in bass_data)

        logger.info(f"  ✓ 低音生成完成: {len(bass_data)} 音符")
        logger.debug(f"  低音音域: {min(m[0] for m in bass_data)} - {max(m[0] for m in bass_data)}")

        # 低音音色读取，默认为 32 (Acoustic Bass)
        bass_program = harmony_cfg.get("bass_program", 32)
        logger.debug(f"  低音音色 (Program): {bass_program}")

        arranger.add_track(
            name="Bass", 
            generator=PrecomputedGenerator(bass_data, "Bass"), 
            channel=2, 
            program=bass_program
        )

    # ==================== 保存文件 ====================
    logger.info("\n保存 MIDI 文件...")

    # 计算总时长（秒）
    duration_seconds = (generation_stats["duration_beats"] / tempo) * 60
    generation_stats["duration_seconds"] = round(duration_seconds, 2)
    generation_stats["total_duration_beats"] = generation_stats["duration_beats"]

    try:
        arranger.save(args.output)
        logger.info("="*60)
        logger.info(f"✓ 成功生成 MIDI 文件: {args.output}")
        logger.info("="*60)

        # 显示统计信息
        if args.verbose >= 1:
            display_generation_stats(generation_stats, logger)

        # 显示文件信息
        file_size = os.path.getsize(args.output)
        logger.info(f"文件大小: {file_size} 字节 ({file_size/1024:.2f} KB)")
        logger.info(f"预计播放时长: {duration_seconds:.2f} 秒 ({duration_seconds/60:.2f} 分钟)")

        # 显示轨道信息
        logger.info(f"生成的音轨:")
        for track in generation_stats["tracks"]:
            logger.info(f"  • {track['name']}: {track['note_count']} 音符 (Channel {track['channel']})")

        logger.info("\n" + "="*60)
        logger.info("生成完成！")
        print(f"Successfully generated MIDI file: {args.output}")
    except Exception as e:
        logger.error(f"保存 MIDI 文件失败: {e}", exc_info=args.verbose >= 2)
        sys.exit(1)

if __name__ == "__main__":
    main()
