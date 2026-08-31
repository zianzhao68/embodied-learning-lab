# embodied-vision

第六课《针孔相机：从三维点到像素》的工程实现。NumPy 与 PyTorch 后端采用匹配 API，约定相机光学坐标系为 x 向右、y 向下、z 向前，像素坐标 u 向右、v 向下。

## API

- `make_intrinsics(fx, fy, cx, cy)`
- `project_points(points_camera, intrinsics)`
- `unproject_pixels(pixels, depth, intrinsics)`
- `pixel_rays(pixels, intrinsics, unit=False)`
- `transform_points(points, transform)`
- `project_world_points(points_world, transform_camera_world, intrinsics)`
- `focal_length_from_fov(image_extent_px, field_of_view_rad)`

投影返回 `(pixels, valid)`。深度不为正、位于相机后方或包含非有限值的点返回 NaN 像素和 `valid=False`，不会被静默投影。

## 安装与测试

```powershell
cd D:\vla\vision-lib
python -m pip install -e .
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python -m unittest discover -s tests -v
```

15 项测试覆盖：

- 可手算投影 `(0.1, 0.05, 1.0) → (370, 265)`；
- 同一射线不同深度映射到同一像素；
- 单变量改变 X/Z 的因果对照；
- 投影与带深度反投影的随机往返；
- 主点射线、FOV 与焦距；
- 世界系经外参到相机系再投影；
- 批量内参与批量外参；
- 无效深度显式状态；
- NumPy/PyTorch 对齐、dtype 与自动微分。
