from manim import *
import numpy as np

# Professional dark visual system for all course animations.
BG = "#0B1020"
PANEL = "#121A2B"
PANEL_2 = "#172235"
TEXT = "#F4F7F6"
MUTED = "#95A3B8"
FAINT = "#334155"
LINE = "#263449"
X_RED = "#F0645A"
Y_GREEN = "#41C987"
Z_BLUE = "#5B8FF9"
ORANGE = "#F5A65B"
VIOLET = "#A78BFA"
CYAN = "#45C4D6"

FONT_ZH = "Microsoft YaHei UI"
FONT_MONO = "Cascadia Code"
FONT_MATH = "Cambria Math"

config.background_color = BG


def ui(text, size=28, color=TEXT, weight=NORMAL, font=FONT_ZH):
    return Text(text, font=font, font_size=size, color=color, weight=weight)


def math_text(text, size=28, color=TEXT, weight=NORMAL):
    return Text(text, font=FONT_MATH, font_size=size, color=color, weight=weight)


def code_text(text, size=24, color=TEXT, weight=NORMAL):
    # YaHei UI covers Chinese labels, Greek letters, subscripts and operators reliably.
    # Cascadia Code remains available for future ASCII-only code blocks.
    return Text(text, font=FONT_ZH, font_size=size, color=color, weight=weight)


def background_grid(opacity=0.11):
    lines = VGroup()
    for x in np.arange(-7.0, 7.1, 0.7):
        lines.add(Line([x, -4, 0], [x, 4, 0], stroke_width=0.7, color=LINE))
    for y in np.arange(-4.0, 4.1, 0.7):
        lines.add(Line([-7.2, y, 0], [7.2, y, 0], stroke_width=0.7, color=LINE))
    lines.set_opacity(opacity)
    return lines


def header(index, kicker, title_text):
    number = code_text(f"{index:02d}", 18, CYAN, BOLD)
    kicker_text = ui(kicker, 18, MUTED, MEDIUM)
    meta = VGroup(number, Line(ORIGIN, RIGHT * 0.34, color=CYAN, stroke_width=2), kicker_text)
    meta.arrange(RIGHT, buff=0.12)
    title_obj = ui(title_text, 36, TEXT, BOLD)
    group = VGroup(meta, title_obj).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
    group.to_corner(UL, buff=0.38)
    return group


def panel(width, height, color=PANEL, stroke=LINE, radius=0.16, opacity=0.96):
    return RoundedRectangle(
        width=width,
        height=height,
        corner_radius=radius,
        fill_color=color,
        fill_opacity=opacity,
        stroke_color=stroke,
        stroke_width=1.2,
    )


def label_chip(text, color=CYAN, size=19, mono=False):
    label = code_text(text, size, color, MEDIUM) if mono else ui(text, size, color, MEDIUM)
    box = RoundedRectangle(
        width=label.width + 0.34,
        height=label.height + 0.20,
        corner_radius=0.10,
        fill_color=PANEL_2,
        fill_opacity=0.98,
        stroke_color=color,
        stroke_width=1.0,
    )
    label.move_to(box)
    return VGroup(box, label)


def clean_arrow(start, end, color=TEXT, width=3.2, tip=0.14, buff=0.0):
    return Arrow(
        start,
        end,
        buff=buff,
        color=color,
        stroke_width=width,
        tip_length=tip,
        max_tip_length_to_length_ratio=0.075,
    )


def clean_axis(start, end, color, label=None, label_direction=RIGHT):
    axis = clean_arrow(start, end, color=color, width=2.8, tip=0.13)
    if label is None:
        return VGroup(axis)
    tag = code_text(label, 18, color, MEDIUM).next_to(axis.get_end(), label_direction, buff=0.08)
    return VGroup(axis, tag)


def statement(title_text, lines, width=4.8, accent=CYAN):
    title_obj = ui(title_text, 23, accent, BOLD)
    body = VGroup()
    for line in lines:
        if line == "":
            body.add(Rectangle(width=0.01, height=0.12, stroke_opacity=0, fill_opacity=0))
        else:
            body.add(ui(line, 20, TEXT if not line.startswith("·") else MUTED))
    body.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
    content = VGroup(title_obj, body).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
    box = panel(width, content.height + 0.58)
    content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.28)
    return VGroup(box, content)


def formula_bar(text, color=CYAN, width=None, size=25):
    formula = code_text(text, size, color, MEDIUM)
    box_width = max(formula.width + 0.52, width or 0)
    box = RoundedRectangle(
        width=box_width,
        height=formula.height + 0.30,
        corner_radius=0.10,
        fill_color=PANEL_2,
        fill_opacity=0.98,
        stroke_color=color,
        stroke_width=1.0,
    )
    formula.move_to(box)
    return VGroup(box, formula)


def bottom_caption(text, color=MUTED):
    cap = ui(text, 20, color, MEDIUM)
    bg = RoundedRectangle(
        width=min(cap.width + 0.55, 12.8),
        height=cap.height + 0.25,
        corner_radius=0.10,
        fill_color=PANEL,
        fill_opacity=0.92,
        stroke_width=0,
    )
    cap.move_to(bg)
    group = VGroup(bg, cap).to_edge(DOWN, buff=0.28)
    return group


def fade_all(scene, run_time=0.55):
    if scene.mobjects:
        scene.play(FadeOut(Group(*scene.mobjects)), run_time=run_time)


def add_base(scene):
    scene.camera.background_color = BG
    scene.add(background_grid())
