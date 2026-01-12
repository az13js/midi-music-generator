# MIDI Music Generator

一个简单的命令行程序，用于生成MIDI音乐文件。该程序支持生成随机旋律、和弦进行和简单节拍。

## 功能

- 生成随机旋律
- 生成和弦进行
- 生成简单节拍模式

## 依赖

- Python 3.6+
- [mido](https://mido.readthedocs.io/) - MIDI处理库

## 安装

1. 克隆或下载此项目
2. 安装依赖库：

```bash
pip install -r requirements.txt
```

或者直接安装mido：

```bash
pip install mido
```


## 使用方法

### 生成随机旋律（默认）

```bash
python midi_generator.py [输出文件名]
```

例如：
```bash
python midi_generator.py my_melody.mid
```

### 指定生成模式

使用 `--mode` 参数指定生成模式：

- `melody` - 生成随机旋律（默认）
- `chord` - 生成和弦进行
- `rhythm` - 生成节拍模式

#### 旋律模式

```bash
python midi_generator.py --mode melody --length 20 --note-range-start 50 --note-range-end 80 output.mid
```

参数：
- `--length` - 音符数量（默认：16）
- `--note-range-start` - 音符范围起始值（默认：60，C4）
- `--note-range-end` - 音符范围结束值（默认：72，C5）

#### 和弦模式

```bash
python midi_generator.py --mode chord --chords 10 --note-range-start 55 output.mid
```

参数：
- `--chords` - 和弦数量（默认：8）
- `--note-range-start` - 起始根音符（默认：60，C4）

#### 节拍模式

```bash
python midi_generator.py --mode rhythm output.mid
```

## 示例

生成一个名为 "example.mid" 的随机旋律文件：
```bash
python midi_generator.py example.mid
```

生成一个名为 "chords.mid" 的和弦进行文件：
```bash
python midi_generator.py --mode chord chords.mid
```

生成一个名为 "drums.mid" 的节拍文件：
```bash
python midi_generator.py --mode rhythm drums.mid
```

## 说明

- MIDI音符编号：C4 = 60, C#4/D♭4 = 61, D4 = 62, ..., C5 = 72
- 生成的MIDI文件可以使用任何支持MIDI的播放器或音乐软件打开
- 在节拍模式中，使用第10通道（通道9）播放鼓组声音

## 技术细节

- 使用 [mido](https://mido.readthedocs.io/) 库处理MIDI文件
- 支持标准MIDI文件格式
- 默认速度为120 BPM

## 许可证

本项目使用 MIT 许可证 - 详见 [LICENSE](./LICENSE) 文件。