"""Differentiable, batched PyTorch forward-kinematics utilities."""

from __future__ import annotations

from collections.abc import Sequence
import torch
from torch import Tensor


def _float_tensor(value: Tensor) -> Tensor:
    if not isinstance(value, Tensor):
        value = torch.as_tensor(value)
    if not value.is_floating_point():
        value = value.to(torch.get_default_dtype())
    return value


def dh_transform(theta: Tensor, d: Tensor, a: Tensor, alpha: Tensor) -> Tensor:
    values = [_float_tensor(value) for value in (theta, d, a, alpha)]
    device, dtype = values[0].device, values[0].dtype
    values = [value.to(device=device, dtype=dtype) for value in values]
    theta, d, a, alpha = torch.broadcast_tensors(*values)
    ct, st = torch.cos(theta), torch.sin(theta)
    ca, sa = torch.cos(alpha), torch.sin(alpha)
    zero, one = torch.zeros_like(theta), torch.ones_like(theta)
    return torch.stack((
        ct, -st * ca, st * sa, a * ct,
        st, ct * ca, -ct * sa, a * st,
        zero, sa, ca, d,
        zero, zero, zero, one,
    ), dim=-1).reshape(theta.shape + (4, 4))


def compose_chain(transforms: Tensor, return_all: bool = False) -> Tensor:
    local = _float_tensor(transforms)
    if local.ndim < 3 or local.shape[-2:] != (4, 4):
        raise ValueError(f"transforms must have shape (..., N, 4, 4); got {tuple(local.shape)}")
    count = local.shape[-3]
    batch = local.shape[:-3]
    current = torch.eye(4, dtype=local.dtype, device=local.device).expand(batch + (4, 4))
    poses = [current]
    for index in range(count):
        current = current @ local[..., index, :, :]
        poses.append(current)
    return torch.stack(poses, dim=-3) if return_all else current


def forward_kinematics_dh(
    parameters: Tensor,
    joint_values: Tensor | None = None,
    joint_types: Sequence[str] | None = None,
    return_all: bool = False,
) -> Tensor:
    params = _float_tensor(parameters)
    if params.ndim < 2 or params.shape[-1] != 4:
        raise ValueError(f"parameters must have shape (..., N, 4); got {tuple(params.shape)}")
    count = params.shape[-2]
    types = tuple("R" for _ in range(count)) if joint_types is None else tuple(item.upper() for item in joint_types)
    if len(types) != count or any(item not in ("R", "P") for item in types):
        raise ValueError("joint_types must contain exactly N entries, each 'R' or 'P'")
    q = torch.zeros(params.shape[:-1], dtype=params.dtype, device=params.device) if joint_values is None else _float_tensor(joint_values).to(device=params.device, dtype=params.dtype)
    if q.ndim == 0 or q.shape[-1] != count:
        raise ValueError(f"joint_values must have shape (..., {count}); got {tuple(q.shape)}")
    batch = torch.broadcast_shapes(params.shape[:-2], q.shape[:-1])
    params = torch.broadcast_to(params, batch + (count, 4))
    q = torch.broadcast_to(q, batch + (count,))
    theta, d, a, alpha = params.unbind(dim=-1)
    revolute = torch.tensor([item == "R" for item in types], device=params.device)
    theta = theta + q * revolute
    d = d + q * (~revolute)
    return compose_chain(dh_transform(theta, d, a, alpha), return_all=return_all)


def planar_2r_fk(lengths: Tensor, joint_values: Tensor) -> Tensor:
    lengths = _float_tensor(lengths)
    q = _float_tensor(joint_values).to(device=lengths.device, dtype=lengths.dtype)
    if lengths.shape[-1:] != (2,):
        raise ValueError(f"lengths must have shape (..., 2); got {tuple(lengths.shape)}")
    if q.shape[-1:] != (2,):
        raise ValueError(f"joint_values must have shape (..., 2); got {tuple(q.shape)}")
    batch = torch.broadcast_shapes(lengths.shape[:-1], q.shape[:-1])
    lengths = torch.broadcast_to(lengths, batch + (2,))
    q = torch.broadcast_to(q, batch + (2,))
    l1, l2 = lengths.unbind(dim=-1)
    q1, q2 = q.unbind(dim=-1)
    base = torch.zeros(batch + (2,), dtype=lengths.dtype, device=lengths.device)
    elbow = torch.stack((l1 * torch.cos(q1), l1 * torch.sin(q1)), dim=-1)
    end = elbow + torch.stack((l2 * torch.cos(q1 + q2), l2 * torch.sin(q1 + q2)), dim=-1)
    return torch.stack((base, elbow, end), dim=-2)
