from pathlib import Path
import sys

from manim import *
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))
from manim_style import *

ORIGIN_ARM = np.array([-3.15, -1.35, 0.0])
L1, L2 = 2.3, 1.7


def points_for(q1, q2):
    elbow = ORIGIN_ARM + L1 * np.array([np.cos(q1), np.sin(q1), 0.0])
    end = elbow + L2 * np.array([np.cos(q1 + q2), np.sin(q1 + q2), 0.0])
    return elbow, end


def arm(q1, q2, opacity=1.0):
    elbow, end = points_for(q1, q2)
    group = VGroup(
        Line(ORIGIN_ARM, elbow, color=Z_BLUE, stroke_width=12),
        Line(elbow, end, color=ORANGE, stroke_width=12),
        Dot(ORIGIN_ARM, radius=0.085, color=TEXT),
        Dot(elbow, radius=0.085, color=TEXT),
        Dot(end, radius=0.095, color=VIOLET),
    )
    group.set_opacity(opacity)
    return group


def analytic_other_branch(target, q2_sign=-1.0):
    x, y = target[0] - ORIGIN_ARM[0], target[1] - ORIGIN_ARM[1]
    c2 = np.clip((x * x + y * y - L1 * L1 - L2 * L2) / (2 * L1 * L2), -1, 1)
    q2 = np.arctan2(q2_sign * np.sqrt(max(0.0, 1 - c2 * c2)), c2)
    q1 = np.arctan2(y, x) - np.arctan2(L2 * np.sin(q2), L1 + L2 * np.cos(q2))
    return q1, q2


def jacobian(q1, q2):
    return np.array([
        [-L1 * np.sin(q1) - L2 * np.sin(q1 + q2), -L2 * np.sin(q1 + q2)],
        [L1 * np.cos(q1) + L2 * np.cos(q1 + q2), L2 * np.cos(q1 + q2)],
    ])


def dls_states(target_local, initial, count=7):
    q = np.array(initial, dtype=float)
    states = [q.copy()]
    for _ in range(count - 1):
        _, end = points_for(q[0], q[1])
        current = end[:2] - ORIGIN_ARM[:2]
        error = target_local - current
        j = jacobian(q[0], q[1])
        step = j.T @ np.linalg.solve(j @ j.T + 0.18 ** 2 * np.eye(2), error)
        q += 0.72 * step
        states.append(q.copy())
    return states


