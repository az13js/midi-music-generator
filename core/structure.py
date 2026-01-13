class PhraseBuilder:
    def __init__(self, length=16):
        self.length = length
        self.pieces = []

    def add_motif(self, notes: list, repeat: int = 1):
        """添加动机并重复"""
        for _ in range(repeat):
            self.pieces.extend(notes)
        return self

    def add_variation(self, motif: list, transform_func):
        """添加变奏"""
        self.pieces.extend(transform_func(motif))
        return self

    def add_cadence(self, key: Key):
        """添加终止式（落回主音）"""
        self.pieces.extend([key.value[0], key.value[0]])
        return self

    def build(self):
        return self.pieces[:self.length]
