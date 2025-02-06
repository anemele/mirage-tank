"""制作部分幻影坦克图片。

给出一张图片，划定一个区域，在该区域生成一个幻影坦克图片。"""

import os
import os.path as op

import numpy as np
from numpy.typing import NDArray
from PIL import Image


def get_mask_img(
    img_l: NDArray[np.uint8],  # 二维向量 w*h
    mask: NDArray[np.bool],  # 二维向量 w*h, 0 or 1
) -> NDArray[np.uint8]:  # 二维向量 w*h
    res_arr = img_l.copy()
    res_arr[mask] = 255
    return res_arr


def merge(
    top_img: NDArray[np.uint8],  # 二维向量 w*h
    bottom_img: NDArray[np.uint8],  # 二维向量 w*h
) -> NDArray[np.uint8]:  # 三维向量 w*h*2
    # 计算新的 alpha 通道
    alpha = top_img - bottom_img
    alpha = np.subtract(255, alpha)
    alpha[alpha == 255] = 0  # 处理边界情况

    # 计算新的亮度值
    lightness = np.zeros_like(alpha, dtype=np.uint8)
    mask = alpha != 0
    lightness[mask] = (bottom_img[mask] / alpha[mask] * 255).astype(np.uint8)

    # 合并新的亮度和 alpha 通道
    new_img_arr = np.dstack((lightness, alpha))

    return new_img_arr


def make(img_path: str, output_path: str) -> None:
    with Image.open(img_path) as img:
        img_rgb_arr = np.asarray(img.convert("RGB"))
        img_l_arr = np.asarray(img.convert("L"))

    mask = np.zeros_like(img_l_arr, dtype=np.bool)
    mask[200:600, 200:700] = True
    mask_img_arr = get_mask_img(img_l_arr, mask)

    t1, t2 = mask_img_arr, img_l_arr
    merge_img_arr = merge(t1, t2)

    w, h, c = img_rgb_arr.shape
    new_arr = 255 * np.ones((w, h, c + 1), dtype=np.uint8)
    new_arr[:, :, :3] = img_rgb_arr
    new_arr[mask, :3] = merge_img_arr[mask, :1]
    new_arr[mask, 3] = merge_img_arr[mask, 1]

    new_img = Image.fromarray(new_arr, mode="RGBA")
    new_img.save(output_path)
    print(f"save at `{output_path}`")


def makeit(img_path: str, output_path: str) -> None:
    if op.isfile(img_path):
        make(img_path, output_path)
        return None

    output_dir = f"output_{img_path}"
    if not op.exists(output_dir):
        os.mkdir(output_dir)
    for top_file in os.scandir(img_path):
        if not top_file.name.endswith(".jpg"):
            continue
        make(
            top_file.path,
            op.join(output_dir, f"{top_file.name[:-4]}.png"),
        )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog="make-partial-tank",
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("img", help="输入图片路径")
    parser.add_argument("-o", "--output", help="输出图片路径")

    args = parser.parse_args()
    t: str = args.img
    o: str | None = args.output

    if o is not None:
        if not o.endswith(".png"):
            o += ".png"
    else:
        p, _ = op.splitext(t)
        o = f"{p}_output.png"

    try:
        makeit(t, o)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
