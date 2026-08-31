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
