#!/usr/bin/env python3
"""
MIDI Music Generator - 一个命令行MIDI音乐生成器
此程序允许用户通过命令行参数生成简单的MIDI音乐文件
"""

import argparse
import random
from mido import Message, MidiFile, MidiTrack, MetaMessage
import os
from config import *

def create_midi_track(track_name: str) -> tuple[MidiFile, MidiTrack]:
    """创建带基础设置的MIDI音轨"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(MetaMessage('track_name', name=track_name, time=0))
    tempo = int(60 * 1000000 / DEFAULT_TEMPO)
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    return mid, track

def generate_random_melody(length=DEFAULT_MELODY_LENGTH, note_range=(DEFAULT_NOTE_RANGE_START, DEFAULT_NOTE_RANGE_END), output_file=DEFAULT_OUTPUT_FILE):
    """
    生成随机旋律的MIDI文件

    :param length: 音符数量
    :param note_range: 音符范围（MIDI音高）
    :param output_file: 输出文件名
    """
    mid, track = create_midi_track('Random Melody Track')

    # 添加一些随机音符
    for i in range(length):
        # 随机选择音高
        note = random.randint(*note_range)

        # 随机力度 (64-127)
        velocity = random.randint(64, 127)

        # 随机时长（以ticks为单位）
        duration = random.choice([200, 400, 600, 800])

        # 添加音符开始消息
        track.append(Message('note_on', channel=MELODY_CHANNEL, note=note, velocity=velocity, time=0))

        # 添加音符结束消息
        track.append(Message('note_off', channel=MELODY_CHANNEL, note=note, velocity=velocity, time=duration))

    # 保存MIDI文件
    mid.save(output_file)
    print(f"随机旋律已保存为 {output_file}")


def generate_chord_progression(root_note=DEFAULT_NOTE_RANGE_START, num_chords=DEFAULT_CHORD_COUNT, output_file=DEFAULT_OUTPUT_FILE):
    """
    生成和弦进行的MIDI文件

    :param root_note: 根音符 (MIDI音高值)
    :param num_chords: 和弦数量
    :param output_file: 输出文件名
    """
    mid, track = create_midi_track('Chord Progression Track')

    for i in range(num_chords):
        # 随机选择一个和弦类型
        chord_type_name = random.choice(list(CHORD_TYPES.keys()))
        chord_type = CHORD_TYPES[chord_type_name]

        # 计算和弦音符
        notes = [root_note + offset for offset in chord_type]

        # 所有note_on同时发出（time=0）
        for note in notes:
            track.append(Message('note_on', channel=MELODY_CHANNEL, note=note, velocity=64, time=0))

        # 只有第一个note_off有延迟，其余time=0
        for i, note in enumerate(notes):
            time = 480 if i == 0 else 0  # 第一个off消息决定和弦时长
            track.append(Message('note_off', channel=MELODY_CHANNEL, note=note, velocity=64, time=time))

        # 随机调整下次循环的根音
        root_note += random.choice([-12, -5, -4, -3, 3, 4, 5, 12])  # 半音程偏移
        # 确保音符在合理范围内
        root_note = max(40, min(80, root_note))

    # 保存MIDI文件
    mid.save(output_file)
    print(f"和弦进行已保存为 {output_file}")


def generate_simple_rhythm(output_file=DEFAULT_OUTPUT_FILE):
    """
    生成简单的节拍MIDI文件

    :param output_file: 输出文件名
    """
    mid, track = create_midi_track('Simple Rhythm Track')

    # 鼓组音符定义 (MIDI标准鼓组)
    kick_drum = 36  # 底鼓
    snare_drum = 38  # 军鼓
    closed_hihat = 42  # 踩镲

    # 生成4/4拍节拍模式
    for bar in range(4):  # 四个小节
        for beat in range(16):  # 每小节四拍，每拍四分音符
            # 底鼓：每小节第一拍
            if beat % 4 == 0:
                track.append(Message('note_on', channel=DRUM_CHANNEL, note=kick_drum, velocity=90, time=0))
                track.append(Message('note_off', channel=DRUM_CHANNEL, note=kick_drum, velocity=90, time=240))

            # 军鼓：第二和第四拍的一半
            elif beat % 4 == 2:
                track.append(Message('note_on', channel=DRUM_CHANNEL, note=snare_drum, velocity=80, time=0))
                track.append(Message('note_off', channel=DRUM_CHANNEL, note=snare_drum, velocity=80, time=240))

            # 踩镲：每一拍
            track.append(Message('note_on', channel=DRUM_CHANNEL, note=closed_hihat, velocity=70, time=0))
            track.append(Message('note_off', channel=DRUM_CHANNEL, note=closed_hihat, velocity=70, time=120))

            # 再添加一个踩镲音符在每拍的后半部分
            track.append(Message('note_on', channel=DRUM_CHANNEL, note=closed_hihat, velocity=60, time=0))
            track.append(Message('note_off', channel=DRUM_CHANNEL, note=closed_hihat, velocity=60, time=120))

    # 保存MIDI文件
    mid.save(output_file)
    print(f"简单节拍已保存为 {output_file}")


def main():
    parser = argparse.ArgumentParser(description='MIDI Music Generator - 生成MIDI音乐文件')
    parser.add_argument(
        'output_file',
        nargs='?',
        default=DEFAULT_OUTPUT_FILE,
        help=f'输出的MIDI文件名 (默认: {DEFAULT_OUTPUT_FILE})'
    )

    parser.add_argument(
        '--mode',
        choices=['melody', 'chord', 'rhythm'],
        default=DEFAULT_MODE,
        help='生成模式: melody(旋律), chord(和弦), rhythm(节拍)'
    )

    parser.add_argument(
        '--length',
        type=int,
        default=DEFAULT_MELODY_LENGTH,
        help=f'音符数量 (仅用于旋律模式, 默认: {DEFAULT_MELODY_LENGTH})'
    )

    parser.add_argument(
        '--note-range-start',
        type=int,
        default=DEFAULT_NOTE_RANGE_START,
        help=f'音符范围起始值 (默认: {DEFAULT_NOTE_RANGE_START}, C4)'
    )

    parser.add_argument(
        '--note-range-end',
        type=int,
        default=DEFAULT_NOTE_RANGE_END,
        help=f'音符范围结束值 (默认: {DEFAULT_NOTE_RANGE_END}, C5)'
    )

    parser.add_argument(
        '--chords',
        type=int,
        default=DEFAULT_CHORD_COUNT,
        help=f'和弦数量 (仅用于和弦模式, 默认: {DEFAULT_CHORD_COUNT})'
    )

    parser.add_argument('--seed', type=int, help='随机种子')
    args = parser.parse_args()
    if args.seed is not None:
        random.seed(args.seed)

    # 确保输出文件以.mid结尾
    if not args.output_file.endswith('.mid'):
        args.output_file += '.mid'

    if args.length <= 0:
        parser.error("音符数量必须为正整数")
    if args.note_range_start >= args.note_range_end:
        parser.error("音符范围起始值必须小于结束值")

    # 根据选择的模式生成MIDI文件
    if args.mode == 'melody':
        generate_random_melody(
            length=args.length,
            note_range=(args.note_range_start, args.note_range_end),
            output_file=args.output_file
        )
    elif args.mode == 'chord':
        generate_chord_progression(
            root_note=args.note_range_start,
            num_chords=args.chords,
            output_file=args.output_file
        )
    elif args.mode == 'rhythm':
        generate_simple_rhythm(output_file=args.output_file)

    print(f"生成配置:")
    print(f"  - 模式: {args.mode}")
    print(f"  - 输出文件: {args.output_file}")
    if args.mode == 'melody':
        print(f"  - 音符数量: {args.length}")

if __name__ == "__main__":
    main()