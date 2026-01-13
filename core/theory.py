from enum import Enum
from dataclasses import dataclass

class Key(Enum):
    C_MAJOR = [60, 62, 64, 65, 67, 69, 71]
    A_MINOR = [57, 59, 60, 62, 64, 65, 67]
    # 可扩展12个调

class ChordQuality(Enum):
    MAJOR = [0, 4, 7]
    MINOR = [0, 3, 7]
    DIMINISHED = [0, 3, 6]

@dataclass
class Chord:
    root: int  # 根音在音阶中的级数（0-6）
    quality: ChordQuality

    def get_midi_notes(self, key: Key, octave: int = 4):
        """计算实际MIDI音高"""
        base_note = key.value[self.root] + (octave-4)*12
        return [base_note + offset for offset in self.quality.value]

# 经典进行是策略，不是硬编码
PROGRESSIONS = {
    "pop": [(0, ChordQuality.MAJOR), (4, ChordQuality.MAJOR),
            (5, ChordQuality.MINOR), (3, ChordQuality.MAJOR)],
    "jazz_251": [(1, ChordQuality.MINOR), (4, ChordQuality.MAJOR),
                 (0, ChordQuality.MAJOR)],
}
