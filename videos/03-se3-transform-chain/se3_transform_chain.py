from pathlib import Path
import sys

from manim import *
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))
from manim_style import *


BLUE = Z_BLUE
GREEN = Y_GREEN
RED = X_RED


def frame_2d(origin, angle=0.0, name="B", scale=1.0):
    x_end = origin + scale * np.array([np.cos(angle), np.sin(angle), 0.0])
    y_end = origin + scale * np.array([-np.sin(angle), np.cos(angle), 0.0])
    x_axis = clean_arrow(origin, x_end, RED, width=3.0, tip=0.13)
    y_axis = clean_arrow(origin, y_end, GREEN, width=3.0, tip=0.13)
    x_tag = code_text(f"x{name}", 17, RED, BOLD).next_to(x_end, RIGHT if np.cos(angle) >= 0 else LEFT, buff=0.07)
    y_tag = code_text(f"y{name}", 17, GREEN, BOLD).next_to(y_end, UP if np.cos(angle) >= 0 else DOWN, buff=0.07)
    dot = Dot(origin, radius=0.045, color=TEXT)
    title = label_chip(name, BLUE if name == "A" else CYAN, 17).next_to(dot, DOWN, buff=0.14)
    return VGroup(x_axis, y_axis, x_tag, y_tag, dot, title)


def node(text_value, color):
    box = panel(2.0, 0.92, color=PANEL_2, stroke=color)
    label = code_text(text_value, 22, color, BOLD).move_to(box)
    return VGroup(box, label)


