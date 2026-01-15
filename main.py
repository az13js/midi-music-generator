import argparse
import json
import sys
import os
import itertools
from typing import List, Tuple, Union

from core.theory import Key, get_scale_notes, get_diatonic_chord, ChordQuality, get_chord_intervals
from generators import MelodyGenerator, HarmonyGenerator, RhythmGenerator, RhythmPattern
from composers import SimpleArranger

def load_preset(name: str) -> dict:
    """加载预设配置文件"""
    preset_path = f"presets/{name}.json"
    if not os.path.exists(preset_path):
        print(f"Error: Preset file '{preset_path}' not found.")
        sys.exit(1)
    try:
        with open(preset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in preset file '{preset_path}'.")
        sys.exit(1)

class PrecomputedGenerator:
    """适配器类：包装预计算好的数据传递给 SimpleArranger"""
    def __init__(self, data: List[Union[int, Tuple[int, float], Tuple[int, float, int]]]):
        self.data = data

    def generate(self, key: Key):
        return self.data

def expand_harmony_to_arpeggio(
    harmony_gen: HarmonyGenerator,
    key: Key,
    voicing: str = "close"
) -> List[Tuple[int, float, int]]:
    """
    将和声扩展为琶音。
    根据 HarmonyGenerator 内部存储的 Progression 信息，
    动态构建和弦（支持三和弦、七和弦等）。
    """
    result = []

    # 1. 获取根音和时值
    # 注意：为了获取时值，我们调用 generate
    roots_durations = harmony_gen.generate(num_bars=16) # 这里的bars会被外部覆盖，但这里需要先获取对象数据结构
    # 实际上，为了简单起见，我们重新调用一次以获取当前配置的数据

    # 更好的方式：直接读取生成器的配置
    # 由于 HarmonyGenerator 内部可能持有 progression 对象，我们可以利用它
    # 这里我们需要重新生成一次以确保数据是同步的
    # 假设 harmony_gen 已经配置好了 num_bars

    # 我们需要一种方法同时获取 Chord 信息和 Duration 信息
    # 由于现有的 HarmonyGenerator.generate() 只返回 (root, duration)，
    # 我们稍微 hack 一下，假设 chord 的顺序和 progression 的循环是对应的。

    # 获取和弦序列对象列表 (如果没有直接接口，我们利用 progression 重建)
    # 在 ProgressionBasedStrategy 中，self.progression 是可用的

    strategy = harmony_gen.strategy
    num_bars = 16 # 默认值，实际应该在调用时传入，这里为了演示逻辑

    # 我们在 main 函数调用时会传入正确的 num_bars，这里主要处理逻辑
    # 因此这个函数改为在 main 中处理可能更好，但为了保持结构，我们假设它是 main 的一部分逻辑

    # 为了解决丢失 ChordQuality 信息的问题，我们在 main.py 中直接操作 Chord 对象
    pass

# 将扩展逻辑移到 main 函数内部以便访问完整的上下文

def main():
    parser = argparse.ArgumentParser(description="MIDI Music Generator CLI")
    parser.add_argument("--preset", default="pop", help="Preset name (e.g., pop, jazz, rock)")
    parser.add_argument("--output", required=True, help="Output MIDI file path")
    parser.add_argument("--bars", type=int, default=None, help="Number of bars to generate")
    args = parser.parse_args()

    preset = load_preset(args.preset)

    try:
        key = Key[preset.get("key", "C_MAJOR")]
    except KeyError:
        key = Key.C_MAJOR

    tempo = preset.get("tempo", 120)
    bars = args.bars if args.bars is not None else preset.get("structure", {}).get("bars", 16)

    arranger = SimpleArranger(tempo=tempo, key=key)

    # --- 旋律轨道 (含力度曲线) ---
    if "melody" in preset:
        melody_cfg = preset["melody"]
        strategy_name = melody_cfg.get("strategy", "structured")

        melody_gen = MelodyGenerator(strategy_name=strategy_name, key=key)
        length = bars * 4 * 2 # 估算长度
        melody_pitches = melody_gen.generate(length=length)

        # 生成节奏
        rhythm_cfg = preset.get("rhythm", {})
        pattern_map = {
            "steady": RhythmPattern.STEADY_QUARTERS, "rock_beat": RhythmPattern.ROCK_BEAT,
            "swing_eighths": RhythmPattern.SWING_EIGHTHS, "syncopated_16": RhythmPattern.SYNCOPATED_16,
            "techno": RhythmPattern.TECHNO, "bossa_nova": RhythmPattern.BOSSA_NOVA,
            "steady_eighths": RhythmPattern.STEADY_EIGHTHS, "steady_quarters": RhythmPattern.STEADY_QUARTERS,
        }
        target_pattern = pattern_map.get(rhythm_cfg.get("pattern", "steady"), RhythmPattern.STEADY_QUARTERS)

        if rhythm_cfg.get("style"):
            rhythm_gen = RhythmGenerator("groove", style=rhythm_cfg.get("style"))
        else:
            rhythm_gen = RhythmGenerator("pattern", pattern=target_pattern)

        durations = rhythm_gen.generate(num_bars=bars)

        # 应用力度曲线
        curve_type = melody_cfg.get("velocity_curve", "flat")
        # 对原始旋律音高应用曲线（这会生成一个与 melody_pitches 长度相同的力度列表）
        base_velocities = melody_gen.strategy.apply_velocity_curve(melody_pitches, curve_type=curve_type)

        # 组合：使用 itertools.cycle 循环旋律音高和力度，同时使用节奏
        # 注意：durations 的长度决定了最终音符数量，旋律和力度需要循环匹配
        melody_data = []

        # 创建循环迭代器
        pitch_iter = itertools.cycle(melody_pitches)
        vel_iter = itertools.cycle(base_velocities)

        for dur in durations:
            note = next(pitch_iter)
            vel = next(vel_iter)
            # 构造三元组 (note, duration, velocity)
            melody_data.append((note, dur, vel))

        arranger.add_track(name="Melody", generator=PrecomputedGenerator(melody_data), channel=0)

    # --- 和声轨道 (和弦琶音优化) ---
    if "harmony" in preset:
        harmony_cfg = preset["harmony"]
        strategy_name = harmony_cfg.get("progression", "pop_basic")
        voicing_type = harmony_cfg.get("voicing", "close")

        # 实例化生成器
        # 我们需要它生成 (root, duration)
        harmony_gen = HarmonyGenerator(
            strategy_name="progression",
            key=key,
            progression_name=strategy_name,
            beats_per_bar=4
        )

        # 生成基础根音和时值
        roots_durations = harmony_gen.generate(num_bars=bars)

        # 优化：根据 voicing 和 chord quality 生成琶音
        # 我们需要获取和弦性质。ProgressionBasedStrategy 持有 progression 对象
        arpeggio_data = []

        if hasattr(harmony_gen.strategy, 'progression') and harmony_gen.strategy.progression:
            prog_chords = harmony_gen.strategy.progression.chords # [(degree, quality), ...]
            prog_len = len(prog_chords)

            for i, (root_note, duration) in enumerate(roots_durations):
                # 获取对应的和弦定义
                degree, quality = prog_chords[i % prog_len]

                # 处理 voicing (open -> 扩展和弦)
                final_quality = quality
                if voicing_type == "open":
                    if quality == ChordQuality.MAJOR:
                        final_quality = ChordQuality.MAJOR_SEVENTH
                    elif quality == ChordQuality.MINOR:
                        final_quality = ChordQuality.MINOR_SEVENTH
                    elif quality == ChordQuality.DOMINANT_SEVENTH:
                        final_quality = ChordQuality.DOMINANT_NINTH # 或者保持七和弦

                # 获取音程
                intervals = get_chord_intervals(final_quality)

                # 生成琶音音符 (note, duration, velocity)
                # 和声伴奏力度稍微低一点，平均 80
                for interval in intervals:
                    arpeggio_data.append((root_note + interval, duration, 80))
        else:
            # 降级处理：如果无法获取 progression，使用简单三和弦
            for root_note, duration in roots_durations:
                for interval in [0, 4, 7]:
                    arpeggio_data.append((root_note + interval, duration, 80))

        arranger.add_track(name="Harmony", generator=PrecomputedGenerator(arpeggio_data), channel=1)

    # --- 低音轨道 (简化) ---
    if "harmony" in preset:
        bass_gen = HarmonyGenerator(strategy_name="progression", key=key, progression_name=preset["harmony"].get("progression"), beats_per_bar=4)
        bass_roots = bass_gen.generate(num_bars=bars)
        bass_data = [(note - 12, dur, 100) for note, dur in bass_roots]
        arranger.add_track(name="Bass", generator=PrecomputedGenerator(bass_data), channel=2)

    try:
        arranger.save(args.output)
        print(f"Successfully generated MIDI file: {args.output}")
    except Exception as e:
        print(f"Error saving MIDI file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
