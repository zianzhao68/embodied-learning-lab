# Manim 课程动画

这里保存可复用的课程动画源代码与分镜。渲染中间产物由根目录 `.gitignore` 排除，最终视频和海报分别发布到 `site/public/videos/` 与 `site/public/assets/`。

## 环境

- Python 3.12
- Manim Community 0.21.0
- FFmpeg
- 中文字体：Microsoft YaHei UI
- 公式/代码备用字体：Cambria Math、Cascadia Code

```powershell
python -m pip install -r videos/requirements.txt
```

Windows 若缺少 FFmpeg：

```powershell
winget install --id Gyan.FFmpeg -e
```

## 共享视觉系统

`manim_style.py` 统一维护：

- 深色专业背景和克制的网格；
- 标题、正文、标签和公式的字号层级；
- x 红、y 绿、z 蓝的固定坐标轴语义；
- 2～4 px 细线、较小箭头尖端和统一信息卡片；
- 16:9 安全边距、底部结论条和场景编号。

课程动画不得直接使用 Manim 默认粗箭头和默认排版。

## 第二课动画

| 主题 | 分镜 | 源代码 | Scene |
|---|---|---|---|
| 旋转表示与 SO(3) | `02-representation-so3/storyboard.md` | `02-representation-so3/representation_so3.py` | `RotationRepresentationsSO3` |
| 欧拉角与万向节锁 | `02-euler-gimbal/storyboard.md` | `02-euler-gimbal/euler_gimbal.py` | `EulerGimbalExplainer` |
| Rodrigues 几何构造 | `02-rodrigues/storyboard.md` | `02-rodrigues/rodrigues_explainer.py` | `RodriguesGeometricExplainer` |
| 四元数与 SLERP | `02-quaternion-slerp/storyboard.md` | `02-quaternion-slerp/quaternion_slerp.py` | `QuaternionSlerpExplainer` |
| SE(3) 与变换链 | `03-se3-transform-chain/storyboard.md` | `03-se3-transform-chain/se3_transform_chain.py` | `SE3TransformChainExplainer` |
| 平面 2R 正运动学 | `04-forward-kinematics/storyboard.md` | `04-forward-kinematics/forward_kinematics.py` | `ForwardKinematicsExplainer` |

## 渲染流程

先在 `D:\vla\videos` 下执行 480p smoke test，并检查关键帧：

```powershell
python -m manim -ql --fps 15 02-euler-gimbal/euler_gimbal.py EulerGimbalExplainer
```

视觉精修后再渲染 1080p/30fps 主片和海报：

```powershell
python -m manim -qh --fps 30 02-euler-gimbal/euler_gimbal.py EulerGimbalExplainer
python -m manim -qh -s 02-euler-gimbal/euler_gimbal.py EulerGimbalPoster
```

## 发布产物

- `site/public/videos/02-rotation-representations-so3.mp4`
- `site/public/videos/02-euler-gimbal-lock.mp4`
- `site/public/videos/02-rodrigues-geometric-explainer.mp4`
- `site/public/videos/02-quaternion-slerp.mp4`
- 对应海报位于 `site/public/assets/02-*-poster.png`
- `site/public/videos/03-se3-transform-chain.mp4`
- `site/public/assets/03-se3-transform-chain-poster.png`
- `site/public/videos/04-planar-2r-forward-kinematics.mp4`
- `site/public/assets/04-planar-2r-forward-kinematics-poster.png`
- `site/public/videos/05-ik-jacobian-singularity.mp4`
- `site/public/assets/05-ik-jacobian-singularity-poster.png`
