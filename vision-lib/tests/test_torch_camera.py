import unittest

import numpy as np
import torch

from embodied_vision import numpy as np_cam
from embodied_vision import torch as th_cam


@unittest.skipIf(th_cam is None, "PyTorch is not installed")
class TestTorchCamera(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(20260901)
        self.dtype = torch.float64
        self.k = th_cam.make_intrinsics(
            torch.tensor(500.0, dtype=self.dtype),
            torch.tensor(500.0, dtype=self.dtype),
            torch.tensor(320.0, dtype=self.dtype),
            torch.tensor(240.0, dtype=self.dtype),
        )

    def test_numpy_torch_projection_parity(self) -> None:
        points = torch.randn(1024, 3, dtype=self.dtype)
        points[:, 2] = points[:, 2].abs() + 0.1
        th_pixels, th_valid = th_cam.project_points(points, self.k)
        np_pixels, np_valid = np_cam.project_points(points.numpy(), self.k.numpy())
        np.testing.assert_allclose(th_pixels.numpy(), np_pixels, atol=1e-12)
        np.testing.assert_array_equal(th_valid.numpy(), np_valid)

    def test_projection_is_differentiable(self) -> None:
        point = torch.tensor([0.1, 0.05, 1.0], dtype=self.dtype, requires_grad=True)
        pixel, valid = th_cam.project_points(point, self.k)
        self.assertTrue(valid.item())
        pixel.sum().backward()
        expected = torch.tensor([500.0, 500.0, -75.0], dtype=self.dtype)
        torch.testing.assert_close(point.grad, expected, atol=1e-12, rtol=1e-12)

    def test_round_trip_and_unit_rays(self) -> None:
        points = torch.rand(512, 3, dtype=self.dtype)
        points[:, :2] -= 0.5
        points[:, 2] += 0.2
        pixels, valid = th_cam.project_points(points, self.k)
        reconstructed, depth_valid = th_cam.unproject_pixels(pixels, points[:, 2], self.k)
        self.assertTrue((valid & depth_valid).all().item())
        torch.testing.assert_close(reconstructed, points, atol=1e-12, rtol=1e-12)
        rays = th_cam.pixel_rays(pixels, self.k, unit=True)
        torch.testing.assert_close(torch.linalg.vector_norm(rays, dim=-1), torch.ones(512, dtype=self.dtype))

    def test_invalid_depth_and_shapes(self) -> None:
        pixels, valid = th_cam.project_points(torch.tensor([[0.0, 0.0, 0.0]], dtype=self.dtype), self.k)
        self.assertFalse(valid.item())
        self.assertTrue(torch.isnan(pixels).all().item())
        with self.assertRaises(ValueError):
            th_cam.project_points(torch.ones(2), self.k)
        with self.assertRaises(ValueError):
            th_cam.make_intrinsics(torch.tensor(-1.0), torch.tensor(1.0), torch.tensor(0.0), torch.tensor(0.0))

    def test_batched_transform_and_projection(self) -> None:
        transforms = torch.eye(4, dtype=self.dtype).repeat(2, 1, 1)
        transforms[0, 0, 3] = -1.0
        transforms[1, 1, 3] = -1.0
        points = torch.tensor([[[1.0, 0.0, 2.0]], [[0.0, 1.0, 2.0]]], dtype=self.dtype)
        camera_points = th_cam.transform_points(points, transforms)
        torch.testing.assert_close(camera_points, torch.tensor([[[0.0, 0.0, 2.0]], [[0.0, 0.0, 2.0]]], dtype=self.dtype))
        pixels, valid = th_cam.project_world_points(points, transforms, self.k)
        self.assertTrue(valid.all().item())
        torch.testing.assert_close(pixels, torch.tensor([[[320.0, 240.0]], [[320.0, 240.0]]], dtype=self.dtype))

    def test_fov_gradient_and_dtype(self) -> None:
        fov = torch.tensor(torch.pi / 2, dtype=self.dtype, requires_grad=True)
        focal = th_cam.focal_length_from_fov(torch.tensor(640.0, dtype=self.dtype), fov)
        self.assertEqual(focal.dtype, self.dtype)
        self.assertAlmostEqual(focal.item(), 320.0)
        focal.backward()
        self.assertTrue(torch.isfinite(fov.grad).item())


if __name__ == "__main__":
    unittest.main()
