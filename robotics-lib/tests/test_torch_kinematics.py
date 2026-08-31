import unittest

import numpy as np
import torch

from embodied_robotics import numpy as np_kin
from embodied_robotics import torch as th_kin


@unittest.skipIf(th_kin is None, "PyTorch is not installed")
class TestTorchKinematics(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(20260901)
        self.dtype = torch.float64

    def test_numpy_torch_parity_for_dh_and_planar_fk(self) -> None:
        params = torch.tensor([[0.1, 0.2, 0.4, -0.3], [-0.2, 0.1, 0.3, 0.4]], dtype=self.dtype)
        q = torch.randn(256, 2, dtype=self.dtype)
        actual = th_kin.forward_kinematics_dh(params, q)
        expected = np_kin.forward_kinematics_dh(params.numpy(), q.numpy())
        np.testing.assert_allclose(actual.numpy(), expected, atol=1e-12)
        np.testing.assert_allclose(
            th_kin.planar_2r_fk(torch.tensor([0.4, 0.3], dtype=self.dtype), q).numpy(),
            np_kin.planar_2r_fk([0.4, 0.3], q.numpy()),
            atol=1e-12,
        )

    def test_forward_kinematics_gradients_are_finite(self) -> None:
        params = torch.tensor([[0.0, 0.0, 0.4, 0.0], [0.0, 0.0, 0.3, 0.0]], dtype=self.dtype)
        q = torch.tensor([[0.2, -0.4], [0.7, 0.1]], dtype=self.dtype, requires_grad=True)
        pose = th_kin.forward_kinematics_dh(params, q)
        weights = torch.arange(1, 17, dtype=self.dtype).reshape(4, 4)
        (pose * weights).sum().backward()
        self.assertTrue(torch.isfinite(q.grad).all().item())

    def test_planar_formula_gradient_matches_finite_difference(self) -> None:
        lengths = torch.tensor([0.4, 0.3], dtype=self.dtype)
        q = torch.tensor([0.3, -0.7], dtype=self.dtype, requires_grad=True)
        x = th_kin.planar_2r_fk(lengths, q)[-1, 0]
        x.backward()
        analytic = q.grad.detach().numpy().copy()
        eps = 1e-6
        numerical = []
        for index in range(2):
            plus = q.detach().numpy().copy(); plus[index] += eps
            minus = q.detach().numpy().copy(); minus[index] -= eps
            f_plus = np_kin.planar_2r_fk([0.4, 0.3], plus)[-1, 0]
            f_minus = np_kin.planar_2r_fk([0.4, 0.3], minus)[-1, 0]
            numerical.append((f_plus - f_minus) / (2 * eps))
        np.testing.assert_allclose(analytic, numerical, atol=1e-9)

    def test_batched_mixed_joint_chain(self) -> None:
        params = torch.tensor([[0.0, 0.0, 0.5, 0.0], [0.0, 0.1, 0.0, 0.0]], dtype=self.dtype)
        q = torch.tensor([[0.0, 0.2], [torch.pi / 2, 0.4]], dtype=self.dtype)
        pose = th_kin.forward_kinematics_dh(params, q, joint_types=["R", "P"])
        torch.testing.assert_close(pose[:, 2, 3], torch.tensor([0.3, 0.5], dtype=self.dtype))
        torch.testing.assert_close(pose[:, :2, 3], torch.tensor([[0.5, 0.0], [0.0, 0.5]], dtype=self.dtype), atol=1e-12, rtol=1e-12)

    def test_return_all_shape_dtype_and_device(self) -> None:
        params = torch.zeros(3, 4, dtype=torch.float32)
        params[:, 2] = torch.tensor([0.4, 0.3, 0.2])
        poses = th_kin.forward_kinematics_dh(params, torch.zeros(5, 3), return_all=True)
        self.assertEqual(poses.shape, (5, 4, 4, 4))
        self.assertEqual(poses.dtype, torch.float32)
        self.assertEqual(poses.device, params.device)

    def test_invalid_input_contracts(self) -> None:
        with self.assertRaises(ValueError):
            th_kin.compose_chain(torch.eye(4))
        with self.assertRaises(ValueError):
            th_kin.forward_kinematics_dh(torch.zeros(2, 4), torch.zeros(3))


if __name__ == "__main__":
    unittest.main()
