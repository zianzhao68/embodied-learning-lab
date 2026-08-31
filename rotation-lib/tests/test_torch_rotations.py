import unittest

import numpy as np
import torch

from embodied_spatial import numpy as np_rot
from embodied_spatial import torch as th_rot


@unittest.skipIf(th_rot is None, "PyTorch is not installed")
class TestTorchRotations(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(20260831)
        self.dtype = torch.float64

    def random_quaternions(self, count: int = 512) -> torch.Tensor:
        q = torch.randn(count, 4, dtype=self.dtype)
        return q / torch.linalg.vector_norm(q, dim=-1, keepdim=True)

    def test_numpy_torch_parity_for_all_conversions(self) -> None:
        q = self.random_quaternions()
        q_np = q.numpy()
        matrix_np = np_rot.quaternion_to_matrix(q_np)
        matrix_th = th_rot.quaternion_to_matrix(q)
        np.testing.assert_allclose(matrix_th.numpy(), matrix_np, atol=1e-12)

        recovered_th = th_rot.matrix_to_quaternion(matrix_th)
        np.testing.assert_allclose(
            th_rot.quaternion_to_matrix(recovered_th).numpy(), matrix_np, atol=1e-12
        )

        vector = torch.randn(512, 3, dtype=self.dtype)
        vector = vector / torch.linalg.vector_norm(vector, dim=-1, keepdim=True)
        vector *= torch.linspace(0.0, torch.pi, 512, dtype=self.dtype)[:, None]
        np.testing.assert_allclose(
            th_rot.axis_angle_to_matrix(vector).numpy(),
            np_rot.axis_angle_to_matrix(vector.numpy()),
            atol=1e-12,
        )

        euler = torch.empty(512, 3, dtype=self.dtype).uniform_(-1.4, 1.4)
        np.testing.assert_allclose(
            th_rot.euler_zyx_to_matrix(euler).numpy(),
            np_rot.euler_zyx_to_matrix(euler.numpy()),
            atol=1e-12,
        )

    def test_batched_properties_and_composition(self) -> None:
        left = self.random_quaternions()
        right = self.random_quaternions()
        matrices = th_rot.quaternion_to_matrix(left)
        orthogonality, determinant = th_rot.rotation_matrix_error(matrices)
        self.assertLess(orthogonality.max().item(), 2e-15)
        self.assertLess(determinant.max().item(), 2e-15)
        composed = th_rot.quaternion_multiply(left, right)
        torch.testing.assert_close(
            th_rot.quaternion_to_matrix(composed),
            th_rot.quaternion_to_matrix(left) @ th_rot.quaternion_to_matrix(right),
            atol=1e-12,
            rtol=1e-12,
        )

    def test_matrix_roundtrips_near_zero_pi_and_gimbal_lock(self) -> None:
        vectors = torch.tensor([
            [0.0, 0.0, 0.0],
            [torch.pi - 1e-10, 0.0, 0.0],
            [0.0, -torch.pi + 1e-9, 0.0],
            [1e-12, -2e-12, 3e-12],
        ], dtype=self.dtype)
        matrices = th_rot.axis_angle_to_matrix(vectors)
        torch.testing.assert_close(
            th_rot.axis_angle_to_matrix(th_rot.matrix_to_axis_angle(matrices)),
            matrices,
            atol=2e-9,
            rtol=2e-9,
        )

        euler = torch.tensor([
            [0.8, torch.pi / 2, -0.3],
            [-1.1, -torch.pi / 2, 0.7],
            [0.2, 0.4, -0.6],
        ], dtype=self.dtype)
        matrices = th_rot.euler_zyx_to_matrix(euler)
        recovered = th_rot.matrix_to_euler_zyx(matrices)
        torch.testing.assert_close(th_rot.euler_zyx_to_matrix(recovered), matrices, atol=2e-9, rtol=2e-9)
        torch.testing.assert_close(recovered[:2, 2], torch.zeros(2, dtype=self.dtype))

    def test_slerp_and_vector_norm(self) -> None:
        q0 = th_rot.axis_angle_to_quaternion(torch.zeros(3, dtype=self.dtype))
        q1 = th_rot.axis_angle_to_quaternion(torch.tensor([0.0, 0.0, 2.0], dtype=self.dtype))
        samples = th_rot.quaternion_slerp(q0, q1, torch.linspace(0.0, 1.0, 11, dtype=self.dtype))
        torch.testing.assert_close(torch.linalg.vector_norm(samples, dim=-1), torch.ones(11, dtype=self.dtype))
        vectors = torch.randn(11, 3, dtype=self.dtype)
        rotated = th_rot.rotate_vectors(th_rot.quaternion_to_matrix(samples), vectors)
        torch.testing.assert_close(
            torch.linalg.vector_norm(rotated, dim=-1),
            torch.linalg.vector_norm(vectors, dim=-1),
            atol=1e-12,
            rtol=1e-12,
        )

    def test_core_forward_paths_have_finite_gradients(self) -> None:
        rotation_vector = torch.tensor([[0.2, -0.3, 0.4], [1e-7, -2e-7, 3e-7]], dtype=self.dtype, requires_grad=True)
        matrix = th_rot.axis_angle_to_matrix(rotation_vector)
        loss = (matrix * torch.arange(1, 10, dtype=self.dtype).reshape(3, 3)).sum()
        loss.backward()
        self.assertTrue(torch.isfinite(rotation_vector.grad).all().item())

        quaternion = torch.tensor([[0.9, 0.1, -0.2, 0.3]], dtype=self.dtype, requires_grad=True)
        th_rot.quaternion_to_matrix(quaternion).square().sum().backward()
        self.assertTrue(torch.isfinite(quaternion.grad).all().item())

    def test_projection_is_proper_and_differentiable(self) -> None:
        matrix = torch.eye(3, dtype=self.dtype).repeat(8, 1, 1)
        matrix = (matrix + 0.03 * torch.randn_like(matrix)).requires_grad_()
        projected = th_rot.project_to_so3(matrix)
        orthogonality, determinant = th_rot.rotation_matrix_error(projected)
        self.assertLess(orthogonality.max().item(), 3e-15)
        self.assertLess(determinant.max().item(), 3e-15)
        projected.sum().backward()
        self.assertTrue(torch.isfinite(matrix.grad).all().item())

    def test_dtype_shape_and_invalid_input_contracts(self) -> None:
        result = th_rot.axis_angle_to_matrix(torch.zeros(2, 3, dtype=torch.float32))
        self.assertEqual(result.shape, (2, 3, 3))
        self.assertEqual(result.dtype, torch.float32)
        with self.assertRaises(ValueError):
            th_rot.normalize_quaternion(torch.zeros(4, dtype=self.dtype))
        with self.assertRaises(ValueError):
            th_rot.euler_zyx_to_matrix(torch.zeros(2, dtype=self.dtype))


if __name__ == "__main__":
    unittest.main()
