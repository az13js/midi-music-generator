"""
MIDI Music Generator - Melody Generation Module

这个模块提供了多种旋律生成策略，包括：
- 马尔可夫链随机游走策略
- 基于乐句模式的策略
- 神经网络风格策略（预留接口）
- 遗传算法优化策略
- 蒙特卡洛树搜索策略
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional, Callable
import random
import math
from core.theory import (
    Key, Chord, get_scale_notes, get_diatonic_chord,
    CHORD_PROGRESSIONS, get_progression_by_name, ScaleType,
    analyze_melody_congruence
)

class MelodyStrategy(ABC):
    """旋律生成策略抽象基类"""

    def __init__(self, key: Key, length: int = 16):
        self.key = key
        self.length = length
        self.scale_notes = get_scale_notes(key, num_octaves=2)

    @abstractmethod
    def generate(self, key: Key, length: int, **kwargs) -> List[int]:
        pass

    def apply_velocity_curve(self, notes: List[int], curve_type: str = "flat") -> List[int]:
        """应用力度曲线：flat, arch, rising, falling, random"""
        velocities = []

        if curve_type == "flat":
            velocities = [80] * len(notes)
        elif curve_type == "arch":
            mid_point = len(notes) // 2
            for i, note in enumerate(notes):
                normalized_pos = abs(i - mid_point) / max(mid_point, 1)
                velocity = int(127 * (1 - normalized_pos * 0.6))
                velocities.append(max(50, min(127, velocity)))
        elif curve_type == "rising":
            velocities = [int(64 + (i / len(notes)) * 63) for i in range(len(notes))]
        elif curve_type == "falling":
            velocities = [int(127 - (i / len(notes)) * 63) for i in range(len(notes))]
        elif curve_type == "random":
            velocities = [random.randint(60, 120) for _ in notes]
        else:
            velocities = [80] * len(notes)

        return velocities

    def add_timing_variations(self, notes: List[int], base_duration: float = 0.5) -> List[Tuple[int, float]]:
        """添加时值变化"""
        result = []
        for note in notes:
            duration_variation = random.choice([0.5, 0.75, 1.0, 1.25, 1.5])
            duration = base_duration * duration_variation
            result.append((note, duration))
        return result

class RandomWalkStrategy(MelodyStrategy):
    """马尔可夫链随机游走策略"""

    def __init__(self, key: Key, transition_matrix: Optional[Dict] = None):
        super().__init__(key)
        self.transition_matrix = transition_matrix or self._create_default_transition_matrix()

    def _create_default_transition_matrix(self) -> Dict[int, Dict[int, float]]:
        """创建默认的马尔可夫转移矩阵"""
        matrix = {}
        interval_weights = {
            0: 0.1, 1: 0.2, 2: 0.3, 3: 0.15, 4: 0.1, 5: 0.05, 7: 0.05,
            -1: 0.2, -2: 0.3, -3: 0.15, -4: 0.1, -5: 0.05, -7: 0.05
        }

        for note in self.scale_notes:
            transitions = {}
            for interval, weight in interval_weights.items():
                target_note = note + interval
                if target_note in self.scale_notes:
                    transitions[target_note] = weight
            total = sum(transitions.values())
            if total > 0:
                transitions = {k: v/total for k, v in transitions.items()}
            matrix[note] = transitions
        return matrix

    def generate(self, key: Key, length: int, **kwargs) -> List[int]:
        melody = []
        current_note = kwargs.get('start_note', self.scale_notes[0])

        for _ in range(length):
            melody.append(current_note)
            if current_note in self.transition_matrix:
                transitions = self.transition_matrix[current_note]
                notes = list(transitions.keys())
                probabilities = list(transitions.values())
                if random.random() < 0.1:  # 10%概率选择音阶外音符
                    chromatic_options = [n for n in range(current_note - 3, current_note + 4)
                                        if n not in notes and 48 <= n <= 84]
                    if chromatic_options:
                        current_note = random.choice(chromatic_options)
                else:
                    current_note = random.choices(notes, probabilities)[0]
            else:
                index = self.scale_notes.index(current_note) if current_note in self.scale_notes else 0
                next_index = max(0, min(len(self.scale_notes) - 1, index + random.choice([-2, -1, 0, 1, 2])))
                current_note = self.scale_notes[next_index]
        return melody

class PatternBasedStrategy(MelodyStrategy):
    """基于乐句模式的策略"""

    def generate(self, key: Key, length: int, **kwargs) -> List[int]:
        from core.structure import PhraseBuilder

        motif_size = kwargs.get('motif_size', 4)
        repeat_count = kwargs.get('repeat_count', 2)
        variation_type = kwargs.get('variation_type', 'interval')

        builder = PhraseBuilder(length)
        motif = random.sample(self.scale_notes, motif_size)
        builder.add_motif(motif, repeat=repeat_count)

        if variation_type == 'interval':
            builder.add_variation(motif, lambda m: [note + 2 for note in m])
        elif variation_type == 'rhythm':
            builder.add_variation(motif, lambda m: [m[i % len(m)] for i in range(len(m)*2)])
        else:
            builder.add_variation(motif, lambda m: [note + 2 if i % 2 == 0 else note
                                                  for i, note in enumerate(m)])
        builder.add_cadence(key)
        return builder.build()

class NeuralStyleStrategy(MelodyStrategy):
    """神经网络风格策略（预留接口）"""

    def __init__(self, key: Key, model_path: Optional[str] = None):
        super().__init__(key)
        self.model_path = model_path
        print("Warning: NeuralStyleStrategy is a placeholder. Install required ML libraries for full functionality.")

    def generate(self, key: Key, length: int, **kwargs) -> List[int]:
        style = kwargs.get('style', 'classical')

        if style == 'jazz':
            melody = []
            for i in range(length):
                if random.random() < 0.6:
                    chord = get_diatonic_chord(random.randint(1, 7), key)
                    chord_notes = chord.get_midi_notes(key)
                    melody.append(random.choice(chord_notes))
                else:
                    melody.append(random.choice(self.scale_notes))
        elif style == 'pop':
            melody = [self.scale_notes[0]]
            for i in range(1, length):
                prev_note = melody[-1]
                neighbors = [n for n in self.scale_notes if abs(n - prev_note) <= 4]
                if neighbors:
                    melody.append(random.choice(neighbors))
                else:
                    melody.append(random.choice(self.scale_notes))
        else:
            melody = []
            current_note = self.scale_notes[0]
            for _ in range(length):
                melody.append(current_note)
                interval = random.choice([-2, -1, 1, 2, -3, 3, -4, 4, -5, 5])
                next_note = current_note + interval
                if next_note in self.scale_notes:
                    current_note = next_note
                else:
                    current_note = random.choice(self.scale_notes)
        return melody

class GeneticOptimizationStrategy(MelodyStrategy):
    """遗传算法优化策略"""

    def __init__(self, key: Key, population_size: int = 50, generations: int = 100):
        super().__init__(key)
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7

    def _fitness_function(self, melody: List[int], chords: List[Chord]) -> float:
        """适应度函数：评估旋律与和弦的协和程度"""
        total_score = 0.0
        for i, note in enumerate(melody):
            chord_index = min(i // (len(melody) // len(chords)), len(chords) - 1)
            chord = chords[chord_index]
            chord_notes = set(chord.get_midi_notes(self.key))
            scale_notes = set(self.scale_notes)

            if note % 12 in {cn % 12 for cn in chord_notes}:
                total_score += 1.0
            elif note % 12 in {sn % 12 for sn in scale_notes}:
                total_score += 0.5
            else:
                total_score += 0.0
        return total_score / len(melody)

    def _crossover(self, parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
        """交叉操作"""
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2

    def _mutate(self, melody: List[int]) -> List[int]:
        """变异操作"""
        mutated = melody.copy()
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                mutated[i] = random.choice(self.scale_notes)
        return mutated

    def _initialize_population(self, length: int) -> List[List[int]]:
        """初始化种群"""
        return [[random.choice(self.scale_notes) for _ in range(length)]
                for _ in range(self.population_size)]

    def generate(self, key: Key, length: int, **kwargs) -> List[int]:
        progression_name = kwargs.get('progression_name', 'pop_basic')
        custom_chords = kwargs.get('custom_chords', None)

        chords = custom_chords if custom_chords else []
        if not custom_chords:
            progression = get_progression_by_name(progression_name)
            if progression:
                from core.theory import Chord as TheoryChord
                chords = [TheoryChord(root=degree-1, quality=quality)
                         for degree, quality in progression.chords]

        population = self._initialize_population(length)

        for generation in range(self.generations):
            fitness_scores = [self._fitness_function(individual, chords)
                            for individual in population]
            sorted_indices = sorted(range(len(fitness_scores)),
                                   key=lambda i: fitness_scores[i], reverse=True)
            selected = [population[i] for i in sorted_indices[:self.population_size // 2]]
            new_population = selected.copy()

            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(selected, 2)
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                new_population.extend([child1, child2])
            population = new_population[:self.population_size]

        fitness_scores = [self._fitness_function(individual, chords)
                         for individual in population]
        best_index = fitness_scores.index(max(fitness_scores))
        return population[best_index]

class MonteCarloTreeSearchStrategy(MelodyStrategy):
    """蒙特卡洛树搜索策略"""

    def __init__(self, key: Key, simulations: int = 1000):
        super().__init__(key)
        self.simulations = simulations
        self.exploration_weight = 1.4

    def _evaluate_state(self, notes: List[int], target_length: int) -> float:
        """评估当前状态的价值"""
        if len(notes) < target_length:
            return 0.0

        completion = len(notes) / target_length
        if len(notes) > 1:
            intervals = [abs(notes[i] - notes[i-1]) for i in range(1, len(notes))]
            interval_diversity = len(set(intervals)) / len(intervals)
        else:
            interval_diversity = 0.0

        pitch_range = (max(notes) - min(notes)) / 12
        range_score = min(1.0, pitch_range / 2.0)
        return (completion * 0.4 + interval_diversity * 0.4 + range_score * 0.2)

    def _get_possible_next_notes(self, current_notes: List[int]) -> List[int]:
        """获取可能的下一个音符"""
        if not current_notes:
            return [self.scale_notes[0]]

        last_note = current_notes[-1]
        possible_notes = [note for note in self.scale_notes
                          if 48 <= note <= 84 and abs(note - last_note) <= 8]
        return possible_notes if possible_notes else [last_note]

    def generate(self, key: Key, length: int, **kwargs) -> List[int]:
        best_melody = []
        best_score = -1

        for simulation in range(self.simulations):
            current_melody = []
            for position in range(length):
                possible_notes = self._get_possible_next_notes(current_melody)

                best_next_note = None
                best_next_score = -1
                for next_note in possible_notes:
                    test_melody = current_melody + [next_note]
                    score = self._evaluate_state(test_melody, length)
                    if score > best_next_score:
                        best_next_score = score
                        best_next_note = next_note

                if random.random() < 0.2:  # 20%概率随机选择
                    best_next_note = random.choice(possible_notes)
                current_melody.append(best_next_note)

            final_score = self._evaluate_state(current_melody, length)
            if final_score > best_score:
                best_score = final_score
                best_melody = current_melody
        return best_melody

class MelodyGenerator:
    """旋律生成器工厂类"""

    STRATEGIES = {
        "random": RandomWalkStrategy,
        "structured": PatternBasedStrategy,
        "neural": NeuralStyleStrategy,
        "genetic": GeneticOptimizationStrategy,
        "mcts": MonteCarloTreeSearchStrategy
    }

    def __init__(self, strategy_name: str, key: Key, **strategy_params):
        strategy_class = self.STRATEGIES.get(strategy_name, PatternBasedStrategy)
        self.strategy = strategy_class(key, **strategy_params)

    def generate(self, length: int = 16, **kwargs) -> List[int]:
        return self.strategy.generate(self.strategy.key, length, **kwargs)

    def generate_with_timing(self, length: int = 16, **kwargs) -> List[Tuple[int, float]]:
        notes = self.generate(length, **kwargs)
        base_duration = kwargs.get('base_duration', 0.5)
        return self.strategy.add_timing_variations(notes, base_duration)

    @classmethod
    def register_strategy(cls, name: str, strategy_class: type):
        cls.STRATEGIES[name] = strategy_class

    @classmethod
    def get_available_strategies(cls) -> List[str]:
        return list(cls.STRATEGIES.keys())

def create_melody_from_strategy(strategy_name: str, key: Key, length: int = 16, **params) -> List[int]:
    """创建旋律的便捷函数"""
    generator = MelodyGenerator(strategy_name, key, **params)
    return generator.generate(length)

def optimize_melody_for_chords(melody: List[int], chords: List[Chord], key: Key, iterations: int = 50) -> List[int]:
    """优化旋律使其更适合指定的和弦进行"""
    generator = GeneticOptimizationStrategy(key, population_size=100, generations=iterations)
    return generator.generate(key, len(melody), custom_chords=chords)
