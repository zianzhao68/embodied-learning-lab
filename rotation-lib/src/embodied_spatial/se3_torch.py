"""Differentiable, batched PyTorch utilities for rigid transforms in SE(3)."""

from __future__ import annotations

import torch
from torch import Tensor

from . import torch as so3


def _float_tensor(value: Tensor) -> Tensor:
    if not isinstance(value, Tensor):
        value = torch.as_tensor(value)
    if not value.is_floating_point():
        value = value.to(torch.get_default_dtype())
    return value


def _check_transform(transform: Tensor, name: str = "transform") -> None:
    if transform.ndim < 2 or transform.shape[-2:] != (4, 4):
        raise ValueError(f"{name} must have shape (..., 4, 4); got {tuple(transform.shape)}")


def make_transform(rotation: Tensor, translation: Tensor) -> Tensor:
    r = _float_tensor(rotation)
    t = _float_tensor(translation).to(device=r.device, dtype=r.dtype)
    if r.ndim < 2 or r.shape[-2:] != (3, 3):
        raise ValueError(f"rotation must have shape (..., 3, 3); got {tuple(r.shape)}")
    if t.ndim == 0 or t.shape[-1] != 3:
        raise ValueError(f"translation must have shape (..., 3); got {tuple(t.shape)}")
    batch = torch.broadcast_shapes(r.shape[:-2], t.shape[:-1])
    r = torch.broadcast_to(r, batch + (3, 3))
    t = torch.broadcast_to(t, batch + (3,))
    upper = torch.cat((r, t[..., None]), dim=-1)
    bottom = torch.zeros(batch + (1, 4), dtype=r.dtype, device=r.device)
    bottom[..., 0, 3] = 1.0
    return torch.cat((upper, bottom), dim=-2)


def split_transform(transform: Tensor) -> tuple[Tensor, Tensor]:
    t = _float_tensor(transform)
    _check_transform(t)
    return t[..., :3, :3], t[..., :3, 3]


def transform_points(transform: Tensor, points: Tensor) -> Tensor:
    t = _float_tensor(transform)
    p = _float_tensor(points).to(device=t.device, dtype=t.dtype)
    _check_transform(t)
    if p.ndim == 0 or p.shape[-1] != 3:
        raise ValueError(f"points must have shape (..., 3); got {tuple(p.shape)}")
    rotation, translation = split_transform(t)
    return torch.matmul(rotation, p.unsqueeze(-1)).squeeze(-1) + translation


def transform_directions(transform: Tensor, directions: Tensor) -> Tensor:
    t = _float_tensor(transform)
    direction = _float_tensor(directions).to(device=t.device, dtype=t.dtype)
    _check_transform(t)
    if direction.ndim == 0 or direction.shape[-1] != 3:
        raise ValueError(f"directions must have shape (..., 3); got {tuple(direction.shape)}")
    return torch.matmul(t[..., :3, :3], direction.unsqueeze(-1)).squeeze(-1)


def compose_transforms(left: Tensor, right: Tensor) -> Tensor:
    a = _float_tensor(left)
    b = _float_tensor(right).to(device=a.device, dtype=a.dtype)
    _check_transform(a, "left")
    _check_transform(b, "right")
    return a @ b


def inverse_transform(transform: Tensor) -> Tensor:
    t = _float_tensor(transform)
    _check_transform(t)
    rotation, translation = split_transform(t)
    rotation_t = rotation.transpose(-1, -2)
    inverse_translation = -torch.matmul(rotation_t, translation.unsqueeze(-1)).squeeze(-1)
    return make_transform(rotation_t, inverse_translation)


def relative_transform(reference_pose: Tensor, target_pose: Tensor) -> Tensor:
    return compose_transforms(inverse_transform(reference_pose), target_pose)


def quaternion_translation_to_transform(quaternion: Tensor, translation: Tensor) -> Tensor:
    return make_transform(so3.quaternion_to_matrix(quaternion), translation)


def transform_error(transform: Tensor) -> tuple[Tensor, Tensor, Tensor]:
    t = _float_tensor(transform)
    _check_transform(t)
    orthogonality, determinant = so3.rotation_matrix_error(t[..., :3, :3])
    expected = t.new_tensor([0.0, 0.0, 0.0, 1.0])
    bottom_row = torch.linalg.vector_norm(t[..., 3, :] - expected, dim=-1)
    return orthogonality, determinant, bottom_row


def project_to_se3(transform: Tensor) -> Tensor:
    t = _float_tensor(transform)
    _check_transform(t)
    return make_transform(so3.project_to_so3(t[..., :3, :3]), t[..., :3, 3])
