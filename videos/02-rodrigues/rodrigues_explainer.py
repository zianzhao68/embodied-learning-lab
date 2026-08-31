from manim import *
import numpy as np

# Site-aligned visual language
BG = "#F7F9F6"
INK = "#17201D"
MUTED = "#66716C"
RED = "#DC4F42"
GREEN = "#24945C"
BLUE = "#3568D4"
ORANGE = "#C97826"
ACCENT = "#176B52"
SOFT = "#E8F3ED"
LINE = "#D9DFDA"
FONT = "SimHei"

config.background_color = BG


def zh(text, size=34, color=INK, weight=NORMAL):
    return Text(text, font=FONT, font_size=size, color=color, weight=weight)


def title(text, kicker=None):
    main = zh(text, 44, INK, BOLD).to_edge(UP, buff=0.78)
    if kicker is None:
        return VGroup(main)
    tag = zh(kicker, 20, ACCENT, BOLD)
    tag.next_to(main, UP, buff=0.12).align_to(main, LEFT)
    return VGroup(tag, main)


def pill(text, color=ACCENT):
    label = zh(text, 23, color, BOLD)
    box = RoundedRectangle(
        corner_radius=0.14,
        width=label.width + 0.44,
        height=label.height + 0.28,
        stroke_color=color,
        stroke_width=1.5,
        fill_color=BG,
        fill_opacity=0.96,
    )
    return VGroup(box, label)


def note_card(lines, width=5.4, accent=ACCENT):
    texts = VGroup()
    for i, line in enumerate(lines):
        if line == "":
            spacer = Rectangle(width=0.01, height=0.16, stroke_opacity=0, fill_opacity=0)
            texts.add(spacer)
        else:
            texts.add(zh(line, 24 if i else 27, INK if i else accent, BOLD if i == 0 else NORMAL))
    texts.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
    box = RoundedRectangle(
        corner_radius=0.18,
        width=width,
        height=texts.height + 0.58,
        stroke_color=LINE,
        stroke_width=1.5,
        fill_color=WHITE,
        fill_opacity=0.97,
    )
    texts.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.28)
    return VGroup(box, texts)


def scene_number(number, text):
    n = zh(f"0{number}", 19, ACCENT, BOLD)
    t = zh(text, 23, MUTED)
    group = VGroup(n, t).arrange(RIGHT, buff=0.16)
    group.to_corner(UL, buff=0.35)
    return group


