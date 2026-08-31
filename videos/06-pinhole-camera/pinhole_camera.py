from pathlib import Path
import sys

from manim import *
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))
from manim_style import *


def image_panel(center=np.array([3.7, -0.35, 0.0])):
    frame = RoundedRectangle(width=5.0, height=3.25, corner_radius=0.12, color=MUTED, stroke_width=2).move_to(center)
    principal = Dot(center, radius=0.08, color=TEXT)
    horizontal = Line(center + LEFT * 2.2, center + RIGHT * 2.2, color=MUTED, stroke_width=1.4)
    vertical = Line(center + DOWN * 1.35, center + UP * 1.35, color=MUTED, stroke_width=1.4)
    tag = label_chip("主点 (cₓ,cᵧ)", TEXT, 15).next_to(principal, DOWN, buff=0.12)
    return VGroup(frame, horizontal, vertical, principal, tag)


class PinholeCameraExplainer(Scene):
    def construct(self):
        add_base(self)
        self.one_ray()
        fade_all(self)
        add_base(self)
        self.change_x()
        fade_all(self)
        add_base(self)
        self.change_z()
        fade_all(self)
        add_base(self)
        self.depth_ambiguity()
        fade_all(self)
        add_base(self)
        self.pipeline()
        self.wait(0.8)

    def one_ray(self):
        title = header(1, "PINHOLE CAMERA", "三维点沿穿过光心的射线落到成像平面")
        optical = Line([-5.2, -0.7, 0], [2.0, -0.7, 0], color=Z_BLUE, stroke_width=2)
        center = Dot([-3.7, -0.7, 0], radius=0.1, color=TEXT)
        plane = Line([-1.4, -2.5, 0], [-1.4, 1.3, 0], color=X_RED, stroke_width=4)
        point = Dot([1.1, 1.15, 0], radius=0.12, color=VIOLET)
        ray = Line(center.get_center(), point.get_center(), color=VIOLET, stroke_width=3)
        projection = Dot(ray.point_from_proportion(((-1.4) - (-3.7)) / (1.1 - (-3.7))), radius=0.1, color=ORANGE)
        labels = VGroup(
            label_chip("光心 O", TEXT, 16).next_to(center, DOWN, buff=0.14),
            label_chip("虚拟成像平面", X_RED, 16).next_to(plane, DOWN, buff=0.15),
            label_chip("空间点 P", VIOLET, 16).next_to(point, RIGHT, buff=0.12),
            label_chip("投影", ORANGE, 16).next_to(projection, RIGHT, buff=0.12),
        )
        card = statement("只保留射线方向", ["三维输入：(X,Y,Z)，单位 m", "二维输出：(u,v)，单位 px"], width=4.1, accent=CYAN).move_to([4.3, -0.45, 0])
        self.play(FadeIn(title), Create(optical), FadeIn(center), Create(plane), run_time=0.7)
        self.play(FadeIn(point), Create(ray), FadeIn(projection), FadeIn(labels), run_time=0.9)
        self.play(FadeIn(card, shift=LEFT * 0.15), run_time=0.6)
        self.add(bottom_caption("前方虚拟平面只是计算画法；真实物体和光线没有被移动。"))
        self.wait(1.1)

    def change_x(self):
        title = header(2, "CHANGE ONE VARIABLE", "固定 Z，只把 X 加倍：像素偏移也加倍")
        panel = image_panel()
        x = ValueTracker(0.10)
        dot = always_redraw(lambda: Dot([3.7 + 5.0 * x.get_value(), -0.35, 0], radius=0.11, color=ORANGE))
        guide = always_redraw(lambda: Line([3.7, -0.35, 0], dot.get_center(), color=ORANGE, stroke_width=3))
        value = always_redraw(lambda: code_text(f"X = {x.get_value():.2f} m", 23, VIOLET, BOLD).move_to([-3.85, 0.55, 0]))
        fixed = statement("保持不变", ["Z = 1.00 m", "fₓ = 500 px", "cₓ = 320 px"], width=3.6, accent=Z_BLUE).move_to([-3.85, -0.85, 0])
        formula = formula_bar("u-cₓ = fₓ X/Z", CYAN, width=4.3, size=24).move_to([0, -2.3, 0])
        offset = always_redraw(lambda: code_text(f"偏移 = {500*x.get_value():.0f} px", 20, ORANGE).next_to(panel, UP, buff=0.12))
        self.play(FadeIn(title), FadeIn(panel), FadeIn(dot), FadeIn(guide), FadeIn(value), FadeIn(fixed), FadeIn(offset), FadeIn(formula), run_time=0.8)
        self.play(x.animate.set_value(0.20), run_time=1.8, rate_func=smooth)
        self.add(bottom_caption("一次只改变 X：50 px → 100 px；垂直像素不受影响。"))
        self.wait(1.1)

    def change_z(self):
        title = header(3, "NEAR AND FAR", "固定 X，只把 Z 加倍：像素偏移减半")
        panel = image_panel()
        z = ValueTracker(1.0)
        dot = always_redraw(lambda: Dot([3.7 + 0.5 / z.get_value(), -0.35, 0], radius=0.11, color=Y_GREEN))
        guide = always_redraw(lambda: Line([3.7, -0.35, 0], dot.get_center(), color=Y_GREEN, stroke_width=3))
        value = always_redraw(lambda: code_text(f"Z = {z.get_value():.2f} m", 23, VIOLET, BOLD).move_to([-3.85, 0.55, 0]))
        fixed = statement("保持不变", ["X = 0.10 m", "fₓ = 500 px", "cₓ = 320 px"], width=3.6, accent=Z_BLUE).move_to([-3.85, -0.85, 0])
        formula = formula_bar("u-cₓ = 50/Z", CYAN, width=4.0, size=24).move_to([0, -2.3, 0])
        offset = always_redraw(lambda: code_text(f"偏移 = {50/z.get_value():.1f} px", 20, Y_GREEN).next_to(panel, UP, buff=0.12))
        self.play(FadeIn(title), FadeIn(panel), FadeIn(dot), FadeIn(guide), FadeIn(value), FadeIn(fixed), FadeIn(offset), FadeIn(formula), run_time=0.8)
        self.play(z.animate.set_value(2.0), run_time=1.8, rate_func=smooth)
        self.add(bottom_caption("物点更远，连接光心的射线更靠近光轴：这就是“近大远小”。"))
        self.wait(1.1)

    def depth_ambiguity(self):
        title = header(4, "DEPTH IS LOST", "同一射线上的不同三维点，落到同一个像素")
        center = np.array([-4.3, -1.25, 0.0])
        center_dot = Dot(center, radius=0.1, color=TEXT)
        direction = np.array([1.0, 0.43, 0.0])
        plane_x = -1.8
        optical = Line(center, [2.0, center[1], 0], color=Z_BLUE, stroke_width=2)
        plane = Line([plane_x, -2.4, 0], [plane_x, 1.4, 0], color=X_RED, stroke_width=4)
        ray = Line(center, center + 6.1 * direction, color=VIOLET, stroke_width=3)
        depths = [3.2, 4.5, 5.7]
        colors = [ORANGE, Y_GREEN, VIOLET]
        points = VGroup(*[Dot(center + d * direction, radius=0.1, color=c) for d, c in zip(depths, colors)])
        labels = VGroup(*[label_chip(f"{d:.1f} m", c, 15).next_to(p, UP, buff=0.1) for d, c, p in zip(depths, colors, points)])
        ratio = (plane_x - center[0]) / direction[0]
        projection = Dot(center + ratio * direction, radius=0.12, color=TEXT)
        card = statement("三个点共同满足", ["X/Z 相同", "Y/Z 相同", "因此 (u,v) 完全相同"], width=4.0, accent=ORANGE).move_to([4.25, -0.35, 0])
        result = formula_bar("一个像素 = 一条射线 ≠ 一个三维点", VIOLET, width=6.3, size=23).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(title), Create(optical), Create(plane), FadeIn(center_dot), Create(ray), run_time=0.75)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in points], lag_ratio=0.2), FadeIn(labels), FadeIn(projection), run_time=0.85)
        self.play(FadeIn(card), FadeIn(result), run_time=0.65)
        self.wait(1.2)

    def pipeline(self):
        title = header(5, "FULL PROJECTION PIPELINE", "外参先换坐标，内参再落像素")
        cards = VGroup(
            statement("世界点", ["p_world", "单位 m"], width=2.4, accent=VIOLET),
            statement("相机点", ["p_camera = Rp+t", "检查 Z>0"], width=2.7, accent=Z_BLUE),
            statement("归一化", ["X/Z, Y/Z", "无单位"], width=2.6, accent=ORANGE),
            statement("像素", ["u,v", "单位 px"], width=2.4, accent=Y_GREEN),
        ).arrange(RIGHT, buff=0.22).move_to([0, 0.35, 0])
        arrows = VGroup(*[clean_arrow(cards[i].get_right(), cards[i+1].get_left(), MUTED, width=2.4, tip=0.11) for i in range(3)])
        labels = VGroup(
            code_text("外参 T_camera←world", 16, Z_BLUE).next_to(arrows[0], UP, buff=0.12),
            code_text("透视除法", 16, ORANGE).next_to(arrows[1], UP, buff=0.12),
            code_text("内参 K", 16, Y_GREEN).next_to(arrows[2], UP, buff=0.12),
        )
        output = formula_bar("输出 pixels · valid；无效深度不能静默通过", CYAN, width=8.0, size=22).move_to([0, -1.55, 0])
        self.play(FadeIn(title), LaggedStart(*[FadeIn(c, shift=UP * 0.12) for c in cards], lag_ratio=0.14), run_time=1.0)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.15), FadeIn(labels), run_time=0.75)
        self.play(FadeIn(output), run_time=0.55)
        self.add(bottom_caption("最小验收：三维点投影后，用同一 Z 反投影，应恢复原点。"))
        self.wait(1.2)


class PinholeCameraPoster(Scene):
    def construct(self):
        add_base(self)
        title = header(0, "PINHOLE CAMERA", "从三维米制坐标到二维像素")
        cards = VGroup(
            statement("相机坐标", ["(X,Y,Z)，单位 m", "先检查 Z>0"], width=3.55, accent=VIOLET),
            statement("透视除法", ["xₙ=X/Z", "yₙ=Y/Z"], width=3.55, accent=ORANGE),
            statement("像素坐标", ["u=fₓxₙ+cₓ", "v=fᵧyₙ+cᵧ"], width=3.55, accent=Y_GREEN),
        ).arrange(RIGHT, buff=0.28).move_to([0, 0.4, 0])
        formula = formula_bar("同一射线 → 同一像素；深度必须由额外信息补回", CYAN, width=9.2, size=23).move_to([0, -1.7, 0])
        caption = bottom_caption("外参：world→camera；内参：normalized→pixel。", color=TEXT)
        self.add(title, cards, formula, caption)
