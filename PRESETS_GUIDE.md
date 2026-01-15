# 预设编写指南
本指南将详细介绍如何通过 JSON 格式创建自定义的音乐风格预设，从而无需修改代码即可生成不同风格的音乐。
## 📍 预设文件位置
所有预设文件应放置在项目根目录下的 `presets/` 文件夹中，文件扩展名必须为 `.json`。
例如：`presets/my_custom_style.json`
## 🏗️ 基本结构
一个最基础的预设配置文件包含以下几个顶层键：
```json
{
  "tempo": 120,
  "key": "C_MAJOR",
  "structure": {
    "bars": 16
  },
  "melody": { ... },
  "harmony": { ... },
  "rhythm": { ... }
}
```
## 🎛️ 详细参数说明
### 1. 全局参数
| 键名 | 类型 | 说明 | 可选值/示例 |
|------|------|------|------------|
| `tempo` | Integer | 乐曲速度 (BPM) | 60 - 200+ |
| `key` | String | 调性 (必须与代码中的枚举一致) | `C_MAJOR`, `A_MINOR`, `D_MAJOR`, `G#_MINOR` 等 |
| `structure.bars` | Integer | 乐曲总小节数 | 8, 16, 32, 64 等 |
### 2. 旋律配置
在 `melody` 对象中配置旋律的生成逻辑。
```json
"melody": {
  "strategy": "structured",
  "velocity_curve": "arch",
  "program": 0
}
```
| 参数 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| `strategy` | String | 旋律生成策略 | `random` (随机游走)<br>`structured` (乐句模式)<br>`motivic` (动机发展)<br>`genetic` (遗传算法优化)<br>`mcts` (蒙特卡洛树搜索)<br>`neural` (神经网络接口) |
| `velocity_curve` | String | 力度曲线 (音量变化) | `flat` (平稳)<br>`arch` (拱形：弱-强-弱)<br>`rising` (渐强)<br>`falling` (渐弱)<br>`random` (随机) |
| `program` | Integer | MIDI 音色编号 (0-127) | 0 (大钢琴), 73 (长笛), 24 (尼龙吉他) 等。默认为 0。 |
| `motif_length` | Integer | 动机长度 (音符数) | 仅对 `motivic` 和 `structured` 策略有效，如 4 |
### 3. 和声配置
在 `harmony` 对象中配置和弦进行、织体及乐器。
```json
"harmony": {
  "progression": "pop_basic",
  "voicing": "close",
  "program": 0,
  "bass_program": 32,
  "apply_voice_leading": true
}
```
| 参数 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| `progression` | String | 和弦进行模式 | `pop_basic` (I-V-vi-IV)<br>`pop_50s` (I-vi-IV-V)<br>`jazz_251` (ii-V-I)<br>`jazz_rhythm` (I-vi-ii-V)<br>`rock_basic` (I-IV-V)<br>`blues_basic` (12小节布鲁斯)<br>`classical_authentic` (V-I)<br>`classical_plagal` (IV-I)<br>`modern_trending` (vi-IV-I-V)<br>`complex_cycle` (五度圈) |
| `voicing` | String | 和弦排列方式 | `close` (密集排列，通常使用三和弦)<br>`open` (开放排列，会自动扩展为七和弦或九和弦) |
| `program` | Integer | 和声伴奏乐器 MIDI 编号 | 默认 0 (钢琴) |
| `bass_program` | Integer | 低音乐器 MIDI 编号 | 默认 32 (原声贝斯)，推荐 33 (电贝斯) |
| `apply_voice_leading` | Boolean | 是否启用声部连接优化 | `true` / `false` (启用后和弦连接会更平滑) |
### 4. 节奏配置
在 `rhythm` 对象中配置节奏律动。
```json
"rhythm": {
  "pattern": "steady_eighths",
  "swing": 0.1
}
```
| 参数 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| `pattern` | String | 节奏型名称 | `steady` (四分)<br>`steady_quarters` (四分)<br>`steady_eighths` (八分)<br>`rock_beat` (摇滚)<br>`swing_eighths` (摇摆八分)<br>`syncopated_16` (十六分切分)<br>`techno` (电子)<br>`bossa_nova` (波萨) |
| `style` | String | 基于风格生成节奏 | `rock`, `jazz`, `pop`, `techno`, `hiphop`, `samba` 等 (如果设置此项，可能会覆盖 `pattern`) |
| `swing` | Float | 摇摆感程度 (0.0 - 1.0) | 0.0 为无摇摆，0.67 为典型爵士摇摆 |
## 🎨 实战示例
### 示例 1：慢板民谣
创建一个缓慢、抒情的小调民谣风格。
```json
{
  "tempo": 85,
  "key": "D_MINOR",
  "structure": {
    "bars": 24
  },
  "melody": {
    "strategy": "motivic",
    "velocity_curve": "falling",
    "program": 24,
    "motif_length": 5
  },
  "harmony": {
    "progression": "pop_50s",
    "voicing": "close",
    "program": 0,
    "bass_program": 32
  },
  "rhythm": {
    "pattern": "steady_quarters",
    "swing": 0.05
  }
}
```
**解析**：
*   使用 `D_MINOR` (D小调) 营造忧伤氛围。
*   速度设为 85 BPM。
*   旋律使用 `motivic` (动机发展) 策略，配合 `falling` (渐弱) 力度，音色设为 `24` (尼龙吉他)。
*   和声使用经典的 50年代流行进行 (`I-vi-IV-V`)，适合民谣。
*   节奏使用平稳的四分音符，微弱的摇摆感增加自然度。
### 示例 2：快节奏放克
创建一个节奏感强、和声色彩丰富的作品。
```json
{
  "tempo": 125,
  "key": "E_MINOR",
  "structure": {
    "bars": 32
  },
  "melody": {
    "strategy": "genetic",
    "velocity_curve": "arch",
    "program": 4
  },
  "harmony": {
    "progression": "modern_trending",
    "voicing": "open",
    "program": 16,
    "bass_program": 33,
    "apply_voice_leading": true
  },
  "rhythm": {
    "pattern": "syncopated_16",
    "swing": 0.0
  }
}
```
**解析**：
*   `E_MINOR` 配合 125 BPM 的高能量。
*   旋律使用 `genetic` (遗传算法) 生成较为复杂的旋律线，音色 `4` (电钢琴)。
*   和声使用 `modern_trending` (vi-IV-I-V)，且 `voicing` 设为 `open`，这会自动生成七和弦/九和弦，增加爵士感。音色 `16` (风琴) 和 `33` (电贝斯) 典型放克配置。
*   节奏使用 `syncopated_16` (十六分切分)，强调节奏的律动感。
## 🚀 使用自定义预设
编写好 JSON 文件后，通过命令行调用即可：
```bash
python main.py --preset my_custom_style --output my_song.mid
```
如果遇到 JSON 格式错误，程序会提示具体的错误信息。
