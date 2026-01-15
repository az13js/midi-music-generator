# MIDI Music Generator
基于分层音乐架构的 Python 自动编曲系统，旨在通过策略模式将音乐理论与生成算法分离，实现灵活、可扩展的 MIDI 音乐创作。
## ✨ 特性
-   **分层架构设计**：将音乐理论（Core）、生成算法、编曲逻辑与输出模块解耦，易于维护和扩展。
-   **丰富的生成策略**：
    -   **旋律生成**：支持马尔可夫链、乐句模式、遗传算法优化、蒙特卡洛树搜索（MCTS）等多种策略。
    -   **和声生成**：支持基于预设进行、调内随机生成、功能和声以及混合策略。
    -   **节奏生成**：支持随机节奏、预设模式、摇摆节奏以及基于风格（如摇滚、爵士）的律动生成。
-   **灵活的预设系统**：通过 JSON 配置文件定义风格（Pop, Jazz, Rock 等），无需修改代码即可调整乐曲参数。
-   **多轨编曲支持**：自动组合旋律、和声、低音等多轨音轨，并支持声部连接与和弦转位。
-   **专业级 MIDI 输出**：基于 `mido` 库，精确控制力度、时值、速度和音高。
## 🛠 安装
### 环境要求
-   Python 3.11+
-   操作系统：Windows / Linux / macOS
### 安装步骤
1.  克隆本仓库：
    ```bash
    git clone <repository-url>
    cd midi_music_gen
    ```
2.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```
## 🚀 快速开始
### 命令行使用 (CLI)
本项目提供了一个功能完善的命令行入口 `main.py`，支持日志记录和多种输出控制。
**基本用法：**
```bash
python main.py --preset pop --output output.mid
```
**参数说明：**
-   `--preset`: 预设名称（默认: `pop`）。可选值包括 `pop`, `jazz`, `rock`, `blues`, `classical`, `bossa`, `folk`, `edm`。
-   `--output`: 输出的 MIDI 文件路径。
-   `--bars`: 生成的小节数量（可选，覆盖预设中的设置）。
-   `--list-presets`: 列出所有可用的预设并退出。
-   `--show-info`: 显示当前预设的详细配置信息。
-   `-v`, `--verbose`: 增加输出详细程度 (`-v` 为 INFO 级别, `-vv` 为 DEBUG 级别)。
-   `-q`, `--quiet`: 安静模式，仅显示错误信息。
-   `--log-file`: 将日志保存到指定文件。
**示例：**
1. 生成一段 32 小节的爵士音乐，并显示详细信息：
```bash
python main.py --preset jazz --bars 32 --output my_jazz_song.mid -v
```
2. 列出所有可用的音乐风格预设：
```bash
python main.py --list-presets
```
3. 生成 EDM 风格音乐，并将生成日志保存到文件：
```bash
python main.py --preset edm --output track.mid --log-file generation.log
```
### 预设配置
预设文件位于 `presets/` 目录下。项目内置了多种风格的配置文件：
- **流行**: `pop.json`
- **爵士**: `jazz.json` (支持 swing 节奏)
- **摇滚**: `rock.json`
- **布鲁斯**: `blues.json`
- **古典**: `classical.json`
- **波萨诺瓦**: `bossa.json`
- **民谣**: `folk.json`
- **电子舞曲**: `edm.json` (使用遗传算法生成旋律)
> 💡 **想要创建自己的音乐风格？**
> 
> 查看 **[预设编写指南](PRESETS_GUIDE.md)** 了解如何通过 JSON 配置文件定制旋律策略、和弦进行、节奏模式和乐器音色。
## 📁 项目架构
项目采用分层架构，各司其职，确保代码的高内聚低耦合。
```
midi_music_gen/
├── core/                # 音乐理论引擎（不可变规则）
│   ├── theory.py        # 音阶、和弦、调性、音程
│   ├── rhythm.py        # 节奏型、拍号、基础数据
│   └── structure.py     # 乐句构造器
├── generators/          # 生成算法层（插件化策略）
│   ├── melody.py        # 旋律生成策略
│   ├── harmony.py       # 和声生成策略
│   └── rhythm.py        # 节奏生成策略
├── composers/           # 编曲层（多轨组合）
│   └── simple_arranger.py # 编排逻辑、MIDI轨道写入
├── output/              # 输出适配器
│   └── midi_writer.py   # MIDI文件创建与保存
├── presets/             # 风格预设（用户可扩展）
│   ├── pop.json
│   ├── jazz.json
│   └── rock.json
├── config.py            # 全局配置
└── main.py              # CLI 入口
```
### 核心模块说明
1.  **Core (音乐理论)**: 定义了基础的音乐数据结构，如 `Key` (调性), `ScaleType` (音阶), `ChordQuality` (和弦性质) 等。这一层不涉及生成逻辑，只提供规则和数据查询。
2.  **Generators (生成器)**: 采用**策略模式**。每个生成器（旋律/和声/节奏）都有多种实现策略（如 `RandomWalkStrategy`, `ProgressionBasedStrategy`），可以灵活切换。
3.  **Composers (编曲器)**: 负责将各生成器产生的数据组合成完整的音乐作品。`SimpleArranger` 处理多轨 MIDI 事件的写入、时间管理和元数据设置。
4.  **Output (输出)**: 负责 MIDI 文件的物理写入，提供 `MidiWriter` 等工具类。
## 🔧 开发与扩展
### 添加新的旋律生成策略
如果你有新的旋律生成算法，只需继承 `MelodyStrategy` 基类并注册即可。
```python
from generators.melody import MelodyStrategy, MelodyGenerator
class MyCustomStrategy(MelodyStrategy):
    def generate(self, key: Key, length: int, **kwargs) -> List[int]:
        # 实现你的生成逻辑
        return [60, 62, 64, 65] * (length // 4)
# 注册策略
MelodyGenerator.register_strategy("my_custom", MyCustomStrategy)
# 使用
gen = MelodyGenerator("my_custom", Key.C_MAJOR)
notes = gen.generate(length=16)
```
### 创建自定义预设
在 `presets/` 目录下创建一个新的 JSON 文件，例如 `my_style.json`：
```json
{
  "tempo": 110,
  "key": "A_MINOR",
  "melody": {
    "strategy": "random",
    "chromatic_probability": 0.1
  },
  "harmony": {
    "progression": "rock_basic"
  },
  "rhythm": {
    "pattern": "rock_beat"
  },
  "structure": {
    "bars": 24
  }
}
```
然后通过 CLI 调用：
```bash
python main.py --preset my_style --output custom.mid
```
## 📄 许可证
本项目基于 [MIT License](LICENSE) 开源。
Copyright (c) 2026 az13js <1654602334@qq.com>
## 🤝 贡献
欢迎提交 Issue 和 Pull Request。如果你希望为项目添加新的风格、算法或文档，请遵循现有的代码风格和架构设计。
