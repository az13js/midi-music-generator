import argparse
import json
from composers import SimpleArranger

# CLI入口



def load_preset(name: str) -> dict:
    with open(f"presets/{name}.json") as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", default="pop")
    parser.add_argument("--output", required=True)
    parser.add_argument("--bars", type=int, default=16)

    args = parser.parse_args()

    # 1. 加载配置
    preset = load_preset(args.preset)
    key = Key[preset["key"]]

    # 2. 初始化编曲器
    arranger = SimpleArranger(
        tempo=preset["tempo"],
        key=key
    )

    # 3. 按需添加音轨
    if preset.get("melody"):
        arranger.add_track(
            name="Melody",
            generator=MelodyGenerator(preset["melody"]),
            channel=0
        )

    if preset.get("harmony"):
        arranger.add_track(...)

    # 4. 输出
    arranger.save(args.output)
    print(f"Generated {args.preset} style MIDI: {args.output}")