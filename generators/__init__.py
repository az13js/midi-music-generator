from .melody import *
from .harmony import *
from .rhythm import *

__all__ = [
    # 从 melody 模块导出的项
    "MelodyGenerator",
    "Note",
    "Scale",
    "Key",
    "generate_melody",
    "create_progression",
    "get_note_from_degree",

    # 从 harmony 模块导出的项
    "ChordProgressionGenerator",
    "Chord",
    "ChordQuality",
    "HarmonicRhythm",
    "generate_chord_progression",
    "create_chord",
    "transpose_chord",

    # 从 rhythm 模块导出的项
    "NoteType",
    "RhythmPattern",
    "RhythmStrategy",
    "RandomRhythmStrategy",
    "PatternBasedRhythmStrategy",
    "SwingRhythmStrategy",
    "GrooveRhythmStrategy",
    "HybridRhythmStrategy",
    "RhythmGenerator",
    "NOTE_DURATION_MAP",
    "RHYTHM_PATTERNS",
    "create_rhythm",
    "create_groove_rhythm",
    "create_pattern_rhythm",
    "get_rhythm_stats",
]