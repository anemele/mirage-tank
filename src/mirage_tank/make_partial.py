"""制作部分幻影坦克图片。

给出一张图片，划定一个区域，在该区域生成一个幻影坦克图片。"""

import os
import os.path as op
import tkinter as tk

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageTk

from .area import convex_hull


class InteractUI(tk.Tk):
    def __init__(self, image: Image.Image):
        super().__init__()
        self.title("Draw on Image")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        image_width, image_height = image.size
        width_ratio = screen_width / image_width
        height_ratio = screen_height / image_height
        scale_ratio = 0.6 * min(width_ratio, height_ratio)
        self._scale_ratio = 1

        # 缩放图片
        if scale_ratio < 1:
            self._scale_ratio = scale_ratio
            new_width = int(image_width * scale_ratio)
            new_height = int(image_height * scale_ratio)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 创建画布并显示图片
        self._canvas = tk.Canvas(self, width=image.width, height=image.height)
        self._canvas.pack()
        photo = ImageTk.PhotoImage(image)
        self._canvas.create_image(0, 0, anchor=tk.NW, image=photo)

        # 鼠标轨迹坐标
        self._mouse_down = False
        self._mouse_point = list[tuple[float, float]]()

        # 鼠标轨迹曲线
        self._mouse_curve = None

        # 绑定鼠标事件
        self._canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self._canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self._canvas.bind("<B1-Motion>", self._on_mouse_move)

        self.mainloop()

    def get_scale_ratio(self) -> float:
        return self._scale_ratio

    def get_mouse_points(self) -> list[tuple[float, float]]:
        return self._mouse_point

    def _on_mouse_down(self, event):
        self._mouse_down = True
        self._mouse_point.clear()

    def _on_mouse_up(self, event):
        self._mouse_down = False
        new_points = convex_hull(self._mouse_point)
        self._mouse_point[:] = [p.to_tuple() for p in new_points]
        self._mouse_point.append(self._mouse_point[0])
        self._draw_mouse_curve()

    def _on_mouse_move(self, event: tk.Event):
        if self._mouse_down:
            self._mouse_point.append((event.x, event.y))
            self._draw_mouse_curve()

    def _draw_mouse_curve(self):
        if self._mouse_curve is not None:
            self._canvas.delete(self._mouse_curve)
        if len(self._mouse_point) > 1:
            self._mouse_curve = self._canvas.create_line(
                self._mouse_point, smooth=True, width=3, fill="red"
            )


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
        points = InteractUI(img).get_mouse_points()
        print(points)
        return

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
