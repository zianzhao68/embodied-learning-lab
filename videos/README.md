# Manim 课程动画

这里保存可复用的课程动画源代码与分镜。渲染中间产物由根目录 `.gitignore` 排除，最终视频和海报分别发布到 `site/public/videos/` 与 `site/public/assets/`。

## 环境

- Python 3.12
- Manim Community 0.21.0
- FFmpeg
- 中文字体：SimHei（黑体）

```powershell
python -m pip install -r videos/requirements.txt
```

Windows 若缺少 FFmpeg，可用：

```powershell
winget install --id Gyan.FFmpeg -e
```

## Rodrigues 动画

分镜：`02-rodrigues/storyboard.md`

源代码：`02-rodrigues/rodrigues_explainer.py`

低清 smoke test：

```powershell
cd D:\vla\videos\02-rodrigues
python -m manim -ql --fps 15 rodrigues_explainer.py RodriguesGeometricExplainer
```

1080p 主片和海报：

```powershell
python -m manim -qh --fps 30 rodrigues_explainer.py RodriguesGeometricExplainer
python -m manim -qh -s rodrigues_explainer.py RodriguesPoster
```

发布产物：

- `site/public/videos/02-rodrigues-geometric-explainer.mp4`
- `site/public/assets/02-rodrigues-video-poster.png`
