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


def planar_2r_jacobian(lengths: Tensor, joint_values: Tensor) -> Tensor:
    lengths = _float_tensor(lengths)
    q = _float_tensor(joint_values).to(device=lengths.device, dtype=lengths.dtype)
    if lengths.shape[-1:] != (2,) or q.shape[-1:] != (2,):
        raise ValueError("lengths and joint_values must both end in dimension 2")
    batch = torch.broadcast_shapes(lengths.shape[:-1], q.shape[:-1])
    lengths = torch.broadcast_to(lengths, batch + (2,))
    q = torch.broadcast_to(q, batch + (2,))
    l1, l2 = lengths.unbind(dim=-1)
    q1, q2 = q.unbind(dim=-1)
    s1, c1 = torch.sin(q1), torch.cos(q1)
    s12, c12 = torch.sin(q1 + q2), torch.cos(q1 + q2)
    return torch.stack((
        -l1 * s1 - l2 * s12, -l2 * s12,
        l1 * c1 + l2 * c12, l2 * c12,
    ), dim=-1).reshape(batch + (2, 2))


def planar_2r_ik(
    lengths: Tensor, target: Tensor, reachability_eps: float = 1e-9
) -> tuple[Tensor, Tensor]:
    lengths = _float_tensor(lengths)
    target = _float_tensor(target).to(device=lengths.device, dtype=lengths.dtype)
    if lengths.shape[-1:] != (2,) or target.shape[-1:] != (2,):
        raise ValueError("lengths and target must both end in dimension 2")
    batch = torch.broadcast_shapes(lengths.shape[:-1], target.shape[:-1])
    lengths = torch.broadcast_to(lengths, batch + (2,))
    target = torch.broadcast_to(target, batch + (2,))
    if torch.any(lengths <= 0).item():
        raise ValueError("link lengths must be positive")
    l1, l2 = lengths.unbind(dim=-1)
    x, y = target.unbind(dim=-1)
    c2_raw = (x * x + y * y - l1 * l1 - l2 * l2) / (2.0 * l1 * l2)
    reachable = (c2_raw >= -1.0 - reachability_eps) & (c2_raw <= 1.0 + reachability_eps)
    c2 = c2_raw.clamp(-1.0, 1.0)
    s2 = torch.sqrt((1.0 - c2 * c2).clamp_min(0.0))
    q2_positive = torch.atan2(s2, c2)
    q2_negative = torch.atan2(-s2, c2)

    def q1_for(q2: Tensor) -> Tensor:
        return torch.atan2(y, x) - torch.atan2(l2 * torch.sin(q2), l1 + l2 * torch.cos(q2))

    solutions = torch.stack((
        torch.stack((q1_for(q2_positive), q2_positive), dim=-1),
        torch.stack((q1_for(q2_negative), q2_negative), dim=-1),
    ), dim=-2)
    return torch.where(reachable[..., None, None], solutions, torch.full_like(solutions, torch.nan)), reachable


def damped_least_squares_step(jacobian: Tensor, error: Tensor, damping: float = 0.05) -> Tensor:
    j = _float_tensor(jacobian)
    e = _float_tensor(error).to(device=j.device, dtype=j.dtype)
    if j.ndim < 2 or e.ndim == 0 or j.shape[-2] != e.shape[-1]:
        raise ValueError("jacobian must be (..., M, N) and error (..., M)")
    identity = torch.eye(j.shape[-2], dtype=j.dtype, device=j.device)
    system = j @ j.transpose(-1, -2) + damping * damping * identity
    solved = torch.linalg.solve(system, e.unsqueeze(-1))
    return (j.transpose(-1, -2) @ solved).squeeze(-1)


def within_joint_limits(joint_values: Tensor, lower: Tensor, upper: Tensor) -> Tensor:
    q = _float_tensor(joint_values)
    low = _float_tensor(lower).to(device=q.device, dtype=q.dtype)
    high = _float_tensor(upper).to(device=q.device, dtype=q.dtype)
    q, low, high = torch.broadcast_tensors(q, low, high)
    if q.ndim == 0:
        raise ValueError("joint values must have a joint dimension")
    return torch.all((q >= low) & (q <= high), dim=-1)


def planar_2r_ik_dls(
    lengths: Tensor,
    target: Tensor,
    initial: Tensor,
    *,
    damping: float = 0.05,
    step_size: float = 1.0,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
    joint_limits: tuple[Tensor, Tensor] | None = None,
) -> tuple[Tensor, Tensor, Tensor]:
    lengths = _float_tensor(lengths)
    target = _float_tensor(target).to(device=lengths.device, dtype=lengths.dtype)
    q = _float_tensor(initial).to(device=lengths.device, dtype=lengths.dtype)
    if lengths.shape[-1:] != (2,) or target.shape[-1:] != (2,) or q.shape[-1:] != (2,):
        raise ValueError("lengths, target and initial must all end in dimension 2")
    batch = torch.broadcast_shapes(lengths.shape[:-1], target.shape[:-1], q.shape[:-1])
    lengths = torch.broadcast_to(lengths, batch + (2,))
    target = torch.broadcast_to(target, batch + (2,))
    q = torch.broadcast_to(q, batch + (2,)).clone()
    if joint_limits is not None:
        lower = torch.broadcast_to(_float_tensor(joint_limits[0]).to(q), batch + (2,))
        upper = torch.broadcast_to(_float_tensor(joint_limits[1]).to(q), batch + (2,))
        if torch.any(lower > upper).item():
            raise ValueError("joint lower limits must not exceed upper limits")
    for _ in range(max_iterations):
        position = planar_2r_fk(lengths, q)[..., -1, :]
        error = target - position
        if torch.all(torch.linalg.vector_norm(error, dim=-1) <= tolerance).item():
            break
        q = q + step_size * damped_least_squares_step(planar_2r_jacobian(lengths, q), error, damping)
        if joint_limits is not None:
            q = torch.maximum(torch.minimum(q, upper), lower)
    final_error = torch.linalg.vector_norm(target - planar_2r_fk(lengths, q)[..., -1, :], dim=-1)
    return q, final_error <= tolerance, final_error
