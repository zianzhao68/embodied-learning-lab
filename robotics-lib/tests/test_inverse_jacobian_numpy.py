import unittest

import numpy as np

from embodied_robotics import numpy as kin


class TestInverseJacobianNumPy(unittest.TestCase):
    def setUp(self) -> None:
        self.lengths = np.array([0.4, 0.3])
        self.rng = np.random.default_rng(20260901)

    def test_analytic_ik_returns_two_valid_branches(self) -> None:
        target = kin.planar_2r_fk(self.lengths, np.deg2rad([30.0, 60.0]))[-1]
        solutions, reachable = kin.planar_2r_ik(self.lengths, target)
        self.assertTrue(bool(reachable))
        self.assertGreaterEqual(solutions[0, 1], 0.0)
        self.assertLessEqual(solutions[1, 1], 0.0)
        for solution in solutions:
            np.testing.assert_allclose(kin.planar_2r_fk(self.lengths, solution)[-1], target, atol=1e-12)

    def test_reachability_annulus_and_nan_contract(self) -> None:
        targets = np.array([[0.7, 0.0], [0.8, 0.0], [0.1, 0.0], [0.05, 0.0]])
        solutions, reachable = kin.planar_2r_ik(self.lengths, targets)
        np.testing.assert_array_equal(reachable, [True, False, True, False])
        self.assertTrue(np.isnan(solutions[1]).all())
        self.assertTrue(np.isnan(solutions[3]).all())
        with self.assertRaises(ValueError):
            kin.planar_2r_ik([0.4, 0.0], [0.2, 0.1])

    def test_jacobian_matches_central_finite_difference(self) -> None:
        q = self.rng.uniform(-2.5, 2.5, size=(128, 2))
        analytic = kin.planar_2r_jacobian(self.lengths, q)
        eps = 1e-6
        numerical = np.empty_like(analytic)
        for joint in range(2):
            delta = np.zeros_like(q); delta[:, joint] = eps
            plus = kin.planar_2r_fk(self.lengths, q + delta)[:, -1]
            minus = kin.planar_2r_fk(self.lengths, q - delta)[:, -1]
            numerical[:, :, joint] = (plus - minus) / (2 * eps)
        np.testing.assert_allclose(analytic, numerical, atol=8e-11)

    def test_singularity_trigger_and_non_triggering_counterexample(self) -> None:
        q = np.array([[0.0, 0.0], [0.7, np.pi], [0.0, np.pi / 2]])
        jacobian = kin.planar_2r_jacobian(self.lengths, q)
        determinant = np.linalg.det(jacobian)
        np.testing.assert_allclose(determinant, self.lengths.prod() * np.sin(q[:, 1]), atol=1e-14)
        np.testing.assert_allclose(determinant[:2], 0.0, atol=1e-14)
        self.assertAlmostEqual(determinant[2], 0.12)
        np.testing.assert_allclose(jacobian[0], [[0.0, 0.0], [0.7, 0.3]], atol=1e-14)

    def test_damped_step_stays_finite_at_singularity(self) -> None:
        jacobian = kin.planar_2r_jacobian(self.lengths, [0.0, 0.0])
        step = kin.damped_least_squares_step(jacobian, [0.1, 0.1], damping=0.05)
        self.assertTrue(np.isfinite(step).all())

    def test_iterative_dls_converges_for_reachable_target(self) -> None:
        target = np.array([0.35, 0.25])
        q, converged, error = kin.planar_2r_ik_dls(
            self.lengths, target, initial=[0.2, 0.5], damping=0.03,
            step_size=0.8, max_iterations=200, tolerance=1e-8,
        )
        self.assertTrue(bool(converged))
        self.assertLess(float(error), 1e-8)
        np.testing.assert_allclose(kin.planar_2r_fk(self.lengths, q)[-1], target, atol=1e-8)

    def test_unreachable_and_joint_limited_targets_do_not_claim_success(self) -> None:
        _, converged_far, error_far = kin.planar_2r_ik_dls(
            self.lengths, [0.9, 0.0], initial=[0.2, 0.2], max_iterations=80
        )
        self.assertFalse(bool(converged_far))
        self.assertGreater(float(error_far), 0.19)
        q, converged_limited, _ = kin.planar_2r_ik_dls(
            self.lengths, [0.0, 0.6], initial=[0.0, 0.0], max_iterations=100,
            joint_limits=([-0.2, -0.2], [0.2, 0.2]),
        )
        self.assertFalse(bool(converged_limited))
        self.assertTrue(bool(kin.within_joint_limits(q, [-0.2, -0.2], [0.2, 0.2])))


if __name__ == "__main__":
    unittest.main()
