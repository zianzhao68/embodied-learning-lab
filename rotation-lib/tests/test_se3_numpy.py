import unittest

import numpy as np

from embodied_spatial import numpy as so3
from embodied_spatial import se3_numpy as se3


class TestSE3NumPy(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = np.random.default_rng(20260901)

    def random_transforms(self, count: int = 256) -> np.ndarray:
        q = self.rng.normal(size=(count, 4))
        q /= np.linalg.norm(q, axis=-1, keepdims=True)
        return se3.make_transform(so3.quaternion_to_matrix(q), self.rng.normal(size=(count, 3)))

    def test_known_frame_transform(self) -> None:
        rotation = so3.axis_angle_to_matrix([0.0, 0.0, np.pi / 2])
        transform = se3.make_transform(rotation, [1.0, 2.0, 0.0])
        np.testing.assert_allclose(se3.transform_points(transform, [1.0, 0.0, 0.0]), [1.0, 3.0, 0.0], atol=1e-12)

    def test_points_and_directions_have_different_translation_semantics(self) -> None:
        transform = se3.make_transform(np.eye(3), [4.0, -2.0, 1.0])
        value = np.array([1.0, 2.0, 3.0])
        np.testing.assert_allclose(se3.transform_points(transform, value), [5.0, 0.0, 4.0])
        np.testing.assert_allclose(se3.transform_directions(transform, value), value)

    def test_composition_block_translation_and_subscript_order(self) -> None:
        t_a_b = se3.make_transform(so3.axis_angle_to_matrix([0.0, 0.0, np.pi / 2]), [1.0, 2.0, 0.0])
        t_b_c = se3.make_transform(np.eye(3), [2.0, 0.0, 0.0])
        t_a_c = se3.compose_transforms(t_a_b, t_b_c)
        np.testing.assert_allclose(t_a_c[:3, 3], [1.0, 4.0, 0.0], atol=1e-12)
        point = np.array([0.5, 0.0, 0.0])
        sequential = se3.transform_points(t_a_b, se3.transform_points(t_b_c, point))
        np.testing.assert_allclose(se3.transform_points(t_a_c, point), sequential, atol=1e-12)

    def test_inverse_and_relative_transform_roundtrips(self) -> None:
        transforms = self.random_transforms()
        inverse = se3.inverse_transform(transforms)
        identity = se3.compose_transforms(transforms, inverse)
        np.testing.assert_allclose(identity, np.broadcast_to(np.eye(4), identity.shape), atol=2e-14)
        relative = se3.relative_transform(transforms[:128], transforms[128:])
        reconstructed = se3.compose_transforms(transforms[:128], relative)
        np.testing.assert_allclose(reconstructed, transforms[128:], atol=2e-14)

    def test_rigid_transform_preserves_pairwise_distance(self) -> None:
        transforms = self.random_transforms()
        p = self.rng.normal(size=(256, 3))
        q = self.rng.normal(size=(256, 3))
        p_out = se3.transform_points(transforms, p)
        q_out = se3.transform_points(transforms, q)
        np.testing.assert_allclose(np.linalg.norm(p_out - q_out, axis=-1), np.linalg.norm(p - q, axis=-1), atol=2e-14)

    def test_project_to_se3_and_error_metrics(self) -> None:
        transforms = self.random_transforms(64)
        noisy = transforms.copy()
        noisy[..., :3, :3] += self.rng.normal(scale=0.02, size=(64, 3, 3))
        noisy[..., 3, :] = self.rng.normal(size=(64, 4))
        projected = se3.project_to_se3(noisy)
        orthogonality, determinant, bottom = se3.transform_error(projected)
        self.assertLess(orthogonality.max(), 4e-15)
        self.assertLess(determinant.max(), 4e-15)
        self.assertEqual(float(bottom.max()), 0.0)
        np.testing.assert_allclose(projected[..., :3, 3], transforms[..., :3, 3])

    def test_batch_broadcast_and_invalid_shape(self) -> None:
        rotations = so3.axis_angle_to_matrix(np.zeros((8, 3)))
        transform = se3.make_transform(rotations, [1.0, 2.0, 3.0])
        self.assertEqual(transform.shape, (8, 4, 4))
        with self.assertRaises(ValueError):
            se3.make_transform(np.eye(4), np.zeros(3))
        with self.assertRaises(ValueError):
            se3.transform_points(np.eye(4), np.zeros(4))


if __name__ == "__main__":
    unittest.main()
