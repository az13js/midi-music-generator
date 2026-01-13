from abc import ABC, abstractmethod

class MelodyStrategy(ABC):
    @abstractmethod
    def generate(self, key: Key, length: int) -> list[int]:
        pass

class RandomWalkStrategy(MelodyStrategy):
    """马尔可夫链随机游走"""
    def generate(self, key, length):
        # 实现状态转移逻辑
        pass

class PatternBasedStrategy(MelodyStrategy):
    """基于乐句模式"""
    def generate(self, key, length):
        builder = PhraseBuilder(length)
        motif = random.sample(key.value, 4)
        return (builder
                .add_motif(motif, repeat=2)
                .add_variation(motif, lambda m: [n+2 for n in m])
                .add_cadence(key)
                .build())

# 注册表（插件化）
MELODY_STRATEGIES = {
    "random": RandomWalkStrategy,
    "structured": PatternBasedStrategy,
}
