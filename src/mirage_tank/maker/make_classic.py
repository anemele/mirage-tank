"""制作黑白幻影坦克图片。
需要两张 jpg 格式的图片，生成一张 png 格式的图片。

幻影坦克原理自行研究，这里仅给出生成程序。"""

from pathlib import Path

import numpy as np
from PIL import Image

from .core import dark, light, merge_top_and_bottom, resize_and_center


def make(top_path: Path, bottom_path: Path, output_path: Path) -> None:
    with Image.open(top_path) as ft, Image.open(bottom_path) as fb:
        ftl = ft.convert("L")
        fbl = fb.convert("L")

    top_img = np.asarray(ftl)
    bottom_img = np.asarray(fbl)
    t1, t2 = resize_and_center(light(top_img), dark(bottom_img))
    new_img = merge_top_and_bottom(t1, t2)
    new_pic = Image.fromarray(new_img, mode="LA")
    new_pic.save(output_path)
    print(f"save at `{output_path}`")


def makeit(top_path: Path, bottom_path: Path, output_path: Path) -> None:
    if top_path.is_file() and bottom_path.is_file():
        make(top_path, bottom_path, output_path)

    elif top_path.is_file() and bottom_path.is_dir():
        output_dir = output_path.parent / f"output_{bottom_path.name}"
        output_dir.mkdir(exist_ok=True)
        for top_file in bottom_path.glob("*.jpg"):
            make(
                top_path,
                top_file,
                output_dir / f"{top_file.stem}.png",
            )

    elif top_path.is_dir() and bottom_path.is_file():
        output_dir = output_path.with_name(f"output_{top_path.name}")
        output_dir.mkdir(exist_ok=True)
        for top_file in top_path.glob("*.jpg"):
            make(
                top_file,
                bottom_path,
                output_dir / f"{top_file.stem}.png",
            )

    else:
        output_dir = Path(f"output_{top_path}_{bottom_path}")
        output_dir.mkdir(exist_ok=True)
        for top_file in top_path.glob("*.jpg"):
            bottom_file = bottom_path / top_file.name
            if not bottom_file.is_file():
                continue
            bottom_file = bottom_path / top_file.name
            if not bottom_file.is_file():
                continue
            make(
                top_file,
                bottom_file,
                output_dir / f"{top_file.stem}.png",
            )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("top_img", type=Path, help="上层图片/白色背景下显示的图片")
    parser.add_argument("bottom_img", type=Path, help="下层图片/黑色背景下显示的图片")
    parser.add_argument("-o", "--output", type=Path, help="输出图片路径")

    args = parser.parse_args()
    t: Path = args.top_img
    b: Path = args.bottom_img
    o: Path | None = args.output

    if o is not None and not o.suffix == ".png":
        o = o.with_suffix(".png")
    else:
        o = t.with_name(f"{t.stem}_output.png")

    try:
        makeit(t, b, o)
    except Exception as e:
        print(f"Error: {e}")
