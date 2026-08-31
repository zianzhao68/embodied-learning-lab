"""Batched NumPy forward-kinematics utilities.

Conventions:
- right-handed frames and column vectors;
- standard Denavit-Hartenberg order ``Rz(theta) Tz(d) Tx(a) Rx(alpha)``;
- revolute joint values add to ``theta``; prismatic values add to ``d``;
- angles are radians and lengths use one consistent unit (recommended: metres).
"""

from __future__ import annotations

from collections.abc import Sequence
import numpy as np
from numpy.typing import ArrayLike, NDArray


def _float_array(value: ArrayLike) -> NDArray[np.floating]:
    array = np.asarray(value)
    if not np.issubdtype(array.dtype, np.floating):
        array = array.astype(np.float64)
    return array


def dh_transform(theta: ArrayLike, d: ArrayLike, a: ArrayLike, alpha: ArrayLike) -> NDArray[np.floating]:
    """Construct standard-DH transforms with broadcastable scalar parameters."""
    theta, d, a, alpha = np.broadcast_arrays(
        _float_array(theta), _float_array(d), _float_array(a), _float_array(alpha)
    )
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    result = np.zeros(theta.shape + (4, 4), dtype=np.result_type(theta, d, a, alpha))
    result[..., 0, 0] = ct
    result[..., 0, 1] = -st * ca
    result[..., 0, 2] = st * sa
    result[..., 0, 3] = a * ct
    result[..., 1, 0] = st
    result[..., 1, 1] = ct * ca
    result[..., 1, 2] = -ct * sa
    result[..., 1, 3] = a * st
    result[..., 2, 1] = sa
    result[..., 2, 2] = ca
    result[..., 2, 3] = d
    result[..., 3, 3] = 1.0
    return result


def compose_chain(transforms: ArrayLike, return_all: bool = False) -> NDArray[np.floating]:
    """Compose ``(..., N, 4, 4)`` local transforms from left to right.

    With ``return_all=True``, return base plus every intermediate pose with shape
    ``(..., N+1, 4, 4)``.
    """
    local = _float_array(transforms)
    if local.ndim < 3 or local.shape[-2:] != (4, 4):
        raise ValueError(f"transforms must have shape (..., N, 4, 4); got {local.shape}")
    count = local.shape[-3]
    batch = local.shape[:-3]
    current = np.broadcast_to(np.eye(4, dtype=local.dtype), batch + (4, 4)).copy()
    poses = [current.copy()]
    for index in range(count):
        current = current @ local[..., index, :, :]
        poses.append(current.copy())
    return np.stack(poses, axis=-3) if return_all else current


def forward_kinematics_dh(
    parameters: ArrayLike,
    joint_values: ArrayLike | None = None,
    joint_types: Sequence[str] | None = None,
    return_all: bool = False,
) -> NDArray[np.floating]:
    """Evaluate a standard-DH serial chain.

    ``parameters`` has shape ``(..., N, 4)`` in ``(theta, d, a, alpha)`` order.
    ``joint_values`` is broadcastable to ``(..., N)``. Joint types are ``R`` or
    ``P``; if omitted, all joints are revolute.
    """
    params = _float_array(parameters)
    if params.ndim < 2 or params.shape[-1] != 4:
        raise ValueError(f"parameters must have shape (..., N, 4); got {params.shape}")
    count = params.shape[-2]
    types = tuple("R" for _ in range(count)) if joint_types is None else tuple(item.upper() for item in joint_types)
    if len(types) != count or any(item not in ("R", "P") for item in types):
        raise ValueError("joint_types must contain exactly N entries, each 'R' or 'P'")
    q = np.zeros(params.shape[:-1], dtype=params.dtype) if joint_values is None else _float_array(joint_values)
    if q.ndim == 0 or q.shape[-1] != count:
        raise ValueError(f"joint_values must have shape (..., {count}); got {q.shape}")
    batch = np.broadcast_shapes(params.shape[:-2], q.shape[:-1])
    params = np.broadcast_to(params, batch + (count, 4))
    q = np.broadcast_to(q, batch + (count,))
    theta, d, a, alpha = np.moveaxis(params, -1, 0)
    revolute = np.asarray([item == "R" for item in types])
    theta = theta + q * revolute
    d = d + q * ~revolute
    local = dh_transform(theta, d, a, alpha)
    return compose_chain(local, return_all=return_all)


