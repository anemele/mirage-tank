"""分离幻影坦克图片。
输入幻影坦克图片路径，输出其顶图和底图。

只保证对本程序生成图片的效果，其他方法生成的图片效果可能不太好。"""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

from .core import undark, unlight


def _extract(
    arr: np.ndarray,  # 三维向量 w*h*2
) -> tuple[np.ndarray, np.ndarray]:  # 二维向量 w*h
    lightness = arr[:, :, 0]
    alpha = arr[:, :, 1]

    bottom_arr = (lightness / 255 * alpha).astype(np.uint8)
    top_arr = (255 - alpha + bottom_arr).astype(np.uint8)

    return unlight(top_arr), undark(bottom_arr)


def extract(img_path: Path) -> tuple[Image.Image, Image.Image]:
    with Image.open(img_path) as img:
        fl = img.convert("LA")

    arr = np.asarray(fl)
    top_arr, bottom_arr = _extract(arr)

    top_img = Image.fromarray(top_arr, mode="L")
    bottom_img = Image.fromarray(bottom_arr, mode="L")

    return top_img, bottom_img


def extract_it(img_path: Path) -> None:
    top_img, bottom_img = extract(img_path)
    p = img_path.stem
    top_img.save(img_path.with_name(f"{p}_top.jpg"))
    bottom_img.save(img_path.with_name(f"{p}_bottom.jpg"))


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("img_path", type=Path, help="幻影坦克图片路径")
    args = parser.parse_args()

    img_path: Path = args.img_path

    extract_it(img_path)