class SE3TransformChainExplainer(Scene):
    def construct(self):
        add_base(self)
        self.scene_rigid_body()
        fade_all(self)
        add_base(self)
        self.scene_translation_language()
        fade_all(self)
        add_base(self)
        self.scene_composition()
        fade_all(self)
        add_base(self)
        self.scene_formula_inverse()
        fade_all(self)
        add_base(self)
        self.scene_eye_in_hand()
        self.wait(0.8)

    def scene_rigid_body(self):
        title = header(1, "ONE RIGID MOTION", "所有点共享同一个 R 和 t")
        body = RoundedRectangle(width=3.7, height=2.2, corner_radius=0.22, fill_color=PANEL_2, fill_opacity=0.95, stroke_color=LINE)
        marks = VGroup(
            Dot(body.get_center() + LEFT * 1.15 + DOWN * 0.35, color=ORANGE),
            Dot(body.get_center() + RIGHT * 0.95 + UP * 0.42, color=VIOLET),
            Dot(body.get_center() + RIGHT * 0.10 + DOWN * 0.56, color=CYAN),
        )
        links = VGroup(*[DashedLine(marks[i], marks[(i + 1) % 3], color=MUTED, stroke_width=1.7) for i in range(3)])
        rigid = VGroup(body, links, marks).shift(LEFT * 2.6 + DOWN * 0.35)
        moved = rigid.copy().rotate(28 * DEGREES).shift(RIGHT * 5.0 + UP * 0.55)
        motion = clean_arrow(rigid.get_right() + RIGHT * 0.2, moved.get_left() + LEFT * 0.2, ORANGE, width=3.5)
        formula = formula_bar("p′ = R p + t", CYAN, width=3.1, size=27).move_to([0, -2.45, 0])
        note = statement("四元数的位置", ["q 只产生 R", "完整位姿还需要 t"], width=3.2, accent=VIOLET).move_to([4.75, -1.65, 0])
        self.play(FadeIn(title), FadeIn(rigid, shift=UP * 0.15), run_time=0.8)
        self.play(GrowArrow(motion), TransformFromCopy(rigid, moved), run_time=1.25)
        self.play(FadeIn(formula, shift=UP * 0.15), FadeIn(note, shift=LEFT * 0.15), run_time=0.7)
        self.play(Indicate(links, color=GREEN, scale_factor=1.03), run_time=0.7)
        self.add(bottom_caption("刚体运动保持内部距离；不是每个点各自选择一条路径。"))
        self.wait(1.2)

    def scene_translation_language(self):
        title = header(2, "TWO FRAME LANGUAGES", "tᴮ_C 必须先改写成 A 系表达")
        origin_a = np.array([-3.4, -1.1, 0.0])
        frame_a = frame_2d(origin_a, 0.0, "A", 1.25)
        t_ab = clean_arrow(origin_a, origin_a + np.array([2.2, 1.05, 0]), ORANGE, width=4.0, tip=0.16)
        b_origin = t_ab.get_end()
        frame_b_aligned = frame_2d(b_origin, 0.0, "B", 1.15)
        local_translation = clean_arrow(b_origin, b_origin + RIGHT * 2.05, GREEN, width=4.0, tip=0.16)
        local_tag = formula_bar("tᴮ_C = (2, 0)", GREEN, size=20).next_to(local_translation, DOWN, buff=0.16)
        rotate_group = VGroup(frame_b_aligned, local_translation)
        caption = bottom_caption("B 的 +x 已转向 A 的 +y；同一个位移不能继续写成 A 的 (2,0)。")
        self.play(FadeIn(title), Create(frame_a), GrowArrow(t_ab), run_time=0.9)
        self.play(FadeIn(rotate_group), FadeIn(local_tag), run_time=0.65)
        pivot = b_origin
        self.play(FadeOut(local_tag), Rotate(rotate_group, angle=PI / 2, about_point=pivot), run_time=1.45, rate_func=smooth)
        rotated_tag = formula_bar("tᴮ_C：沿 B 的 +x", GREEN, size=19).next_to(local_translation, LEFT, buff=0.14)
        corrected = formula_bar("Rᴬ_B tᴮ_C = (0, 2)", CYAN, width=3.8, size=21).move_to([3.9, -2.0, 0])
        self.play(FadeIn(rotated_tag), FadeIn(corrected, shift=UP * 0.2), FadeIn(caption), run_time=0.65)
        self.wait(1.3)

    def scene_composition(self):
        title = header(3, "COMPOSE TRANSLATIONS", "先旋转第二段，再首尾相加")
        origin = np.array([-4.2, -1.45, 0.0])
        t1 = clean_arrow(origin, origin + np.array([2.5, 1.15, 0]), ORANGE, width=4.2, tip=0.17)
        t2_correct = clean_arrow(t1.get_end(), t1.get_end() + UP * 2.0, GREEN, width=4.2, tip=0.17)
        total = DashedLine(origin, t2_correct.get_end(), color=VIOLET, stroke_width=3.0, dash_length=0.12)
        labels = VGroup(
            formula_bar("tᴬ_B", ORANGE, size=20).next_to(t1, DOWN, buff=0.1),
            formula_bar("Rᴬ_B tᴮ_C", GREEN, size=20).next_to(t2_correct, RIGHT, buff=0.14),
            formula_bar("tᴬ_C", VIOLET, size=20).next_to(total.get_center(), LEFT, buff=0.13),
        )
        wrong_panel = statement("错误做法", ["tᴬ_B + tᴮ_C", "两个向量语言不同"], width=3.6, accent=RED).move_to([4.2, 0.8, 0])
        right_panel = statement("正确做法", ["Rᴬ_B tᴮ_C + tᴬ_B", "先统一成 A 系表达"], width=3.9, accent=GREEN).move_to([4.05, -1.45, 0])
        self.play(FadeIn(title), GrowArrow(t1), FadeIn(labels[0]), run_time=0.8)
        self.play(GrowArrow(t2_correct), FadeIn(labels[1]), run_time=0.8)
        self.play(Create(total), FadeIn(labels[2]), run_time=0.6)
        self.play(FadeIn(wrong_panel, shift=LEFT * 0.15), run_time=0.55)
        self.play(wrong_panel.animate.set_opacity(0.35), FadeIn(right_panel, shift=LEFT * 0.15), run_time=0.65)
        self.add(bottom_caption("数值例：Rz(90°)(2,0)+(1,2)=(0,2)+(1,2)=(1,4)"))
        self.wait(1.1)

    def scene_formula_inverse(self):
        title = header(4, "BLOCK MATRIX", "4×4 乘法自动执行正确规则")
        chain = VGroup(node("C", BLUE), code_text("Tᴮ_C", 21, GREEN, BOLD), node("B", GREEN), code_text("Tᴬ_B", 21, ORANGE, BOLD), node("A", ORANGE))
        chain.arrange(RIGHT, buff=0.32).move_to([0, 1.2, 0])
        arrows = VGroup(
            clean_arrow(chain[0].get_right(), chain[2].get_left(), GREEN, width=2.8, tip=0.12),
            clean_arrow(chain[2].get_right(), chain[4].get_left(), ORANGE, width=2.8, tip=0.12),
        )
        chain[1].next_to(arrows[0], UP, buff=0.07)
        chain[3].next_to(arrows[1], UP, buff=0.07)
        formula1 = formula_bar("Tᴬ_C = Tᴬ_B Tᴮ_C", CYAN, width=4.5, size=26).move_to([0, -0.45, 0])
        formula2 = formula_bar("tᴬ_C = Rᴬ_B tᴮ_C + tᴬ_B", GREEN, width=5.8, size=23).move_to([0, -1.35, 0])
        inverse = formula_bar("T⁻¹ = [ Rᵀ   −Rᵀt ; 0   1 ]", VIOLET, width=5.8, size=22).move_to([0, -2.25, 0])
        self.play(FadeIn(title), FadeIn(chain[0]), FadeIn(chain[2]), FadeIn(chain[4]), run_time=0.6)
        self.play(GrowArrow(arrows[0]), FadeIn(chain[1]), GrowArrow(arrows[1]), FadeIn(chain[3]), run_time=0.8)
        self.play(FadeIn(formula1), FadeIn(formula2), run_time=0.75)
        self.play(FadeIn(inverse, shift=UP * 0.15), run_time=0.6)
        self.add(bottom_caption("逆向返回时，平移不仅取反，还要改写到返回后的坐标系。"))
        self.wait(1.2)

    def scene_eye_in_hand(self):
        title = header(5, "EYE-IN-HAND", "动态观测与固定标定组成一条链")
        names = [("base", ORANGE), ("ee", BLUE), ("camera", GREEN), ("object", VIOLET), ("grasp", RED)]
        nodes = VGroup(*[node(name, color).scale(0.82) for name, color in names]).arrange(RIGHT, buff=0.56).move_to([0, 0.65, 0])
        arrows = VGroup()
        labels = ["Tᵇᵃˢᵉ_ee", "Tᵉᵉ_cam", "Tᶜᵃᵐ_obj", "Tᵒᵇʲ_grasp"]
        colors = [BLUE, GREEN, BLUE, GREEN]
        for i in range(4):
            arrow = clean_arrow(nodes[i + 1].get_left(), nodes[i].get_right(), colors[i], width=2.8, tip=0.12)
            arrows.add(arrow)
        tag_group = VGroup(*[code_text(labels[i], 16, colors[i], BOLD).next_to(arrows[i], UP, buff=0.08) for i in range(4)])
        dynamic = statement("动态", ["base←ee：关节状态", "camera←object：视觉帧"], width=4.35, accent=BLUE).move_to([-3.5, -1.25, 0])
        fixed = statement("固定", ["ee←camera：手眼标定", "object←grasp：抓取模板"], width=4.35, accent=GREEN).move_to([3.5, -1.25, 0])
        self.play(FadeIn(title), LaggedStart(*[FadeIn(n, shift=UP * 0.15) for n in nodes], lag_ratio=0.12), run_time=1.0)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows[::-1]], lag_ratio=0.16), FadeIn(tag_group), run_time=1.15)
        self.play(FadeIn(dynamic, shift=RIGHT * 0.15), FadeIn(fixed, shift=LEFT * 0.15), run_time=0.75)
        formula = formula_bar("Tᵇᵃˢᵉ_grasp = Tᵇᵃˢᵉ_ee · Tᵉᵉ_cam · Tᶜᵃᵐ_obj · Tᵒᵇʲ_grasp", CYAN, width=10.7, size=20).to_edge(DOWN, buff=0.28)
        self.play(FadeIn(formula, shift=UP * 0.12), run_time=0.65)
        self.wait(1.4)


class SE3TransformChainPoster(Scene):
    def construct(self):
        add_base(self)
        title = header(0, "SE(3) · TRANSFORM CHAIN", "旋转统一表达，平移连接原点")
        cards = VGroup(
            statement("点与方向", ["点：w=1 → Rp+t", "方向：w=0 → Rv"], width=3.7, accent=CYAN),
            statement("复合平移", ["tᴬ_C = Rᴬ_B tᴮ_C", "+ tᴬ_B"], width=3.7, accent=GREEN),
            statement("眼在手上", ["动态：关节与视觉", "固定：标定与模板"], width=3.7, accent=ORANGE),
        ).arrange(RIGHT, buff=0.28).move_to([0, 0.35, 0])
        formula = formula_bar("Tᴬ_C = Tᴬ_B Tᴮ_C", VIOLET, width=5.0, size=28).move_to([0, -1.75, 0])
        caption = bottom_caption("先检查 frame 方向，再检查数值；相邻上下标必须配对。", color=TEXT)
        self.add(title, cards, formula, caption)
