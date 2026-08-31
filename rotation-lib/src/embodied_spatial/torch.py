"""Differentiable, batched PyTorch rotation utilities.

Conventions match :mod:`embodied_spatial.numpy`: active right-handed matrices,
column vectors, scalar-first quaternions, and ZYX ``(yaw, pitch, roll)``.
"""

from __future__ import annotations

import torch
from torch import Tensor

_EPS = 1e-8
_SMALL = 1e-4


def _float_tensor(value: Tensor) -> Tensor:
    if not isinstance(value, Tensor):
        value = torch.as_tensor(value)
    if not value.is_floating_point():
        value = value.to(torch.get_default_dtype())
    return value


def _check_last_dim(value: Tensor, size: int, name: str) -> None:
    if value.ndim == 0 or value.shape[-1] != size:
        raise ValueError(f"{name} must have shape (..., {size}); got {tuple(value.shape)}")


def _check_matrix(value: Tensor, name: str = "matrix") -> None:
    if value.ndim < 2 or value.shape[-2:] != (3, 3):
        raise ValueError(f"{name} must have shape (..., 3, 3); got {tuple(value.shape)}")


def normalize_quaternion(quaternion: Tensor, eps: float = _EPS) -> Tensor:
    q = _float_tensor(quaternion)
    _check_last_dim(q, 4, "quaternion")
    norm = torch.linalg.vector_norm(q, dim=-1, keepdim=True)
    if torch.any(norm <= eps).item():
        raise ValueError("quaternion norm must be greater than zero")
    return q / norm


def quaternion_to_matrix(quaternion: Tensor) -> Tensor:
    q = normalize_quaternion(quaternion)
    w, x, y, z = q.unbind(dim=-1)
    rows = (
        1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y),
        2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x),
        2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y),
    )
    return torch.stack(rows, dim=-1).reshape(q.shape[:-1] + (3, 3))


def matrix_to_quaternion(matrix: Tensor) -> Tensor:
    m = _float_tensor(matrix)
    _check_matrix(m)
    m00, m01, m02 = m[..., 0, 0], m[..., 0, 1], m[..., 0, 2]
    m10, m11, m12 = m[..., 1, 0], m[..., 1, 1], m[..., 1, 2]
    m20, m21, m22 = m[..., 2, 0], m[..., 2, 1], m[..., 2, 2]
    q_abs = torch.sqrt(torch.clamp(torch.stack((
        1 + m00 + m11 + m22,
        1 + m00 - m11 - m22,
        1 - m00 + m11 - m22,
        1 - m00 - m11 + m22,
    ), dim=-1), min=0.0))
    candidates = torch.stack((
        torch.stack((q_abs[..., 0] ** 2, m21 - m12, m02 - m20, m10 - m01), dim=-1),
        torch.stack((m21 - m12, q_abs[..., 1] ** 2, m10 + m01, m02 + m20), dim=-1),
        torch.stack((m02 - m20, m10 + m01, q_abs[..., 2] ** 2, m12 + m21), dim=-1),
        torch.stack((m10 - m01, m20 + m02, m21 + m12, q_abs[..., 3] ** 2), dim=-1),
    ), dim=-2)
    candidates = candidates / (2.0 * q_abs[..., :, None].clamp_min(0.1))
    index = q_abs.argmax(dim=-1)[..., None, None].expand(q_abs.shape[:-1] + (1, 4))
    q = torch.gather(candidates, -2, index).squeeze(-2)
    q = normalize_quaternion(q)
    return torch.where(q[..., :1] < 0, -q, q)


def axis_angle_to_quaternion(rotation_vector: Tensor) -> Tensor:
    vector = _float_tensor(rotation_vector)
    _check_last_dim(vector, 3, "rotation_vector")
    angle = torch.linalg.vector_norm(vector, dim=-1, keepdim=True)
    angle2 = angle * angle
    regular = torch.sin(0.5 * angle) / angle.clamp_min(torch.finfo(vector.dtype).tiny)
    series = 0.5 - angle2 / 48.0 + angle2 * angle2 / 3840.0
    scale = torch.where(angle < _SMALL, series, regular)
    return torch.cat((torch.cos(0.5 * angle), vector * scale), dim=-1)


def quaternion_to_axis_angle(quaternion: Tensor) -> Tensor:
    q = normalize_quaternion(quaternion)
    q = torch.where(q[..., :1] < 0, -q, q)
    xyz = q[..., 1:]
    sin_half = torch.linalg.vector_norm(xyz, dim=-1, keepdim=True)
    angle = 2.0 * torch.atan2(sin_half, q[..., :1].clamp(0.0, 1.0))
    regular = angle / sin_half.clamp_min(torch.finfo(q.dtype).tiny)
    series = 2.0 + sin_half * sin_half / 3.0
    return xyz * torch.where(sin_half < _SMALL, series, regular)


