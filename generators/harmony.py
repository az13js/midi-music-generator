""" MIDI Music Generator - Harmony Generation Module
这个模块提供了和声生成策略，包括：
- 基于预设和弦进行的生成
- 随机和弦进行生成
- 支持和弦转位
- 支持声部排列（密集/开放）
- 和弦节奏模式
"""

from typing import List, Tuple, Optional, Dict, Callable
import random
from abc import ABC, abstractmethod
from core.theory import (
    Key, Chord, ChordQuality, ChordProgression,
    CHORD_PROGRESSIONS, get_progression_by_name,
    get_progressions_by_style, get_random_progression,
    get_diatonic_chord, get_scale_notes, VoiceLeading, apply_voice_leading
)

# ==================== 和弦生成策略抽象基类 ====================

class HarmonyStrategy(ABC):
    """和声生成策略抽象基类"""
    
    def __init__(self, key: Key, beats_per_bar: int = 4):
        """
        初始化和声生成策略
        
        Args:
            key: 调
            beats_per_bar: 每小节拍数
        """
        self.key = key
        self.beats_per_bar = beats_per_bar
    
    @abstractmethod
    def generate(self, num_bars: int, **kwargs) -> List[Tuple[int, float]]:
        """
        生成和弦序列
        
        Args:
            num_bars: 小节数量
            **kwargs: 其他参数
            
        Returns:
            [(和弦根音MIDI编号, 时值(拍)), ...] 列表
        """
        pass
    
    def _apply_inversion(self, chord: Chord, inversion: int) -> Chord:
        """应用和弦转位"""
        return Chord(
            root=chord.root,
            quality=chord.quality,
            inversion=inversion,
            bass_note=chord.bass_note
        )


class ProgressionBasedStrategy(HarmonyStrategy):
    """基于预设和弦进行的策略"""
    
    def __init__(
        self, 
        key: Key, 
        beats_per_bar: int = 4,
        progression_name: Optional[str] = None,
        style: Optional[str] = None
    ):
        super().__init__(key, beats_per_bar)
        
        # 获取和弦进行
        if progression_name:
            self.progression = get_progression_by_name(progression_name)
            if self.progression is None:
                raise ValueError(f"Progression '{progression_name}' not found")
        elif style:
            progressions = get_progressions_by_style(style)
            self.progression = random.choice(progressions) if progressions else None
        else:
            self.progression = get_random_progression()
    
    def generate(
        self, 
        num_bars: int, 
        chords_per_bar: int = 1,
        rhythm: str = "steady",
        apply_voice_leading_flag: bool = False,
        inversion_mode: str = "none",  # "none", "random", "bass_motion"
        **kwargs
    ) -> List[Tuple[int, float]]:
        """
        基于和弦进行生成和弦序列
        
        Args:
            num_bars: 小节数量
            chords_per_bar: 每小节和弦数量
            rhythm: 节奏模式 ("steady", "syncopated", "random")
            apply_voice_leading_flag: 是否应用声部连接
            inversion_mode: 转位模式
            
        Returns:
            [(根音MIDI, 时值), ...]
        """
        if not self.progression:
            raise ValueError("No chord progression available")
        
        # 构建和弦对象列表
        chords = []
        progression_chords = self.progression.chords
        
        # 重复进行以填充小节数
        total_chords = num_bars * chords_per_bar
        chord_index = 0
        
        for _ in range(total_chords):
            degree, quality = progression_chords[chord_index % len(progression_chords)]
            chord = Chord(root=degree - 1, quality=quality)
            
            # 应用转位
            if inversion_mode == "random":
                chord = self._apply_inversion(chord, random.randint(0, 2))
            elif inversion_mode == "bass_motion":
                # 基于低音走向的转位（简化版）
                if chords:
                    prev_bass = chords[-1][0]
                    current_bass = chord.get_midi_notes(self.key)[0]
                    # 如果低音跳动太大，考虑转位
                    if abs(current_bass - prev_bass) > 7:
                        chord = self._apply_inversion(chord, random.randint(1, 2))
            
            chords.append(chord)
            chord_index += 1
        
        # 应用声部连接
        if apply_voice_leading_flag:
            chords = apply_voice_leading(chords, self.key, VoiceLeading.SMOOTH)
        
        # 计算每个和弦的时值
        beats_per_chord = self.beats_per_bar / chords_per_bar
        
        # 应用节奏模式
        if rhythm == "steady":
            durations = [beats_per_chord] * total_chords
        elif rhythm == "syncopated":
            # 简单的切分模式
            durations = []
            for i in range(total_chords):
                if i % 2 == 1:
                    durations.append(beats_per_chord * 0.5)
                else:
                    durations.append(beats_per_chord * 1.5)
        elif rhythm == "random":
            durations = []
            for i in range(total_chords):
                # 在0.5倍到1.5倍之间随机
                factor = random.uniform(0.5, 1.5)
                durations.append(beats_per_chord * factor)
        else:
            durations = [beats_per_chord] * total_chords
        
        # 返回 (根音MIDI, 时值) 列表
        result = []
        for chord, duration in zip(chords, durations):
            root_note = chord.get_midi_notes(self.key)[0]
            result.append((root_note, duration))
        
        return result


