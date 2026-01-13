#!/usr/bin/env python3
"""
MIDI Music Generator - 演示脚本
此脚本演示如何使用MIDI生成器的不同功能
"""

import os
import time
import random
from midi_generator import (
    generate_random_melody,
    generate_chord_progression,
    generate_simple_rhythm
)

def demo_melody():
    """演示旋律生成功能"""
    print("🎵 正在生成随机旋律...")
    filename = f"demo_melody_{int(time.time())}.mid"
    generate_random_melody(length=20, note_range=(55, 75), output_file=filename)
    print(f"✅ 旋律已保存为 {filename}\n")


def demo_chord_progression():
    """演示和弦生成功能"""
    print("🎹 正在生成和弦进行...")
    filename = f"demo_chord_{int(time.time())}.mid"
    generate_chord_progression(root_note=60, num_chords=6, output_file=filename)
    print(f"✅ 和弦进行已保存为 {filename}\n")


def demo_rhythm():
    """演示节拍生成功能"""
    print("🥁 正在生成简单节拍...")
    filename = f"demo_rhythm_{int(time.time())}.mid"
    generate_simple_rhythm(output_file=filename)
    print(f"✅ 节拍已保存为 {filename}\n")


def demo_custom_melody():
    """演示自定义旋律生成"""
    print("🎼 正在生成自定义旋律...")
    filename = f"demo_custom_{int(time.time())}.mid"

    # 创建一个稍微复杂一点的旋律
    from mido import Message, MidiFile, MidiTrack, MetaMessage
    from config import MELODY_CHANNEL, DEFAULT_TEMPO  # 修改为具体导入

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # 添加标题元信息
    track.append(MetaMessage('track_name', name='Custom Demo Track', time=0))
    tempo = int(60 * 1000000 / DEFAULT_TEMPO)  # 默认速度 120 BPM
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    # 创建一个简单的旋律模式
    scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C大调音阶
    for i in range(16):
        note = random.choice(scale)
        velocity = random.randint(70, 100)
        duration = random.choice([240, 480])  # 八分音符或四分音符

        track.append(Message('note_on', channel=MELODY_CHANNEL, note=note, velocity=velocity, time=0))
        track.append(Message('note_off', channel=MELODY_CHANNEL, note=note, velocity=velocity, time=duration))

    mid.save(filename)
    print(f"✅ 自定义旋律已保存为 {filename}\n")


def main():
    print("🌟 MIDI Music Generator 演示程序 🌟\n")
    print("此程序将演示MIDI生成器的不同功能\n")

    try:
        # 执行各个演示
        demo_melody()
        time.sleep(1)  # 稍作停顿

        demo_chord_progression()
        time.sleep(1)

        demo_rhythm()
        time.sleep(1)

        demo_custom_melody()

        print("🎉 所有演示已完成！")
        print("\n您可以使用任何MIDI播放器或音乐编辑软件打开生成的文件。")
        print("如果您想尝试更多选项，请使用命令行运行 midi_generator.py 查看详细帮助。")

    except KeyboardInterrupt:
        print("\n❌ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")


if __name__ == "__main__":
    main()