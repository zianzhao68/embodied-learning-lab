"""Batched NumPy utilities for rigid transforms in SE(3).

A transform ``T_A_B`` maps coordinates from frame B to frame A and has block
form ``[[R_A_B, t_A_B], [0, 1]]``. Points use homogeneous weight 1;
directions use weight 0 and therefore ignore translation.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from . import numpy as so3


def _float_array(value: ArrayLike) -> NDArray[np.floating]:
    array = np.asarray(value)
    if not np.issubdtype(array.dtype, np.floating):
        array = array.astype(np.float64)
    return array


def _check_transform(transform: NDArray, name: str = "transform") -> None:
    if transform.ndim < 2 or transform.shape[-2:] != (4, 4):
        raise ValueError(f"{name} must have shape (..., 4, 4); got {transform.shape}")


def make_transform(rotation: ArrayLike, translation: ArrayLike) -> NDArray[np.floating]:
    """Build ``[...,4,4]`` transforms from broadcastable rotations/translations."""
    r = _float_array(rotation)
    t = _float_array(translation)
    if r.ndim < 2 or r.shape[-2:] != (3, 3):
        raise ValueError(f"rotation must have shape (..., 3, 3); got {r.shape}")
    if t.ndim == 0 or t.shape[-1] != 3:
        raise ValueError(f"translation must have shape (..., 3); got {t.shape}")
    batch = np.broadcast_shapes(r.shape[:-2], t.shape[:-1])
    r = np.broadcast_to(r, batch + (3, 3))
    t = np.broadcast_to(t, batch + (3,))
    result = np.zeros(batch + (4, 4), dtype=np.result_type(r, t))
    result[..., :3, :3] = r
    result[..., :3, 3] = t
    result[..., 3, 3] = 1.0
    return result


def split_transform(transform: ArrayLike) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
    t = _float_array(transform)
    _check_transform(t)
    return t[..., :3, :3], t[..., :3, 3]


def transform_points(transform: ArrayLike, points: ArrayLike) -> NDArray[np.floating]:
    """Apply ``R p + t`` to point coordinates with broadcast batch dimensions."""
    t = _float_array(transform)
    p = _float_array(points)
    _check_transform(t)
    if p.ndim == 0 or p.shape[-1] != 3:
        raise ValueError(f"points must have shape (..., 3); got {p.shape}")
    rotation, translation = split_transform(t)
    return np.einsum("...ij,...j->...i", rotation, p) + translation


def transform_directions(transform: ArrayLike, directions: ArrayLike) -> NDArray[np.floating]:
    """Rotate free vectors; translation is intentionally ignored."""
    t = _float_array(transform)
    direction = _float_array(directions)
    _check_transform(t)
    if direction.ndim == 0 or direction.shape[-1] != 3:
        raise ValueError(f"directions must have shape (..., 3); got {direction.shape}")
    return np.einsum("...ij,...j->...i", t[..., :3, :3], direction)


def compose_transforms(left: ArrayLike, right: ArrayLike) -> NDArray[np.floating]:
    """Compose transforms; the right transform acts first."""
    a = _float_array(left)
    b = _float_array(right)
    _check_transform(a, "left")
    _check_transform(b, "right")
    return a @ b


def inverse_transform(transform: ArrayLike) -> NDArray[np.floating]:
    """Analytic rigid inverse ``[R.T, -R.T t; 0, 1]``."""
    t = _float_array(transform)
    _check_transform(t)
    rotation, translation = split_transform(t)
    rotation_t = np.swapaxes(rotation, -1, -2)
    inverse_translation = -np.einsum("...ij,...j->...i", rotation_t, translation)
    return make_transform(rotation_t, inverse_translation)


def relative_transform(reference_pose: ArrayLike, target_pose: ArrayLike) -> NDArray[np.floating]:
    """Return target pose expressed in the reference frame.

    If inputs are ``T_W_A`` and ``T_W_B``, output is ``T_A_B``.
    """
    return compose_transforms(inverse_transform(reference_pose), target_pose)


def quaternion_translation_to_transform(quaternion: ArrayLike, translation: ArrayLike) -> NDArray[np.floating]:
    return make_transform(so3.quaternion_to_matrix(quaternion), translation)


def transform_error(transform: ArrayLike) -> tuple[NDArray[np.floating], NDArray[np.floating], NDArray[np.floating]]:
    """Return SO(3) orthogonality, determinant, and homogeneous-row errors."""
    t = _float_array(transform)
    _check_transform(t)
    orthogonality, determinant = so3.rotation_matrix_error(t[..., :3, :3])
    expected = np.array([0.0, 0.0, 0.0, 1.0], dtype=t.dtype)
    bottom_row = np.linalg.norm(t[..., 3, :] - expected, axis=-1)
    return orthogonality, determinant, bottom_row


def project_to_se3(transform: ArrayLike) -> NDArray[np.floating]:
    """Project the rotation block to SO(3), retain translation, fix bottom row."""
    t = _float_array(transform)
    _check_transform(t)
    return make_transform(so3.project_to_so3(t[..., :3, :3]), t[..., :3, 3])
