from mido import MidiFile, MidiTrack, MetaMessage, Message
from core.theory import Key

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

        # 1. 设置速度(Tempo)
        # Microseconds per beat = 60,000,000 / BPM
        microseconds_per_beat = int(60_000_000 / tempo)
        self.meta_track.append(MetaMessage('set_tempo', tempo=microseconds_per_beat))

        # 2. 设置拍号 (Time Signature) - 默认 4/4
        self.meta_track.append(MetaMessage('time_signature', numerator=4, denominator=4,
                                           clocks_per_click=24, notated_32nd_notes_per_beat=8))
        self.meta_track.append(MetaMessage('key_signature', key=key.value))

    def _get_note_duration_ticks(self, duration_beats: float) -> int:
        """将拍数转换为 ticks"""
        return int(duration_beats * self.ticks_per_beat)

    def add_track(self, name: str, generator, channel: int):
        """
        动态添加音轨
        :param name: 音轨名称
        :param generator: 生成器实例，必须实现 generate(key) 方法
        :param channel: MIDI 通道号 (0-15)
        """
        track = MidiTrack()
        self.mid.tracks.append(track)

        # 添加音轨名称
        track.append(MetaMessage('track_name', name=name))

        # 获取音符数据
        # 这里的 generator 可能是 MelodyGenerator 或 HarmonyGenerator
        # 它们通常返回 List[int] (仅有音高) 或 List[Tuple[int, float]] (音高, 时值)
        notes_data = generator.generate(self.key)

        # 统一转换为 (note, duration) 格式进行处理
        normalized_notes = []
        if isinstance(notes_data, list) and len(notes_data) > 0:
            first_item = notes_data[0]
            if isinstance(first_item, (tuple, list)):
                # 如果是元组，直接使用 (假设格式为 pitch, duration)
                normalized_notes = notes_data
            elif isinstance(first_item, int):
                # 如果只有音高，默认时值为 1.0 (一拍)
                normalized_notes = [(note, 1.0) for note in notes_data]

        # 写入音符消息
        current_time = 0
        default_velocity = 100

        for note, duration_beats in normalized_notes:
            duration_ticks = self._get_note_duration_ticks(duration_beats)

            # Note On (time=0 表示紧接上一个事件)
            track.append(Message('note_on', note=note, velocity=default_velocity, time=0, channel=channel))

            # Note Off (time=duration_ticks 表示保持多久)
            track.append(Message('note_off', note=note, velocity=0, time=duration_ticks, channel=channel))

        return self

    def _write_notes(self, track, notes, channel):
        """
        统一的MIDI 写入逻辑 (保留方法以兼容旧代码，实际逻辑已整合到 add_track)
        可在这里统一处理力度曲线、人性化等
        """
        # 预留接口：如果未来需要对已有的 notes 列表进行后处理再写入
        pass

    def save(self, filepath: str):
        self.mid.save(filepath)
