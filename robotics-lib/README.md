# Embodied Robotics：NumPy / PyTorch 运动学工具库

第四、五课的工程实现。NumPy 与 PyTorch 后端采用相同 API，覆盖平面 2R、标准 DH 正运动学、解析逆运动学、Jacobian 与阻尼最小二乘迭代。

## 固定约定

- 右手坐标系、列向量，角度单位为弧度；
- 长度统一使用同一单位，机器人项目推荐米；
- 标准 DH 顺序：`Rz(theta) @ Tz(d) @ Tx(a) @ Rx(alpha)`；
- 转动关节（revolute joint）变量加到 `theta`；
- 移动关节（prismatic joint）变量加到 `d`；
- 矩阵从右向左作用，串联链按 base 到末端的局部变换依次左乘。

标准 DH 与改进 DH（modified DH）不是同一约定，参数表不能直接混用。

## 安装与测试

```powershell
cd D:\vla\robotics-lib
python -m pip install -e .
python -m unittest discover -s tests -v
```

PyTorch 为可选依赖：

```powershell
python -m pip install -e ".[torch]"
```

## 平面 2R 示例

```python
import numpy as np
from embodied_robotics import numpy as kin

points = kin.planar_2r_fk(
    lengths=[0.4, 0.3],
    joint_values=np.deg2rad([30.0, 60.0]),
)

base, elbow, end_effector = points
# end_effector ≈ [0.3464, 0.5]
```

其中第二关节角是相对第一连杆的角度，因此第二连杆相对世界的绝对方向为 `q1 + q2`。

## 标准 DH 示例

```python
parameters = np.array([
    # theta, d,   a, alpha
    [0.0,   0.0, 0.4, 0.0],
    [0.0,   0.0, 0.3, 0.0],
])

T_base_ee = kin.forward_kinematics_dh(
    parameters,
    joint_values=np.deg2rad([30.0, 60.0]),
    joint_types=["R", "R"],
)
```

## API

两个后端均提供：

- `dh_transform(theta, d, a, alpha)`
- `compose_chain(transforms, return_all=False)`
- `forward_kinematics_dh(parameters, joint_values, joint_types, return_all=False)`
- `planar_2r_fk(lengths, joint_values)`
- `planar_2r_jacobian(lengths, joint_values)`
- `planar_2r_ik(lengths, target)`
- `damped_least_squares_step(jacobian, error, damping)`
- `planar_2r_ik_dls(...)`
- `within_joint_limits(...)`

所有函数支持前导批量维度。PyTorch 后端继承 dtype/device，并可对关节变量进行自动微分。

## 性质测试

当前测试验证：

- 2R 手算结果；
- 第二关节角的相对角语义；
- 任意关节角下连杆长度保持；
- 标准 DH 链与二维向量和结果一致；
- `return_all` 返回 base、各关节和末端位姿；
- 转动/移动关节变量进入正确参数；
- 串联复合顺序正确；
- NumPy/PyTorch 后端一致；
- PyTorch 自动微分与有限差分一致；
- 输入形状和关节类型错误被显式拒绝；
- 解析 IK 的肘上/肘下两支都能重建目标；
- 工作空间内外边界被显式判断；
- Jacobian 与有限差分/自动微分一致；
- 奇异触发条件 `det(J)=l1*l2*sin(q2)` 正确；
- 阻尼步在奇异附近保持有限；
- DLS 对可达目标收敛，对不可达或受限目标不谎报成功。

随机测试使用固定种子，便于复现。
