"""幻影坦克的核心是计算 alpha 通道。"""

import numpy as np
from numpy.typing import NDArray


def compute_alpha(
    top_arr: NDArray[np.uint8], bottom_arr: NDArray[np.uint8]
) -> NDArray[np.uint8]:
    """根据前后两张图像计算 alpha 通道。"""
    alpha_arr = 255 - (top_arr - bottom_arr)
    alpha_arr[alpha_arr == 255] = 0
    return alpha_arr.astype(np.uint8)


def compute_lightness(
    alpha_arr: NDArray[np.uint8], bottom_arr: NDArray[np.uint8]
) -> NDArray[np.uint8]:
    """根据线性插值算法计算灰度值。"""
    mask = alpha_arr != 0
    gray_arr = np.zeros_like(alpha_arr, dtype=np.uint8)
    gray_arr[mask] = (bottom_arr[mask] / alpha_arr[mask] * 255).astype(np.uint8)
    return gray_arr


def merge_top_and_bottom(
    top_arr: NDArray[np.uint8], bottom_arr: NDArray[np.uint8]
) -> NDArray[np.uint8]:
    """合并顶部和底部图像得到灰度透明图像"""
    alpha_arr = compute_alpha(top_arr, bottom_arr)
    lightness_arr = compute_lightness(alpha_arr, bottom_arr)
    merged_arr = np.dstack((lightness_arr, alpha_arr))
    return merged_arr.astype(np.uint8)


def resize_and_center(
    top_img: NDArray[np.uint8], bottom_img: NDArray[np.uint8]
) -> tuple[NDArray[np.uint8], NDArray[np.uint8]]:
    """将两个图像调整大小并居中。
    输出图像宽度和高度取两个图像的最大值，将原来两个图像居中放置，
    前景图边缘填充为白色，后景图边缘填充为黑色。
    """
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


def light(arr: NDArray[np.uint8]) -> NDArray[np.uint8]:
    return np.right_shift(arr, 1) + 128


def unlight(arr: NDArray[np.uint8]) -> NDArray[np.uint8]:
    return np.left_shift(arr - 128, 1)


def dark(arr: NDArray[np.uint8]) -> NDArray[np.uint8]:
    return np.right_shift(arr, 1)


def undark(arr: NDArray[np.uint8]) -> NDArray[np.uint8]:
    return np.left_shift(arr, 1)