def planar_2r_fk(lengths: ArrayLike, joint_values: ArrayLike) -> NDArray[np.floating]:
    """Return base, elbow and end-effector positions for a planar 2R arm.

    Output shape is ``(..., 3, 2)``. ``q2`` is relative to link 1, so the
    absolute orientation of link 2 is ``q1 + q2``.
    """
    lengths = _float_array(lengths)
    q = _float_array(joint_values)
    if lengths.shape[-1:] != (2,):
        raise ValueError(f"lengths must have shape (..., 2); got {lengths.shape}")
    if q.shape[-1:] != (2,):
        raise ValueError(f"joint_values must have shape (..., 2); got {q.shape}")
    batch = np.broadcast_shapes(lengths.shape[:-1], q.shape[:-1])
    lengths = np.broadcast_to(lengths, batch + (2,))
    q = np.broadcast_to(q, batch + (2,))
    l1, l2 = lengths[..., 0], lengths[..., 1]
    q1, q2 = q[..., 0], q[..., 1]
    base = np.zeros(batch + (2,), dtype=np.result_type(lengths, q))
    elbow = np.stack((l1 * np.cos(q1), l1 * np.sin(q1)), axis=-1)
    end = elbow + np.stack((l2 * np.cos(q1 + q2), l2 * np.sin(q1 + q2)), axis=-1)
    return np.stack((base, elbow, end), axis=-2)


def planar_2r_jacobian(lengths: ArrayLike, joint_values: ArrayLike) -> NDArray[np.floating]:
    """Return the 2x2 position Jacobian ``dp/dq`` for a planar 2R arm."""
    lengths = _float_array(lengths)
    q = _float_array(joint_values)
    if lengths.shape[-1:] != (2,) or q.shape[-1:] != (2,):
        raise ValueError("lengths and joint_values must both end in dimension 2")
    batch = np.broadcast_shapes(lengths.shape[:-1], q.shape[:-1])
    lengths = np.broadcast_to(lengths, batch + (2,))
    q = np.broadcast_to(q, batch + (2,))
    l1, l2 = lengths[..., 0], lengths[..., 1]
    q1, q2 = q[..., 0], q[..., 1]
    s1, c1 = np.sin(q1), np.cos(q1)
    s12, c12 = np.sin(q1 + q2), np.cos(q1 + q2)
    return np.stack((
        -l1 * s1 - l2 * s12, -l2 * s12,
        l1 * c1 + l2 * c12, l2 * c12,
    ), axis=-1).reshape(batch + (2, 2))


def planar_2r_ik(
    lengths: ArrayLike, target: ArrayLike, reachability_eps: float = 1e-9
) -> tuple[NDArray[np.floating], NDArray[np.bool_]]:
    """Analytic elbow-up/down IK for planar position targets.

    Return ``(solutions, reachable)`` where solutions has shape ``(...,2,2)``:
    branch 0 has non-negative q2 and branch 1 non-positive q2. Unreachable
    targets receive NaN solutions instead of a silently clipped answer.
    """
    lengths = _float_array(lengths)
    target = _float_array(target)
    if lengths.shape[-1:] != (2,) or target.shape[-1:] != (2,):
        raise ValueError("lengths and target must both end in dimension 2")
    batch = np.broadcast_shapes(lengths.shape[:-1], target.shape[:-1])
    lengths = np.broadcast_to(lengths, batch + (2,))
    target = np.broadcast_to(target, batch + (2,))
    if np.any(lengths <= 0):
        raise ValueError("link lengths must be positive")
    l1, l2 = lengths[..., 0], lengths[..., 1]
    x, y = target[..., 0], target[..., 1]
    c2_raw = (x * x + y * y - l1 * l1 - l2 * l2) / (2.0 * l1 * l2)
    reachable = (c2_raw >= -1.0 - reachability_eps) & (c2_raw <= 1.0 + reachability_eps)
    c2 = np.clip(c2_raw, -1.0, 1.0)
    s2 = np.sqrt(np.maximum(1.0 - c2 * c2, 0.0))
    q2_positive = np.arctan2(s2, c2)
    q2_negative = np.arctan2(-s2, c2)

    def q1_for(q2: NDArray[np.floating]) -> NDArray[np.floating]:
        return np.arctan2(y, x) - np.arctan2(l2 * np.sin(q2), l1 + l2 * np.cos(q2))

    positive = np.stack((q1_for(q2_positive), q2_positive), axis=-1)
    negative = np.stack((q1_for(q2_negative), q2_negative), axis=-1)
    solutions = np.stack((positive, negative), axis=-2)
    return np.where(reachable[..., None, None], solutions, np.nan), reachable


