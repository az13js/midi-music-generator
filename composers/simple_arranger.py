from mido import MidiFile, MidiTrack

class SimpleArranger:
    def __init__(self, tempo: int, key: Key):
        self.mid = MidiFile()
        self.tempo = tempo
        self.key = key

    def add_track(self, name: str, generator, channel: int):
        """动态添加音轨"""
        track = MidiTrack()
        self.mid.tracks.append(track)
        # 添加元信息...

        notes = generator.generate(self.key)
        self._write_notes(track, notes, channel)
        return self

    def _write_notes(self, track, notes, channel):
        """统一的MIDI写入逻辑"""
        # 可在这里统一处理力度曲线、人性化等
        pass

    def save(self, filepath: str):
        self.mid.save(filepath)
