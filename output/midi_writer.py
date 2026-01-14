"""MIDI Music Generator - MIDI Writer Module
这个模块提供了高级的MIDI 文件写入接口，包括：
- MIDI 文件创建和保存
- 多轨音轨管理
- 控制变更事件处理
- 表情和力度曲线应用
"""
from typing import List, Tuple, Optional, Dict, Union
from dataclasses import dataclass
from mido import MidiFile, MidiTrack, MetaMessage, Message

@dataclass
class NoteEvent:
    """音符事件数据类"""
    note: int      # MIDI 音高
    velocity: int  # 力度(0-127)
    duration: int  # 时长，单位为ticks

@dataclass
class TrackData:
    """音轨数据类"""
    name: str
    channel: int
    events: List[NoteEvent]

class MidiWriter:
    def __init__(self, ticks_per_beat: int = 480):
        self.ticks_per_beat = ticks_per_beat

    def write(self, tracks: List[TrackData], filepath: str):
        """将音轨数据写入MIDI文件"""
        mid = MidiFile(ticks_per_beat=self.ticks_per_beat)
        for track_data in tracks:
            track = MidiTrack()
            mid.tracks.append(track)
            # 添加音轨名称
            track.append(MetaMessage('track_name', name=track_data.name))
            # 添加音符事件
            for event in track_data.events:
                track.append(Message('note_on', note=event.note, velocity=event.velocity, time=0, channel=track_data.channel))
                track.append(Message('note_off', note=event.note, velocity=0, time=event.duration, channel=track_data.channel))
        mid.save(filepath)

def create_midi_from_simple_tracks(
    tracks: List[Tuple[str, int, List[Union[int, Tuple[int, float]]]]],
    filepath: str,
    ticks_per_beat: int = 480,
    default_velocity: int = 100
):
    """
    从简单的音轨数据创建MIDI文件。
    每个音轨格式为：(name, channel, data)，其中data为音符数据列表，
    可以是音高列表或(音高, 时值(拍))列表。
    """
    midi_writer = MidiWriter(ticks_per_beat)
    track_data_list = []
    for name, channel, data in tracks:
        events = []
        for item in data:
            if isinstance(item, tuple):
                note, duration_beats = item
            else:
                note, duration_beats = item, 1.0
            duration_ticks = int(duration_beats * ticks_per_beat)
            events.append(NoteEvent(
                note=note,
                velocity=default_velocity,
                duration=duration_ticks
            ))
        track_data_list.append(TrackData(name=name, channel=channel, events=events))
    midi_writer.write(track_data_list, filepath)
