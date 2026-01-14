"""MIDI Music Generator - Global Configuration

这个模块提供全局配置选项，包括：
- MIDI默认设置
- 生成器默认参数
- 文件路径配置
- 调试和日志设置
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class MidiConfig:
    """MIDI配置"""
    default_tempo: int = 120
    default_ticks_per_beat: int = 480
    default_time_signature: tuple = (4, 4)
    default_velocity: int = 100
    min_velocity: int = 40
    max_velocity: int = 127

    # 音符范围
    min_note: int = 36  # C2
    m
