from mido import MidiFile, MidiTrack, MetaMessage, Message
from core.theory import Key
import random

class SimpleArranger:
    def __init__(self, tempo: int, key: Key):
        self.mid = MidiFile()
        self.tempo = tempo
        self.key = key

        # 设定 MIDI 分辨率 (TPQN: Ticks Per Quarter Note)
        self.ticks_per_beat = 480

        # 0号轨道用于存放全局 Meta 信息 (速度、调号、拍号)
        self.meta_track = MidiTrack()
        self.mid.tracks.append(self.meta_track)

        # 1. 设置速度
        microseconds_per_beat = int(60_000_000 / tempo)
        self.meta_track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat))

        # 2. 设置拍号 - 默认 4/4
        self.meta_track.append(MetaMessage('time_signature', numerator=4, denominator=4,
                                           clocks_per_click=24, notated_32nd_notes_per_beat=8))
        self.meta_track.append(MetaMessage('key_signature', key=key.value))

    def _get_note_duration_ticks(self, duration_beats: float) -> int:
        """将拍数转换为 ticks"""
        ticks = int(duration_beats * self.ticks_per_beat)
        # 添加微小的随机偏移（人性化）
        variation = int(ticks * 0.05 * (random.random() - 0.5))
        return max(1, ticks + variation)

    def _calculate_structure_factor(self, current_time_ticks: int, total_ticks: int) -> float:
        """
        根据乐曲位置计算结构因子（力度系数）
        模拟前奏（弱）、高潮（强）、尾声（弱）的效果
        """
        if total_ticks == 0:
            return 1.0

        progress = current_time_ticks / total_ticks

        # 简单的结构逻辑：
        # 前 15% (前奏): 0.6 ~ 1.0 渐入
        # 15% - 70% (主体): 1.0
        # 70% - 90% (高潮): 1.0 ~ 1.2 渐强
        # 90% - 100% (尾声): 1.2 ~ 0.7 渐出

        if progress < 0.15:
            # 前奏渐入
            return 0.6 + (progress / 0.15) * 0.4
        elif progress < 0.70:
            # 主体保持
            return 1.0
        elif progress < 0.90:
            # 高潮渐强
            return 1.0 + ((progress - 0.70) / 0.20) * 0.2
        else:
            # 尾声渐弱
            return 1.2 - ((progress - 0.90) / 0.10) * 0.5

    def add_track(self, name: str, generator, channel: int, program: int = 0):
        """
        动态添加音轨
        :param name: 音轨名称
        :param generator: 生成器实例，必须实现 generate(key) 方法
        :param channel: MIDI 通道号 (0-15)
        :param program: GM音色编号 (0-127)，默认为0 (Acoustic Grand Piano)
        """
        track = MidiTrack()
        self.mid.tracks.append(track)

        # 添加音轨名称
        track.append(MetaMessage('track_name', name=name))

        # 设置音色 (Program Change)
        # 注意：time=0 表示紧随前面的消息立即发送
        track.append(Message('program_change', program=program, time=0, channel=channel))

        # 获取音符数据
        notes_data = generator.generate(self.key)

        # 统一转换为 (note, duration, velocity) 格式进行处理
        normalized_notes = []
        if isinstance(notes_data, list) and len(notes_data) > 0:
            first_item = notes_data[0]

            # 1. 预计算总时长，用于结构分析
            total_duration_beats = 0
            for item in notes_data:
                if isinstance(item, (tuple, list)):
                    total_duration_beats += item[1]
                else:
                    total_duration_beats += 1.0

            total_ticks = int(total_duration_beats * self.ticks_per_beat)
            current_time_ticks = 0

            for item in notes_data:
                # 解析数据
                if isinstance(item, (tuple, list)):
                    if len(item) >= 3:
                        note, duration_beats, velocity = item[0], item[1], item[2]
                    elif len(item) == 2:
                        note, duration_beats = item[0], item[1]
                        velocity = 100 # 默认力度
                    else:
                        continue
                elif isinstance(item, int):
                    note = item
                    duration_beats = 1.0
                    velocity = 100
                else:
                    continue

                duration_ticks = self._get_note_duration_ticks(duration_beats)

                # 应用结构因子（高潮、前奏、尾声处理）
                structure_factor = self._calculate_structure_factor(current_time_ticks, total_ticks)
                final_velocity = int(min(127, max(1, velocity * structure_factor)))

                # Note On
                track.append(Message('note_on', note=note, velocity=final_velocity, time=0, channel=channel))

                # Note Off
                track.append(Message('note_off', note=note, velocity=0, time=duration_ticks, channel=channel))

                # 更新时间指针
                current_time_ticks += duration_ticks

        return self

    def save(self, filepath: str):
        self.mid.save(filepath)
