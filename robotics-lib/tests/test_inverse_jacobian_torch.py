import unittest

import numpy as np
import torch

from embodied_robotics import numpy as np_kin
from embodied_robotics import torch as th_kin


@unittest.skipIf(th_kin is None, "PyTorch is not installed")
class TestInverseJacobianTorch(unittest.TestCase):
    def setUp(self) -> None:
        torch.manual_seed(20260901)
        self.dtype = torch.float64
        self.lengths = torch.tensor([0.4, 0.3], dtype=self.dtype)

    def test_numpy_torch_parity(self) -> None:
        q = torch.randn(256, 2, dtype=self.dtype)
        np.testing.assert_allclose(
            th_kin.planar_2r_jacobian(self.lengths, q).numpy(),
            np_kin.planar_2r_jacobian(self.lengths.numpy(), q.numpy()), atol=1e-12,
        )
        targets = th_kin.planar_2r_fk(self.lengths, q[:64])[:, -1]
        th_solutions, th_reachable = th_kin.planar_2r_ik(self.lengths, targets)
        np_solutions, np_reachable = np_kin.planar_2r_ik(self.lengths.numpy(), targets.numpy())
        np.testing.assert_allclose(th_solutions.numpy(), np_solutions, atol=1e-12)
        np.testing.assert_array_equal(th_reachable.numpy(), np_reachable)

    def test_jacobian_equals_autograd_derivative(self) -> None:
        q = torch.tensor([0.4, -0.8], dtype=self.dtype, requires_grad=True)
        function = lambda value: th_kin.planar_2r_fk(self.lengths, value)[-1]
        automatic = torch.autograd.functional.jacobian(function, q)
        torch.testing.assert_close(th_kin.planar_2r_jacobian(self.lengths, q), automatic, atol=1e-12, rtol=1e-12)

    def test_analytic_ik_reconstructs_target_and_handles_unreachable(self) -> None:
        targets = torch.tensor([[0.35, 0.25], [0.9, 0.0]], dtype=self.dtype)
        solutions, reachable = th_kin.planar_2r_ik(self.lengths, targets)
        torch.testing.assert_close(reachable, torch.tensor([True, False]))
        reconstructed = th_kin.planar_2r_fk(self.lengths, solutions[0])[:, -1]
        torch.testing.assert_close(reconstructed, targets[0].expand_as(reconstructed), atol=1e-12, rtol=1e-12)
        self.assertTrue(torch.isnan(solutions[1]).all().item())

    def test_damped_step_is_differentiable_and_finite(self) -> None:
        q = torch.tensor([0.0, 1e-4], dtype=self.dtype, requires_grad=True)
        jacobian = th_kin.planar_2r_jacobian(self.lengths, q)
        step = th_kin.damped_least_squares_step(jacobian, torch.tensor([0.1, 0.1], dtype=self.dtype), damping=0.05)
        step.square().sum().backward()
        self.assertTrue(torch.isfinite(step).all().item())
        self.assertTrue(torch.isfinite(q.grad).all().item())

    def test_iterative_solver_batch_and_limits(self) -> None:
        target = torch.tensor([[0.35, 0.25], [0.0, 0.6]], dtype=self.dtype)
        initial = torch.tensor([[0.2, 0.5], [0.0, 0.0]], dtype=self.dtype)
        q, converged, error = th_kin.planar_2r_ik_dls(
            self.lengths, target, initial, damping=0.03, step_size=0.8,
            max_iterations=200, tolerance=1e-8,
        )
        self.assertTrue(converged.all().item())
        self.assertLess(error.max().item(), 1e-8)
        limited_q, limited_ok, _ = th_kin.planar_2r_ik_dls(
            self.lengths, target[1], initial[1], max_iterations=80,
            joint_limits=(torch.tensor([-0.2, -0.2]), torch.tensor([0.2, 0.2])),
        )
        self.assertFalse(limited_ok.item())
        self.assertTrue(th_kin.within_joint_limits(limited_q, torch.tensor([-0.2, -0.2]), torch.tensor([0.2, 0.2])).item())

    def test_invalid_contracts(self) -> None:
        with self.assertRaises(ValueError):
            th_kin.planar_2r_ik(torch.ones(3), torch.ones(2))
        with self.assertRaises(ValueError):
            th_kin.planar_2r_ik(torch.tensor([0.4, 0.0]), torch.ones(2))
        with self.assertRaises(ValueError):
            th_kin.damped_least_squares_step(torch.eye(2), torch.ones(3))
        with self.assertRaises(ValueError):
            th_kin.planar_2r_ik_dls(self.lengths, torch.ones(2), torch.ones(3))


if __name__ == "__main__":
    unittest.main()
