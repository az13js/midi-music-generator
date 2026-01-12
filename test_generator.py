#!/usr/bin/env python3
"""
MIDI Music Generator - 测试脚本
此脚本测试MIDI生成器的各种功能
"""

import os
import sys
from mido import MidiFile
from midi_generator import (
    generate_random_melody,
    generate_chord_progression,
    generate_simple_rhythm
)

def test_melody_generation():
    """测试旋律生成功能"""
    print("测试旋律生成功能...")
    try:
        generate_random_melody(length=10, note_range=(60, 72), output_file='test_melody.mid')
        
        # 验证文件是否创建
        if os.path.exists('test_melody.mid'):
            mid = MidiFile('test_melody.mid')
            print(f"  ✓ 文件创建成功，包含 {len(mid.tracks)} 个音轨")
            
            # 删除测试文件
            os.remove('test_melody.mid')
            print("  ✓ 测试文件已清理")
        else:
            print("  ✗ 文件未创建")
            return False
            
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False
        
    print("  ✓ 旋律生成功能测试通过\n")
    return True


def test_chord_generation():
    """测试和弦生成功能"""
    print("测试和弦生成功能...")
    try:
        generate_chord_progression(root_note=60, num_chords=4, output_file='test_chord.mid')
        
        # 验证文件是否创建
        if os.path.exists('test_chord.mid'):
            mid = MidiFile('test_chord.mid')
            print(f"  ✓ 文件创建成功，包含 {len(mid.tracks)} 个音轨")
            
            # 删除测试文件
            os.remove('test_chord.mid')
            print("  ✓ 测试文件已清理")
        else:
            print("  ✗ 文件未创建")
            return False
            
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False
        
    print("  ✓ 和弦生成功能测试通过\n")
    return True


def test_rhythm_generation():
    """测试节拍生成功能"""
    print("测试节拍生成功能...")
    try:
        generate_simple_rhythm(output_file='test_rhythm.mid')
        
        # 验证文件是否创建
        if os.path.exists('test_rhythm.mid'):
            mid = MidiFile('test_rhythm.mid')
            print(f"  ✓ 文件创建成功，包含 {len(mid.tracks)} 个音轨")
            
            # 删除测试文件
            os.remove('test_rhythm.mid')
            print("  ✓ 测试文件已清理")
        else:
            print("  ✗ 文件未创建")
            return False
            
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        return False
        
    print("  ✓ 节拍生成功能测试通过\n")
    return True


def main():
    print("开始测试 MIDI Music Generator...\n")
    
    all_tests_passed = True
    
    all_tests_passed &= test_melody_generation()
    all_tests_passed &= test_chord_generation()
    all_tests_passed &= test_rhythm_generation()
    
    if all_tests_passed:
        print("所有测试均已通过！✓")
    else:
        print("部分测试失败 ✗")
        sys.exit(1)


if __name__ == "__main__":
    main()