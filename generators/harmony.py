class HarmonyGenerator:
    def __init__(self, progression_name: str):
        self.progression = PROGRESSIONS[progression_name]

    def generate(self, key: Key, chords_per_bar: int = 1):
        """生成和弦序列"""
        chords = []
        for degree, quality in self.progression:
            chord = Chord(root=degree, quality=quality)
            chords.extend([chord] * chords_per_bar)
        return chords