class DiatonicStrategy(HarmonyStrategy):
    """基于调内和弦的随机生成策略"""
    
    def __init__(self, key: Key, beats_per_bar: int = 4):
        super().__init__(key, beats_per_bar)
        # 预计算调内和弦
        self.diatonic_chords = [
            get_diatonic_chord(degree, key)
            for degree in range(1, 8)
        ]
    
    def generate(
        self,
        num_bars: int,
        density: float = 0.5,
        avoid_repetition: bool = True,
        cadence_pattern: Optional[List[int]] = None,
        **kwargs
    ) -> List[Tuple[int, float]]:
        """
        生成基于调内和弦的序列
        
        Args:
            num_bars: 小节数量
            density: 和弦密度 (0.1-1.0)，控制每个拍出现和弦的概率
            avoid_repetition: 是否避免连续重复相同和弦
            cadence_pattern: 终止式模式，如 [5, 1] 表示在结束时用V-I
            
        Returns:
            [(根音MIDI, 时值), ...]
        """
        total_beats = num_bars * self.beats_per_bar
        result = []
        last_chord_index = -1
        current_beat = 0
        
        while current_beat < total_beats:
            # 检查是否应该插入和弦
            if random.random() < density:
                # 避免重复
                if avoid_repetition:
                    available_indices = [i for i in range(7) if i != last_chord_index]
                    chord_index = random.choice(available_indices)
                else:
                    chord_index = random.randint(0, 6)
                
                chord = self.diatonic_chords[chord_index]
                root_note = chord.get_midi_notes(self.key)[0]
                
                # 随机时值 (1-4拍)
                duration = random.choice([0.5, 1.0, 2.0, 4.0])
                
                # 确保不超过剩余拍数
                remaining = total_beats - current_beat
                duration = min(duration, remaining)
                
                result.append((root_note, duration))
                last_chord_index = chord_index
                current_beat += duration
            else:
                current_beat += 0.5  # 跳过半拍
        
        # 应用终止式（如果指定）
        if cadence_pattern and len(cadence_pattern) >= 2:
            # 替换最后两个和弦为终止式
            if len(result) >= 2:
                result[-2] = (
                    self.diatonic_chords[cadence_pattern[0] - 1].get_midi_notes(self.key)[0],
                    result[-2][1]
                )
                result[-1] = (
                    self.diatonic_chords[cadence_pattern[1] - 1].get_midi_notes(self.key)[0],
                    result[-1][1]
                )
        
        return result


