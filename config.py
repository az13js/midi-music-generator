"""
MIDI Music Generator - 配置文件
存储默认设置和常量
"""

# 默认设置
DEFAULT_OUTPUT_FILE = 'generated_music.mid'
DEFAULT_MODE = 'melody'
DEFAULT_MELODY_LENGTH = 16
DEFAULT_NOTE_RANGE_START = 60  # C4
DEFAULT_NOTE_RANGE_END = 72    # C5
DEFAULT_CHORD_COUNT = 8
DEFAULT_TEMPO = 120  # BPM

# MIDI通道设置
MELODY_CHANNEL = 0
DRUM_CHANNEL = 9  # MIDI标准鼓组通道

# 音符名称映射 (MIDI编号 -> 名称)
NOTE_NAMES = {
    0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 
    8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
}

# 鼓组音符映射 (MIDI编号 -> 乐器名称)
DRUM_NOTE_NAMES = {
    35: 'Acoustic Bass Drum', 36: 'Bass Drum 1', 37: 'Side Stick', 38: 'Acoustic Snare',
    39: 'Hand Clap', 40: 'Electric Snare', 41: 'Low Floor Tom', 42: 'Closed Hi-Hat',
    43: 'High Floor Tom', 44: 'Pedal Hi-Hat', 45: 'Low Tom', 46: 'Open Hi-Hat',
    47: 'Low-Mid Tom', 48: 'Hi-Mid Tom', 49: 'Crash Cymbal 1', 50: 'High Tom',
    51: 'Ride Cymbal 1', 52: 'Chinese Cymbal', 53: 'Ride Bell', 54: 'Tambourine',
    55: 'Splash Cymbal', 56: 'Cowbell', 57: 'Crash Cymbal 2', 58: 'Vibraslap',
    59: 'Ride Cymbal 2', 60: 'Hi Bongo', 61: 'Low Bongo', 62: 'Mute Hi Conga',
    63: 'Open Hi Conga', 64: 'Low Conga', 65: 'High Timbale', 66: 'Low Timbale',
    67: 'High Agogo', 68: 'Low Agogo', 69: 'Cabasa', 70: 'Maracas',
    71: 'Short Whistle', 72: 'Long Whistle', 73: 'Short Guiro', 74: 'Long Guiro',
    75: 'Claves', 76: 'Hi Wood Block', 77: 'Low Wood Block', 78: 'Mute Cuica',
    79: 'Open Cuica', 80: 'Mute Triangle', 81: 'Open Triangle'
}

# 常见和弦类型定义
CHORD_TYPES = {
    'major': [0, 4, 7],      # 大三和弦
    'minor': [0, 3, 7],      # 小三和弦
    'diminished': [0, 3, 6], # 减三和弦
    'augmented': [0, 4, 8],  # 增三和弦
    'dom7': [0, 4, 7, 10],   # 属七和弦
    'maj7': [0, 4, 7, 11],   # 大七和弦
    'min7': [0, 3, 7, 10]    # 小七和弦
}

# 常见调性音阶定义
SCALE_TYPES = {
    'major': [0, 2, 4, 5, 7, 9, 11],      # 大调音阶
    'minor': [0, 2, 3, 5, 7, 8, 10],      # 自然小调音阶
    'pentatonic_major': [0, 2, 4, 7, 9],  # 五声音阶（大调）
    'pentatonic_minor': [0, 3, 5, 7, 10], # 五声音阶（小调）
    'blues': [0, 3, 5, 6, 7, 10]          # 布鲁斯音阶
}