def damped_least_squares_step(
    jacobian: ArrayLike, error: ArrayLike, damping: float = 0.05
) -> NDArray[np.floating]:
    """Compute ``J.T (J J.T + lambda^2 I)^-1 error``."""
    j = _float_array(jacobian)
    e = _float_array(error)
    if j.ndim < 2 or e.ndim == 0 or j.shape[-2] != e.shape[-1]:
        raise ValueError("jacobian must be (..., M, N) and error (..., M)")
    identity = np.eye(j.shape[-2], dtype=j.dtype)
    system = j @ np.swapaxes(j, -1, -2) + damping * damping * identity
    solved = np.linalg.solve(system, e[..., None])
    return (np.swapaxes(j, -1, -2) @ solved)[..., 0]


def within_joint_limits(joint_values: ArrayLike, lower: ArrayLike, upper: ArrayLike) -> NDArray[np.bool_]:
    q, low, high = np.broadcast_arrays(_float_array(joint_values), _float_array(lower), _float_array(upper))
    if q.shape[-1:] == ():
        raise ValueError("joint values must have a joint dimension")
    return np.all((q >= low) & (q <= high), axis=-1)


def planar_2r_ik_dls(
    lengths: ArrayLike,
    target: ArrayLike,
    initial: ArrayLike,
    *,
    damping: float = 0.05,
    step_size: float = 1.0,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
    joint_limits: tuple[ArrayLike, ArrayLike] | None = None,
) -> tuple[NDArray[np.floating], NDArray[np.bool_], NDArray[np.floating]]:
    """Iteratively solve planar 2R position IK with damped least squares."""
    lengths = _float_array(lengths)
    target = _float_array(target)
    q = _float_array(initial).copy()
    if lengths.shape[-1:] != (2,) or target.shape[-1:] != (2,) or q.shape[-1:] != (2,):
        raise ValueError("lengths, target and initial must all end in dimension 2")
    batch = np.broadcast_shapes(lengths.shape[:-1], target.shape[:-1], q.shape[:-1])
    lengths = np.broadcast_to(lengths, batch + (2,))
    target = np.broadcast_to(target, batch + (2,))
    q = np.broadcast_to(q, batch + (2,)).copy()
    if joint_limits is not None:
        lower = np.broadcast_to(_float_array(joint_limits[0]), batch + (2,))
        upper = np.broadcast_to(_float_array(joint_limits[1]), batch + (2,))
        if np.any(lower > upper):
            raise ValueError("joint lower limits must not exceed upper limits")
    for _ in range(max_iterations):
        position = planar_2r_fk(lengths, q)[..., -1, :]
        error = target - position
        if np.all(np.linalg.norm(error, axis=-1) <= tolerance):
            break
        q += step_size * damped_least_squares_step(planar_2r_jacobian(lengths, q), error, damping)
        if joint_limits is not None:
            q = np.clip(q, lower, upper)
    final_error = np.linalg.norm(target - planar_2r_fk(lengths, q)[..., -1, :], axis=-1)
    return q, final_error <= tolerance, final_error
