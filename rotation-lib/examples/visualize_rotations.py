"""Generate a dependency-free SVG that visualizes frame rotation and SLERP.

Run from ``rotation-lib`` after ``pip install -e .``:
    python examples/visualize_rotations.py
"""

from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

from embodied_spatial import numpy as rot

WIDTH, HEIGHT = 1200, 430
COLORS = {"x": "#ff6b5f", "y": "#47d79b", "z": "#5b8cff", "vector": "#ffad4d"}
PROJECTION = np.array([[1.0, -0.58, 0.0], [0.22, 0.34, -0.92]])


def point3_to_svg(point: np.ndarray, origin: tuple[float, float], scale: float = 92.0) -> tuple[float, float]:
    projected = PROJECTION @ point
    return origin[0] + scale * projected[0], origin[1] + scale * projected[1]


def line(start, end, color, width=3, dashed=False, marker=True) -> str:
    dash = ' stroke-dasharray="6 6"' if dashed else ""
    arrow = ' marker-end="url(#arrow)"' if marker else ""
    return f'<line x1="{start[0]:.1f}" y1="{start[1]:.1f}" x2="{end[0]:.1f}" y2="{end[1]:.1f}" stroke="{color}" stroke-width="{width}"{dash}{arrow}/>'


def text(x, y, value, size=17, color="#dce5f2", weight=400, anchor="start") -> str:
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Microsoft YaHei UI, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>'


def frame(origin, matrix, prefix="") -> list[str]:
    result = []
    center = point3_to_svg(np.zeros(3), origin)
    for index, name in enumerate(("x", "y", "z")):
        endpoint = point3_to_svg(matrix[:, index], origin)
        result.append(line(center, endpoint, COLORS[name]))
        outward = np.asarray(endpoint) - np.asarray(center)
        label = np.asarray(endpoint) + 13.0 * outward / np.linalg.norm(outward)
        result.append(text(label[0], label[1] + 5, prefix + name, 16, COLORS[name], 700, "middle"))
    result.append(f'<circle cx="{center[0]}" cy="{center[1]}" r="4" fill="#f2f5f9"/>')
    return result


def main() -> None:
    identity = np.eye(3)
    rz90 = rot.axis_angle_to_matrix([0.0, 0.0, np.pi / 2])
    vector = np.array([0.85, 0.15, 0.65])
    rotated_vector = rot.rotate_vectors(rz90, vector)

    q0 = rot.axis_angle_to_quaternion([0.0, 0.0, 0.0])
    q1 = rot.axis_angle_to_quaternion([0.0, 0.0, 2 * np.pi / 3])
    samples = rot.quaternion_slerp(q0, q1, np.linspace(0.0, 1.0, 9))
    sample_vectors = rot.rotate_vectors(rot.quaternion_to_matrix(samples), vector)

    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<rect width="100%" height="100%" rx="24" fill="#0b1020"/>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs>
<path d="M400 72V385M800 72V385" stroke="#263449"/>
''']
    titles = [(200, "原始坐标系"), (600, "主动旋转：Rz(90°)"), (1000, "SLERP：单位球最短路径")]
    for x, title_value in titles:
        parts.append(text(x, 43, title_value, 20, "#f2f5f9", 700, "middle"))

    left_origin = (205, 252)
    parts.extend(frame(left_origin, identity))
    center = point3_to_svg(np.zeros(3), left_origin)
    endpoint = point3_to_svg(vector, left_origin)
    parts.append(line(center, endpoint, COLORS["vector"], width=4))
    parts.append(text(200, 380, "p = (0.85, 0.15, 0.65)", 16, "#aab7c9", anchor="middle"))

    middle_origin = (602, 252)
    parts.extend(frame(middle_origin, rz90, prefix="R"))
    center = point3_to_svg(np.zeros(3), middle_origin)
    endpoint = point3_to_svg(rotated_vector, middle_origin)
    parts.append(line(center, endpoint, COLORS["vector"], width=4))
    parts.append(text(600, 380, "Rp = (-0.15, 0.85, 0.65)", 16, "#aab7c9", anchor="middle"))

    right_origin = (1000, 252)
    parts.extend(frame(right_origin, identity))
    points = [point3_to_svg(item, right_origin) for item in sample_vectors]
    path_data = " ".join(("M" if i == 0 else "L") + f" {p[0]:.1f} {p[1]:.1f}" for i, p in enumerate(points))
    parts.append(f'<path d="{path_data}" fill="none" stroke="#ffad4d" stroke-width="3" stroke-dasharray="7 5"/>')
    for index, point in enumerate(points):
        radius = 6 if index in (0, len(points) - 1) else 3.5
        parts.append(f'<circle cx="{point[0]:.1f}" cy="{point[1]:.1f}" r="{radius}" fill="#ffad4d"/>')
    parts.append(text(1000, 380, "等角速度采样 · 四元数始终保持单位范数", 16, "#aab7c9", anchor="middle"))
    parts.append(text(24, 414, "约定：右手系 · 主动旋转 · 列向量 · q=(w,x,y,z)", 14, "#718198"))
    parts.append("</svg>")

    output = Path(__file__).resolve().parents[1] / "artifacts" / "rotation-demo.svg"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(parts), encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