class FunctionalStrategy(HarmonyStrategy):
    """功能和声生成策略（基于功能和声学）"""
    
    def __init__(self, key: Key, beats_per_bar: int = 4):
        super().__init__(key, beats_per_bar)
        
        # 定义功能和声分类
        self.functional_groups = {
            "T": [0],  # Tonic (I)
            "S": [3, 4],  # Subdominant (IV, V in minor)
            "D": [4, 6]  # Dominant (V, VII)
        }
    
    def generate(
        self,
        num_bars: int,
        phrase_structure: str = "AABA",
        **kwargs
    ) -> List[Tuple[int, float]]:
        """
        基于功能和声生成
        
        Args:
            num_bars: 小节数量
            phrase_structure: 乐句结构模式 ("AABA", "ABAB", etc.)
            
        Returns:
            [(根音MIDI, 时值), ...]
        """
        total_beats = num_bars * self.beats_per_bar
        bars_per_phrase = num_bars // len(phrase_structure)
        
        result = []
        
        for phrase in phrase_structure:
            phrase_beats = bars_per_phrase * self.beats_per_bar
            phrase_chords = self._generate_phrase(phrase, phrase_beats)
            result.extend(phrase_chords)
        
        return result
    
    def _generate_phrase(self, phrase_type: str, beats: int) -> List[Tuple[int, float]]:
        """生成单个乐句的和弦"""
        scale_notes = get_scale_notes(self.key, num_octaves=2)
        chords = []
        current_beat = 0
        
        # 不同乐句类型的功能进行
        if phrase_type == "A":
            # 主题句：T-S-D-T
            functional_pattern = ["T", "S", "D", "T"]
        elif phrase_type == "B":
            # 对比句：S-T-S-D
            functional_pattern = ["S", "T", "S", "D"]
        else:
            # 随机
            functional_pattern = ["T", "S", "D", "T"]
        
        for func in functional_pattern:
            chord_degree = random.choice(self.functional_groups[func])
            chord = get_diatonic_chord(chord_degree + 1, self.key)
            root_note = chord.get_midi_notes(self.key)[0]
            
            # 分配时值
            duration = beats / len(functional_pattern)
            chords.append((root_note, duration))
        
        return chords


class HybridHarmonyStrategy(HarmonyStrategy):
    """混合和声策略 - 组合多种策略"""
    
    def __init__(
        self,
        key: Key,
        beats_per_bar: int = 4,
        strategies: Optional[List[HarmonyStrategy]] = None
    ):
        super().__init__(key, beats_per_bar)
        
        if strategies is None:
            # 默认组合：进行式 + 随机变化
            self.strategies = [
                ProgressionBasedStrategy(key, beats_per_bar),
                DiatonicStrategy(key, beats_per_bar)
            ]
        else:
            self.strategies = strategies
    
    def generate(self, num_bars: int, split_ratio: float = 0.7, **kwargs) -> List[Tuple[int, float]]:
        """
        生成混合和声
        
        Args:
            num_bars: 小节数量
            split_ratio: 第一个策略占的比例 (0.0-1.0)
            
        Returns:
            [(根音MIDI, 时值), ...]
        """
        first_bars = int(num_bars * split_ratio)
        second_bars = num_bars - first_bars
        
        # 使用不同策略生成不同部分
        first_part = self.strategies[0].generate(first_bars, **kwargs)
        second_part = self.strategies[1].generate(second_bars, **kwargs)
        
        return first_part + second_part


# ==================== 和声生成器工厂类 ====================

class HarmonyGenerator:
    """和声生成器工厂类"""
    
    STRATEGIES = {
        "progression": ProgressionBasedStrategy,
        "diatonic": DiatonicStrategy,
        "functional": FunctionalStrategy,
        "hybrid": HybridHarmonyStrategy
    }
    
    def __init__(
        self,
        strategy_name: str = "progression",
        key: Optional[Key] = None,
        beats_per_bar: int = 4,
        **strategy_params
    ):
        """
        初始化和声生成器
        
        Args:
            strategy_name: 策略名称
            key: 调
            beats_per_bar: 每小节拍数
            **strategy_params: 策略特定参数
        """
        strategy_class = self.STRATEGIES.get(strategy_name, ProgressionBasedStrategy)
        
        # 如果没有提供key，使用默认C大调
        if key is None:
            from core.theory import Key as KeyEnum
            key = KeyEnum.C_MAJOR
        
        self.strategy = strategy_class(key, beats_per_bar, **strategy_params)
        self.key = key
    
    def generate(self, num_bars: int = 16, **kwargs) -> List[Tuple[int, float]]:
        """
        生成和弦序列
        
        Args:
            num_bars: 小节数量
            **kwargs: 策略特定参数
            
        Returns:
            [(根音MIDI编号, 时值(拍)), ...]
        """
        return self.strategy.generate(num_bars, **kwargs)
    
    def generate_chord_objects(self, num_bars: int = 16, **kwargs) -> List[Chord]:
        """
        生成和弦对象列表（用于更复杂的处理）
        
        Args:
            num_bars: 小节数量
            **kwargs: 策略特定参数
            
        Returns:
            Chord对象列表
        """
        root_duration_list = self.generate(num_bars, **kwargs)
        scale_notes = get_scale_notes(self.key, num_octaves=2)
        
        chords = []
        for root_midi, duration in root_duration_list:
            # 找到对应的音级
            try:
                root_index = scale_notes.index(root_midi)
            except ValueError:
                # 如果不在音阶中，找最近的音阶音
                root_index = min(
                    range(len(scale_notes)),
                    key=lambda i: abs(scale_notes[i] - root_midi)
                )
            
            # 创建和弦对象（默认使用大三和弦）
            chord = Chord(root=root_index, quality=ChordQuality.MAJOR)
            chords.append(chord)
        
        return chords
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """注册新的和声策略"""
        cls.STRATEGIES[name] = strategy_class
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """获取可用的策略列表"""
        return list(cls.STRATEGIES.keys())


