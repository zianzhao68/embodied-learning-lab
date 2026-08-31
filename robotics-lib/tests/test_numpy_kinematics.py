import unittest

import numpy as np

from embodied_robotics import numpy as kin


class TestNumPyKinematics(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = np.random.default_rng(20260901)

    def test_planar_2r_known_example(self) -> None:
        points = kin.planar_2r_fk([0.4, 0.3], np.deg2rad([30.0, 60.0]))
        np.testing.assert_allclose(points[-1], [0.2 * np.sqrt(3), 0.5], atol=1e-12)
        np.testing.assert_allclose(points[1], [0.2 * np.sqrt(3), 0.2], atol=1e-12)

    def test_q2_is_relative_not_world_angle(self) -> None:
        points = kin.planar_2r_fk([1.0, 1.0], np.deg2rad([90.0, -90.0]))
        np.testing.assert_allclose(points[-1], [1.0, 1.0], atol=1e-12)

    def test_planar_fk_preserves_each_link_length(self) -> None:
        q = self.rng.uniform(-np.pi, np.pi, size=(1000, 2))
        points = kin.planar_2r_fk([0.4, 0.3], q)
        np.testing.assert_allclose(np.linalg.norm(points[:, 1] - points[:, 0], axis=-1), 0.4, atol=1e-14)
        np.testing.assert_allclose(np.linalg.norm(points[:, 2] - points[:, 1], axis=-1), 0.3, atol=1e-14)

    def test_standard_dh_matches_planar_formula(self) -> None:
        params = np.array([[0.0, 0.0, 0.4, 0.0], [0.0, 0.0, 0.3, 0.0]])
        q = self.rng.uniform(-np.pi, np.pi, size=(512, 2))
        transforms = kin.forward_kinematics_dh(params, q)
        expected = kin.planar_2r_fk([0.4, 0.3], q)[..., -1, :]
        np.testing.assert_allclose(transforms[..., :2, 3], expected, atol=1e-14)
        np.testing.assert_allclose(transforms[..., 2, 3], 0.0, atol=1e-14)

    def test_return_all_contains_base_elbow_and_end_pose(self) -> None:
        params = np.array([[0.0, 0.0, 0.4, 0.0], [0.0, 0.0, 0.3, 0.0]])
        poses = kin.forward_kinematics_dh(params, np.deg2rad([30.0, 60.0]), return_all=True)
        self.assertEqual(poses.shape, (3, 4, 4))
        np.testing.assert_allclose(poses[0], np.eye(4))
        np.testing.assert_allclose(poses[1, :2, 3], [0.2 * np.sqrt(3), 0.2], atol=1e-12)
        np.testing.assert_allclose(poses[2, :2, 3], [0.2 * np.sqrt(3), 0.5], atol=1e-12)

    def test_prismatic_joint_changes_d_not_theta(self) -> None:
        params = np.array([[0.0, 0.2, 0.0, 0.0]])
        transform = kin.forward_kinematics_dh(params, [0.35], joint_types=["P"])
        np.testing.assert_allclose(transform[:3, 3], [0.0, 0.0, 0.55])
        np.testing.assert_allclose(transform[:3, :3], np.eye(3))

    def test_compose_chain_matches_manual_product(self) -> None:
        local = np.stack((
            kin.dh_transform(0.2, 0.1, 0.3, -0.4),
            kin.dh_transform(-0.5, 0.2, 0.4, 0.3),
            kin.dh_transform(0.7, -0.1, 0.2, 0.1),
        ))
        np.testing.assert_allclose(kin.compose_chain(local), local[0] @ local[1] @ local[2], atol=1e-14)

    def test_invalid_shapes_and_joint_types(self) -> None:
        with self.assertRaises(ValueError):
            kin.planar_2r_fk([1.0], [0.0, 0.0])
        with self.assertRaises(ValueError):
            kin.forward_kinematics_dh(np.zeros((2, 3)), [0.0, 0.0])
        with self.assertRaises(ValueError):
            kin.forward_kinematics_dh(np.zeros((2, 4)), [0.0, 0.0], joint_types=["R", "X"])


if __name__ == "__main__":
    unittest.main()
