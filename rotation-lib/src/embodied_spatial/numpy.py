"""Batched NumPy rotation utilities.

Conventions:
- active, right-handed rotations acting on column vectors;
- quaternions use scalar-first ``(w, x, y, z)`` order;
- Euler vectors use ZYX ``(yaw, pitch, roll)`` order in radians;
- axis-angle is represented as a rotation vector ``axis * angle``.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

_EPS = 1e-8
_SMALL = 1e-4


def _float_array(value: ArrayLike) -> NDArray[np.floating]:
    array = np.asarray(value)
    if not np.issubdtype(array.dtype, np.floating):
        array = array.astype(np.float64)
    return array


def _check_last_dim(value: NDArray, size: int, name: str) -> None:
    if value.ndim == 0 or value.shape[-1] != size:
        raise ValueError(f"{name} must have shape (..., {size}); got {value.shape}")


def _check_matrix(value: NDArray, name: str = "matrix") -> None:
    if value.ndim < 2 or value.shape[-2:] != (3, 3):
        raise ValueError(f"{name} must have shape (..., 3, 3); got {value.shape}")


def normalize_quaternion(quaternion: ArrayLike, eps: float = _EPS) -> NDArray[np.floating]:
    """Normalize scalar-first quaternions and reject zero-norm inputs."""
    q = _float_array(quaternion)
    _check_last_dim(q, 4, "quaternion")
    norm = np.linalg.norm(q, axis=-1, keepdims=True)
    if np.any(norm <= eps):
        raise ValueError("quaternion norm must be greater than zero")
    return q / norm


def quaternion_to_matrix(quaternion: ArrayLike) -> NDArray[np.floating]:
    """Convert scalar-first quaternions to active rotation matrices."""
    q = normalize_quaternion(quaternion)
    w, x, y, z = np.moveaxis(q, -1, 0)
    two = 2.0
    rows = (
        1 - two * (y * y + z * z), two * (x * y - w * z), two * (x * z + w * y),
        two * (x * y + w * z), 1 - two * (x * x + z * z), two * (y * z - w * x),
        two * (x * z - w * y), two * (y * z + w * x), 1 - two * (x * x + y * y),
    )
    return np.stack(rows, axis=-1).reshape(q.shape[:-1] + (3, 3))


def matrix_to_quaternion(matrix: ArrayLike) -> NDArray[np.floating]:
    """Convert rotation matrices to canonical scalar-first quaternions.

    The returned representative has ``w >= 0``. Near a 180-degree rotation,
    either axis sign is valid because quaternions double-cover SO(3).
    """
    m = _float_array(matrix)
    _check_matrix(m)
    m00, m01, m02 = m[..., 0, 0], m[..., 0, 1], m[..., 0, 2]
    m10, m11, m12 = m[..., 1, 0], m[..., 1, 1], m[..., 1, 2]
    m20, m21, m22 = m[..., 2, 0], m[..., 2, 1], m[..., 2, 2]

    q_abs = np.sqrt(np.maximum(np.stack((
        1 + m00 + m11 + m22,
        1 + m00 - m11 - m22,
        1 - m00 + m11 - m22,
        1 - m00 - m11 + m22,
    ), axis=-1), 0.0))

    candidates = np.stack((
        np.stack((q_abs[..., 0] ** 2, m21 - m12, m02 - m20, m10 - m01), axis=-1),
        np.stack((m21 - m12, q_abs[..., 1] ** 2, m10 + m01, m02 + m20), axis=-1),
        np.stack((m02 - m20, m10 + m01, q_abs[..., 2] ** 2, m12 + m21), axis=-1),
        np.stack((m10 - m01, m20 + m02, m21 + m12, q_abs[..., 3] ** 2), axis=-1),
    ), axis=-2)
    candidates /= 2.0 * np.maximum(q_abs[..., :, None], 0.1)
    index = np.argmax(q_abs, axis=-1)
    q = np.take_along_axis(candidates, index[..., None, None], axis=-2)[..., 0, :]
    q = normalize_quaternion(q)
    return np.where(q[..., :1] < 0, -q, q)


def axis_angle_to_quaternion(rotation_vector: ArrayLike) -> NDArray[np.floating]:
    """Convert rotation vectors ``axis * angle`` to quaternions."""
    vector = _float_array(rotation_vector)
    _check_last_dim(vector, 3, "rotation_vector")
    angle = np.linalg.norm(vector, axis=-1, keepdims=True)
    angle2 = angle * angle
    scale = np.empty_like(angle)
    np.divide(np.sin(0.5 * angle), angle, out=scale, where=angle >= _SMALL)
    scale = np.where(angle < _SMALL, 0.5 - angle2 / 48.0 + angle2 * angle2 / 3840.0, scale)
    return np.concatenate((np.cos(0.5 * angle), vector * scale), axis=-1)


def quaternion_to_axis_angle(quaternion: ArrayLike) -> NDArray[np.floating]:
    """Return the principal rotation vector with angle in ``[0, pi]``."""
    q = normalize_quaternion(quaternion)
    q = np.where(q[..., :1] < 0, -q, q)
    xyz = q[..., 1:]
    sin_half = np.linalg.norm(xyz, axis=-1, keepdims=True)
    angle = 2.0 * np.arctan2(sin_half, np.clip(q[..., :1], 0.0, 1.0))
    scale = np.empty_like(angle)
    np.divide(angle, sin_half, out=scale, where=sin_half >= _SMALL)
    scale = np.where(sin_half < _SMALL, 2.0 + sin_half * sin_half / 3.0, scale)
    return xyz * scale


def axis_angle_to_matrix(rotation_vector: ArrayLike) -> NDArray[np.floating]:
    """Convert rotation vectors to matrices through stable unit quaternions."""
    return quaternion_to_matrix(axis_angle_to_quaternion(rotation_vector))


def matrix_to_axis_angle(matrix: ArrayLike) -> NDArray[np.floating]:
    """Convert matrices to principal rotation vectors."""
    return quaternion_to_axis_angle(matrix_to_quaternion(matrix))


def euler_zyx_to_matrix(euler: ArrayLike) -> NDArray[np.floating]:
    """Convert ``(yaw, pitch, roll)`` to ``Rz(yaw) @ Ry(pitch) @ Rx(roll)``."""
    angles = _float_array(euler)
    _check_last_dim(angles, 3, "euler")
    yaw, pitch, roll = np.moveaxis(angles, -1, 0)
    cy, sy = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cr, sr = np.cos(roll), np.sin(roll)
    rows = (
        cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr,
        sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr,
        -sp, cp * sr, cp * cr,
    )
    return np.stack(rows, axis=-1).reshape(angles.shape[:-1] + (3, 3))


def matrix_to_euler_zyx(matrix: ArrayLike, singular_eps: float = 1e-7) -> NDArray[np.floating]:
    """Convert matrices to one valid ZYX Euler solution.

    Away from gimbal lock, pitch lies in ``[-pi/2, pi/2]``. At pitch
    ``+/-pi/2`` yaw and roll are not separately observable; this function
    deterministically sets roll to zero and stores the observable combination
    in yaw.
    """
    m = _float_array(matrix)
    _check_matrix(m)
    pitch = np.arcsin(np.clip(-m[..., 2, 0], -1.0, 1.0))
    cos_pitch = np.cos(pitch)
    regular = np.abs(cos_pitch) > singular_eps
    yaw_regular = np.arctan2(m[..., 1, 0], m[..., 0, 0])
    roll_regular = np.arctan2(m[..., 2, 1], m[..., 2, 2])
    yaw_singular = np.arctan2(-m[..., 0, 1], m[..., 1, 1])
    yaw = np.where(regular, yaw_regular, yaw_singular)
    roll = np.where(regular, roll_regular, 0.0)
    return np.stack((yaw, pitch, roll), axis=-1)


def quaternion_multiply(left: ArrayLike, right: ArrayLike) -> NDArray[np.floating]:
    """Hamilton product; ``q_left * q_right`` applies right, then left."""
    q1 = normalize_quaternion(left)
    q2 = normalize_quaternion(right)
    w1, x1, y1, z1 = np.moveaxis(q1, -1, 0)
    w2, x2, y2, z2 = np.moveaxis(q2, -1, 0)
    return normalize_quaternion(np.stack((
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
    ), axis=-1))


def quaternion_slerp(start: ArrayLike, end: ArrayLike, t: ArrayLike) -> NDArray[np.floating]:
    """Shortest-path spherical interpolation between unit quaternions."""
    q0 = normalize_quaternion(start)
    q1 = normalize_quaternion(end)
    dot = np.sum(q0 * q1, axis=-1)
    q1 = np.where((dot < 0)[..., None], -q1, q1)
    dot = np.clip(np.abs(dot), 0.0, 1.0)
    amount, dot = np.broadcast_arrays(_float_array(t), dot)
    theta = np.arccos(dot)
    sin_theta = np.sin(theta)
    safe = np.where(sin_theta > 1e-6, sin_theta, 1.0)
    w0 = np.sin((1.0 - amount) * theta) / safe
    w1 = np.sin(amount * theta) / safe
    spherical = w0[..., None] * q0 + w1[..., None] * q1
    linear = (1.0 - amount)[..., None] * q0 + amount[..., None] * q1
    result = np.where((sin_theta > 1e-6)[..., None], spherical, linear)
    return normalize_quaternion(result)


def rotate_vectors(matrix: ArrayLike, vectors: ArrayLike) -> NDArray[np.floating]:
    """Apply active rotation matrices to column-vector data."""
    rotation = _float_array(matrix)
    vector = _float_array(vectors)
    _check_matrix(rotation)
    _check_last_dim(vector, 3, "vectors")
    return np.einsum("...ij,...j->...i", rotation, vector)


def project_to_so3(matrix: ArrayLike) -> NDArray[np.floating]:
    """Project noisy 3x3 matrices to the nearest proper rotation via SVD."""
    m = _float_array(matrix)
    _check_matrix(m)
    u, _, vh = np.linalg.svd(m)
    correction = np.ones(m.shape[:-2] + (3,), dtype=m.dtype)
    correction[..., -1] = np.where(np.linalg.det(u @ vh) < 0, -1.0, 1.0)
    return (u * correction[..., None, :]) @ vh


def rotation_matrix_error(matrix: ArrayLike) -> tuple[NDArray[np.floating], NDArray[np.floating]]:
    """Return Frobenius orthogonality error and determinant error ``|det-1|``."""
    m = _float_array(matrix)
    _check_matrix(m)
    identity = np.eye(3, dtype=m.dtype)
    orthogonality = np.linalg.norm(np.swapaxes(m, -1, -2) @ m - identity, axis=(-2, -1))
    determinant = np.abs(np.linalg.det(m) - 1.0)
    return orthogonality, determinant
