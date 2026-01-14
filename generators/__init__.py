from .melody import *
from .harmony import *
from .rhythm import *

__all__ = [
    # 从 melody 模块导出的项 (已修正名称)
    "MelodyGenerator",
    "MelodyStrategy",
    "RandomWalkStrategy",
    "PatternBasedStrategy",
    "NeuralStyleStrategy",
    "GeneticOptimizationStrategy",
    "MonteCarloTreeSearchStrategy",
    "create_melody_from_strategy",
    "optimize_melody_for_chords",

    # 从 harmony 模块导出的项
    "HarmonyStrategy",
    "ProgressionBasedStrategy",
    "DiatonicStrategy",
    "FunctionalStrategy",
    "HybridHarmonyStrategy",
    "HarmonyGenerator",
    "create_harmony",
    "create_progression_harmony",
    "create_style_harmony",
    "HarmonyGenerator_Legacy",

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
