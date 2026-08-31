"""Differentiable PyTorch pinhole-camera geometry."""

from __future__ import annotations

import torch
from torch import Tensor


def _float_tensor(value: Tensor) -> Tensor:
    if not isinstance(value, Tensor):
        value = torch.as_tensor(value)
    if not value.is_floating_point():
        value = value.to(torch.get_default_dtype())
    return value


def make_intrinsics(fx: Tensor, fy: Tensor, cx: Tensor, cy: Tensor) -> Tensor:
    values = [_float_tensor(v) for v in (fx, fy, cx, cy)]
    device, dtype = values[0].device, values[0].dtype
    fx, fy, cx, cy = torch.broadcast_tensors(*[v.to(device=device, dtype=dtype) for v in values])
    if torch.any(fx <= 0).item() or torch.any(fy <= 0).item():
        raise ValueError("fx and fy must be positive")
    zeros, ones = torch.zeros_like(fx), torch.ones_like(fx)
    return torch.stack((fx, zeros, cx, zeros, fy, cy, zeros, zeros, ones), dim=-1).reshape(fx.shape + (3, 3))


def _intrinsic_parameters(intrinsics: Tensor, point_batch_ndim: int) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    k = _float_tensor(intrinsics)
    if k.shape[-2:] != (3, 3):
        raise ValueError(f"intrinsics must have shape (..., 3, 3); got {tuple(k.shape)}")
    if len(k.shape[:-2]) > point_batch_ndim:
        raise ValueError("intrinsic batch dimensions must be present in the point/pixel batch")
    if torch.any(k[..., 0, 0] <= 0).item() or torch.any(k[..., 1, 1] <= 0).item():
        raise ValueError("fx and fy must be positive")
    expected = torch.tensor([0.0, 0.0, 1.0], dtype=k.dtype, device=k.device)
    if not torch.allclose(k[..., 2, :], expected.expand_as(k[..., 2, :])):
        raise ValueError("intrinsics bottom row must be [0, 0, 1]")
    extra = point_batch_ndim - len(k.shape[:-2])
    shape = k.shape[:-2] + (1,) * extra
    return tuple(k[..., row, col].reshape(shape) for row, col in ((0, 0), (1, 1), (0, 2), (1, 2)))  # type: ignore[return-value]


def project_points(points_camera: Tensor, intrinsics: Tensor, *, min_depth: float = 1e-8) -> tuple[Tensor, Tensor]:
    points = _float_tensor(points_camera)
    if points.shape[-1:] != (3,):
        raise ValueError(f"points_camera must have shape (..., 3); got {tuple(points.shape)}")
    k = _float_tensor(intrinsics).to(device=points.device, dtype=points.dtype)
    fx, fy, cx, cy = _intrinsic_parameters(k, points.ndim - 1)
    x, y, z = points.unbind(dim=-1)
    valid = torch.isfinite(points).all(dim=-1) & (z > min_depth)
    safe_z = torch.where(valid, z, torch.ones_like(z))
    pixels = torch.stack((fx * x / safe_z + cx, fy * y / safe_z + cy), dim=-1)
    return torch.where(valid[..., None], pixels, torch.full_like(pixels, torch.nan)), valid


def unproject_pixels(
    pixels: Tensor, depth: Tensor, intrinsics: Tensor, *, min_depth: float = 1e-8
) -> tuple[Tensor, Tensor]:
    pixels = _float_tensor(pixels)
    depth = _float_tensor(depth).to(device=pixels.device, dtype=pixels.dtype)
    if pixels.shape[-1:] != (2,):
        raise ValueError(f"pixels must have shape (..., 2); got {tuple(pixels.shape)}")
    try:
        batch = torch.broadcast_shapes(pixels.shape[:-1], depth.shape)
    except RuntimeError as exc:
        raise ValueError("depth must broadcast with the pixel batch") from exc
    pixels = torch.broadcast_to(pixels, batch + (2,))
    depth = torch.broadcast_to(depth, batch)
    k = _float_tensor(intrinsics).to(device=pixels.device, dtype=pixels.dtype)
    fx, fy, cx, cy = _intrinsic_parameters(k, len(batch))
    u, v = pixels.unbind(dim=-1)
    valid = torch.isfinite(pixels).all(dim=-1) & torch.isfinite(depth) & (depth > min_depth)
    points = torch.stack(((u - cx) * depth / fx, (v - cy) * depth / fy, depth), dim=-1)
    return torch.where(valid[..., None], points, torch.full_like(points, torch.nan)), valid


def pixel_rays(pixels: Tensor, intrinsics: Tensor, *, unit: bool = False) -> Tensor:
    pixels = _float_tensor(pixels)
    if pixels.shape[-1:] != (2,):
        raise ValueError(f"pixels must have shape (..., 2); got {tuple(pixels.shape)}")
    k = _float_tensor(intrinsics).to(device=pixels.device, dtype=pixels.dtype)
    fx, fy, cx, cy = _intrinsic_parameters(k, pixels.ndim - 1)
    u, v = pixels.unbind(dim=-1)
    x, y = (u - cx) / fx, (v - cy) / fy
    rays = torch.stack(torch.broadcast_tensors(x, y, torch.ones_like(x)), dim=-1)
    if unit:
        rays = rays / torch.linalg.vector_norm(rays, dim=-1, keepdim=True)
    return rays


def transform_points(points: Tensor, transform: Tensor) -> Tensor:
    points = _float_tensor(points)
    transform = _float_tensor(transform).to(device=points.device, dtype=points.dtype)
    if points.shape[-1:] != (3,) or transform.shape[-2:] != (4, 4):
        raise ValueError("points must be (..., 3) and transform (..., 4, 4)")
    transform_batch, point_batch = transform.shape[:-2], points.shape[:-1]
    if len(transform_batch) > len(point_batch):
        raise ValueError("transform batch dimensions must be present in the point batch")
    extra = len(point_batch) - len(transform_batch)
    rotation = transform[..., :3, :3].reshape(transform_batch + (1,) * extra + (3, 3))
    translation = transform[..., :3, 3].reshape(transform_batch + (1,) * extra + (3,))
    return (rotation @ points.unsqueeze(-1)).squeeze(-1) + translation


def project_world_points(
    points_world: Tensor,
    transform_camera_world: Tensor,
    intrinsics: Tensor,
    *,
    min_depth: float = 1e-8,
) -> tuple[Tensor, Tensor]:
    points_camera = transform_points(points_world, transform_camera_world)
    return project_points(points_camera, intrinsics, min_depth=min_depth)


def focal_length_from_fov(image_extent_px: Tensor, field_of_view_rad: Tensor) -> Tensor:
    values = [_float_tensor(v) for v in (image_extent_px, field_of_view_rad)]
    extent, fov = torch.broadcast_tensors(values[0], values[1].to(values[0]))
    if torch.any(extent <= 0).item() or torch.any(fov <= 0).item() or torch.any(fov >= torch.pi).item():
        raise ValueError("image extent must be positive and field of view must be in (0, pi)")
    return 0.5 * extent / torch.tan(0.5 * fov)
