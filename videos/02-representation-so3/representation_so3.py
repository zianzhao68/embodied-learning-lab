from manim import *
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manim_style import *


def triad(center, angle=0.0, scale=1.5, mirrored=False):
    x = np.array([np.cos(angle), np.sin(angle), 0]) * scale
    y = np.array([-np.sin(angle), np.cos(angle), 0]) * scale
    if mirrored:
        x = -x
    z = np.array([-0.48, 0.62, 0]) * scale
    return VGroup(
        clean_arrow(center, center + x, X_RED, 3.0, 0.14),
        clean_arrow(center, center + y, Y_GREEN, 3.0, 0.14),
        clean_arrow(center, center + z, Z_BLUE, 3.0, 0.14),
        code_text("x", 18, X_RED, BOLD).next_to(center + x, RIGHT, buff=0.05),
        code_text("y", 18, Y_GREEN, BOLD).next_to(center + y, UP, buff=0.05),
        code_text("z", 18, Z_BLUE, BOLD).next_to(center + z, LEFT, buff=0.05),
        Dot(center, radius=0.055, color=TEXT),
    )


class RotationRepresentationsSO3(Scene):
    def construct(self):
        self.same_pose()
        self.four_languages()
        self.constraints()
        self.reflection()
        self.choose_tool()

    def same_pose(self):
        add_base(self)
        h = header(1, "ONE POSE", "先固定物理事实：末端只有一个姿态")
        c = LEFT * 2.6 + DOWN * 0.25
        theta = ValueTracker(0)
        axes = always_redraw(lambda: triad(c, theta.get_value(), 1.65))
        orbit = Circle(1.65, color=LINE, stroke_width=1.4).move_to(c)
        card = statement("观察重点", ["三根轴一起转动", "长度和夹角始终不变", "表示方法不会改变物理姿态"], 4.8, CYAN)
        card.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.18)
        angle = always_redraw(lambda: code_text(f"yaw = {int(round(theta.get_value()/DEGREES))}°", 21, CYAN, MEDIUM).next_to(c, DOWN, buff=1.95))

        self.play(FadeIn(h), Create(orbit), FadeIn(axes), run_time=0.8)
        self.play(FadeIn(card, shift=LEFT * 0.15), run_time=0.6)
        self.add(angle)
        self.play(theta.animate.set_value(60 * DEGREES), run_time=2.5, rate_func=smooth)
        self.wait(1.2)
        fade_all(self)

    def four_languages(self):
        add_base(self)
        h = header(2, "SAME POSE · DIFFERENT COORDINATES", "同一个 60° 姿态，可以用四种语言记录")
        c = LEFT * 4.6 + DOWN * 0.15
        pose = triad(c, 60 * DEGREES, 1.45)
        cards = VGroup(
            statement("旋转矩阵 R", ["直接作用于向量", "列向量就是旋转后的轴"], 3.7, Z_BLUE),
            statement("欧拉角", ["(roll, pitch, yaw)", "= (0°, 0°, 60°)"], 3.7, ORANGE),
            statement("轴角", ["u = +z", "α = 60°"], 3.7, Y_GREEN),
            statement("单位四元数", ["q = (0.866, 0, 0, 0.5)", "标量在前"], 3.7, VIOLET),
        ).arrange_in_grid(rows=2, cols=2, buff=(0.25, 0.25)).to_edge(RIGHT, buff=0.35).shift(DOWN * 0.12)
        same = formula_bar("四组数字 → 同一组三轴方向", CYAN, size=21).to_edge(DOWN, buff=0.25)

        self.play(FadeIn(h), FadeIn(pose), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.08) for c in cards], lag_ratio=0.18), run_time=1.4)
        self.play(FadeIn(same), run_time=0.5)
        self.wait(1.5)
        fade_all(self)

    def constraints(self):
        add_base(self)
        h = header(3, "SO(3) · VALID ROTATION", "不是任意 3×3 数字都能当旋转矩阵")
        left_c, right_c = LEFT * 3.2 + DOWN * 0.15, RIGHT * 3.2 + DOWN * 0.15
        bad = VGroup(
            clean_arrow(left_c, left_c + np.array([1.9, 0.25, 0]), X_RED, 3.0, 0.14),
            clean_arrow(left_c, left_c + np.array([0.9, 1.15, 0]), Y_GREEN, 3.0, 0.14),
            clean_arrow(left_c, left_c + np.array([-0.4, 0.55, 0]), Z_BLUE, 3.0, 0.14),
        )
        good = triad(right_c, 20 * DEGREES, 1.4)
        bad_title = label_chip("任意 9 个数", X_RED).next_to(left_c, DOWN, buff=1.75)
        good_title = label_chip("单位 + 正交", Y_GREEN).next_to(right_c, DOWN, buff=1.75)
        arrow = clean_arrow(LEFT * 0.8 + DOWN * 0.1, RIGHT * 0.8 + DOWN * 0.1, CYAN, 2.5, 0.13)
        fix = code_text("约束 / 投影", 18, CYAN, MEDIUM).next_to(arrow, UP, buff=0.08)
        formula = formula_bar("RᵀR = I   →   长度与夹角保持", CYAN, size=23).to_edge(DOWN, buff=0.25)

        self.play(FadeIn(h), LaggedStart(*[GrowArrow(a) for a in bad], lag_ratio=0.15), FadeIn(bad_title), run_time=1.0)
        self.play(GrowArrow(arrow), FadeIn(fix), run_time=0.7)
        self.play(FadeIn(good, shift=LEFT * 0.15), FadeIn(good_title), run_time=0.9)
        self.play(FadeIn(formula), run_time=0.5)
        self.wait(1.5)
        fade_all(self)

    def reflection(self):
        add_base(self)
        h = header(4, "RIGHT-HANDEDNESS", "正交还不够：镜像必须被排除")
        lc, rc = LEFT * 3.1 + DOWN * 0.15, RIGHT * 3.1 + DOWN * 0.15
        valid = triad(lc, 0, 1.35)
        mirror = triad(rc, 0, 1.35, mirrored=True)
        check = label_chip("det(R) = +1 · 真旋转", Y_GREEN).next_to(lc, DOWN, buff=1.75)
        cross = label_chip("det(R) = −1 · 镜像", X_RED).next_to(rc, DOWN, buff=1.75)
        divider = DashedLine(UP * 2.2, DOWN * 2.25, color=LINE, stroke_width=1.2)
        cap = bottom_caption("SO(3) = 正交矩阵中保持右手性的那一半。", TEXT)

        self.play(FadeIn(h), Create(divider), run_time=0.6)
        self.play(FadeIn(valid), FadeIn(check), run_time=0.8)
        self.play(FadeIn(mirror), FadeIn(cross), run_time=0.8)
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(1.7)
        fade_all(self)

    def choose_tool(self):
        add_base(self)
        h = header(5, "CHOOSE BY OPERATION", "不要问谁最好，要问接下来要做什么")
        cards = VGroup(
            statement("矩阵", ["变换向量", "复合与几何推导"], 2.85, Z_BLUE),
            statement("欧拉角", ["给人阅读", "日志与界面"], 2.85, ORANGE),
            statement("轴角", ["解释最短旋转", "构造姿态误差"], 2.85, Y_GREEN),
            statement("四元数", ["姿态传输", "连续插值"], 2.85, VIOLET),
        ).arrange(RIGHT, buff=0.22).shift(UP * 0.05)
        formula = formula_bar("表示不同，物理姿态相同", CYAN, size=25).next_to(cards, DOWN, buff=0.42)
        cap = bottom_caption("先确定操作，再选择最合适的旋转语言。", TEXT)
        self.play(FadeIn(h), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.10) for c in cards], lag_ratio=0.15), run_time=1.2)
        self.play(FadeIn(formula), FadeIn(cap), run_time=0.7)
        self.wait(2.5)


class RotationRepresentationsSO3Poster(Scene):
    def construct(self):
        add_base(self)
        h = header(0, "ONE POSE · FOUR LANGUAGES", "旋转表示与 SO(3)")
        c = LEFT * 4.5 + DOWN * 0.10
        axes = triad(c, 45 * DEGREES, 1.55)
        cards = VGroup(
            statement("矩阵", ["作用于向量", "RᵀR=I, det=1"], 3.65, Z_BLUE),
            statement("欧拉角", ["适合人读", "顺序决定含义"], 3.65, ORANGE),
            statement("轴角", ["绕哪根轴", "转多少角度"], 3.65, Y_GREEN),
            statement("四元数", ["插值与传输", "单位范数"], 3.65, VIOLET),
        ).arrange_in_grid(rows=2, cols=2, buff=(0.25, 0.25)).to_edge(RIGHT, buff=0.35).shift(DOWN * 0.05)
        cap = bottom_caption("四种表示，描述同一个末端姿态。", TEXT)
        self.add(h, axes, cards, cap)
