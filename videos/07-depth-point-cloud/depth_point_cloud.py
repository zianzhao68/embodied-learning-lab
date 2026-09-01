from pathlib import Path
import sys

from manim import *
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1]))
from manim_style import *


def depth_grid(values, center=(-3.6, -0.25, 0), cell=0.72):
    group = VGroup()
    for v, row in enumerate(values):
        for u, value in enumerate(row):
            square = Square(cell, color=MUTED, stroke_width=1.7)
            square.move_to(np.array(center) + [(u - 1) * cell, (1 - v) * cell, 0])
            color = RED if value in ("0", "NaN") else (ORANGE if value == "2.0" else TEXT)
            text = code_text(value, 18, color, BOLD if value == "2.0" else NORMAL).move_to(square)
            group.add(VGroup(square, text))
    return group


def cloud_shape(center=(0, 0, 0), scale=1.0, invalid=False):
    coords = [(-1, .75), (0, .92), (1, .74), (-1.1, 0), (0, -.2), (1.05, .05), (-.9, -.8), (.05, -.95), (.95, -.76)]
    dots = VGroup()
    for i, (x, y) in enumerate(coords):
        if invalid and i in (1, 4):
            mark = Cross(stroke_color=RED, stroke_width=3).scale(0.12)
            mark.move_to(np.array(center) + scale * np.array([x, y, 0]))
            dots.add(mark)
        else:
            color = ORANGE if i == 4 else Z_BLUE
            dots.add(Dot(np.array(center) + scale * np.array([x, y, 0]), radius=0.085, color=color))
    return dots


