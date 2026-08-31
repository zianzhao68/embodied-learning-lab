from manim import *
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manim_style import *


def rx(a):
    return np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])


def ry(a):
    return np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])


def proj(v, center, scale=1.25):
    x, y, z = v
    return center + scale * np.array([x - 0.55 * y, 0.32 * x + 0.30 * y + z, 0])


def projected_arrow(center, vector, color, label=None, width=3.0):
    end = proj(vector, center)
    arr = clean_arrow(center, end, color, width, 0.14)
    if label is None:
        return VGroup(arr)
    tag = code_text(label, 18, color, BOLD).next_to(end, RIGHT if end[0] >= center[0] else LEFT, buff=0.07)
    return VGroup(arr, tag)


def world_triad(center, scale=1.0):
    return VGroup(
        projected_arrow(center, np.array([scale, 0, 0]), X_RED, "x"),
        projected_arrow(center, np.array([0, scale, 0]), Y_GREEN, "y"),
        projected_arrow(center, np.array([0, 0, scale]), Z_BLUE, "z"),
        Dot(center, radius=0.05, color=TEXT),
    )


class EulerGimbalExplainer(Scene):
    def construct(self):
        self.order_matters()
        self.intrinsic_extrinsic()
        self.normal_axes()
        self.align_axes()
        self.non_unique()
        self.recap()

    def order_matters(self):
        add_base(self)
        h = header(1, "NON-COMMUTATIVE", "先绕 x 再绕 y，不等于先绕 y 再绕 x")
        lc, rc = LEFT * 3.25 + DOWN * 0.35, RIGHT * 3.25 + DOWN * 0.35
        divider = DashedLine(UP * 2.2, DOWN * 2.2, color=LINE, stroke_width=1.0)
        p0 = np.array([0, 0, 1])
        left0 = projected_arrow(lc, p0, MUTED, "起点 p")
        right0 = projected_arrow(rc, p0, MUTED, "起点 p")
        l1 = projected_arrow(lc, rx(90*DEGREES) @ p0, X_RED, "Rx 后")
        l2 = projected_arrow(lc, ry(90*DEGREES) @ rx(90*DEGREES) @ p0, CYAN, "最终 −y")
        r1 = projected_arrow(rc, ry(90*DEGREES) @ p0, Y_GREEN, "Ry 后")
        r2 = projected_arrow(rc, rx(90*DEGREES) @ ry(90*DEGREES) @ p0, VIOLET, "最终 +x")
        lt = label_chip("Rx → Ry", X_RED, mono=True).next_to(lc, DOWN, buff=1.75)
        rt = label_chip("Ry → Rx", Y_GREEN, mono=True).next_to(rc, DOWN, buff=1.75)
        cap = bottom_caption("矩阵从右向左作用；交换顺序会改变最终方向。", TEXT)

        self.play(FadeIn(h), Create(divider), FadeIn(left0, right0, lt, rt), run_time=0.8)
        self.play(Transform(left0, l1), Transform(right0, r1), run_time=1.0)
        self.play(Transform(left0, l2), Transform(right0, r2), run_time=1.0)
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(1.5)
        fade_all(self)

    def intrinsic_extrinsic(self):
        add_base(self)
        h = header(2, "REFERENCE AXES", "内旋看物体自身轴，外旋看固定世界轴")
        lc, rc = LEFT * 3.2 + DOWN * 0.25, RIGHT * 3.2 + DOWN * 0.25
        fixed_left = world_triad(lc, 1.25).set_opacity(0.25)
        moving = world_triad(lc, 1.15)
        fixed_right = world_triad(rc, 1.25)
        moved_right = world_triad(rc, 1.05).rotate(35*DEGREES, about_point=rc).set_opacity(0.55)
        lcard = statement("内旋 intrinsic", ["绕已经转动的自身轴", "叙事：ZYX（yaw→pitch→roll）"], 5.0, VIOLET).next_to(lc, DOWN, buff=1.55)
        rcard = statement("外旋 extrinsic", ["绕始终固定的世界轴", "叙事：XYZ（roll→pitch→yaw）"], 5.0, CYAN).next_to(rc, DOWN, buff=1.55)
        eq = formula_bar("同一矩阵：内旋 ZYX  ≡  外旋 XYZ", Y_GREEN, size=22).to_edge(DOWN, buff=0.22)

        self.play(FadeIn(h), FadeIn(fixed_left, moving, fixed_right), run_time=0.8)
        self.play(Rotate(moving, 35*DEGREES, about_point=lc), FadeIn(moved_right), run_time=1.2)
        self.play(FadeIn(lcard, rcard, shift=UP*0.08), run_time=0.8)
        self.play(FadeIn(eq), run_time=0.5)
        self.wait(1.4)
        fade_all(self)

    def normal_axes(self):
        add_base(self)
        h = header(3, "ZYX · NORMAL", "pitch 未到 ±90°：三个有效方向彼此独立")
        c = LEFT * 2.7 + DOWN * 0.30
        yaw = projected_arrow(c, np.array([0, 0, 1.35]), Z_BLUE, "yaw · 世界 z", 2.8)
        pitch = projected_arrow(c, np.array([0, 1.25, 0]), Y_GREEN, "pitch · 中间 y", 2.8)
        roll = projected_arrow(c, np.array([1.25, 0, 0]), X_RED, "roll · 当前 x", 2.8)
        rings = VGroup(
            Ellipse(4.1, 1.1, color=Z_BLUE, stroke_width=1.4).move_to(c).set_fill(opacity=0).set_stroke(opacity=0.55),
            Ellipse(2.0, 3.7, color=Y_GREEN, stroke_width=1.4).move_to(c).rotate(-18*DEGREES).set_fill(opacity=0).set_stroke(opacity=0.55),
            Ellipse(2.0, 3.7, color=X_RED, stroke_width=1.4).move_to(c).rotate(50*DEGREES).set_fill(opacity=0).set_stroke(opacity=0.55),
        )
        card = statement("此时可以独立调节", ["yaw：改变朝向", "pitch：抬头/低头", "roll：绕前向轴翻滚", "· 参数到姿态仍局部一一对应"], 4.9, CYAN)
        card.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.18)
        cap = bottom_caption("三个箭头不共线，因此能产生三种独立的小旋转。", TEXT)

        self.play(FadeIn(h), LaggedStart(*[Create(r) for r in rings], lag_ratio=0.15), run_time=1.0)
        self.play(LaggedStart(FadeIn(yaw), FadeIn(pitch), FadeIn(roll), lag_ratio=0.16), run_time=0.9)
        self.play(FadeIn(card, shift=LEFT*0.12), FadeIn(cap), run_time=0.8)
        self.wait(1.5)
        fade_all(self)

    def align_axes(self):
        add_base(self)
        h = header(4, "GIMBAL LOCK", "增加 pitch，roll 轴会逐渐转向 yaw 轴")
        c = LEFT * 2.8 + DOWN * 0.25
        theta = ValueTracker(0)
        yaw = projected_arrow(c, np.array([0, 0, 1.45]), Z_BLUE, "yaw · +z", 2.8)
        pitch = projected_arrow(c, np.array([0, 1.25, 0]), Y_GREEN, "pitch", 2.8)
        roll = always_redraw(lambda: projected_arrow(c, np.array([np.cos(theta.get_value()), 0, -np.sin(theta.get_value())])*1.35, X_RED, "roll · 当前 x", 2.8))
        angle = always_redraw(lambda: code_text(f"pitch = {int(round(theta.get_value()/DEGREES))}°", 21, CYAN, MEDIUM).next_to(c, DOWN, buff=1.70))
        card = statement("到 90° 时发生什么？", ["roll 轴 = −z", "yaw 轴  = +z", "两根轴反向共线", "· 两个控制量只剩一个有效方向"], 4.9, ORANGE)
        card.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.20)
        alert = formula_bar("锁住的是方向独立性，不是 pitch 电机", X_RED, size=21).to_edge(DOWN, buff=0.23)

        self.play(FadeIn(h), FadeIn(yaw, pitch, roll, angle), run_time=0.8)
        self.play(FadeIn(card, shift=LEFT*0.12), run_time=0.6)
        self.play(theta.animate.set_value(90*DEGREES), run_time=3.0, rate_func=smooth)
        self.play(FadeIn(alert, shift=UP*0.08), run_time=0.5)
        self.wait(1.6)
        fade_all(self)

    def non_unique(self):
        add_base(self)
        h = header(5, "PARAMETER AMBIGUITY", "pitch = 90° 后，矩阵只看得到 roll − yaw")
        left = statement("三组参数", ["roll 20° · yaw   0°", "roll 50° · yaw 30°", "roll   0° · yaw −20°"], 5.2, CYAN)
        left.to_edge(LEFT, buff=0.65).shift(DOWN*0.10)
        right = statement("共同结果", ["roll − yaw = 20°", "三组参数 → 同一个姿态", "", "反例：roll 单独到 90°", "只要 pitch ≠ ±90° 就不会锁"], 5.2, Y_GREEN)
        right.to_edge(RIGHT, buff=0.65).shift(DOWN*0.10)
        arrow = clean_arrow(LEFT*0.75+DOWN*0.1, RIGHT*0.75+DOWN*0.1, ORANGE, 2.5, 0.13)
        cap = bottom_caption("若更换轴顺序，发生奇异的仍是中间那次旋转。", TEXT)

        self.play(FadeIn(h), FadeIn(left, shift=RIGHT*0.12), run_time=0.8)
        self.play(GrowArrow(arrow), FadeIn(right, shift=LEFT*0.12), run_time=0.9)
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(1.8)
        fade_all(self)

    def recap(self):
        add_base(self)
        h = header(6, "RECAP", "万向节锁是欧拉角坐标的奇异，不是物理姿态消失")
        cards = VGroup(
            statement("触发条件", ["三个不同轴的顺序中", "中间角到 ±90°"], 3.65, ORANGE),
            statement("几何机制", ["首末有效轴共线", "三个方向只剩两个"], 3.65, X_RED),
            statement("工程处理", ["内部使用矩阵/四元数", "界面再转换欧拉角"], 3.65, Y_GREEN),
        ).arrange(RIGHT, buff=0.30).shift(UP*0.05)
        formula = formula_bar("ZYX：pitch = ±90°  →  roll 与 yaw 耦合", CYAN, size=22).next_to(cards, DOWN, buff=0.38)
        cap = bottom_caption("参数化出了问题，机器人仍然可以经过这个姿态。", TEXT)
        self.play(FadeIn(h), LaggedStart(*[FadeIn(c, shift=UP*0.08) for c in cards], lag_ratio=0.16), run_time=1.2)
        self.play(FadeIn(formula), FadeIn(cap), run_time=0.7)
        self.wait(2.5)


class EulerGimbalPoster(Scene):
    def construct(self):
        add_base(self)
        h = header(0, "ZYX EULER ANGLES", "万向节锁：不是 pitch 被锁死")
        c = LEFT * 3.7 + DOWN * 0.2
        yaw = projected_arrow(c, np.array([0,0,1.55]), Z_BLUE, "yaw · +z", 3.0)
        roll = projected_arrow(c, np.array([0,0,-1.35]), X_RED, "roll · −z", 3.0)
        pitch = projected_arrow(c, np.array([0,1.25,0]), Y_GREEN, "pitch = 90°", 3.0)
        card = statement("真正发生的事", ["yaw 与 roll 反向共线", "三个控制方向只剩两个", "roll − yaw 才能被观察到", "", "奇异的是参数化，不是机器人"], 5.3, ORANGE)
        card.to_edge(RIGHT, buff=0.55).shift(DOWN*0.12)
        cap = bottom_caption("固定 ZYX 下，roll 或 yaw 单独到 90° 不会触发。", TEXT)
        self.add(h, yaw, roll, pitch, card, cap)
