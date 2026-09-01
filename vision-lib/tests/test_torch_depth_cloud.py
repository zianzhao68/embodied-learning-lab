import unittest

import numpy as np
import torch

from embodied_vision import numpy as np_cam
from embodied_vision import torch as th_cam


@unittest.skipIf(th_cam is None, "PyTorch is not installed")
class TestTorchDepthCloud(unittest.TestCase):
    def setUp(self) -> None:
        self.dtype = torch.float64
        self.k = th_cam.make_intrinsics(
            torch.tensor(2.0, dtype=self.dtype), torch.tensor(2.0, dtype=self.dtype),
            torch.tensor(1.0, dtype=self.dtype), torch.tensor(1.0, dtype=self.dtype),
        )

    def test_numpy_torch_parity(self) -> None:
        depth = torch.rand(3, 4, 5, dtype=self.dtype) * 2.0 + 0.1
        th_points, th_valid = th_cam.depth_image_to_points(depth, self.k, flatten=True)
        np_points, np_valid = np_cam.depth_image_to_points(depth.numpy(), self.k.numpy(), flatten=True)
        np.testing.assert_allclose(th_points.numpy(), np_points, atol=1e-12)
        np.testing.assert_array_equal(th_valid.numpy(), np_valid)

    def test_depth_unprojection_is_differentiable(self) -> None:
        depth = torch.ones(3, 3, dtype=self.dtype, requires_grad=True)
        points, valid = th_cam.depth_image_to_points(depth, self.k)
        self.assertTrue(valid.all().item())
        points.square().sum().backward()
        self.assertTrue(torch.isfinite(depth.grad).all().item())
        self.assertGreater(depth.grad.abs().sum().item(), 0.0)

    def test_hand_calculation_and_flatten(self) -> None:
        depth = torch.tensor([[1.0, 1.0, 1.0], [1.0, 2.0, 1.0], [1.0, 1.0, 1.0]], dtype=self.dtype)
        points, valid = th_cam.depth_image_to_points(depth, self.k, flatten=True)
        self.assertEqual(tuple(points.shape), (9, 3))
        self.assertTrue(valid.all().item())
        torch.testing.assert_close(points[4], torch.tensor([0.0, 0.0, 2.0], dtype=self.dtype))
        torch.testing.assert_close(points[5], torch.tensor([0.5, 0.0, 1.0], dtype=self.dtype))

    def test_range_points_have_requested_euclidean_norm(self) -> None:
        distance = torch.full((3, 3), 2.0, dtype=self.dtype)
        points, valid = th_cam.range_image_to_points(distance, self.k)
        self.assertTrue(valid.all().item())
        torch.testing.assert_close(torch.linalg.vector_norm(points, dim=-1), distance)
        self.assertLess(points[0, 0, 2].item(), 2.0)

    def test_resize_and_crop_numpy_parity(self) -> None:
        k = th_cam.make_intrinsics(
            torch.tensor(500.0, dtype=self.dtype), torch.tensor(520.0, dtype=self.dtype),
            torch.tensor(320.0, dtype=self.dtype), torch.tensor(240.0, dtype=self.dtype),
        )
        th_resized = th_cam.rescale_intrinsics(k, torch.tensor(0.5), torch.tensor(0.25))
        np_resized = np_cam.rescale_intrinsics(k.numpy(), 0.5, 0.25)
        np.testing.assert_allclose(th_resized.numpy(), np_resized)
        th_cropped = th_cam.crop_intrinsics(k, torch.tensor(100.0), torch.tensor(40.0))
        np_cropped = np_cam.crop_intrinsics(k.numpy(), 100.0, 40.0)
        np.testing.assert_allclose(th_cropped.numpy(), np_cropped)

    def test_invalid_depth_mask(self) -> None:
        depth = torch.tensor([[1.0, 0.0], [torch.nan, -1.0]], dtype=self.dtype)
        points, valid = th_cam.depth_image_to_points(depth, self.k)
        torch.testing.assert_close(valid, torch.tensor([[True, False], [False, False]]))
        self.assertTrue(torch.isnan(points[~valid]).all().item())


if __name__ == "__main__":
    unittest.main()
