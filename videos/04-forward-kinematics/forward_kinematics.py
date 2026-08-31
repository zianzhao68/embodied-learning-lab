from pathlib import Path
import sys

from manim import *
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))
from manim_style import *


def arm_geometry(q1, q2, origin=np.array([-3.2, -1.25, 0.0]), l1=2.35, l2=1.72):
    elbow = origin + l1 * np.array([np.cos(q1), np.sin(q1), 0.0])
    end = elbow + l2 * np.array([np.cos(q1 + q2), np.sin(q1 + q2), 0.0])
    link1 = Line(origin, elbow, color=Z_BLUE, stroke_width=13)
    link2 = Line(elbow, end, color=ORANGE, stroke_width=13)
    joints = VGroup(Dot(origin, radius=0.09, color=TEXT), Dot(elbow, radius=0.09, color=TEXT), Dot(end, radius=0.10, color=VIOLET))
    return VGroup(link1, link2, joints), elbow, end


def chain_node(text_value, color):
    box = panel(1.82, 0.82, color=PANEL_2, stroke=color)
    label = code_text(text_value, 20, color, BOLD).move_to(box)
    return VGroup(box, label)


class ForwardKinematicsExplainer(Scene):
    def construct(self):
        add_base(self)
        self.upstream_motion()
        fade_all(self)
        add_base(self)
        self.relative_angle()
        fade_all(self)
        add_base(self)
        self.vector_sum()
        fade_all(self)
        add_base(self)
        self.transform_chain()
        fade_all(self)
        add_base(self)
        self.dh_sequence()
        self.wait(0.8)

    def upstream_motion(self):
        title = header(1, "UPSTREAM JOINT", "改变 q₁，整条下游链一起运动")
        q1 = ValueTracker(18 * DEGREES)
        q2 = 42 * DEGREES
        arm = always_redraw(lambda: arm_geometry(q1.get_value(), q2)[0])
        trace = TracedPath(lambda: arm_geometry(q1.get_value(), q2)[2], stroke_color=VIOLET, stroke_width=2.5, dissipating_time=1.6)
        axes = VGroup(
            clean_axis([-3.2, -1.25, 0], [-0.35, -1.25, 0], X_RED, "x", DOWN),
            clean_axis([-3.2, -1.25, 0], [-3.2, 1.55, 0], Y_GREEN, "y", LEFT),
        )
        panel_note = statement("固定", ["q₂ = 42°", "l₁、l₂ 不变"], width=3.2, accent=ORANGE).move_to([4.55, 0.6, 0])
        moving_note = statement("观察", ["肘部移动", "末端也移动"], width=3.2, accent=CYAN).move_to([4.55, -1.25, 0])
        self.play(FadeIn(title), Create(axes), FadeIn(arm), FadeIn(panel_note), run_time=0.8)
        self.add(trace)
        self.play(q1.animate.set_value(72 * DEGREES), FadeIn(moving_note, shift=LEFT * 0.15), run_time=2.0, rate_func=smooth)
        self.play(q1.animate.set_value(35 * DEGREES), run_time=1.25, rate_func=smooth)
        self.add(bottom_caption("q₁ 位于链的上游：它会左乘并带动后面所有局部变换。"))
        self.wait(1.0)

    def relative_angle(self):
        title = header(2, "RELATIVE JOINT ANGLE", "q₂ 是相对第一连杆的角度")
        q1 = 30 * DEGREES
        q2 = ValueTracker(0.0)
        arm = always_redraw(lambda: arm_geometry(q1, q2.get_value())[0])
        guide = always_redraw(lambda: DashedLine(
            arm_geometry(q1, q2.get_value())[1],
            arm_geometry(q1, q2.get_value())[1] + 1.45 * np.array([np.cos(q1), np.sin(q1), 0]),
            color=MUTED, stroke_width=1.8,
        ))
        q1_tag = formula_bar("q₁ = 30°", Z_BLUE, size=21).move_to([3.9, 1.0, 0])
        q2_tag = formula_bar("q₂：相对 link 1", ORANGE, width=3.8, size=20).move_to([3.9, 0.05, 0])
        absolute = formula_bar("link 2 绝对方向 = q₁ + q₂", VIOLET, width=5.1, size=21).move_to([3.7, -1.25, 0])
        self.play(FadeIn(title), FadeIn(arm), FadeIn(guide), FadeIn(q1_tag), run_time=0.8)
        self.play(q2.animate.set_value(60 * DEGREES), FadeIn(q2_tag), run_time=1.75, rate_func=smooth)
        self.play(FadeIn(absolute, shift=UP * 0.15), run_time=0.65)
        self.add(bottom_caption("只有 q₁=0 时，第二连杆绝对方向才会碰巧等于 q₂。"))
        self.wait(1.1)

    def vector_sum(self):
        title = header(3, "VECTOR SUM", "末端位置 = 第一连杆向量 + 第二连杆向量")
        q1, q2 = 30 * DEGREES, 60 * DEGREES
        arm, elbow, end = arm_geometry(q1, q2)
        origin = np.array([-3.2, -1.25, 0.0])
        v1 = clean_arrow(origin, elbow, Z_BLUE, width=4.2, tip=0.16)
        v2 = clean_arrow(elbow, end, ORANGE, width=4.2, tip=0.16)
        total = DashedLine(origin, end, color=VIOLET, stroke_width=3.0, dash_length=0.11)
        labels = VGroup(
            label_chip("l₁[cos q₁, sin q₁]", Z_BLUE, 18).next_to(v1, DOWN, buff=0.12),
            label_chip("l₂[cos(q₁+q₂), sin(q₁+q₂)]", ORANGE, 17).next_to(v2, RIGHT, buff=0.12),
        )
        formula = statement("代入数值", ["l₁=0.4, l₂=0.3 m", "q₁=30°, q₂=60°", "pₑₑ=(0.346, 0.500) m"], width=4.3, accent=GREEN).move_to([4.35, 0.1, 0])
        self.play(FadeIn(title), FadeIn(arm, shift=UP * 0.1), run_time=0.65)
        self.play(Transform(arm[0], v1), Transform(arm[1], v2), FadeIn(labels), run_time=0.8)
        self.play(Create(total), FadeIn(formula, shift=LEFT * 0.15), run_time=0.7)
        self.add(bottom_caption("第二个向量从肘部出发；两根向量首尾相加得到末端。"))
        self.wait(1.15)

    def transform_chain(self):
        title = header(4, "SE(3) CHAIN", "二维向量和升级为有序变换链")
        nodes = VGroup(
            chain_node("base", ORANGE), chain_node("link 1", Z_BLUE),
            chain_node("link 2", GREEN), chain_node("ee", VIOLET),
        ).arrange(RIGHT, buff=0.72).move_to([0, 0.65, 0])
        arrows = VGroup(*[
            clean_arrow(nodes[i].get_right(), nodes[i + 1].get_left(), [Z_BLUE, GREEN, VIOLET][i], width=2.8, tip=0.12)
            for i in range(3)
        ])
        tags = VGroup(
            code_text("⁰T₁(q₁)", 18, Z_BLUE, BOLD).next_to(arrows[0], UP, buff=0.08),
            code_text("¹T₂(q₂)", 18, GREEN, BOLD).next_to(arrows[1], UP, buff=0.08),
            code_text("²Tₑₑ", 18, VIOLET, BOLD).next_to(arrows[2], UP, buff=0.08),
        )
        formula = formula_bar("⁰Tₑₑ(q) = ⁰T₁(q₁) · ¹T₂(q₂) · ²Tₑₑ", CYAN, width=8.2, size=23).move_to([0, -1.0, 0])
        note = statement("上游影响范围", ["q₁：link 1、link 2、ee", "q₂：link 2、ee"], width=5.4, accent=ORANGE).move_to([0, -2.05, 0])
        self.play(FadeIn(title), LaggedStart(*[FadeIn(n, shift=UP * 0.12) for n in nodes], lag_ratio=0.12), run_time=0.9)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.16), FadeIn(tags), run_time=0.9)
        self.play(FadeIn(formula), FadeIn(note, shift=UP * 0.12), run_time=0.75)
        self.wait(1.1)

    def dh_sequence(self):
        title = header(5, "STANDARD DH", "四个基本动作描述一对相邻 frame")
        data = [
            ("Rz(θᵢ)", "绕旧 z 转", Z_BLUE),
            ("Tz(dᵢ)", "沿旧 z 移", GREEN),
            ("Tx(aᵢ)", "沿新 x 移", ORANGE),
            ("Rx(αᵢ)", "绕新 x 转", VIOLET),
        ]
        cards = VGroup()
        for formula_text, meaning, color in data:
            box = panel(2.65, 1.65, color=PANEL, stroke=color)
            top = code_text(formula_text, 23, color, BOLD)
            lower = ui(meaning, 18, TEXT)
            content = VGroup(top, lower).arrange(DOWN, buff=0.22).move_to(box)
            cards.add(VGroup(box, content))
        cards.arrange(RIGHT, buff=0.25).move_to([0, 0.45, 0])
        formula = formula_bar("ⁱ⁻¹Tᵢ = Rz(θᵢ) · Tz(dᵢ) · Tx(aᵢ) · Rx(αᵢ)", CYAN, width=9.4, size=21).move_to([0, -1.35, 0])
        warning = statement("约定必须配套", ["standard DH ≠ modified DH", "参数表不能直接混用"], width=5.6, accent=RED).move_to([0, -2.25, 0])
        self.play(FadeIn(title), LaggedStart(*[FadeIn(card, shift=UP * 0.12) for card in cards], lag_ratio=0.18), run_time=1.2)
        self.play(FadeIn(formula), run_time=0.55)
        self.play(FadeIn(warning, shift=UP * 0.12), run_time=0.6)
        self.wait(1.2)


class ForwardKinematicsPoster(Scene):
    def construct(self):
        add_base(self)
        title = header(0, "FORWARD KINEMATICS", "关节变量如何变成末端位姿")
        cards = VGroup(
            statement("相对关节角", ["link 2 绝对方向", "= q₁ + q₂"], width=3.55, accent=ORANGE),
            statement("向量首尾相加", ["pₑₑ = p₁ + p₂", "连杆长度保持"], width=3.55, accent=GREEN),
            statement("SE(3) 变换链", ["⁰Tₙ = ⁰T₁ ··· ⁿ⁻¹Tₙ", "上游带动下游"], width=3.55, accent=CYAN),
        ).arrange(RIGHT, buff=0.3).move_to([0, 0.35, 0])
        formula = formula_bar("x=l₁cos q₁+l₂cos(q₁+q₂)   ·   y=l₁sin q₁+l₂sin(q₁+q₂)", VIOLET, width=10.5, size=21).move_to([0, -1.65, 0])
        caption = bottom_caption("先验证每个中间 frame，再相信末端结果。", color=TEXT)
        self.add(title, cards, formula, caption)
