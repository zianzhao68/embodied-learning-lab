from manim import *
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from manim_style import *


class RodriguesGeometricExplainer(Scene):
    def construct(self):
        self.problem()
        self.decompose()
        self.tangent()
        self.rotate_in_plane()
        self.rebuild()
        self.summary()

    @staticmethod
    def side_points(shift=ORIGIN):
        origin = np.array([-3.2, -2.2, 0]) + shift
        center = np.array([-3.2, 0.35, 0]) + shift
        x_basis = np.array([2.65, 0.0, 0])
        y_basis = np.array([-0.85, 0.62, 0])
        return origin, center, x_basis, y_basis

    def side_orbit(self, shift=ORIGIN):
        origin, center, xb, yb = self.side_points(shift)
        orbit = ParametricFunction(
            lambda t: center + xb * np.cos(t) + yb * np.sin(t),
            t_range=[0, TAU], color=Y_GREEN, stroke_width=2.0,
        ).set_fill(opacity=0).set_stroke(opacity=0.65)
        axis = clean_axis(origin + DOWN * 0.18, center + UP * 2.0, Z_BLUE, "u = +z", RIGHT)
        return origin, center, xb, yb, orbit, axis

    def problem(self):
        add_base(self)
        h = header(1, "RODRIGUES · 几何目标", "点 P 绕轴旋转，轨迹为什么是一个圆？")
        origin, center, xb, _, orbit, axis = self.side_orbit(DOWN * 0.35)
        point = center + xb
        p = clean_arrow(origin, point, X_RED, 3.6, 0.16)
        dot = Dot(point, radius=0.075, color=X_RED)
        p_tag = label_chip("p = (2, 0, 3)", X_RED, mono=True).scale(0.9).next_to(point, RIGHT, buff=0.12)
        card = statement("计算路线", ["① 找旋转圆的圆心", "② 找旋转圆的半径", "③ 在圆平面内旋转"], 4.6, CYAN)
        card.to_edge(RIGHT, buff=0.62).shift(DOWN * 0.30)
        warning = formula_bar("p 只分成两个真实分量", ORANGE, size=22).to_edge(DOWN, buff=0.30)

        self.play(FadeIn(h, shift=DOWN * 0.12), run_time=0.7)
        self.play(Create(axis), Create(orbit), run_time=1.0)
        self.play(GrowArrow(p), FadeIn(dot, p_tag), run_time=0.9)
        self.play(FadeIn(card, shift=LEFT * 0.18), run_time=0.7)
        self.play(FadeIn(warning, shift=UP * 0.10), run_time=0.5)
        self.wait(1.5)
        fade_all(self)

    def decompose(self):
        add_base(self)
        h = header(2, "圆心 + 半径", "第一步：只拆成平行与垂直两个分量")
        origin, center, xb, yb, orbit, axis = self.side_orbit(DOWN * 0.35)
        point = center + xb
        parallel = clean_arrow(origin, center, Z_BLUE, 3.5, 0.15)
        radius = clean_arrow(center, point, Y_GREEN, 3.5, 0.15)
        c_dot = Dot(center, radius=0.06, color=TEXT)
        p_dot = Dot(point, radius=0.075, color=X_RED)
        para_tag = label_chip("p_parallel = (0, 0, 3)", Z_BLUE, mono=True).scale(0.82)
        para_tag.next_to(parallel, RIGHT, buff=0.18).shift(DOWN * 0.85)
        perp_tag = label_chip("p_perp = (2, 0, 0)", Y_GREEN, mono=True).scale(0.82)
        perp_tag.next_to(radius, UP, buff=0.14)
        facts = statement("两个量分别解决什么？", ["圆心：沿轴的高度保持不变", "半径：点到旋转轴的距离", "· 旋转只改变半径方向"], 4.8, CYAN)
        facts.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.30)
        equation = formula_bar("p = p_parallel + p_perp", CYAN, size=23).to_edge(DOWN, buff=0.28)

        self.play(FadeIn(h), FadeIn(axis), Create(orbit), run_time=0.8)
        self.play(GrowArrow(parallel), FadeIn(c_dot, para_tag), run_time=0.8)
        self.play(GrowArrow(radius), FadeIn(p_dot, perp_tag), run_time=0.8)
        self.play(FadeIn(facts, shift=LEFT * 0.15), run_time=0.7)

        theta = ValueTracker(0)
        mover = always_redraw(lambda: Dot(center + xb * np.cos(theta.get_value()) + yb * np.sin(theta.get_value()), radius=0.07, color=X_RED))
        moving_radius = always_redraw(lambda: Line(center, center + xb * np.cos(theta.get_value()) + yb * np.sin(theta.get_value()), color=Y_GREEN, stroke_width=2.8))
        self.add(moving_radius, mover)
        self.play(theta.animate.set_value(TAU), run_time=2.8, rate_func=linear)
        self.play(FadeIn(equation, shift=UP * 0.08), run_time=0.5)
        self.wait(1.2)
        fade_all(self)

    def tangent(self):
        add_base(self)
        h = header(3, "旋转圆 · 俯视图", "第二步：叉乘只是在平面里补一根方向")
        c = LEFT * 2.75 + DOWN * 0.20
        r = 2.15
        circle = Circle(r, color=LINE, stroke_width=1.5).move_to(c)
        radial = clean_arrow(c, c + RIGHT * r, Y_GREEN, 3.2, 0.15)
        tangent = clean_arrow(c, c + UP * r, ORANGE, 3.2, 0.15)
        right = RightAngle(Line(c, c + RIGHT), Line(c, c + UP), length=0.22, color=MUTED, stroke_width=1.5)
        r_tag = label_chip("p_perp · 当前半径", Y_GREEN, mono=True).scale(0.82).next_to(radial, DOWN, buff=0.16)
        t_tag = label_chip("u × p · 正切辅助方向", ORANGE, mono=True).scale(0.82).next_to(tangent, RIGHT, buff=0.12)
        card = statement("为什么需要第二根方向？", ["一根半径只能表示当前位置", "任意平面位置需要两根坐标方向", "· u × p 与半径垂直", "· 指向右手正旋转方向", "· 长度与半径相同"], 5.1, CYAN)
        card.to_edge(RIGHT, buff=0.45).shift(DOWN * 0.25)
        no = formula_bar("错误：p = p_parallel + p_perp + p_tan", X_RED, size=19)
        yes = formula_bar("正确：p = p_parallel + p_perp", Y_GREEN, size=19)
        compare = VGroup(no, yes).arrange(RIGHT, buff=0.25).to_edge(DOWN, buff=0.25)

        self.play(FadeIn(h), Create(circle), run_time=0.8)
        self.play(GrowArrow(radial), FadeIn(r_tag), run_time=0.7)
        self.play(GrowArrow(tangent), FadeIn(t_tag), Create(right), run_time=0.8)
        self.play(FadeIn(card, shift=LEFT * 0.15), run_time=0.7)
        self.play(FadeIn(compare, shift=UP * 0.08), run_time=0.6)
        self.wait(1.8)
        fade_all(self)

    def rotate_in_plane(self):
        add_base(self)
        h = header(4, "圆平面 = 二维坐标", "第三步：cos α 与 sin α 控制两根方向的权重")
        c = LEFT * 2.75 + DOWN * 0.15
        r = 2.10
        circle = Circle(r, color=LINE, stroke_width=1.5).move_to(c)
        x_axis = clean_arrow(c, c + RIGHT * r, Y_GREEN, 2.5, 0.13)
        y_axis = clean_arrow(c, c + UP * r, ORANGE, 2.5, 0.13)
        theta = ValueTracker(0)
        rotated = always_redraw(lambda: clean_arrow(c, c + r * np.array([np.cos(theta.get_value()), np.sin(theta.get_value()), 0]), X_RED, 3.5, 0.16))
        x_comp = always_redraw(lambda: Line(c, c + RIGHT * r * np.cos(theta.get_value()), color=Y_GREEN, stroke_width=3.5))
        y_comp = always_redraw(lambda: clean_arrow(c + RIGHT * r * np.cos(theta.get_value()), c + r * np.array([np.cos(theta.get_value()), np.sin(theta.get_value()), 0]), ORANGE, 3.2, 0.13))
        arc = always_redraw(lambda: Arc(radius=0.52, start_angle=0, angle=max(theta.get_value(), 0.01), arc_center=c, color=MUTED, stroke_width=1.6))
        angle = always_redraw(lambda: code_text(f"α = {int(round(theta.get_value()/DEGREES))}°", 18, TEXT, MEDIUM).next_to(c + UR * 0.58, UR, buff=0.02))
        formula = statement("旋转后的半径", ["cosα · p_perp", "+ sinα · (u × p)", "", "0°  →  只剩 p_perp", "90° →  只剩 u × p"], 4.9, CYAN)
        formula.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.15)

        self.play(FadeIn(h), Create(circle), GrowArrow(x_axis), GrowArrow(y_axis), run_time=0.9)
        self.add(x_comp, y_comp, rotated, arc, angle)
        self.play(FadeIn(formula, shift=LEFT * 0.15), run_time=0.6)
        self.play(theta.animate.set_value(30 * DEGREES), run_time=1.8, rate_func=smooth)
        self.wait(0.6)
        self.play(theta.animate.set_value(90 * DEGREES), run_time=2.2, rate_func=smooth)
        self.wait(1.2)
        fade_all(self)

    def rebuild(self):
        add_base(self)
        h = header(5, "重新组合", "最后：把转过的半径加回不动的圆心")
        origin, center, xb, yb, orbit, axis = self.side_orbit(DOWN * 0.35)
        final = center + yb
        parallel = clean_arrow(origin, center, Z_BLUE, 3.2, 0.14)
        old_r = clean_arrow(center, center + xb, Y_GREEN, 2.8, 0.14)
        new_r = clean_arrow(center, final, ORANGE, 3.2, 0.15)
        result = clean_arrow(origin, final, X_RED, 3.5, 0.16)
        card = statement("90° 结果", ["圆心 (0, 0, 3) 不动", "半径从 +x 转到 +y", "", "(2, 0, 3) → (0, 2, 3)"], 4.8, Y_GREEN)
        card.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.10)
        p30 = formula_bar("30°： (2, 0, 3) → (√3, 1, 3)", CYAN, size=21).to_edge(DOWN, buff=0.27)

        self.play(FadeIn(h), FadeIn(axis), Create(orbit), run_time=0.8)
        self.play(GrowArrow(parallel), GrowArrow(old_r), run_time=0.8)
        self.play(Transform(old_r, new_r), run_time=1.1)
        self.play(GrowArrow(result), FadeIn(card, shift=LEFT * 0.15), run_time=0.8)
        self.play(FadeIn(p30, shift=UP * 0.08), run_time=0.5)
        self.wait(1.6)
        fade_all(self)

    def summary(self):
        add_base(self)
        h = header(6, "ONE-SCREEN RECAP", "Rodrigues：先找圆，再在圆平面里做二维旋转")
        cards = VGroup(
            statement("p_parallel", ["圆心位置", "p 的真实分量", "旋转时不动"], 3.7, Z_BLUE),
            statement("p_perp", ["旋转半径", "p 的真实分量", "在圆平面内转动"], 3.7, Y_GREEN),
            statement("u × p", ["正切辅助方向", "不是 p 的第三分量", "用于描述平面旋转"], 3.7, ORANGE),
        ).arrange(RIGHT, buff=0.28).shift(UP * 0.20)
        relation = formula_bar("p = p_parallel + p_perp", Y_GREEN, size=22).next_to(cards, DOWN, buff=0.35)
        formula = formula_bar("p′ = p_parallel + cosα·p_perp + sinα·(u × p)", X_RED, size=21).next_to(relation, DOWN, buff=0.20)
        cap = bottom_caption("切向量不是第三个分量；它只是圆平面里的第二根坐标方向。", TEXT)

        self.play(FadeIn(h), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.10) for c in cards], lag_ratio=0.16), run_time=1.1)
        self.play(FadeIn(relation), FadeIn(formula), run_time=0.8)
        self.play(FadeIn(cap), run_time=0.5)
        self.wait(2.8)


class RodriguesPoster(Scene):
    def construct(self):
        add_base(self)
        h = header(0, "三维旋转几何直觉", "Rodrigues：圆心、半径与辅助切向方向")
        cards = VGroup(
            statement("p_parallel", ["圆心 · 不动", "真实分量"], 3.65, Z_BLUE),
            statement("p_perp", ["半径 · 转动", "真实分量"], 3.65, Y_GREEN),
            statement("u × p", ["切向辅助方向", "不是第三分量"], 3.65, ORANGE),
        ).arrange(RIGHT, buff=0.30).shift(UP * 0.10)
        relation = formula_bar("p = p_parallel + p_perp", Y_GREEN, size=23).next_to(cards, DOWN, buff=0.38)
        formula = formula_bar("p′ = p_parallel + cosα·p_perp + sinα·(u × p)", X_RED, size=22).next_to(relation, DOWN, buff=0.22)
        cap = bottom_caption("示例：(2, 0, 3) 绕 +z 旋转 90° → (0, 2, 3)", TEXT)
        self.add(h, cards, relation, formula, cap)
