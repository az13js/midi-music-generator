"""MIDI Music Generator - MIDI Writer Module

这个模块提供了高级的MIDI文件写入接口，包括：
- MIDI文件创建和保存
- 多轨音轨管理
- 控制变更事件处理
- 表情和力度曲线应用
"""

from typing import List, Tuple, Optional, Dict, Union
from dataclasses import dataclass
import copy

from mido import MidiFile, MidiTrack, MetaMessage, Message, bpm2tempo
from core.theory import Key, Chord, get_scale_notes, get_chord_intervals


@dataclass
class NoteEvent:
    """音符事件数据类"""
    note: int  # MIDI音高
    velocity: int  # 力度 (0-127)
    start_time: int  # 开始时间（ti
