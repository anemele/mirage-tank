"""分离幻影坦克图片。
输入幻影坦克图片路径，输出其顶图和底图。

只保证对本程序生成图片的效果，其他方法生成的图片效果可能不太好。"""

import os
import os.path as osp

import numpy as np
from PIL import Image

from .core import undark, unlight

type PathLike = str | os.PathLike[str]


def _extract(
    arr: np.ndarray,  # 三维向量 w*h*2
) -> tuple[np.ndarray, np.ndarray]:  # 二维向量 w*h
    lightness = arr[:, :, 0]
    alpha = arr[:, :, 1]

    bottom_arr = (lightness / 255 * alpha).astype(np.uint8)
    top_arr = (255 - alpha + bottom_arr).astype(np.uint8)

    return unlight(top_arr), undark(bottom_arr)


def extract(img_path: PathLike) -> tuple[Image.Image, Image.Image]:
    with Image.open(img_path) as img:
        fl = img.convert("LA")

    arr = np.asarray(fl)
    top_arr, bottom_arr = _extract(arr)

    top_img = Image.fromarray(top_arr, mode="L")
    bottom_img = Image.fromarray(bottom_arr, mode="L")

    return top_img, bottom_img


def extract_it(img_path: PathLike) -> None:
    top_img, bottom_img = extract(img_path)
    p, _ = osp.splitext(img_path)
    top_img.save(f"{p}_top.jpg")
    bottom_img.save(f"{p}_bottom.jpg")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="extract-tank",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("img_path", help="幻影坦克图片路径")
    args = parser.parse_args()

    try:
        extract_it(args.img_path)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
