"""
MIDI Music Generator - Core Music Theory Module

这个模块提供了完整的音乐理论基础，包括：
- 所有12个大调和小调
- 各种和弦类型（三和弦、七和弦、九和弦等）
- 音阶类型（大调、小调、各种教会调式等）
- 和弦进行模式
- 音程关系
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
import random

# ==================== 基础常量 ====================

# MIDI音符编号
C4 = 60
A4 = 69

# 音程名称对应的半音数
INTERVALS = {
    "unison": 0,
    "minor_second": 1,
    "major_second": 2,
    "minor_third": 3,
    "major_third": 4,
    "perfect_fourth": 5,
    "tritone": 6,
    "perfect_fifth": 7,
    "minor_sixth": 8,
    "major_sixth": 9,
    "minor_seventh": 10,
    "major_seventh": 11,
    "octave": 12
}

# ==================== 调式和音阶 ====================

class ScaleType(Enum):
    """音阶类型枚举"""
    MAJOR = "major"           # 大调
    MINOR = "minor"           # 自然小调
    HARMONIC_MINOR = "harmonic_minor"  # 和声小调
    MELODIC_MINOR = "melodic_minor"   # 旋律小调

    # 教会调式
    DORIAN = "dorian"         # 多里安调式
    PHRYGIAN = "phrygian"     # 弗里吉亚调式
    LYDIAN = "lydian"         # 利底亚调式
    MIXOLYDIAN = "mixolydian" # 混合利底亚调式
    LOCRIAN = "locrian"       # 洛克里安调式

    # 其他音阶
    PENTATONIC_MAJOR = "pentatonic_major"   # 大调五声音阶
    PENTATONIC_MINOR = "pentatonic_minor"   # 小调五声音阶
    BLUES = "blues"           # 布鲁斯音阶
    CHROMATIC = "chromatic"   # 半音阶
    WHOLE_TONE = "whole_tone" # 全音阶

class Key(Enum):
    """所有12个调，包含大调和小调"""

    # 大调 (C大调 = C4到B4)
    C_MAJOR = "C"
    C_SHARP_MAJOR = "C#"
    D_FLAT_MAJOR = "Db"
    D_MAJOR = "D"
    D_SHARP_MAJOR = "D#"
    E_FLAT_MAJOR = "Eb"
    E_MAJOR = "E"
    F_MAJOR = "F"
    F_SHARP_MAJOR = "F#"
    G_FLAT_MAJOR = "Gb"
    G_MAJOR = "G"
    G_SHARP_MAJOR = "G#"
    A_FLAT_MAJOR = "Ab"
    A_MAJOR = "A"
    A_SHARP_MAJOR = "A#"
    B_FLAT_MAJOR = "Bb"
    B_MAJOR = "B"

    # 小调
    C_MINOR = "Cm"
    C_SHARP_MINOR = "C#m"
    D_MINOR = "Dm"
    D_SHARP_MINOR = "D#m"
    E_MINOR = "Em"
    F_MINOR = "Fm"
    F_SHARP_MINOR = "F#m"
    G_MINOR = "Gm"
    G_SHARP_MINOR = "G#m"
    A_MINOR = "Am"
    A_SHARP_MINOR = "A#m"
    B_MINOR = "Bm"

    @property
    def tonic(self) -> int:
        """获取主音的MIDI音符编号（默认以C4=60为基准）"""
        base_notes = {
            "C": 60, "C#": 61, "Db": 61, "D": 62, "D#": 63, "Eb": 63,
            "E": 64, "F": 65, "F#": 66, "Gb": 66, "G": 67, "G#": 68,
            "Ab": 68, "A": 69, "A#": 70, "Bb": 70, "B": 71
        }
        key_name = self.value.replace("m", "")  # 移除小调标记
        return base_notes.get(key_name, 60)

    @property
    def is_minor(self) -> bool:
        """判断是否为小调"""
        return self.value.endswith("m")

    @property
    def scale_type(self) -> ScaleType:
        """获取默认音阶类型"""
        return ScaleType.MINOR if self.is_minor else ScaleType.MAJOR

def get_scale_intervals(scale_type: ScaleType) -> List[int]:
    """
    获取指定音阶类型的半音间隔模式

    参数:
        scale_type: 音阶类型

    返回:
        半音间隔列表，例如大调是 [2,2,1,2,2,2,1]
    """
    scales = {
        ScaleType.MAJOR: [2, 2, 1, 2, 2, 2, 1],
        ScaleType.MINOR: [2, 1, 2, 2, 1, 2, 2],
        ScaleType.HARMONIC_MINOR: [2, 1, 2, 2, 1, 3, 1],
        ScaleType.MELODIC_MINOR: [2, 1, 2, 2, 2, 2, 1],
        ScaleType.DORIAN: [2, 1, 2, 2, 2, 1, 2],
        ScaleType.PHRYGIAN: [1, 2, 2, 2, 1, 2, 2],
        ScaleType.LYDIAN: [2, 2, 2, 1, 2, 2, 1],
        ScaleType.MIXOLYDIAN: [2, 2, 1, 2, 2, 1, 2],
        ScaleType.LOCRIAN: [1, 2, 2, 1, 2, 2, 2],
        ScaleType.PENTATONIC_MAJOR: [2, 2, 3, 2, 3],
        ScaleType.PENTATONIC_MINOR: [3, 2, 2, 3, 2],
        ScaleType.BLUES: [3, 2, 1, 1, 3, 2],
        ScaleType.CHROMATIC: [1] * 12,
        ScaleType.WHOLE_TONE: [2] * 6
    }
    return scales.get(scale_type, [2, 2, 1, 2, 2, 2, 1])

def get_scale_notes(key: Key, scale_type: Optional[ScaleType] = None,
                   octave: int = 4, num_octaves: int = 1) -> List[int]:
    """
    获取指定调式的音阶音符

    参数:
        key: 调
        scale_type: 音阶类型，默认使用调的默认音阶类型
        octave: 起始八度
        num_octaves: 八度数量

    返回:
        MIDI音符编号列表
    """
    if scale_type is None:
        scale_type = key.scale_type

    intervals = get_scale_intervals(scale_type)
    tonic = key.tonic + (octave - 4) * 12

    notes = [tonic]
    current_note = tonic

    for interval in intervals * num_octaves:
        current_note += interval
        notes.append(current_note)

    return notes[:-1]  # 移除最后一个重复的主音

# ==================== 和弦类型和构建 ====================

class ChordQuality(Enum):
    """和弦性质枚举"""
    # 三和弦
    MAJOR = "major"           # 大三和弦 (1-3-5)
    MINOR = "minor"           # 小三和弦 (1-b3-5)
    DIMINISHED = "diminished" # 减三和弦 (1-b3-b5)
    AUGMENTED = "augmented"   # 增三和弦 (1-3-#5)
    SUSPENDED2 = "sus2"       # 挂二和弦 (1-2-5)
    SUSPENDED4 = "sus4"       # 挂四和弦 (1-4-5)

    # 七和弦
    MAJOR_SEVENTH = "major7"           # 大七和弦 (1-3-5-7)
    MINOR_SEVENTH = "minor7"           # 小七和弦 (1-b3-5-b7)
    DOMINANT_SEVENTH = "7"             # 属七和弦 (1-3-5-b7)
    DIMINISHED_SEVENTH = "dim7"        # 减七和弦 (1-b3-b5-bb7)
    HALF_DIMINISHED_SEVENTH = "m7b5"   # 半减七和弦 (1-b3-b5-b7)
    MINOR_MAJOR_SEVENTH = "mM7"        # 小大七和弦 (1-b3-5-7)
    AUGMENTED_MAJOR_SEVENTH = "augM7"  # 增大七和弦 (1-3-#5-7)
    AUGMENTED_SEVENTH = "aug7"         # 增七和弦 (1-3-#5-b7)

    # 九和弦
    MAJOR_NINTH = "maj9"      # 大九和弦
    MINOR_NINTH = "m9"        # 小九和弦
    DOMINANT_NINTH = "9"      # 属九和弦
    MINOR_MAJOR_NINTH = "mM9" # 小大九和弦

    # 十一和弦
    MAJOR_ELEVENTH = "maj11"   # 大十一和弦
    MINOR_ELEVENTH = "m11"     # 小十一和弦
    DOMINANT_ELEVENTH = "11"   # 属十一和弦

    # 十三和弦
    MAJOR_THIRTEENTH = "maj13" # 大十三和弦
    MINOR_THIRTEENTH = "m13"   # 小十三和弦
    DOMINANT_THIRTEENTH = "13" # 属十三和弦

def get_chord_intervals(quality: ChordQuality) -> List[int]:
    """
    获取和弦性质的半音间隔

    参数:
        quality: 和弦性质

    返回:
        半音间隔列表，相对于根音
    """
    chord_intervals = {
        # 三和弦
        ChordQuality.MAJOR: [0, 4, 7],
        ChordQuality.MINOR: [0, 3, 7],
        ChordQuality.DIMINISHED: [0, 3, 6],
        ChordQuality.AUGMENTED: [0, 4, 8],
        ChordQuality.SUSPENDED2: [0, 2, 7],
        ChordQuality.SUSPENDED4: [0, 5, 7],

        # 七和弦
        ChordQuality.MAJOR_SEVENTH: [0, 4, 7, 11],
        ChordQuality.MINOR_SEVENTH: [0, 3, 7, 10],
        ChordQuality.DOMINANT_SEVENTH: [0, 4, 7, 10],
        ChordQuality.DIMINISHED_SEVENTH: [0, 3, 6, 9],
        ChordQuality.HALF_DIMINISHED_SEVENTH: [0, 3, 6, 10],
        ChordQuality.MINOR_MAJOR_SEVENTH: [0, 3, 7, 11],
        ChordQuality.AUGMENTED_MAJOR_SEVENTH: [0, 4, 8, 11],
        ChordQuality.AUGMENTED_SEVENTH: [0, 4, 8, 10],

        # 九和弦
        ChordQuality.MAJOR_NINTH: [0, 4, 7, 11, 14],
        ChordQuality.MINOR_NINTH: [0, 3, 7, 10, 14],
        ChordQuality.DOMINANT_NINTH: [0, 4, 7, 10, 14],
        ChordQuality.MINOR_MAJOR_NINTH: [0, 3, 7, 11, 14],

        # 十一和弦
        ChordQuality.MAJOR_ELEVENTH: [0, 4, 7, 11, 14, 17],
        ChordQuality.MINOR_ELEVENTH: [0, 3, 7, 10, 14, 17],
        ChordQuality.DOMINANT_ELEVENTH: [0, 4, 7, 10, 14, 17],

        # 十三和弦
        ChordQuality.MAJOR_THIRTEENTH: [0, 4, 7, 11, 14, 17, 21],
        ChordQuality.MINOR_THIRTEENTH: [0, 3, 7, 10, 14, 17, 21],
        ChordQuality.DOMINANT_THIRTEENTH: [0, 4, 7, 10, 14, 17, 21],
    }

    return chord_intervals.get(quality, [0, 4, 7])

@dataclass
class Chord:
    """
    和弦数据类

    属性:
        root: 根音在音阶中的级数 (0-6)，0为主音
        quality: 和弦性质
        inversion: 和弦转位 (0=原位, 1=第一转位, 2=第二转位)
        bass_note: 低音音符编号（用于转位）
    """
    root: int
    quality: ChordQuality
    inversion: int = 0
    bass_note: Optional[int] = None

    def get_midi_notes(self, key: Key, octave: int = 4) -> List[int]:
        """
        计算实际的MIDI音符

        参数:
            key: 调
            octave: 八度

        返回:
            MIDI音符编号列表
        """
        # 获取音阶音符
        scale_notes = get_scale_notes(key, octave=octave, num_octaves=2)

        # 获取根音
        if self.root < len(scale_notes):
            root_note = scale_notes[self.root]
        else:
            root_note = scale_notes[0] + self.root * 2  # 近似计算

        # 获取和弦间隔
        intervals = get_chord_intervals(self.quality)

        # 计算和弦音符
        chord_notes = [root_note + interval for interval in intervals]

        # 处理转位
        if self.inversion > 0:
            # 将最低音上移一个八度
            inversion_count = min(self.inversion, len(chord_notes) - 1)
            for i in range(inversion_count):
                chord_notes[i] += 12

        # 如果有指定的低音，确保低音在最低位置
        if self.bass_note is not None:
            chord_notes = [self.bass_note] + [note for note in chord_notes if note != self.bass_note]

        return chord_notes

    def get_chord_name(self, key: Key) -> str:
        """
        获取和弦名称

        参数:
            key: 调

        返回:
            和弦名称字符串
        """
        # 获取音级名称
        scale_degrees = ["I", "II", "III", "IV", "V", "VI", "VII"]
        degree = scale_degrees[self.root % 7]

        # 转位标记
        inversion_suffix = ""
        if self.inversion == 1:
            inversion_suffix = "6"
        elif self.inversion == 2:
            inversion_suffix = "64"

        return f"{degree}{self.quality.value}{inversion_suffix}"

# ==================== 音级和和弦分析 ====================

class ScaleDegree(Enum):
    """音级枚举"""
    TONIC = 1        # 主音 (I)
    SUPERTONIC = 2   # 上主音 (II)
    MEDIANT = 3      # 中音 (III)
    SUBDOMINANT = 4  # 下属音 (IV)
    DOMINANT = 5     # 属音 (V)
    SUBMEDIANT = 6   # 下中音 (VI)
    SUBTONIC = 7     # 导音 (VII)

def get_diatonic_chord(degree: int, key: Key, quality_type: str = "major") -> Chord:
    """
    获取调内自然和弦

    参数:
        degree: 音级 (1-7)
        key: 调
        quality_type: 和弦质量类型 ("major" 或 "minor")

    返回:
        调内和弦
    """
    # 大调和弦等级性质
    major_qualities = [
        ChordQuality.MAJOR,        # I
        ChordQuality.MINOR,        # II
        ChordQuality.MINOR,        # III
        ChordQuality.MAJOR,        # IV
        ChordQuality.MAJOR,        # V
        ChordQuality.MINOR,        # VI
        ChordQuality.DIMINISHED    # VII
    ]

    # 小调和弦等级性质
    minor_qualities = [
        ChordQuality.MINOR,        # I
        ChordQuality.DIMINISHED,   # II
        ChordQuality.MAJOR,        # III
        ChordQuality.MINOR,        # IV
        ChordQuality.MINOR,        # V
        ChordQuality.MAJOR,        # VI
        ChordQuality.MAJOR         # VII (和声小调)
    ]

    if quality_type == "major" or not key.is_minor:
        qualities = major_qualities
    else:
        qualities = minor_qualities

    root = (degree - 1) % 7
    quality = qualities[root]

    return Chord(root=root, quality=quality)

# ==================== 和弦进行模式 ====================

@dataclass
class ChordProgression:
    """和弦进行模式"""
    name: str
    description: str
    chords: List[Tuple[int, ChordQuality]]  # (音级, 和弦性质)
    style: str = "general"  # 风格标记
    complexity: int = 1     # 复杂度等级 (1-5)

# 经典和弦进行库
CHORD_PROGRESSIONS = {
    # 流行音乐进行
    "pop_basic": ChordProgression(
        name="pop_basic",
        description="基础流行进行 I-V-vi-IV",
        chords=[(1, ChordQuality.MAJOR), (5, ChordQuality.MAJOR),
                (6, ChordQuality.MINOR), (4, ChordQuality.MAJOR)],
        style="pop",
        complexity=1
    ),

    "pop_50s": ChordProgression(
        name="pop_50s",
        description="50年代流行进行 I-vi-IV-V",
        chords=[(1, ChordQuality.MAJOR), (6, ChordQuality.MINOR),
                (4, ChordQuality.MAJOR), (5, ChordQuality.MAJOR)],
        style="pop",
        complexity=1
    ),

    # 爵士进行
    "jazz_251": ChordProgression(
        name="jazz_251",
        description="经典爵士ii-V-I进行",
        chords=[(2, ChordQuality.MINOR), (5, ChordQuality.DOMINANT_SEVENTH),
                (1, ChordQuality.MAJOR_SEVENTH)],
        style="jazz",
        complexity=2
    ),

    "jazz_rhythm": ChordProgression(
        name="jazz_rhythm",
        description="爵士节奏变化 I-vi-ii-V",
        chords=[(1, ChordQuality.MAJOR_SEVENTH), (6, ChordQuality.MINOR_SEVENTH),
                (2, ChordQuality.MINOR_SEVENTH), (5, ChordQuality.DOMINANT_SEVENTH)],
        style="jazz",
        complexity=2
    ),

    # 摇滚进行
    "rock_basic": ChordProgression(
        name="rock_basic",
        description="基础摇滚进行 I-IV-V",
        chords=[(1, ChordQuality.MAJOR), (4, ChordQuality.MAJOR),
                (5, ChordQuality.MAJOR)],
        style="rock",
        complexity=1
    ),

    # 布鲁斯进行
    "blues_basic": ChordProgression(
        name="blues_basic",
        description="12小节布鲁斯",
        chords=[(1, ChordQuality.DOMINANT_SEVENTH), (4, ChordQuality.DOMINANT_SEVENTH),
                (1, ChordQuality.DOMINANT_SEVENTH), (5, ChordQuality.DOMINANT_SEVENTH),
                (4, ChordQuality.DOMINANT_SEVENTH), (1, ChordQuality.DOMINANT_SEVENTH)],
        style="blues",
        complexity=2
    ),

    # 古典进行
    "classical_authentic": ChordProgression(
        name="classical_authentic",
        description="古典正格终止 V-I",
        chords=[(5, ChordQuality.MAJOR), (1, ChordQuality.MAJOR)],
        style="classical",
        complexity=1
    ),

    "classical_plagal": ChordProgression(
        name="classical_plagal",
        description="古典变格终止 IV-I",
        chords=[(4, ChordQuality.MAJOR), (1, ChordQuality.MAJOR)],
        style="classical",
        complexity=1
    ),

    # 现代流行
    "modern_trending": ChordProgression(
        name="modern_trending",
        description="现代流行趋势进行 vi-IV-I-V",
        chords=[(6, ChordQuality.MINOR), (4, ChordQuality.MAJOR),
                (1, ChordQuality.MAJOR), (5, ChordQuality.MAJOR)],
        style="pop",
        complexity=2
    ),

    # 复杂进行
    "complex_cycle": ChordProgression(
        name="complex_cycle",
        description="复杂五度圈进行",
        chords=[(1, ChordQuality.MAJOR_SEVENTH), (4, ChordQuality.DOMINANT_SEVENTH),
                (7, ChordQuality.DIMINISHED_SEVENTH), (3, ChordQuality.MINOR_SEVENTH),
                (6, ChordQuality.MINOR_SEVENTH), (2, ChordQuality.MINOR_SEVENTH),
                (5, ChordQuality.DOMINANT_SEVENTH), (1, ChordQuality.MAJOR_SEVENTH)],
        style="jazz",
        complexity=4
    )
}

def get_progression_by_name(name: str) -> Optional[ChordProgression]:
    """
    根据名称获取和弦进行

    参数:
        name: 进行名称

    返回:
        和弦进行对象，如果不存在返回None
    """
    return CHORD_PROGRESSIONS.get(name)

def get_progressions_by_style(style: str) -> List[ChordProgression]:
    """
    根据风格获取和弦进行列表

    参数:
        style: 风格名称

    返回:
        该风格的和弦进行列表
    """
    return [prog for prog in CHORD_PROGRESSIONS.values() if prog.style == style]

def get_random_progression(style: Optional[str] = None,
                          max_complexity: int = 5) -> ChordProgression:
    """
    获取随机和弦进行

    参数:
        style: 风格过滤，None表示所有风格
        max_complexity: 最大复杂度

    返回:
        随机和弦进行
    """
    if style:
        candidates = [prog for prog in CHORD_PROGRESSIONS.values()
                     if prog.style == style and prog.complexity <= max_complexity]
    else:
        candidates = [prog for prog in CHORD_PROGRESSIONS.values()
                     if prog.complexity <= max_complexity]

    return random.choice(candidates) if candidates else CHORD_PROGRESSIONS["pop_basic"]

# ==================== 和弦转位和声部连接 ====================

class VoiceLeading(Enum):
    """声部连接策略"""
    CLOSE = "close"       # 密集排列
    OPEN = "open"         # 开放排列
    MIXED = "mixed"       # 混合排列
    SMOOTH = "smooth"     # 平滑连接（最小化声部移动）

def apply_voice_leading(chords: List[Chord], key: Key,
                       strategy: VoiceLeading = VoiceLeading.SMOOTH) -> List[Chord]:
    """
    应用声部连接策略

    参数:
        chords: 和弦列表
        key: 调
        strategy: 连接策略

    返回:
        应用声部连接后的和弦列表
    """
    if strategy == VoiceLeading.SMOOTH and len(chords) > 1:
        # 平滑连接：最小化声部移动
        previous_notes = chords[0].get_midi_notes(key)

        for i in range(1, len(chords)):
            current_notes = chords[i].get_midi_notes(key)

            # 寻找最佳转位以最小化音程移动
            min_movement = float('inf')
            best_inversion = chords[i].inversion

            for inversion in range(4):  # 尝试不同转位
                test_chord = Chord(
                    root=chords[i].root,
                    quality=chords[i].quality,
                    inversion=inversion
                )
                test_notes = test_chord.get_midi_notes(key)

                # 计算总移动距离
                movement = sum(abs(test_notes[j] - previous_notes[j])
                             for j in range(min(len(test_notes), len(previous_notes))))

                if movement < min_movement:
                    min_movement = movement
                    best_inversion = inversion

            # 应用最佳转位
            chords[i].inversion = best_inversion
            previous_notes = chords[i].get_midi_notes(key)

    return chords

# ==================== 音乐分析和工具函数 ====================

def analyze_melody_congruence(melody_notes: List[int], chord: Chord, key: Key) -> float:
    """
    分析旋律与和弦的协和程度

    参数:
        melody_notes: 旋律音符列表
        chord: 和弦
        key: 调

    返回:
        协和度分数 (0.0-1.0)
    """
    chord_notes = set(chord.get_midi_notes(key))
    scale_notes = set(get_scale_notes(key))

    congruent_count = 0

    for note in melody_notes:
        # 检查是否在和弦音上
        if note % 12 in {cn % 12 for cn in chord_notes}:
            congruent_count += 1
        # 检查是否在调内音上
        elif note % 12 in {sn % 12 for sn in scale_notes}:
            congruent_count += 0.5

    return congruent_count / len(melody_notes) if melody_notes else 0.0

def get_suitable_chords_for_note(note: int, key: Key) -> List[Chord]:
    """
    获取适合指定音符的调内和弦

    参数:
        note: MIDI音符
        key: 调

    返回:
        包含该音符的调内和弦列表
    """
    suitable_chords = []

    # 检查所有调内和弦
    for degree in range(1, 8):
        chord = get_diatonic_chord(degree, key)
        chord_notes = chord.get_midi_notes(key)

        if any(note % 12 == cn % 12 for cn in chord_notes):
            suitable_chords.append(chord)

    return suitable_chords

def modulate(current_key: Key, target_degree: int = 5) -> Key:
    """
    计算转调后的调

    参数:
        current_key: 当前调
        target_degree: 目标音级 (默认为属音转调)

    返回:
        转调后的调
    """
    # 获取当前调的主音
    current_tonic = current_key.tonic

    # 获取音阶音程
    intervals = get_scale_intervals(current_key.scale_type)

    # 计算目标音级的音高
    target_note = current_tonic
    for i in range(target_degree - 1):
        if i < len(intervals):
            target_note += intervals[i]

    # 找到最接近的调
    all_keys = list(Key)
    min_distance = float('inf')
    target_key = current_key

    for key in all_keys:
        distance = abs(key.tonic - target_note)
        if distance < min_distance:
            min_distance = distance
            target_key = key

    return target_key

# ==================== 导出和初始化 ====================

def __init__():
    """模块初始化"""
    pass

# 便捷函数
def create_chord(degree: int, quality: ChordQuality,
                key: Key, inversion: int = 0) -> Chord:
    """
    创建和弦的便捷函数

    参数:
        degree: 音级 (1-7)
        quality: 和弦性质
        key: 调
        inversion: 转位

    返回:
        和弦对象
    """
    return Chord(root=degree - 1, quality=quality, inversion=inversion)

def create_progression_from_degrees(degrees: List[int],
                                   qualities: List[ChordQuality],
                                   name: str = "custom",
                                   style: str = "custom") -> ChordProgression:
    """
    从音级列表创建和弦进行

    参数:
        degrees: 音级列表 [1, 4, 5, 1]
        qualities: 和弦性质列表
        name: 进行名称
        style: 风格

    返回:
        和弦进行对象
    """
    chords = list(zip(degrees, qualities))
    return ChordProgression(name=name, description=f"Custom {name} progression",
                          chords=chords, style=style)

# 模块级变量，用于快速访问
COMMON_KEYS = {
    "C_major": Key.C_MAJOR,
    "G_major": Key.G_MAJOR,
    "D_major": Key.D_MAJOR,
    "A_major": Key.A_MAJOR,
    "E_major": Key.E_MAJOR,
    "A_minor": Key.A_MINOR,
    "E_minor": Key.E_MINOR,
    "D_minor": Key.D_MINOR
}

COMMON_QUALITIES = {
    "major": ChordQuality.MAJOR,
    "minor": ChordQuality.MINOR,
    "7": ChordQuality.DOMINANT_SEVENTH,
    "maj7": ChordQuality.MAJOR_SEVENTH,
    "m7": ChordQuality.MINOR_SEVENTH,
    "dim7": ChordQuality.DIMINISHED_SEVENTH
}
