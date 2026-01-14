TODO README目前只是开发者随便记录的内容……

## 一、系统架构设计

```
midi_generator/
├── core/                    # 音乐理论引擎（不可变规则）
│   ├── theory.py           # 音阶、和弦、调性
│   ├── rhythm.py           # 节奏型、节拍
│   └── structure.py        # 乐句、段落、曲式
├── generators/              # 生成算法（可切换策略）
│   ├── __init__.py
│   ├── melody.py           # 旋律生成器
│   ├── harmony.py          # 和声生成器
│   └── rhythm.py           # 节奏生成器
├── composers/               # 编曲器（组合多轨）
│   ├── __init__.py
│   └── simple_arranger.py  # 基础编曲逻辑
├── presets/                 # 风格预设（用户可扩展）
│   ├── pop.json
│   ├── jazz.json
│   └── rock.json
├── output/                  # 输出适配器
│   ├── midi_writer.py      # MIDI格式写入
│   └── __init__.py
├── config.py               # 全局配置
└── main.py                 # CLI入口
```

---

## 二、核心层设计（音乐理论引擎）

### `core/theory.py` - 不可变的音乐规则
### `core/structure.py` - 乐句构造器

## 三、生成层设计（插件化策略）

### `generators/melody.py` - 策略模式

### `generators/harmony.py` - 和声生成器
## 四、编曲层（多轨组合）

### `composers/simple_arranger.py`
## 五、预设系统（JSON配置）

### `presets/pop.json`
```json
{
    "tempo": 120,
    "key": "C_MAJOR",
    "melody": {
        "strategy": "structured",
        "velocity_curve": "arch"
    },
    "harmony": {
        "progression": "pop",
        "voicing": "close"
    },
    "rhythm": {
        "pattern": "steady",
        "swing": 0.05
    },
    "structure": {
        "bars": 16,
        "sections": ["intro", "verse", "chorus"]
    }
}
```

**加载预设**：
```python
# main.py
def load_preset(name: str) -> dict:
    with open(f"presets/{name}.json") as f:
        return json.load(f)
```

---

## 六、CLI入口（简化交互）

### `main.py` - 关注编排流程，而非细节
## 七、系统优势

| 维度 | 旧脚本 | 新系统 |
|------|--------|--------|
| ** 扩展性 ** | 修改源码 | 添加JSON预设或继承`Strategy`类 |
| ** 可测试性** | 几乎无法测试 | 每个Generator可独立单元测试 |
| **复用性** | 复制粘贴 | 通过Composer组合不同Generator |
| **音乐性** | 随机噪音 | 基于理论模型，支持复杂曲式 |
| **协作 ** | 单人维护 | 多人可分别开发Generator和Preset |

---

## 八、迁移路径（渐进式重构）

1. ** 阶段1 **（1天）：建立`core/theory.py`，替换硬编码音阶
2. **阶段2**（2天）：抽取`generators/melody.py`，保留旧逻辑作为`LegacyStrategy`
3. **阶段3**（1天）：实现`SimpleArranger`，支持多轨
4. **阶段4**（持续）：逐步迁移预设到JSON，新增策略

**结论**：系统化设计的核心价值在于** 将音乐知识（Theory）与生成算法（Strategy）分离 **。你可以让音乐人写`presets/pop.json`，让程序员实现`generators/ai_melody.py`，两者通过配置组合，这才是可持续的架构。