import argparse
import json
import sys
import os
from typing import List, Tuple, Union

# 导入核心模块
from core.theory import Key, get_scale_notes, get_diatonic_chord, ChordQuality
# 导入生成器
from generators import MelodyGenerator, HarmonyGenerator
# 导入编曲器
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
    """
    适配器类：
    由于 SimpleArranger.add_track 期望 generator.generate(self.key) 格式，
    而现代的 Generator (Melody/Harmony) 接口各异，
    我们先在 main 中生成数据，然后用这个适配器包装起来传给 Arranger。
    """
    def __init__(self, data: List[Union[int, Tuple[int, float]]]):
        self.data = data

    def generate(self, key: Key):
        # 忽略传入的 key，直接返回预设计算好的数据
        return self.data

def expand_harmony_to_arpeggio(
    root_duration_list: List[Tuple[int, float]], 
    key: Key
) -> List[Tuple[int, float]]:
    """
    将 和声 (根音, 时值) 扩展为琶音 (音符, 时值)。
    这样可以让 SimpleArranger 播放和弦的分解形式，而不是单音根音。
    """
    result = []
    # 获取两个八度的音阶，用于构建和弦
    scale_notes = get_scale_notes(key, octave=4, num_octaves=2)
    
    for root_midi, duration in root_duration_list:
        # 尝试找到根音在音阶中的索引
        try:
            root_idx = scale_notes.index(root_midi)
        except ValueError:
            # 如果根音不在音阶里（极少数情况），就用单音
            result.append((root_midi, duration))
            continue
        
        # 构建一个基础的大三或小三和弦 (根据调性决定简单起见)
        # 这里为了演示，使用大三和弦模式 (1, 3, 5度)
        intervals = [0, 4, 7] 
        
        # 将每个和弦音符转化为序列
        chord_notes = []
        for interval in intervals:
            chord_notes.append((root_midi + interval, duration))
        
        # 将这些和弦音符添加到结果中，形成琶音效果
        result.extend(chord_notes)
        
    return result

def main():
    # 1. 解析命令行参数
    parser = argparse.ArgumentParser(description="MIDI Music Generator CLI")
    parser.add_argument("--preset", default="pop", help="Preset name (e.g., pop, jazz, rock)")
    parser.add_argument("--output", required=True, help="Output MIDI file path")
    parser.add_argument("--bars", type=int, default=16, help="Number of bars to generate")
    args = parser.parse_args()

    # 2. 加载配置
    print(f"Loading preset: {args.preset}")
    preset = load_preset(args.preset)
    
    # 解析 Key
    try:
        key = Key[preset.get("key", "C_MAJOR")]
    except KeyError:
        print(f"Error: Invalid key '{preset.get('key')}' in preset. Defaulting to C_MAJOR.")
        key = Key.C_MAJOR

    tempo = preset.get("tempo", 120)
    bars = args.bars

    # 3. 初始化编曲器
    print(f"Initializing arranger: Key={key.value}, Tempo={tempo}")
    arranger = SimpleArranger(tempo=tempo, key=key)

    # 4. 生成并添加音轨

    # --- 旋律轨道 ---
    if "melody" in preset:
        melody_cfg = preset["melody"]
        strategy_name = melody_cfg.get("strategy", "structured")
        print(f"Generating Melody with strategy: {strategy_name}")
        
        # 实例化旋律生成器
        melody_gen = MelodyGenerator(
            strategy_name=strategy_name, 
            key=key
        )
        
        # 手动调用生成逻辑 (注意：这里传入 length 或 bars 相关参数)
        # 假设每小节4拍，音符平均时长0.5拍估算长度，或者直接填满
        length = bars * 4 * 2 # 生成足够多的音符
        
        try:
            melody_notes = melody_gen.generate(length=length)
            # 使用适配器包装数据
            arranger.add_track(
                name="Melody", 
                generator=PrecomputedGenerator(melody_notes), 
                channel=0
            )
        except Exception as e:
            print(f"Warning: Failed to generate melody: {e}")

    # --- 和声轨道 (和弦) ---
    if "harmony" in preset:
        harmony_cfg = preset["harmony"]
        strategy_name = harmony_cfg.get("progression", "progression")
        print(f"Generating Harmony with strategy: {strategy_name}")

        # 实例化和声生成器
        harmony_gen = HarmonyGenerator(
            strategy_name="progression", # 指定使用基于进行生成的策略
            key=key,
            progression_name=strategy_name, # 传入具体的进行名称 (如 pop)
            beats_per_bar=4
        )
        
        try:
            # 获取根音和时值
            harmony_roots = harmony_gen.generate(num_bars=bars)
            
            # 将和声转换为琶音数据以适应 SimpleArranger 的单轨写入逻辑
            harmony_notes = expand_harmony_to_arpeggio(harmony_roots, key)
            
            arranger.add_track(
                name="Harmony", 
                generator=PrecomputedGenerator(harmony_notes), 
                channel=1
            )
        except Exception as e:
            print(f"Warning: Failed to generate harmony: {e}")

    # --- 低音轨道 ---
    # 简单的和声根音轨道，作为伴奏
    if "harmony" in preset:
        harmony_cfg = preset["harmony"]
        strategy_name = harmony_cfg.get("progression", "progression")
        
        # 重新获取一次根音数据用于低音 (实际项目中可以复用上面的数据)
        bass_gen = HarmonyGenerator(
            strategy_name="progression",
            key=key,
            progression_name=strategy_name,
            beats_per_bar=4
        )
        try:
            bass_roots = bass_gen.generate(num_bars=bars)
            # 低音直接使用根音，降低一个八度让听感更厚实
            bass_notes = [(note - 12, dur) for note, dur in bass_roots]
            
            arranger.add_track(
                name="Bass",
                generator=PrecomputedGenerator(bass_notes),
                channel=2
            )
        except Exception as e:
            print(f"Warning: Failed to generate bass: {e}")

    # 5. 保存文件
    try:
        arranger.save(args.output)
        print(f"Successfully generated MIDI file: {args.output}")
    except Exception as e:
        print(f"Error saving MIDI file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