def axis_angle_to_matrix(rotation_vector: Tensor) -> Tensor:
    return quaternion_to_matrix(axis_angle_to_quaternion(rotation_vector))


def matrix_to_axis_angle(matrix: Tensor) -> Tensor:
    return quaternion_to_axis_angle(matrix_to_quaternion(matrix))


def euler_zyx_to_matrix(euler: Tensor) -> Tensor:
    angles = _float_tensor(euler)
    _check_last_dim(angles, 3, "euler")
    yaw, pitch, roll = angles.unbind(dim=-1)
    cy, sy = torch.cos(yaw), torch.sin(yaw)
    cp, sp = torch.cos(pitch), torch.sin(pitch)
    cr, sr = torch.cos(roll), torch.sin(roll)
    rows = (
        cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr,
        sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr,
        -sp, cp * sr, cp * cr,
    )
    return torch.stack(rows, dim=-1).reshape(angles.shape[:-1] + (3, 3))


def matrix_to_euler_zyx(matrix: Tensor, singular_eps: float = 1e-7) -> Tensor:
    m = _float_tensor(matrix)
    _check_matrix(m)
    pitch = torch.asin((-m[..., 2, 0]).clamp(-1.0, 1.0))
    regular = torch.abs(torch.cos(pitch)) > singular_eps
    yaw_regular = torch.atan2(m[..., 1, 0], m[..., 0, 0])
    roll_regular = torch.atan2(m[..., 2, 1], m[..., 2, 2])
    yaw_singular = torch.atan2(-m[..., 0, 1], m[..., 1, 1])
    yaw = torch.where(regular, yaw_regular, yaw_singular)
    roll = torch.where(regular, roll_regular, torch.zeros_like(roll_regular))
    return torch.stack((yaw, pitch, roll), dim=-1)


def quaternion_multiply(left: Tensor, right: Tensor) -> Tensor:
    q1 = normalize_quaternion(left)
    q2 = normalize_quaternion(right)
    w1, x1, y1, z1 = q1.unbind(dim=-1)
    w2, x2, y2, z2 = q2.unbind(dim=-1)
    return normalize_quaternion(torch.stack((
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
    ), dim=-1))


def quaternion_slerp(start: Tensor, end: Tensor, t: Tensor) -> Tensor:
    q0 = normalize_quaternion(start)
    q1 = normalize_quaternion(end)
    dot = torch.sum(q0 * q1, dim=-1)
    q1 = torch.where((dot < 0)[..., None], -q1, q1)
    dot = torch.abs(dot).clamp(0.0, 1.0)
    amount, dot = torch.broadcast_tensors(_float_tensor(t).to(device=q0.device, dtype=q0.dtype), dot)
    theta = torch.acos(dot)
    sin_theta = torch.sin(theta)
    safe = torch.where(sin_theta > 1e-6, sin_theta, torch.ones_like(sin_theta))
    spherical = (
        (torch.sin((1.0 - amount) * theta) / safe)[..., None] * q0
        + (torch.sin(amount * theta) / safe)[..., None] * q1
    )
    linear = (1.0 - amount)[..., None] * q0 + amount[..., None] * q1
    return normalize_quaternion(torch.where((sin_theta > 1e-6)[..., None], spherical, linear))


def rotate_vectors(matrix: Tensor, vectors: Tensor) -> Tensor:
    rotation = _float_tensor(matrix)
    vector = _float_tensor(vectors).to(device=rotation.device, dtype=rotation.dtype)
    _check_matrix(rotation)
    _check_last_dim(vector, 3, "vectors")
    return torch.matmul(rotation, vector.unsqueeze(-1)).squeeze(-1)


def project_to_so3(matrix: Tensor) -> Tensor:
    m = _float_tensor(matrix)
    _check_matrix(m)
    u, _, vh = torch.linalg.svd(m)
    correction = torch.ones(m.shape[:-2] + (3,), dtype=m.dtype, device=m.device)
    correction[..., -1] = torch.where(torch.linalg.det(u @ vh) < 0, -1.0, 1.0)
    return (u * correction[..., None, :]) @ vh


def rotation_matrix_error(matrix: Tensor) -> tuple[Tensor, Tensor]:
    m = _float_tensor(matrix)
    _check_matrix(m)
    identity = torch.eye(3, dtype=m.dtype, device=m.device)
    orthogonality = torch.linalg.matrix_norm(m.transpose(-1, -2) @ m - identity, dim=(-2, -1))
    determinant = torch.abs(torch.linalg.det(m) - 1.0)
    return orthogonality, determinant
