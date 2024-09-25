# Mirage Tank 幻影坦克

一种图片编码技术。

灰度透明图效果很好，彩色透明图效果欠佳。
彩图参考：<https://www.bilibili.com/read/cv9474512/>

> 衍生：光棱坦克。
> [光棱坦克工厂](https://prism.uyanide.com/)

核心在于 PNG 图像中的 alpha 通道。

alpha 取值范围是 0-1 ，其中 1 表示不透明， 0 表示完全透明。
JPEG 图像可以认为是 alpha=1 的 PNG 图像。

> 亮度 lightness 取值范围是 0-1 ，其中 0 表示黑色， 1 表示白色。

## 核心原理/公式

> *不知如何来的：）*
>
>*以灰度图为例，彩图很复杂，且效果常不尽人意。*

PNG 图像中的某个像素具有亮度 L 和透明度 A，
则在亮度为 B 的背景下**显示的**亮度 L' 为：

$$
\begin{align*}
    L' &= LA + B(1-A)\\
    &= (L-B)A + B
\end{align*}
$$

幻影坦克在黑/白背景下显示不同图像，原理就是 B 的值取 0 或 1 时 L' 的取值不同。

## 实现

现有两张灰度透明图像，分别为 X 和 Y，实现生成在白色背景下显示 X，在黑色背景下显示 Y。

设 X 某一位置像素的亮度为 $L_X$，Y 同一位置某一像素的亮度为 $L_Y$，根据公式，可以得到：

$$
\begin{align*}
    L_X &= LA+1-A\\
    L_Y &= LA
\end{align*}
$$

解方程得到 $A=1+L_Y-L_X$，$L=\dfrac{L_Y}{A}$ 。

进一步根据取值范围计算边界关系：$0\lt L_Y\lt L_X\lt 1\\$ ，也就是说同一位置的像素亮度 X 要大于 Y 。

通常方法是预处理图像时将 X 的亮度调整为大于 0.5 的值，Y 的亮度调整为小于 0.5 的值。

## 展示

<div>
    <img src="./8d34538823dbef3474d4e89e8ba98e18137252921.png" alt="" style="background-color: white; height: 200px; margin-right: 10px;">
    <img src="./8d34538823dbef3474d4e89e8ba98e18137252921.png" alt="" style="background-color: black; height: 200px;">
</div>