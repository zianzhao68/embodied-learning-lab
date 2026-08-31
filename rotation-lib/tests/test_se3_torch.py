import unittest

import numpy as np
import torch

from embodied_spatial import numpy as np_so3
from embodied_spatial import se3_numpy as np_se3
from embodied_spatial import se3_torch as th_se3
from embodied_spatial import torch as th_so3


@unittest.skipIf(th_se3 is None, "PyTorch is not installed")
class TestSE3Torch(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(20260901)
        self.dtype = torch.float64

    def random_transforms(self, count: int = 128) -> torch.Tensor:
        q = torch.randn(count, 4, dtype=self.dtype)
        q /= torch.linalg.vector_norm(q, dim=-1, keepdim=True)
        return th_se3.make_transform(th_so3.quaternion_to_matrix(q), torch.randn(count, 3, dtype=self.dtype))

    def test_numpy_torch_parity(self) -> None:
        transforms = self.random_transforms()
        points = torch.randn(128, 3, dtype=self.dtype)
        np.testing.assert_allclose(
            th_se3.transform_points(transforms, points).numpy(),
            np_se3.transform_points(transforms.numpy(), points.numpy()),
            atol=1e-12,
        )
        np.testing.assert_allclose(
            th_se3.inverse_transform(transforms).numpy(),
            np_se3.inverse_transform(transforms.numpy()),
            atol=1e-12,
        )

    def test_composition_inverse_and_relative_pose(self) -> None:
        left = self.random_transforms()
        right = self.random_transforms()
        composed = th_se3.compose_transforms(left, right)
        torch.testing.assert_close(composed, left @ right)
        identity = composed @ th_se3.inverse_transform(composed)
        torch.testing.assert_close(identity, torch.eye(4, dtype=self.dtype).expand_as(identity), atol=2e-14, rtol=2e-14)
        relative = th_se3.relative_transform(left, right)
        torch.testing.assert_close(left @ relative, right, atol=2e-14, rtol=2e-14)

    def test_point_direction_and_distance_semantics(self) -> None:
        transform = th_se3.make_transform(torch.eye(3, dtype=self.dtype), torch.tensor([4.0, -2.0, 1.0], dtype=self.dtype))
        value = torch.tensor([1.0, 2.0, 3.0], dtype=self.dtype)
        torch.testing.assert_close(th_se3.transform_points(transform, value), torch.tensor([5.0, 0.0, 4.0], dtype=self.dtype))
        torch.testing.assert_close(th_se3.transform_directions(transform, value), value)

        transforms = self.random_transforms()
        p = torch.randn(128, 3, dtype=self.dtype)
        q = torch.randn(128, 3, dtype=self.dtype)
        torch.testing.assert_close(
            torch.linalg.vector_norm(th_se3.transform_points(transforms, p) - th_se3.transform_points(transforms, q), dim=-1),
            torch.linalg.vector_norm(p - q, dim=-1),
            atol=2e-14,
            rtol=2e-14,
        )

    def test_gradients_through_build_compose_inverse_and_points(self) -> None:
        rotation_vector = torch.tensor([[0.2, -0.3, 0.4], [-0.1, 0.5, 0.2]], dtype=self.dtype, requires_grad=True)
        translation = torch.tensor([[0.4, 0.2, -0.1], [0.2, -0.3, 0.6]], dtype=self.dtype, requires_grad=True)
        transform = th_se3.make_transform(th_so3.axis_angle_to_matrix(rotation_vector), translation)
        inverse = th_se3.inverse_transform(transform)
        points = torch.tensor([[1.0, 2.0, 3.0], [-1.0, 0.5, 2.0]], dtype=self.dtype)
        loss = th_se3.transform_points(inverse, points).square().sum()
        loss.backward()
        self.assertTrue(torch.isfinite(rotation_vector.grad).all().item())
        self.assertTrue(torch.isfinite(translation.grad).all().item())

    def test_project_to_se3_is_valid_and_differentiable(self) -> None:
        noisy = self.random_transforms(16)
        noisy = (noisy + 0.01 * torch.randn_like(noisy)).requires_grad_()
        projected = th_se3.project_to_se3(noisy)
        orthogonality, determinant, bottom = th_se3.transform_error(projected)
        self.assertLess(orthogonality.max().item(), 4e-15)
        self.assertLess(determinant.max().item(), 4e-15)
        self.assertEqual(bottom.max().item(), 0.0)
        projected.sum().backward()
        self.assertTrue(torch.isfinite(noisy.grad).all().item())

    def test_quaternion_translation_constructor_and_dtype(self) -> None:
        q = torch.tensor([1.0, 0.0, 0.0, 0.0], dtype=torch.float32)
        transform = th_se3.quaternion_translation_to_transform(q, torch.tensor([1.0, 2.0, 3.0]))
        self.assertEqual(transform.dtype, torch.float32)
        self.assertEqual(transform.shape, (4, 4))
        with self.assertRaises(ValueError):
            th_se3.inverse_transform(torch.eye(3))


if __name__ == "__main__":
    unittest.main()
