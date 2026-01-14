"""MIDI Music Generator - Rhythm Generation Module

这个模块提供了节奏生成策略，包括：
- 基础节奏型定义
- 随机节奏生成策略
- 模式化节奏生成策略
- 摇摆节奏策略
- 风格化节奏模板
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
import random
from enum import Enum


# ==================== 基础定义 ====================

class NoteType(Enum):
    """音符类型枚举"""
    WHOLE = "whole"           # 全音符 (4拍)
    HALF = "half"             # 二分音符 (2拍)
    QUARTER = "quarter"       # 四分音符 (1拍)
    EIGHTH = "eighth"         # 八分音符 (0.5拍)
    SIXTEENTH = "sixteenth"   # 十六分音符 (0.25拍)
    DOTTED_QUARTER = "dotted_quarter"  # 附点四分音符 (1.5拍)
    DOTTED_EIGHTH = "dotted_eighth"    # 附点八分音符 (0.75拍)
    TRIPLET_EIGHTH = "triplet_eighth"   # 三连音八分音符 (约0.33拍)
    REST = "rest"             # 休止符


# 音符类型到拍数的映射
NOTE_DURATION_MAP = {
    NoteType.WHOLE: 4.0,
    NoteType.HALF: 2.0,
    NoteType.QUARTER: 1.0,
    NoteType.EIGHTH: 0.5,
    NoteType.SIXTEENTH: 0.25,
    NoteType.DOTTED_QUARTER: 1.5,
    NoteType.DOTTED_EIGHTH: 0.75,
    NoteType.TRIPLET_EIGHTH: 1/3,
    NoteType.REST: 0.0
}


# ==================== 预定义节奏型 ====================

class RhythmPattern(Enum):
    """预定义节奏型枚举"""

    # 基础节奏型
    STEADY_QUARTERS = "steady_quarters"        # 稳定四分音符
    STEADY_EIGHTHS = "steady_eighths"          # 稳定八分音符
    HALF_QUARTER = "half_quarter"              # 二分+四分

    # 切分节奏型
    SYNCOPATED_8 = "syncopated_8"              # 八分切分
    SYNCOPATED_16 = "syncopated_16"            # 十六分切分
    ANTICIPATION = "anticipation"              # 预拍

    # 舞曲节奏型
    ROCK_BEAT = "rock_beat"                    # 摇滚节奏
    DISCO = "disco"                            # 迪斯科
    HIP_HOP = "hip_hop"                        # 嘻哈
    HOUSE = "house"                            # 浩室

    # 爵士节奏型
    SWING_EIGHTHS = "swing_eighths"            # 摇摆八分
    JAZZ_COMP = "jazz_comp"                    # 爵士伴奏
    BOSSA_NOVA = "bossa_nova"                  # 波萨诺瓦

    # 拉丁节奏型
    SAMBA = "samba"                            # 桑巴
    SALSA = "salsa"                            # 萨尔萨

    # 电子节奏型
    TECHNO = "techno"                          # 泰克诺
    TRANCE = "trance"                          # 传思
    DUBSTEP = "dubstep"                        # 达布斯特普


# 预定义节奏型模式 (拍数列表)
RHYTHM_PATTERNS = {
    # 基础节奏型 (4拍)
    RhythmPattern.STEADY_QUARTERS: [1.0, 1.0, 1.0, 1.0],
    RhythmPattern.STEADY_EIGHTHS: [0.5] * 8,
    RhythmPattern.HALF_QUARTER: [2.0, 1.0, 1.0],

    # 切分节奏型
    RhythmPattern.SYNCOPATED_8: [1.0, 0.5, 0.5, 1.0, 1.0],
    RhythmPattern.SYNCOPATED_16: [0.5, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    RhythmPattern.ANTICIPATION: [0.5, 0.5, 1.0, 0.5, 0.5, 1.0],

    # 舞曲节奏型
    RhythmPattern.ROCK_BEAT: [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
    RhythmPattern.DISCO: [0.5, 0.5, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.25, 0.25],
    RhythmPattern.HIP_HOP: [0.5, 0.5, 0.5, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5],
    RhythmPattern.HOUSE: [0.25] * 16,

    # 爵士节奏型
    RhythmPattern.SWING_EIGHTHS: [0.66, 0.33, 0.66, 0.33, 0.66, 0.33, 0.66, 0.33],
    RhythmPattern.JAZZ_COMP: [1.0, 0.5, 0.5, 1.0, 0.5, 0.5],
    RhythmPattern.BOSSA_NOVA: [0.5, 0.5, 0.5, 0.25, 0.25, 0.5, 0.5, 0.5],

    # 拉丁节奏型
    RhythmPattern.SAMBA: [0.5, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25],
    RhythmPattern.SALSA: [0.5, 0.5, 0.5, 0.5, 0.25, 0.25, 0.5, 0.5],

    # 电子节奏型
    RhythmPattern.TECHNO: [0.25] * 16,
    RhythmPattern.TRANCE: [0.25] * 16,
    RhythmPattern.DUBSTEP: [1.0, 0.25, 0.75, 1.0, 0.5, 0.5, 0.25, 0.25, 0.5],
}


# ==================== 节奏生成策略 ====================

class RhythmStrategy(ABC):
    """节奏生成策略抽象基类"""

    def __init__(self, beats_per_bar: int = 4):
        """
        初始化节奏生成策略

        Args:
            beats_per_bar: 每小节拍数，默认4拍
        """
        self.beats_per_bar = beats_per_bar

    @abstractmethod
    def generate(self, num_bars: int, **kwargs) -> List[float]:
        """
        生成节奏模式

        Args:
            num_bars: 小节数量
            **kwargs: 其他参数

        Returns:
            时值列表，单位为拍
        """
        pass

    def _normalize_to_bars(self, durations: List[float], num_bars: int) -> List[float]:
        """将节奏规范化到指定小节数"""
        total_beats = num_bars * self.beats_per_bar
        current_total = sum(durations)

        if current_total == 0:
            return [1.0] * total_beats

        if current_total < total_beats:
            # 不足则补充最后一个音符
            last_duration = durations[-1] if durations else 1.0
            durations.extend([last_duration] * int((total_beats - current_total) / last_duration))
        elif current_total > total_beats:
            # 过多则截断
            trimmed = []
            current = 0.0
            for dur in durations:
                if current + dur <= total_beats:
                    trimmed.append(dur)
                    current += dur
                else:
                    # 调整最后一个音符使其精确填满
                    remaining = total_beats - current
                    if remaining > 0:
                        trimmed.append(remaining)
                    break
            durations = trimmed

        return durations


class RandomRhythmStrategy(RhythmStrategy):
    """随机节奏生成策略"""

    def __init__(self, beats_per_bar: int = 4, allowed_durations: Optional[List[float]] = None):
        """
        初始化随机节奏策略

        Args:
            beats_per_bar: 每小节拍数
            allowed_durations: 允许的时值列表，单位拍
        """
        super().__init__(beats_per_bar)
        # 默认允许的时值：八分、四分、附点四分、二分
        self.allowed_durations = allowed_durations or [0.5, 1.0, 1.5, 2.0]

    def generate(self, num_bars: int, **kwargs) -> List[float]:
        """生成随机节奏"""
        total_beats = num_bars * self.beats_per_bar
        durations = []
        current = 0.0

        while current < total_beats:
            # 随机选择时值
            duration = random.choice(self.allowed_durations)

            # 确保不超过剩余拍数
            remaining = total_beats - current
            if duration > remaining:
                # 如果剩余空间不足，选择较小的时值或精确填充
                smaller_options = [d for d in self.allowed_durations if d <= remaining]
                duration = random.choice(smaller_options) if smaller_options else remaining

            durations.append(duration)
            current += duration

        return durations


class PatternBasedRhythmStrategy(RhythmStrategy):
    """基于预定义模式的节奏生成策略"""

    def __init__(self, beats_per_bar: int = 4, pattern: Optional[RhythmPattern] = None):
        """
        初始化基于模式的节奏策略

        Args:
            beats_per_bar: 每小节拍数
            pattern: 节奏型，None则随机选择
        """
        super().__init__(beats_per_bar)
        self.pattern = pattern

    def generate(self, num_bars: int, **kwargs) -> List[float]:
        """基于模式生成节奏"""
        if self.pattern is None:
            # 随机选择一个模式
            self.pattern = random.choice(list(RhythmPattern))

        base_pattern = RHYTHM_PATTERNS.get(self.pattern, [1.0, 1.0, 1.0, 1.0])
        durations = []

        # 重复模式以填充所需小节数
        total_beats = num_bars * self.beats_per_bar
        pattern_beats = sum(base_pattern)
        repetitions = int(num_bars * self.beats_per_bar / pattern_beats) + 1

        for _ in range(repetitions):
            durations.extend(base_pattern)

        return self._normalize_to_bars(durations, num_bars)


class SwingRhythmStrategy(RhythmStrategy):
    """摇摆节奏策略"""

    def __init__(self, beats_per_bar: int = 4, swing_ratio: float = 0.66):
        """
        初始化摇摆节奏策略

        Args:
            beats_per_bar: 每小节拍数
            swing_ratio: 摇摆比例 (0.5-1.0)，0.66为标准三连音感觉
        """
        super().__init__(beats_per_bar)
        self.swing_ratio = swing_ratio

    def generate(self, num_bars: int, **kwargs) -> List[float]:
        """生成摇摆节奏"""
        total_beats = num_bars * self.beats_per_bar
        durations = []

        for _ in range(total_beats):
            # 将每拍分为两个不等的部分
            first_part = self.swing_ratio  # 第一拍较长
            second_part = 1.0 - self.swing_ratio  # 第二拍较短
            durations.extend([first_part, second_part])

        return durations


class GrooveRhythmStrategy(RhythmStrategy):
    """风格化节奏策略"""

    def __init__(self, beats_per_bar: int = 4, style: str = "rock"):
        """
        初始化风格化节奏策略

        Args:
            beats_per_bar: 每小节拍数
            style: 音乐风格
        """
        super().__init__(beats_per_bar)
        self.style = style.lower()

    def generate(self, num_bars: int, **kwargs) -> List[float]:
        """根据风格生成节奏"""
        style_patterns = {
            "rock": RhythmPattern.ROCK_BEAT,
            "disco": RhythmPattern.DISCO,
            "hiphop": RhythmPattern.HIP_HOP,
            "house": RhythmPattern.HOUSE,
            "techno": RhythmPattern.TECHNO,
            "trance": RhythmPattern.TRANCE,
            "jazz": RhythmPattern.SWING_EIGHTHS,
            "bossa": RhythmPattern.BOSSA_NOVA,
            "samba": RhythmPattern.SAMBA,
            "salsa": RhythmPattern.SALSA,
            "dubstep": RhythmPattern.DUBSTEP,
        }

        pattern = style_patterns.get(self.style, RhythmPattern.STEADY_QUARTERS)
        strategy = PatternBasedRhythmStrategy(self.beats_per_bar, pattern)
        return strategy.generate(num_bars, **kwargs)


class HybridRhythmStrategy(RhythmStrategy):
    """混合节奏策略 - 结合多种策略"""

    def __init__(self, beats_per_bar: int = 4, strategies: Optional[List[RhythmStrategy]] = None):
        """
        初始化混合节奏策略

        Args:
            beats_per_bar: 每小节拍数
            strategies: 策略列表，None则使用默认组合
        """
        super().__init__(beats_per_bar)
        if strategies is None:
            # 默认组合：模式节奏 + 随机变化
            self.strategies = [
                PatternBasedRhythmStrategy(beats_per_bar, RhythmPattern.STEADY_QUARTERS),
                RandomRhythmStrategy(beats_per_bar)
            ]
        else:
            self.strategies = strategies

    def generate(self, num_bars: int, **kwargs) -> List[float]:
        """生成混合节奏"""
        # 将小节分为两部分
        first_half_bars = num_bars // 2
        second_half_bars = num_bars - first_half_bars

        # 第一部分使用第一个策略
        first_rhythm = self.strategies[0].generate(first_half_bars, **kwargs)

        # 第二部分使用第二个策略（如果存在）
        if len(self.strategies) > 1:
            second_rhythm = self.strategies[1].generate(second_half_bars, **kwargs)
        else:
            second_rhythm = self.strategies[0].generate(second_half_bars, **kwargs)

        return first_rhythm + second_rhythm


# ==================== 节奏生成器工厂类 ====================

class RhythmGenerator:
    """节奏生成器工厂类"""

    STRATEGIES = {
        "random": RandomRhythmStrategy,
        "pattern": PatternBasedRhythmStrategy,
        "swing": SwingRhythmStrategy,
        "groove": GrooveRhythmStrategy,
        "hybrid": HybridRhythmStrategy,
    }

    def __init__(self, strategy_name: str, beats_per_bar: int = 4, **strategy_params):
        """
        初始化节奏生成器

        Args:
            strategy_name: 策略名称
            beats_per_bar: 每小节拍数
            **strategy_params: 策略参数
        """
        strategy_class = self.STRATEGIES.get(strategy_name, PatternBasedRhythmStrategy)
        self.strategy = strategy_class(beats_per_bar, **strategy_params)

    def generate(self, num_bars: int = 4, **kwargs) -> List[float]:
        """
        生成节奏

        Args:
            num_bars: 小节数量
            **kwargs: 其他参数

        Returns:
            时值列表
        """
        return self.strategy.generate(num_bars, **kwargs)

    def generate_with_rests(self, num_bars: int = 4, rest_probability: float = 0.1,
                            **kwargs) -> List[Tuple[float, bool]]:
        """
        生成带有休止符的节奏

        Args:
            num_bars: 小节数量
            rest_probability: 休止符出现概率
            **kwargs: 其他参数

        Returns:
            [(时值, 是否为音符), ...] 列表
        """
        durations = self.generate(num_bars, **kwargs)
        result = []

        for duration in durations:
            if random.random() < rest_probability:
                # 插入休止符
                result.append((duration, False))
            else:
                result.append((duration, True))

        return result

    def apply_velocity_pattern(self, durations: List[float],
                               pattern: str = "flat") -> List[int]:
        """
        为节奏应用力度模式

        Args:
            durations: 时值列表
            pattern: 力度模式 ("flat", "accent_downbeats", "syncopated", "crescendo", "diminuendo")

        Returns:
            力度列表 (0-127)
        """
        velocities = []

        if pattern == "flat":
            velocities = [90] * len(durations)

        elif pattern == "accent_downbeats":
            # 强拍重音
            beat_position = 0
            for i, dur in enumerate(durations):
                # 计算当前音符在每小节中的位置
                if beat_position % self.strategy.beats_per_bar < 0.1:
                    velocities.append(110)  # 强拍更响
                else:
                    velocities.append(75)   # 弱拍更轻
                beat_position += dur

        elif pattern == "syncopated":
            # 切分音重音
            for i in range(len(durations)):
                if i % 2 == 1:  # 反拍重音
                    velocities.append(100)
                else:
                    velocities.append(70)

        elif pattern == "crescendo":
            # 渐强
            velocities = [
                int(60 + (i / len(durations)) * 60)
                for i in range(len(durations))
            ]

        elif pattern == "diminuendo":
            # 渐弱
            velocities = [
                int(120 - (i / len(durations)) * 60)
                for i in range(len(durations))
            ]

        else:
            velocities = [90] * len(durations)

        return velocities

    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        """注册新的节奏策略"""
        cls.STRATEGIES[name] = strategy_class

    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """获取可用的策略列表"""
        return list(cls.STRATEGIES.keys())

    @classmethod
    def get_available_patterns(cls) -> List[str]:
        """获取可用的节奏型列表"""
        return [pattern.value for pattern in RhythmPattern]


# ==================== 便捷函数 ====================

def create_rhythm(strategy_name: str, num_bars: int = 4,
                   beats_per_bar: int = 4, **params) -> List[float]:
    """
    创建节奏的便捷函数

    Args:
        strategy_name: 策略名称
        num_bars: 小节数量
        beats_per_bar: 每小节拍数
        **params: 策略参数

    Returns:
        时值列表
    """
    generator = RhythmGenerator(strategy_name, beats_per_bar, **params)
    return generator.generate(num_bars)


def create_groove_rhythm(style: str, num_bars: int = 4,
                         beats_per_bar: int = 4) -> List[float]:
    """
    创建风格化节奏的便捷函数

    Args:
        style: 音乐风格
        num_bars: 小节数量
        beats_per_bar: 每小节拍数

    Returns:
        时值列表
    """
    return create_rhythm("groove", num_bars, beats_per_bar, style=style)


def create_pattern_rhythm(pattern: RhythmPattern, num_bars: int = 4,
                         beats_per_bar: int = 4) -> List[float]:
    """
    创建基于模式的节奏的便捷函数

    Args:
        pattern: 节奏型
        num_bars: 小节数量
        beats_per_bar: 每小节拍数

    Returns:
        时值列表
    """
    return create_rhythm("pattern", num_bars, beats_per_bar, pattern=pattern)


def get_rhythm_stats(durations: List[float]) -> Dict[str, float]:
    """
    分析节奏统计信息

    Args:
        durations: 时值列表

    Returns:
        统计信息字典
    """
    if not durations:
        return {}

    return {
        "total_beats": sum(durations),
        "note_count": len(durations),
        "average_duration": sum(durations) / len(durations),
        "shortest_duration": min(durations),
        "longest_duration": max(durations),
        "unique_durations": len(set(durations))
    }