# ==================== 便捷函数 ====================

def create_harmony(
    strategy_name: str = "progression",
    key: Optional[Key] = None,
    num_bars: int = 16,
    beats_per_bar: int = 4,
    **params
) -> List[Tuple[int, float]]:
    """
    创建和声的便捷函数
    
    Args:
        strategy_name: 策略名称
        key: 调
        num_bars: 小节数量
        beats_per_bar: 每小节拍数
        **params: 策略特定参数
        
    Returns:
        [(根音MIDI, 时值), ...]
    """
    generator = HarmonyGenerator(strategy_name, key, beats_per_bar, **params)
    return generator.generate(num_bars, **params)


def create_progression_harmony(
    progression_name: str,
    key: Optional[Key] = None,
    num_bars: int = 16,
    chords_per_bar: int = 1,
    **params
) -> List[Tuple[int, float]]:
    """
    基于预设和弦进行创建和声
    
    Args:
        progression_name: 和弦进行名称
        key: 调
        num_bars: 小节数量
        chords_per_bar: 每小节和弦数量
        **params: 其他参数
        
    Returns:
        [(根音MIDI, 时值), ...]
    """
    return create_harmony(
        strategy_name="progression",
        key=key,
        num_bars=num_bars,
        progression_name=progression_name,
        chords_per_bar=chords_per_bar,
        **params
    )


def create_style_harmony(
    style: str,
    key: Optional[Key] = None,
    num_bars: int = 16,
    **params
) -> List[Tuple[int, float]]:
    """
    基于风格创建和声
    
    Args:
        style: 音乐风格 ("pop", "jazz", "rock", "blues", "classical")
        key: 调
        num_bars: 小节数量
        **params: 其他参数
        
    Returns:
        [(根音MIDI, 时值), ...]
    """
    return create_harmony(
        strategy_name="progression",
        key=key,
        num_bars=num_bars,
        style=style,
        **params
    )


# ==================== 向后兼容 ====================

# 保留原有的简单接口，但实现新的逻辑
class HarmonyGenerator_Legacy:
    """旧版和声生成器（向后兼容）"""
    
    def __init__(self, progression_name: str):
        """初始化旧版生成器"""
        self.progression_name = progression_name
        self.progression = CHORD_PROGRESSIONS.get(progression_name)
        
        if not self.progression:
            raise ValueError(f"Progression '{progression_name}' not found. "
                           f"Available: {list(CHORD_PROGRESSIONS.keys())}")
    
    def generate(self, key: Key, chords_per_bar: int = 1):
        """
        生成和弦序列（返回Chord对象列表，兼容旧代码）
        
        Args:
            key: 调
            chords_per_bar: 每小节和弦数量
            
        Returns:
            Chord对象列表
        """
        chords = []
        for degree, quality in self.progression.chords:
            chord = Chord(root=degree, quality=quality)
            chords.extend([chord] * chords_per_bar)
        return chords


# 使用新的生成器作为默认实现
HarmonyGenerator = HarmonyGenerator

# 注意：__all__ 现在由包的 __init__.py 文件统一管理
