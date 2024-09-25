"""制作黑白幻影坦克图片。
需要两张 jpg 格式的图片，生成一张 png 格式的图片。

幻影坦克原理自行研究，这里仅给出生成程序。"""

import os
import os.path as op

import numpy as np
from PIL import Image

# 以下除了 merge 返回值是 3 维向量，其他参数都是 2 维向量。


def light(arr: np.ndarray) -> np.ndarray:
    # read-only
    arr = arr >> 1
    arr += 128
    return arr


def dark(arr: np.ndarray) -> np.ndarray:
    return arr >> 1


def resize_and_center(
    top_img: np.ndarray, bottom_img: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    h_t, w_t = top_img.shape
    h_b, w_b = bottom_img.shape
    w, h = max(w_t, w_b), max(h_t, h_b)
    wm, hm = abs(w_t - w_b) // 2, abs(h_t - h_b) // 2

    # 创建新的背景图像
    t_ret = np.full((h, w), 255, dtype=np.uint8)
    b_ret = np.zeros((h, w), dtype=np.uint8)

    # 将 图片 粘贴到新的背景上
    if w == w_t and h == h_t:
        t_ret[:h_t, :w_t] = top_img
        b_ret[hm : hm + h_b, wm : wm + w_b] = bottom_img
    elif w == w_t and h == h_b:
        t_ret[hm : hm + h_t, :w_t] = top_img
        b_ret[:h_b, wm : wm + w_b] = bottom_img
    elif w == w_b and h == h_t:
        t_ret[:h_t, wm : wm + w_t] = top_img
        b_ret[hm : hm + h_b, :w_b] = bottom_img
    else:
        t_ret[hm : hm + h_t, wm : wm + w_t] = top_img
        b_ret[:h_b, :w_b] = bottom_img

    return t_ret, b_ret


def merge(top_img: np.ndarray, bottom_img: np.ndarray) -> np.ndarray:  # 三维向量 w*h*2
    # 计算新的 alpha 通道
    alpha = 255 - (top_img - bottom_img)
    alpha[alpha == 255] = 0  # 处理边界情况

    # 计算新的亮度值
    lightness = np.zeros_like(alpha, dtype=np.uint8)
    mask = alpha != 0
    lightness[mask] = (bottom_img[mask] / alpha[mask] * 255).astype(np.uint8)

    # 合并新的亮度和 alpha 通道
    new_img_arr = np.dstack((lightness, alpha))

    return new_img_arr


def make(top_path: str, bottom_path: str, output_path: str) -> None:
    with Image.open(top_path) as ft, Image.open(bottom_path) as fb:
        ftl = ft.convert("L")
        fbl = fb.convert("L")

    top_img = np.asarray(ftl)
    bottom_img = np.asarray(fbl)
    t1, t2 = resize_and_center(light(top_img), dark(bottom_img))
    new_img = merge(t1, t2)
    new_pic = Image.fromarray(new_img, mode="LA")
    new_pic.save(output_path)
    print(f"save at `{output_path}`")


def makeit(top_path: str, bottom_path: str, output_path: str) -> None:
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