class RodriguesGeometricExplainer(Scene):
    def construct(self):
        self.camera.background_color = BG
        self.scene_1_question()
        self.scene_2_circle()
        self.scene_3_tangent()
        self.scene_4_weights()
        self.scene_5_add_center()
        self.scene_6_summary()

    def clear_scene(self, run_time=0.7):
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=run_time)

    def side_geometry(self):
        origin = np.array([-3.1, -2.15, 0])
        center = np.array([-3.1, 0.85, 0])
        point = np.array([0.05, 0.85, 0])

        axis = Arrow(origin + DOWN * 0.25, center + UP * 2.3, buff=0, color=BLUE,
                     stroke_width=7, max_tip_length_to_length_ratio=0.08)
        axis_label = zh("旋转轴  u = +z", 24, BLUE, BOLD).next_to(axis.get_end(), RIGHT, buff=0.15)
        orbit = ParametricFunction(
            lambda t: center + np.array([3.15 * np.cos(t) - 1.0 * np.sin(t), 0.70 * np.sin(t), 0]),
            t_range=[0, TAU], color=GREEN, stroke_width=3.5,
        )
        orbit.set_stroke(opacity=0.65)
        p_arrow = Arrow(origin, point, buff=0.05, color=RED, stroke_width=6)
        p_label = zh("p = (2, 0, 3)", 25, RED, BOLD).next_to(p_arrow.get_end(), RIGHT, buff=0.15)
        dot = Dot(point, radius=0.11, color=RED)
        center_dot = Dot(center, radius=0.075, color=INK)
        o_label = zh("O", 22, MUTED).next_to(origin, DOWN + LEFT, buff=0.08)
        c_label = zh("圆心", 21, MUTED).next_to(center_dot, LEFT, buff=0.14)
        return {
            "origin": origin, "center": center, "point": point,
            "axis": axis, "axis_label": axis_label, "orbit": orbit,
            "p_arrow": p_arrow, "p_label": p_label, "dot": dot,
            "center_dot": center_dot, "o_label": o_label, "c_label": c_label,
        }

    def scene_1_question(self):
        marker = scene_number(1, "先看我们要解决的问题")
        heading = title("点 P 绕 z 轴旋转，怎样算出它的新位置？")
        g = self.side_geometry()
        diagram = VGroup(g["axis"], g["axis_label"], g["orbit"], g["p_arrow"],
                         g["p_label"], g["dot"], g["center_dot"], g["o_label"])
        diagram.shift(LEFT * 0.8 + DOWN * 0.95)
        steps = note_card([
            "轨迹是一个圆",
            "① 找圆心",
            "② 找半径",
            "③ 找平面内第二方向",
        ], width=4.5)
        steps.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.35)

        self.play(FadeIn(marker), Write(heading), run_time=1.0)
        self.play(Create(g["axis"]), FadeIn(g["axis_label"]), run_time=0.8)
        self.play(GrowArrow(g["p_arrow"]), FadeIn(g["p_label"], g["dot"], g["o_label"]), run_time=1.0)
        self.play(Create(g["orbit"]), FadeIn(g["center_dot"]), run_time=1.0)
        self.play(FadeIn(steps, shift=LEFT * 0.25), run_time=0.9)
        warning = pill("注意：不是把 p 拆成三个分量", ORANGE)
        warning.to_edge(DOWN, buff=0.38)
        self.play(FadeIn(warning, shift=UP * 0.15), run_time=0.7)
        self.wait(1.6)
        self.clear_scene()

    def scene_2_circle(self):
        marker = scene_number(2, "平行分量找圆心，垂直分量找半径")
        heading = title("第一步：只拆成两个真实分量")
        g = self.side_geometry()
        all_geo = VGroup(g["axis"], g["axis_label"], g["orbit"], g["dot"],
                         g["center_dot"], g["o_label"], g["c_label"])
        all_geo.shift(LEFT * 0.9 + DOWN * 0.95)
        origin = g["origin"] + LEFT * 0.9 + DOWN * 0.95
        center = g["center"] + LEFT * 0.9 + DOWN * 0.95
        point = g["point"] + LEFT * 0.9 + DOWN * 0.95

        parallel = Arrow(origin, center, buff=0.04, color=BLUE, stroke_width=7)
        perpendicular = Arrow(center, point, buff=0.05, color=GREEN, stroke_width=7)
        l_parallel = pill("p_parallel = (0, 0, 3)", BLUE).scale(0.92).next_to(parallel, RIGHT, buff=0.18).shift(DOWN * 1.05)
        l_perp = pill("p_perp = (2, 0, 0)", GREEN).scale(0.92).next_to(perpendicular, UP, buff=0.18)

        self.play(FadeIn(marker), Write(heading), run_time=1.0)
        self.play(FadeIn(all_geo), run_time=0.8)
        self.play(GrowArrow(parallel), FadeIn(l_parallel), run_time=1.0)
        center_note = zh("高度不变 → 圆心", 24, BLUE, BOLD).to_edge(RIGHT, buff=0.7).shift(UP * 1.0)
        self.play(FadeIn(center_note, shift=LEFT * 0.2), run_time=0.6)
        self.play(GrowArrow(perpendicular), FadeIn(l_perp), run_time=1.0)
        radius_note = zh("水平距离 → 半径", 24, GREEN, BOLD).next_to(center_note, DOWN, aligned_edge=LEFT, buff=0.3)
        self.play(FadeIn(radius_note, shift=LEFT * 0.2), run_time=0.6)

        theta = ValueTracker(0)
        moving_dot = always_redraw(lambda: Dot(
            center + np.array([3.15 * np.cos(theta.get_value()) - 1.0 * np.sin(theta.get_value()), 0.70 * np.sin(theta.get_value()), 0]),
            radius=0.11, color=RED
        ))
        moving_radius = always_redraw(lambda: Line(
            center,
            center + np.array([3.15 * np.cos(theta.get_value()) - 1.0 * np.sin(theta.get_value()), 0.70 * np.sin(theta.get_value()), 0]),
            color=GREEN, stroke_width=5
        ))
        self.remove(g["dot"])
        self.add(moving_radius, moving_dot)
        self.play(theta.animate.set_value(TAU), run_time=3.3, rate_func=linear)

        equation = pill("p = p_parallel + p_perp   （只有两个分量）", ACCENT)
        equation.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(equation, shift=UP * 0.15), run_time=0.8)
        self.wait(1.4)
        self.clear_scene()

    def scene_3_tangent(self):
        marker = scene_number(3, "切换到旋转圆的俯视图")
        heading = title("第二步：切向量是辅助方向，不是第三个分量")
        center = LEFT * 2.65 + DOWN * 0.25
        radius = 2.35
        circle = Circle(radius=radius, color=LINE, stroke_width=3).move_to(center)
        c = Dot(center, color=INK, radius=0.08)
        radius_arrow = Arrow(center, center + RIGHT * radius, buff=0.05, color=GREEN, stroke_width=7)
        tangent_arrow = Arrow(center, center + UP * radius, buff=0.05, color=ORANGE, stroke_width=7)
        r_label = pill("p_perp：当前半径", GREEN).scale(0.9).next_to(radius_arrow, DOWN, buff=0.2)
        t_label = pill("u × p：正切方向", ORANGE).scale(0.9).next_to(tangent_arrow, RIGHT, buff=0.15)
        right_angle = RightAngle(Line(center, center + RIGHT), Line(center, center + UP),
                                 length=0.28, color=MUTED)

        explanation = note_card([
            "为什么需要它？",
            "只有一根半径，无法表示",
            "圆平面内转过任意角的位置。",
            "",
            "u × p 恰好：",
            "· 在同一圆平面内",
            "· 与半径垂直",
            "· 指向右手正方向",
            "· 长度等于半径",
        ], width=5.35)
        explanation.to_edge(RIGHT, buff=0.5).shift(DOWN * 0.25)

        self.play(FadeIn(marker), Write(heading), run_time=1.0)
        self.play(Create(circle), FadeIn(c), run_time=0.8)
        self.play(GrowArrow(radius_arrow), FadeIn(r_label), run_time=0.9)
        self.play(GrowArrow(tangent_arrow), FadeIn(t_label), Create(right_angle), run_time=0.9)
        self.play(FadeIn(explanation, shift=LEFT * 0.2), run_time=0.9)
        not_part = pill("p ≠ p_parallel + p_perp + p_tan", ORANGE)
        correct = pill("正确：p = p_parallel + p_perp", ACCENT)
        pair = VGroup(not_part, correct).arrange(RIGHT, buff=0.35).to_edge(DOWN, buff=0.34)
        self.play(FadeIn(pair, shift=UP * 0.15), run_time=0.8)
        self.wait(1.8)
        self.clear_scene()

    def scene_4_weights(self):
        marker = scene_number(4, "圆平面内就是一次二维旋转")
        heading = title("第三步：cos α 与 sin α 改变两根方向的权重")
        center = LEFT * 2.8 + DOWN * 0.2
        radius = 2.45
        circle = Circle(radius=radius, color=LINE, stroke_width=3).move_to(center)
        base_x = Arrow(center, center + RIGHT * radius, buff=0.04, color=GREEN, stroke_width=5)
        base_y = Arrow(center, center + UP * radius, buff=0.04, color=ORANGE, stroke_width=5)
        theta = ValueTracker(0)

        rotated = always_redraw(lambda: Arrow(
            center,
            center + radius * np.array([np.cos(theta.get_value()), np.sin(theta.get_value()), 0]),
            buff=0.04, color=RED, stroke_width=8
        ))
        x_component = always_redraw(lambda: Line(
            center,
            center + RIGHT * radius * np.cos(theta.get_value()),
            color=GREEN, stroke_width=8
        ))
        y_component = always_redraw(lambda: Arrow(
            center + RIGHT * radius * np.cos(theta.get_value()),
            center + radius * np.array([np.cos(theta.get_value()), np.sin(theta.get_value()), 0]),
            buff=0.02, color=ORANGE, stroke_width=7
        ))
        angle_arc = always_redraw(lambda: Arc(
            radius=0.62, start_angle=0, angle=max(theta.get_value(), 0.01),
            arc_center=center, color=MUTED, stroke_width=3
        ))
        angle_text = always_redraw(lambda: zh(
            f"α = {int(round(theta.get_value() / DEGREES))}°", 24, INK, BOLD
        ).next_to(center + UR * 0.65, UR, buff=0.02))

        formula = note_card([
            "旋转后的半径",
            "= cosα · p_perp",
            "  + sinα · (u × p)",
            "",
            "0°：只剩 p_perp",
            "90°：只剩 u × p",
        ], width=5.0)
        formula.to_edge(RIGHT, buff=0.6).shift(DOWN * 0.2)

        self.play(FadeIn(marker), Write(heading), run_time=1.0)
        self.play(Create(circle), GrowArrow(base_x), GrowArrow(base_y), run_time=1.0)
        self.add(x_component, y_component, rotated, angle_arc, angle_text)
        self.play(FadeIn(formula, shift=LEFT * 0.2), run_time=0.8)
        self.play(theta.animate.set_value(30 * DEGREES), run_time=2.1, rate_func=smooth)
        self.wait(0.8)
        self.play(theta.animate.set_value(90 * DEGREES), run_time=2.5, rate_func=smooth)
        self.wait(1.4)
        self.clear_scene()

    def scene_5_add_center(self):
        marker = scene_number(5, "回到三维侧视图")
        heading = title("最后：把旋转后的半径加回不动的圆心")
        g = self.side_geometry()
        shift = LEFT * 1.0 + DOWN * 0.95
        base = VGroup(g["axis"], g["axis_label"], g["orbit"], g["center_dot"], g["o_label"])
        base.shift(shift)
        origin = g["origin"] + shift
        center = g["center"] + shift
        initial = g["point"] + shift
        final = center + np.array([-1.0, 0.70, 0])

        parallel = Arrow(origin, center, buff=0.04, color=BLUE, stroke_width=7)
        old_radius = Arrow(center, initial, buff=0.05, color=GREEN, stroke_width=6)
        new_radius = Arrow(center, final, buff=0.05, color=ORANGE, stroke_width=7)
        result = Arrow(origin, final, buff=0.05, color=RED, stroke_width=7)
        old_dot = Dot(initial, radius=0.11, color=GREEN)
        new_dot = Dot(final, radius=0.11, color=RED)

        result_card = note_card([
            "90° 结果",
            "圆心： (0, 0, 3) 不动",
            "半径： +x  转到  +y",
            "",
            "(2, 0, 3)  →  (0, 2, 3)",
        ], width=5.2)
        result_card.to_edge(RIGHT, buff=0.5).shift(DOWN * 0.15)

        self.play(FadeIn(marker), Write(heading), run_time=1.0)
        self.play(FadeIn(base), GrowArrow(parallel), run_time=0.9)
        self.play(GrowArrow(old_radius), FadeIn(old_dot), run_time=0.8)
        self.play(Transform(old_radius, new_radius), Transform(old_dot, new_dot), run_time=1.4)
        self.play(GrowArrow(result), FadeIn(result_card, shift=LEFT * 0.2), run_time=1.0)
        p30 = pill("30°： (2, 0, 3) → (√3, 1, 3)", ACCENT)
        p30.to_edge(DOWN, buff=0.36)
        self.play(FadeIn(p30, shift=UP * 0.15), run_time=0.8)
        self.wait(1.7)
        self.clear_scene()

    def scene_6_summary(self):
        marker = scene_number(6, "把三个角色彻底分开")
        heading = title("Rodrigues 的几何核心")
        cards = VGroup(
            note_card(["p_parallel", "圆心位置", "p 的真实分量", "旋转时不动"], width=3.55, accent=BLUE),
            note_card(["p_perp", "旋转半径", "p 的真实分量", "在圆平面内转动"], width=3.55, accent=GREEN),
            note_card(["u × p", "正切辅助方向", "不是 p 的第三分量", "用于描述平面旋转"], width=3.55, accent=ORANGE),
        ).arrange(RIGHT, buff=0.35).shift(UP * 0.45)

        relation = pill("真实分解：p = p_parallel + p_perp", ACCENT)
        relation.next_to(cards, DOWN, buff=0.48)
        formula = pill("p′ = p_parallel + cosα · p_perp + sinα · (u × p)", RED)
        formula.next_to(relation, DOWN, buff=0.26)
        close = zh("先找圆，再在圆平面里做二维旋转。", 28, INK, BOLD)
        close.to_edge(DOWN, buff=0.35)

        self.play(FadeIn(marker), Write(heading), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.18) for c in cards], lag_ratio=0.22), run_time=1.5)
        self.play(FadeIn(relation, shift=UP * 0.12), run_time=0.7)
        self.play(FadeIn(formula, shift=UP * 0.12), run_time=0.8)
        self.play(Write(close), run_time=0.8)
        self.wait(3.0)


class RodriguesPoster(Scene):
    def construct(self):
        self.camera.background_color = BG
        heading = title("Rodrigues：先找圆，再做二维旋转", "三维旋转几何直觉")
        cards = VGroup(
            note_card(["p_parallel", "圆心 · 不动", "真实分量"], width=3.55, accent=BLUE),
            note_card(["p_perp", "半径 · 转动", "真实分量"], width=3.55, accent=GREEN),
            note_card(["u × p", "正切辅助方向", "不是第三分量"], width=3.55, accent=ORANGE),
        ).arrange(RIGHT, buff=0.36).shift(UP * 0.35)
        relation = pill("p = p_parallel + p_perp", ACCENT).next_to(cards, DOWN, buff=0.5)
        formula = pill("p′ = p_parallel + cosα · p_perp + sinα · (u × p)", RED)
        formula.next_to(relation, DOWN, buff=0.28)
        example = zh("示例：(2, 0, 3)  绕 +z 旋转 90°  →  (0, 2, 3)", 27, INK, BOLD)
        example.to_edge(DOWN, buff=0.55)
        self.add(heading, cards, relation, formula, example)
