"""MIDI Music Generator - Core Rhythm Module
这个模块提供了节奏型的定义和基础数据，属于不可变的音乐理论层。
包括： - 基础节拍类型 - 预定义节奏型 - 节奏模式分析工具
"""
from enum import Enum
from typing import List, Tuple, Dict
import math

class BeatType(Enum):
    """拍号类型枚举"""
    SIMPLE_DUPLE = 2      # 单二拍
    SIMPLE_TRIPLE = 3     # 单三拍
    SIMPLE_QUADRUPLE = 4  # 单四拍
    COMPOUND_DUPLE = 6    # 复二拍
    COMPOUND_TRIPLE = 9   # 复三拍
    COMPOUND_QUADRUPLE = 12  # 复四拍

class TimeSignature(Enum):
    """拍号枚举"""
    TWO_FOUR = (2, 4)   # 2/4 拍
    THREE_FOUR = (3, 4) # 3/4 拍
    FOUR_FOUR = (4, 4)  # 4/4 拍
    SIX_EIGHT = (6, 8)  # 6/8 拍
    THREE_EIGHT = (3, 8) # 3/8 拍
    NINE_EIGHT = (9, 8)  # 9/8 拍
    TWELVE_EIGHT = (12, 8) # 12/8 拍
