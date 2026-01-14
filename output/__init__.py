"""MIDI Music Generator - Output Package

输出模块，负责将生成的音乐数据保存为各种格式。
"""

from .midi_writer import (
    NoteEvent,
    TrackData,
    MidiWriter,
    create_midi_from_simple_tracks,
)

__all__ = [
    'NoteEvent',
    'TrackData',
    'MidiWriter',
    'create_midi_from_simple_tracks',
]
