# Embodied Spatial：NumPy / PyTorch 旋转工具库

第二课《三维旋转表示》的工程实现。NumPy 与 PyTorch 后端采用相同函数名、批量维度和数值约定，覆盖 SO(3)、轴角、四元数、ZYX 欧拉角、复合和 SLERP。

## 固定约定

| 项目 | 本库约定 |
|---|---|
| 坐标系 | 右手坐标系 |
| 旋转语义 | 主动旋转向量，不是被动更换坐标表达 |
| 向量 | 列向量，`p_rot = R @ p` |
| 四元数 | 标量在前 `(w, x, y, z)` |
| 欧拉角 | `(yaw, pitch, roll)`，`R = Rz(yaw) @ Ry(pitch) @ Rx(roll)` |
| 轴角 | 旋转向量 `axis * angle`，角度单位为弧度 |
| 复合 | `quaternion_multiply(left, right)` 先作用 `right`，再作用 `left` |

不要把本库的 `(w,x,y,z)` 直接传给默认采用 `(x,y,z,w)` 的第三方 API。

## 安装与测试

```powershell
cd D:\vla\rotation-lib
python -m pip install -e .
python -m unittest discover -s tests -v
```

若需要 PyTorch 后端：

```powershell
python -m pip install -e ".[torch]"
```

## 最小示例

```python
import numpy as np
from embodied_spatial import numpy as rot

# p=(2,0,3) 绕 +z 旋转 90°
rotation_vector = np.array([0.0, 0.0, np.pi / 2])
R = rot.axis_angle_to_matrix(rotation_vector)
p_rot = rot.rotate_vectors(R, np.array([2.0, 0.0, 3.0]))
# p_rot ≈ [0, 2, 3]

q = rot.matrix_to_quaternion(R)           # (w,x,y,z)
euler = rot.matrix_to_euler_zyx(R)        # (yaw,pitch,roll)
R_again = rot.quaternion_to_matrix(q)
```

PyTorch 后端支持批量输入、dtype/device 继承和核心前向路径自动微分：

```python
import torch
from embodied_spatial import torch as rot

rotation_vectors = torch.randn(64, 3, device="cuda", requires_grad=True)
matrices = rot.axis_angle_to_matrix(rotation_vectors)  # (64,3,3)
loss = matrices.square().mean()
loss.backward()
```

## API

两个后端均提供：

- `normalize_quaternion`
- `quaternion_to_matrix` / `matrix_to_quaternion`
- `axis_angle_to_quaternion` / `quaternion_to_axis_angle`
- `axis_angle_to_matrix` / `matrix_to_axis_angle`
- `euler_zyx_to_matrix` / `matrix_to_euler_zyx`
- `quaternion_multiply`
- `quaternion_slerp`
- `rotate_vectors`
- `project_to_so3`
- `rotation_matrix_error`

所有转换都接受前导批量维度，例如 `(B,T,4) -> (B,T,3,3)`。

## 数值与奇异性策略

1. **零角附近**：`sin(theta/2)/theta` 使用泰勒展开，避免 `0/0`。
2. **180°附近**：矩阵转四元数选择数值最大的候选分量，避免仅用迹公式造成消减误差。
3. **四元数双覆盖**：矩阵转四元数返回 `w >= 0` 的规范代表；在 180°处轴正负仍不唯一。
4. **万向节锁**：ZYX 的 `pitch=±pi/2` 时无法分别恢复 yaw 与 roll。本库令 `roll=0`，将可观测组合放在 yaw 中；恢复出的矩阵仍与输入一致。
5. **无效矩阵**：转换函数默认输入已接近 SO(3)。传感器或网络输出有噪声时，先调用 `project_to_so3` 做 SVD 投影。
6. **SLERP**：若起终点点积为负，自动翻转终点四元数，选择单位球上的最短符号分支。

## 性质测试覆盖

测试不是只核对几个固定答案，而是对数百组随机输入验证：

- `R.T @ R = I` 且 `det(R) = 1`；
- 旋转前后向量范数不变；
- 各表示往返后代表同一个矩阵；
- `q` 与 `-q` 代表同一个旋转；
- Hamilton 积与矩阵复合顺序一致；
- 欧拉角在普通位置和 `pitch=±90°` 时均能矩阵往返；
- 零角、微小角和接近 180°的边界输入稳定；
- SLERP 端点、单位范数与最短分支正确；
- NumPy/PyTorch 数值一致；
- PyTorch 梯度有限；
- 带噪矩阵及反射矩阵可投影到合法 SO(3)。

随机测试使用固定种子，便于复现失败。

## 3D 可视化

```powershell
python examples/visualize_rotations.py
```

输出 `artifacts/rotation-demo.svg`，展示原始坐标系、`Rz(90°)` 主动旋转和 SLERP 等角速度采样。脚本只依赖 NumPy，可作为后续 SE(3) 与变换链可视化的基础。
