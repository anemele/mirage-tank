"""制作黑白幻影坦克图片。
需要两张 jpg 格式的图片，生成一张 png 格式的图片。
"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from .core import dark, light, merge_top_and_bottom, resize_and_center


def make(top_path: Path, bottom_path: Path, output_path: Path) -> None:
    with Image.open(top_path) as ft:
        ftl = ft.convert("L")
    with Image.open(bottom_path) as fb:
        fbl = fb.convert("L")
    top_img = np.asarray(ftl)
    bottom_img = np.asarray(fbl)
    t1, t2 = resize_and_center(light(top_img), dark(bottom_img))
    new_img = merge_top_and_bottom(t1, t2)
    new_pic = Image.fromarray(new_img, mode="LA")
    new_pic.save(output_path)
    print(f"save at `{output_path}`")


def main():
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

    if o is not None and o.suffix != ".png":
        o = o.with_suffix(".png")
    else:
        o = t.with_name(f"{t.stem}_output.png")

    make(t, b, o)