class IKJacobianExplainer(Scene):
    def construct(self):
        add_base(self)
        self.multiple_branches()
        fade_all(self)
        add_base(self)
        self.jacobian_columns()
        fade_all(self)
        add_base(self)
        self.singularity_motion()
        fade_all(self)
        add_base(self)
        self.dls_iteration()
        fade_all(self)
        add_base(self)
        self.constraint_filter()
        self.wait(0.8)

    def multiple_branches(self):
        title = header(1, "INVERSE KINEMATICS", "同一个目标，不一定只有一组关节角")
        q_a = (30 * DEGREES, 65 * DEGREES)
        _, target = points_for(*q_a)
        q_b = analytic_other_branch(target, q2_sign=-1.0)
        first = arm(*q_a)
        second = arm(*q_b, opacity=0.62)
        target_dot = Dot(target, radius=0.12, color=VIOLET)
        target_tag = label_chip("目标 p_d", VIOLET, 18).next_to(target_dot, RIGHT, buff=0.12)
        branch_a = statement("分支 A", [f"q₁ = {np.degrees(q_a[0]):.0f}°", f"q₂ = {np.degrees(q_a[1]):.0f}°"], width=2.7, accent=ORANGE).move_to([4.7, 0.65, 0])
        branch_b = statement("分支 B", [f"q₁ = {np.degrees(q_b[0]):.1f}°", f"q₂ = {np.degrees(q_b[1]):.0f}°"], width=2.7, accent=GREEN).move_to([4.7, -1.2, 0])
        self.play(FadeIn(title), FadeIn(target_dot), FadeIn(target_tag), run_time=0.6)
        self.play(FadeIn(first, shift=UP * 0.1), FadeIn(branch_a), run_time=0.8)
        self.play(FadeIn(second, shift=DOWN * 0.1), FadeIn(branch_b), run_time=0.8)
        self.add(bottom_caption("IK 验收要把候选送回 FK；不要只与某一组参考关节角比较。"))
        self.wait(1.2)

    def jacobian_columns(self):
        title = header(2, "JACOBIAN COLUMNS", "每一列是单个关节造成的末端速度")
        q1, q2 = 28 * DEGREES, 62 * DEGREES
        robot = arm(q1, q2)
        elbow, end = points_for(q1, q2)
        j = jacobian(q1, q2)
        scale = 0.55
        arrow1 = clean_arrow(end, end + scale * np.array([j[0, 0], j[1, 0], 0.0]), Z_BLUE, width=4.2, tip=0.16)
        arrow2 = clean_arrow(end, end + scale * np.array([j[0, 1], j[1, 1], 0.0]), Y_GREEN, width=4.2, tip=0.16)
        radius1 = DashedLine(ORIGIN_ARM, end, color=Z_BLUE, stroke_width=1.8)
        radius2 = DashedLine(elbow, end, color=Y_GREEN, stroke_width=1.8)
        panel1 = statement("J 的第 1 列", ["只令 q̇₁ = 1", "末端沿蓝色切向"], width=3.3, accent=Z_BLUE).move_to([4.55, 0.75, 0])
        panel2 = statement("J 的第 2 列", ["只令 q̇₂ = 1", "末端沿绿色切向"], width=3.3, accent=Y_GREEN).move_to([4.55, -1.15, 0])
        formula = formula_bar("ṗ = J₁ q̇₁ + J₂ q̇₂", CYAN, width=4.6, size=22).to_edge(DOWN, buff=0.28)
        self.play(FadeIn(title), FadeIn(robot), Create(radius1), Create(radius2), run_time=0.75)
        self.play(GrowArrow(arrow1), FadeIn(panel1), run_time=0.65)
        self.play(GrowArrow(arrow2), FadeIn(panel2), run_time=0.65)
        self.play(FadeIn(formula, shift=UP * 0.1), run_time=0.5)
        self.wait(1.1)

    def singularity_motion(self):
        title = header(3, "SINGULARITY", "q₂→0：两根速度箭头逐渐共线")
        q1 = 20 * DEGREES
        q2 = ValueTracker(75 * DEGREES)
        robot = always_redraw(lambda: arm(q1, q2.get_value()))

        def velocity_arrow(column, color):
            _, end = points_for(q1, q2.get_value())
            vec = 0.32 * jacobian(q1, q2.get_value())[:, column]
            return clean_arrow(end, end + np.array([vec[0], vec[1], 0]), color, width=4.0, tip=0.15)

        v1 = always_redraw(lambda: velocity_arrow(0, Z_BLUE))
        v2 = always_redraw(lambda: velocity_arrow(1, Y_GREEN))
        trigger = formula_bar("det J = l₁l₂ sin q₂ → 0", RED, width=4.8, size=23).move_to([4.25, 0.45, 0])
        mechanism = statement("发生了什么", ["两列方向相同", "瞬时速度从二维降到一维", "径向速度丢失，切向仍存在"], width=4.4, accent=ORANGE).move_to([4.15, -1.35, 0])
        self.play(FadeIn(title), FadeIn(robot), FadeIn(v1), FadeIn(v2), run_time=0.7)
        self.play(q2.animate.set_value(0.0), FadeIn(trigger), run_time=2.0, rate_func=smooth)
        self.play(FadeIn(mechanism, shift=LEFT * 0.15), run_time=0.7)
        self.add(bottom_caption("奇异不是机械臂完全锁死；它仍能沿共同的切向速度方向离开。"))
        self.wait(1.1)

    def dls_iteration(self):
        title = header(4, "DAMPED LEAST SQUARES", "重复线性化，让任务误差逐步缩小")
        goal_q = np.array([45 * DEGREES, 55 * DEGREES])
        _, target = points_for(*goal_q)
        target_local = target[:2] - ORIGIN_ARM[:2]
        states = dls_states(target_local, initial=[-5 * DEGREES, 35 * DEGREES], count=7)
        current = arm(*states[0])
        target_dot = Dot(target, radius=0.12, color=VIOLET)
        target_tag = label_chip("目标", VIOLET, 17).next_to(target_dot, RIGHT, buff=0.1)
        _, start_end = points_for(*states[0])
        error_line = DashedLine(start_end, target, color=RED, stroke_width=2.8)
        iteration = code_text("k = 0", 22, CYAN, BOLD).move_to([4.5, 0.75, 0])
        formula = formula_bar("Δq = Jᵀ(JJᵀ+λ²I)⁻¹e", CYAN, width=5.4, size=22).move_to([4.15, -0.25, 0])
        note = statement("阻尼 λ", ["限制奇异附近的大步长", "不创造可达性"], width=3.8, accent=ORANGE).move_to([4.35, -1.65, 0])
        self.play(FadeIn(title), FadeIn(current), FadeIn(target_dot), FadeIn(target_tag), Create(error_line), FadeIn(iteration), run_time=0.8)
        self.play(FadeIn(formula), FadeIn(note), run_time=0.6)
        for index, state in enumerate(states[1:], start=1):
            next_arm = arm(*state)
            _, next_end = points_for(*state)
            next_error = DashedLine(next_end, target, color=RED, stroke_width=2.8)
            next_iteration = code_text(f"k = {index}", 22, CYAN, BOLD).move_to(iteration)
            self.play(Transform(current, next_arm), Transform(error_line, next_error), Transform(iteration, next_iteration), run_time=0.36)
        self.add(bottom_caption("每一步都重新计算 FK、误差和 Jacobian；达到最大迭代次数不等于成功。"))
        self.wait(1.0)

    def constraint_filter(self):
        title = header(5, "VALID SOLUTION", "数学候选还要经过工程约束")
        labels = [
            ("工作空间", "reachable?", Z_BLUE),
            ("关节限位", "q_min ≤ q ≤ q_max", ORANGE),
            ("碰撞检查", "self / environment", RED),
            ("连续选解", "closest to q_prev", GREEN),
        ]
        cards = VGroup()
        for heading, body, color in labels:
            card = statement(heading, [body], width=2.65, accent=color)
            cards.add(card)
        cards.arrange(RIGHT, buff=0.22).move_to([0, 0.45, 0])
        arrows = VGroup(*[
            clean_arrow(cards[i].get_right(), cards[i + 1].get_left(), MUTED, width=2.4, tip=0.11)
            for i in range(3)
        ])
        result = formula_bar("输出：q · converged · error · failure_reason", VIOLET, width=8.0, size=22).move_to([0, -1.45, 0])
        warning = bottom_caption("不要把不可达、限位、碰撞、奇异和超时全部压成一个 False。", color=TEXT)
        self.play(FadeIn(title), LaggedStart(*[FadeIn(card, shift=UP * 0.12) for card in cards], lag_ratio=0.16), run_time=1.05)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.18), run_time=0.65)
        self.play(FadeIn(result), FadeIn(warning), run_time=0.6)
        self.wait(1.2)


class IKJacobianPoster(Scene):
    def construct(self):
        add_base(self)
        title = header(0, "IK · JACOBIAN · SINGULARITY", "从目标位姿回到可执行关节角")
        cards = VGroup(
            statement("IK 不是唯一反函数", ["无解 / 多解 / 无限多解", "候选必须回代 FK"], width=3.65, accent=ORANGE),
            statement("Jacobian 的列", ["单关节单位速度", "造成的末端速度"], width=3.65, accent=CYAN),
            statement("奇异点", ["列向量线性相关", "丢失部分瞬时方向"], width=3.65, accent=RED),
        ).arrange(RIGHT, buff=0.27).move_to([0, 0.38, 0])
        formula = formula_bar("det J = l₁l₂ sin q₂   ·   Δq = Jᵀ(JJᵀ+λ²I)⁻¹e", VIOLET, width=9.8, size=22).move_to([0, -1.7, 0])
        caption = bottom_caption("先验证 FK 与可达性，再讨论求解器收敛。", color=TEXT)
        self.add(title, cards, formula, caption)
