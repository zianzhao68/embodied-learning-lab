"""NumPy pinhole-camera geometry using OpenCV optical-frame conventions."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _float_array(value: ArrayLike) -> NDArray[np.floating]:
    array = np.asarray(value)
    if not np.issubdtype(array.dtype, np.floating):
        array = array.astype(np.float64)
    return array


def make_intrinsics(fx: Any, fy: Any, cx: Any, cy: Any) -> NDArray[np.floating]:
    """Build camera intrinsic matrices with shape ``(..., 3, 3)``."""
    fx, fy, cx, cy = np.broadcast_arrays(*[_float_array(v) for v in (fx, fy, cx, cy)])
    if np.any(fx <= 0) or np.any(fy <= 0):
        raise ValueError("fx and fy must be positive")
    zeros = np.zeros_like(fx)
    ones = np.ones_like(fx)
    return np.stack((fx, zeros, cx, zeros, fy, cy, zeros, zeros, ones), axis=-1).reshape(fx.shape + (3, 3))


def _intrinsic_parameters(intrinsics: ArrayLike, point_batch_ndim: int) -> tuple[NDArray, NDArray, NDArray, NDArray]:
    k = _float_array(intrinsics)
    if k.shape[-2:] != (3, 3):
        raise ValueError(f"intrinsics must have shape (..., 3, 3); got {k.shape}")
    if len(k.shape[:-2]) > point_batch_ndim:
        raise ValueError("intrinsic batch dimensions must be present in the point/pixel batch")
    if np.any(k[..., 0, 0] <= 0) or np.any(k[..., 1, 1] <= 0):
        raise ValueError("fx and fy must be positive")
    if not np.allclose(k[..., 2, :], np.array([0.0, 0.0, 1.0])):
        raise ValueError("intrinsics bottom row must be [0, 0, 1]")
    extra = point_batch_ndim - len(k.shape[:-2])
    shape = k.shape[:-2] + (1,) * extra
    return tuple(k[..., row, col].reshape(shape) for row, col in ((0, 0), (1, 1), (0, 2), (1, 2)))  # type: ignore[return-value]


def project_points(
    points_camera: ArrayLike, intrinsics: ArrayLike, *, min_depth: float = 1e-8
) -> tuple[NDArray[np.floating], NDArray[np.bool_]]:
    """Project camera-frame points to pixels.

    Camera convention: x right, y down, z forward. Points at or behind the
    camera receive NaN pixels and ``valid=False``.
    """
    points = _float_array(points_camera)
    if points.shape[-1:] != (3,):
        raise ValueError(f"points_camera must have shape (..., 3); got {points.shape}")
    fx, fy, cx, cy = _intrinsic_parameters(intrinsics, points.ndim - 1)
    x, y, z = np.moveaxis(points, -1, 0)
    valid = np.isfinite(points).all(axis=-1) & (z > min_depth)
    safe_z = np.where(valid, z, 1.0)
    u = fx * x / safe_z + cx
    v = fy * y / safe_z + cy
    pixels = np.stack((u, v), axis=-1)
    return np.where(valid[..., None], pixels, np.nan), valid


def unproject_pixels(
    pixels: ArrayLike, depth: ArrayLike, intrinsics: ArrayLike, *, min_depth: float = 1e-8
) -> tuple[NDArray[np.floating], NDArray[np.bool_]]:
    """Back-project pixels plus metric z-depth to camera-frame 3D points."""
    pixels = _float_array(pixels)
    depth = _float_array(depth)
    if pixels.shape[-1:] != (2,):
        raise ValueError(f"pixels must have shape (..., 2); got {pixels.shape}")
    try:
        batch = np.broadcast_shapes(pixels.shape[:-1], depth.shape)
    except ValueError as exc:
        raise ValueError("depth must broadcast with the pixel batch") from exc
    pixels = np.broadcast_to(pixels, batch + (2,))
    depth = np.broadcast_to(depth, batch)
    fx, fy, cx, cy = _intrinsic_parameters(intrinsics, len(batch))
    u, v = np.moveaxis(pixels, -1, 0)
    valid = np.isfinite(pixels).all(axis=-1) & np.isfinite(depth) & (depth > min_depth)
    x = (u - cx) * depth / fx
    y = (v - cy) * depth / fy
    points = np.stack((x, y, depth), axis=-1)
    return np.where(valid[..., None], points, np.nan), valid


def pixel_rays(pixels: ArrayLike, intrinsics: ArrayLike, *, unit: bool = False) -> NDArray[np.floating]:
    """Return camera rays ``[(u-cx)/fx, (v-cy)/fy, 1]``."""
    pixels = _float_array(pixels)
    if pixels.shape[-1:] != (2,):
        raise ValueError(f"pixels must have shape (..., 2); got {pixels.shape}")
    fx, fy, cx, cy = _intrinsic_parameters(intrinsics, pixels.ndim - 1)
    u, v = np.moveaxis(pixels, -1, 0)
    rays = np.stack(((u - cx) / fx, (v - cy) / fy, np.ones(np.broadcast_shapes(u.shape, fx.shape))), axis=-1)
    if unit:
        rays = rays / np.linalg.norm(rays, axis=-1, keepdims=True)
    return rays


def transform_points(points: ArrayLike, transform: ArrayLike) -> NDArray[np.floating]:
    """Apply ``p_out = R p_in + t`` with prefix-aligned transform batches."""
    points = _float_array(points)
    transform = _float_array(transform)
    if points.shape[-1:] != (3,) or transform.shape[-2:] != (4, 4):
        raise ValueError("points must be (..., 3) and transform (..., 4, 4)")
    transform_batch = transform.shape[:-2]
    point_batch = points.shape[:-1]
    if len(transform_batch) > len(point_batch):
        raise ValueError("transform batch dimensions must be present in the point batch")
    extra = len(point_batch) - len(transform_batch)
    rotation = transform[..., :3, :3].reshape(transform_batch + (1,) * extra + (3, 3))
    translation = transform[..., :3, 3].reshape(transform_batch + (1,) * extra + (3,))
    return (rotation @ points[..., None])[..., 0] + translation


def project_world_points(
    points_world: ArrayLike,
    transform_camera_world: ArrayLike,
    intrinsics: ArrayLike,
    *,
    min_depth: float = 1e-8,
) -> tuple[NDArray[np.floating], NDArray[np.bool_]]:
    """Transform world points into the camera frame, then project to pixels."""
    points_camera = transform_points(points_world, transform_camera_world)
    return project_points(points_camera, intrinsics, min_depth=min_depth)


def focal_length_from_fov(image_extent_px: ArrayLike, field_of_view_rad: ArrayLike) -> NDArray[np.floating]:
    """Convert horizontal or vertical field of view to focal length in pixels."""
    extent, fov = np.broadcast_arrays(_float_array(image_extent_px), _float_array(field_of_view_rad))
    if np.any(extent <= 0) or np.any(fov <= 0) or np.any(fov >= np.pi):
        raise ValueError("image extent must be positive and field of view must be in (0, pi)")
    return 0.5 * extent / np.tan(0.5 * fov)
