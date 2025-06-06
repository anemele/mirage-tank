"""制作黑白幻影坦克图片。
需要两张 jpg 格式的图片，生成一张 png 格式的图片。

幻影坦克原理自行研究，这里仅给出生成程序。"""

import os
import os.path as op

import numpy as np
from PIL import Image

from .core import dark, light, merge_top_and_bottom, resize_and_center

type PathLike = str | os.PathLike[str]


def make(top_path: PathLike, bottom_path: PathLike, output_path: PathLike) -> None:
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


def makeit(top_path: PathLike, bottom_path: PathLike, output_path: PathLike) -> None:
    if op.isfile(top_path) and op.isfile(bottom_path):
        make(top_path, bottom_path, output_path)
    elif op.isfile(top_path) and op.isdir(bottom_path):
        output_dir = f"output_{bottom_path}"
        if not op.exists(output_dir):
            os.mkdir(output_dir)
        for top_file in os.scandir(bottom_path):
            if not top_file.name.endswith(".jpg"):
                continue
            make(
                top_path,
                top_file.path,
                op.join(output_dir, f"{top_file.name[:-4]}.png"),
            )
    elif op.isdir(top_path) and op.isfile(bottom_path):
        output_dir = f"output_{top_path}"
        if not op.exists(output_dir):
            os.mkdir(output_dir)
        for top_file in os.scandir(top_path):
            if not top_file.name.endswith(".jpg"):
                continue
            make(
                top_file.path,
                bottom_path,
                op.join(output_dir, f"{top_file.name[:-4]}.png"),
            )
    else:
        output_dir = f"output_{top_path}_{bottom_path}"
        if not op.exists(output_dir):
            os.mkdir(output_dir)
        for top_file in os.scandir(top_path):
            if not top_file.name.endswith(".jpg"):
                continue
            bottom_file = op.join(bottom_path, top_file.name)
            if not op.isfile(bottom_file):
                continue
            make(
                top_file.path,
                bottom_file,
                op.join(output_dir, f"{top_file.name[:-4]}.png"),
            )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="make-tank",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("top_img", help="上层图片/白色背景下显示的图片")
    parser.add_argument("bottom_img", help="下层图片/黑色背景下显示的图片")
    parser.add_argument("-o", "--output", help="输出图片路径")

    args = parser.parse_args()
    t: str = args.top_img
    b: str = args.bottom_img
    o: str | None = args.output

    if o is not None:
        if not o.endswith(".png"):
            o += ".png"
    else:
        p, _ = op.splitext(t)
        o = f"{p}_output.png"

    try:
        makeit(t, b, o)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