class DepthPointCloudExplainer(Scene):
    def construct(self):
        add_base(self)
        self.depth_table()
        fade_all(self)
        add_base(self)
        self.unproject_rays()
        fade_all(self)
        add_base(self)
        self.organized_filter()
        fade_all(self)
        add_base(self)
        self.camera_to_base()
        fade_all(self)
        add_base(self)
        self.pipeline()
        self.wait(0.8)

    def depth_table(self):
        title = header(1, "DEPTH IMAGE", "每个像素格子存一个 z-depth")
        values = [["1.0", "1.0", "1.0"], ["1.0", "2.0", "1.0"], ["1.0", "1.0", "1.0"]]
        grid = depth_grid(values)
        grid_label = label_chip("D[v,u] · 单位 m", Z_BLUE, 18).next_to(grid, UP, buff=0.18)
        principal = SurroundingRectangle(grid[4], color=ORANGE, buff=0.04, stroke_width=3)
        card = statement("极小手算相机", ["fₓ=fᵧ=2 px", "主点 (cₓ,cᵧ)=(1,1)", "中心格 Z=2 m"], width=4.0, accent=ORANGE).move_to([3.55, 0.0, 0])
        formula = formula_bar("X=(u-cₓ)Z/fₓ  ·  Y=(v-cᵧ)Z/fᵧ", CYAN, width=6.8, size=22).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(title), LaggedStart(*[FadeIn(c, scale=0.8) for c in grid], lag_ratio=0.07), run_time=1.0)
        self.play(FadeIn(grid_label), Create(principal), FadeIn(card), FadeIn(formula), run_time=0.75)
        self.add(bottom_caption("几何说像素 (u,v)，数组查值写 D[v,u]。"))
        self.wait(1.1)

    def unproject_rays(self):
        title = header(2, "UNPROJECT", "像素给射线，深度决定点停在哪里")
        origin = np.array([-4.6, -1.45, 0])
        origin_dot = Dot(origin, radius=0.1, color=TEXT)
        target_coords = [(-1.9, .8), (-1.5, 1.0), (-1.0, .75), (-1.8, -.05), (.0, .0), (-.8, .0), (-1.75, -.9), (-1.45, -1.1), (-1.0, -.85)]
        points = VGroup(*[Dot([x, y, 0], radius=0.09, color=ORANGE if i == 4 else Z_BLUE) for i, (x, y) in enumerate(target_coords)])
        rays = VGroup(*[Line(origin, p.get_center(), color=MUTED, stroke_width=1.8) for p in points])
        labels = VGroup(
            label_chip("光心 O", TEXT, 15).next_to(origin_dot, DOWN, buff=0.12),
            label_chip("中心：Z=2 m", ORANGE, 16).next_to(points[4], UP, buff=0.12),
            label_chip("周围：Z=1 m", Z_BLUE, 16).move_to([-0.2, 1.25, 0]),
        )
        result = statement("输出仍有像素结构", ["shape = H×W×3", "P[v,u] ↔ D[v,u]"], width=4.1, accent=Y_GREEN).move_to([4.15, -0.35, 0])
        self.play(FadeIn(title), FadeIn(origin_dot), FadeIn(labels[0]), LaggedStart(*[Create(r) for r in rays], lag_ratio=0.06), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in points], lag_ratio=0.07), FadeIn(labels[1:]), run_time=0.9)
        self.play(FadeIn(result), run_time=0.55)
        self.add(bottom_caption("点云不是新测量：它是 depth + pixel ray + K 的坐标改写。"))
        self.wait(1.1)

    def organized_filter(self):
        title = header(3, "VALID MASK", "无效格子保留位置，再过滤成有效点列表")
        grid = depth_grid([["1.1", "0", "1.3"], ["1.0", "NaN", "1.2"]], center=(-4.5, -.2, 0), cell=.75)
        organized = cloud_shape(center=(0, -.15, 0), scale=.9, invalid=True)
        valid_points = VGroup(*[Dot([4.2 + .35 * (i % 2), .85 - .55 * (i // 2), 0], radius=.085, color=Y_GREEN) for i in range(7)])
        labels = VGroup(
            label_chip("depth H×W", Z_BLUE, 17).next_to(grid, UP, buff=.18),
            label_chip("organized H×W×3", ORANGE, 17).next_to(organized, UP, buff=.25),
            label_chip("valid N×3", Y_GREEN, 17).next_to(valid_points, UP, buff=.25),
        )
        arrow1 = clean_arrow(grid.get_right(), organized.get_left(), VIOLET, width=3, tip=.12)
        arrow2 = clean_arrow(organized.get_right(), valid_points.get_left(), Y_GREEN, width=3, tip=.12)
        mask = formula_bar("valid = finite(Z) ∧ Z_min < Z < Z_max", CYAN, width=7.2, size=21).to_edge(DOWN, buff=.3)
        self.play(FadeIn(title), FadeIn(grid), FadeIn(labels[0]), run_time=.65)
        self.play(GrowArrow(arrow1), FadeIn(organized), FadeIn(labels[1]), run_time=.7)
        self.play(GrowArrow(arrow2), FadeIn(valid_points), FadeIn(labels[2]), FadeIn(mask), run_time=.75)
        self.add(bottom_caption("给点附 RGB 颜色时，颜色必须使用同一个 mask 和同一展平顺序。"))
        self.wait(1.1)

    def camera_to_base(self):
        title = header(4, "CHANGE COORDINATE FRAME", "物理点云不变，只把 camera 表达改写成 base 表达")
        left = cloud_shape(center=(-3.6, -.25, 0), scale=1.05)
        right = cloud_shape(center=(3.6, -.15, 0), scale=1.05).rotate(18 * DEGREES)
        left_box = RoundedRectangle(width=3.5, height=3.2, corner_radius=.14, color=MUTED).move_to([-3.6, -.25, 0])
        right_box = RoundedRectangle(width=3.5, height=3.2, corner_radius=.14, color=MUTED).move_to([3.6, -.25, 0])
        labels = VGroup(
            label_chip("camera frame", Z_BLUE, 18).next_to(left_box, UP, buff=.15),
            label_chip("base frame", Y_GREEN, 18).next_to(right_box, UP, buff=.15),
        )
        arrow = clean_arrow(left_box.get_right(), right_box.get_left(), VIOLET, width=4, tip=.16)
        transform_label = code_text("T_base←camera", 20, VIOLET, BOLD).next_to(arrow, UP, buff=.15)
        formula = formula_bar("p_base = R p_camera + t", CYAN, width=5.4, size=23).to_edge(DOWN, buff=.3)
        self.play(FadeIn(title), FadeIn(left_box), FadeIn(left), FadeIn(labels[0]), run_time=.7)
        self.play(GrowArrow(arrow), FadeIn(transform_label), run_time=.55)
        self.play(TransformFromCopy(left, right), FadeIn(right_box), FadeIn(labels[1]), FadeIn(formula), run_time=.9)
        self.add(bottom_caption("先在 camera 系检查几何，再检查 base 系桌面高度与左右方向。"))
        self.wait(1.1)

    def pipeline(self):
        title = header(5, "RGB-D PIPELINE", "从深度数组到机器人可用点云")
        cards = VGroup(
            statement("depth + K", ["单位 / valid", "D[v,u]"], width=2.45, accent=Z_BLUE),
            statement("camera cloud", ["H×W×3", "保留像素对应"], width=2.55, accent=ORANGE),
            statement("filter / RGB", ["同一 mask", "对齐后着色"], width=2.55, accent=VIOLET),
            statement("base cloud", ["T_base←camera", "抓取 / 规划"], width=2.55, accent=Y_GREEN),
        ).arrange(RIGHT, buff=.2).move_to([0, .3, 0])
        arrows = VGroup(*[clean_arrow(cards[i].get_right(), cards[i+1].get_left(), MUTED, width=2.4, tip=.1) for i in range(3)])
        checks = formula_bar("检查：depth scale · z/range · resize K · RGB alignment · TF direction", CYAN, width=10.2, size=19).move_to([0, -1.55, 0])
        self.play(FadeIn(title), LaggedStart(*[FadeIn(c, shift=UP*.1) for c in cards], lag_ratio=.13), run_time=1.0)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=.15), FadeIn(checks), run_time=.75)
        self.add(bottom_caption("每一步记录 shape、单位、有效点数和 frame；不要只看最终可视化。"))
        self.wait(1.2)


class DepthPointCloudPoster(Scene):
    def construct(self):
        add_base(self)
        title = header(0, "DEPTH → POINT CLOUD", "把每个像素沿自己的射线放回三维")
        cards = VGroup(
            statement("像素", ["(u,v)", "决定射线方向"], width=3.4, accent=Z_BLUE),
            statement("深度", ["Z=D[v,u]", "决定射线上位置"], width=3.4, accent=ORANGE),
            statement("三维点", ["X=(u-cₓ)Z/fₓ", "Y=(v-cᵧ)Z/fᵧ"], width=3.8, accent=Y_GREEN),
        ).arrange(RIGHT, buff=.28).move_to([0, .4, 0])
        formula = formula_bar("organized H×W×3  →  valid mask  →  N×3  →  base frame", VIOLET, width=9.5, size=22).move_to([0, -1.7, 0])
        caption = bottom_caption("先确认单位与 z-depth/range，再做任何点云算法。", color=TEXT)
        self.add(title, cards, formula, caption)
