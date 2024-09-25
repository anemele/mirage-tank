from .make import makeit


def main():
    import argparse

    parser = argparse.ArgumentParser(prog="tank", description=__doc__)
    parser.add_argument("top_img", help="上层图片/白色背景下显示的图片")
    parser.add_argument("bottom_img", help="下层图片/黑色背景下显示的图片")
    default_o = "output.png"
    parser.add_argument(
        "-o", "--output", default=default_o, help=f"输出图片路径，默认：{default_o}"
    )

    args = parser.parse_args()
    t: str = args.top_img
    b: str = args.bottom_img
    o: str = args.output
    if not o.endswith(".png"):
        o += ".png"
    makeit(t, b, o)
