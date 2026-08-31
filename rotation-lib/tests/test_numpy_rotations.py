import unittest

import numpy as np

from embodied_spatial import numpy as rot


class TestNumPyRotations(unittest.TestCase):
    def setUp(self) -> None:
        self.rng = np.random.default_rng(20260831)

    def random_quaternions(self, count: int = 512) -> np.ndarray:
        q = self.rng.normal(size=(count, 4))
        return q / np.linalg.norm(q, axis=-1, keepdims=True)

    def assert_matrices_close(self, actual, expected, atol=1e-10) -> None:
        np.testing.assert_allclose(actual, expected, atol=atol, rtol=atol)

    def test_quaternion_matrices_are_in_so3(self) -> None:
        matrices = rot.quaternion_to_matrix(self.random_quaternions())
        orthogonality, determinant = rot.rotation_matrix_error(matrices)
        self.assertLess(float(orthogonality.max()), 2e-15)
        self.assertLess(float(determinant.max()), 2e-15)

    def test_quaternion_matrix_roundtrip_including_pi(self) -> None:
        q = np.vstack((self.random_quaternions(), [0.0, 1.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]))
        matrices = rot.quaternion_to_matrix(q)
        recovered = rot.matrix_to_quaternion(matrices)
        self.assert_matrices_close(rot.quaternion_to_matrix(recovered), matrices)
        self.assertTrue(np.all(recovered[:, 0] >= -1e-15))

    def test_axis_angle_roundtrip_near_zero_and_pi(self) -> None:
        axes = self.rng.normal(size=(512, 3))
        axes /= np.linalg.norm(axes, axis=-1, keepdims=True)
        angles = self.rng.uniform(0.0, np.pi, size=(512, 1))
        vectors = np.vstack((axes * angles, [0.0, 0.0, 0.0], [np.pi - 1e-10, 0.0, 0.0]))
        matrices = rot.axis_angle_to_matrix(vectors)
        recovered = rot.matrix_to_axis_angle(matrices)
        self.assert_matrices_close(rot.axis_angle_to_matrix(recovered), matrices, atol=2e-9)

    def test_euler_roundtrip_regular_and_gimbal_lock(self) -> None:
        regular = np.column_stack((
            self.rng.uniform(-np.pi, np.pi, 512),
            self.rng.uniform(-1.4, 1.4, 512),
            self.rng.uniform(-np.pi, np.pi, 512),
        ))
        singular = np.array([
            [0.8, np.pi / 2, -0.3],
            [-1.1, -np.pi / 2, 0.7],
            [2.0, np.pi / 2, 1.2],
        ])
        angles = np.vstack((regular, singular))
        matrices = rot.euler_zyx_to_matrix(angles)
        recovered = rot.matrix_to_euler_zyx(matrices)
        self.assert_matrices_close(rot.euler_zyx_to_matrix(recovered), matrices, atol=2e-9)
        np.testing.assert_allclose(recovered[-3:, 2], 0.0, atol=1e-12)

    def test_hamilton_product_matches_matrix_composition(self) -> None:
        left = self.random_quaternions(256)
        right = self.random_quaternions(256)
        composed = rot.quaternion_multiply(left, right)
        expected = rot.quaternion_to_matrix(left) @ rot.quaternion_to_matrix(right)
        self.assert_matrices_close(rot.quaternion_to_matrix(composed), expected)

    def test_q_and_negative_q_are_same_rotation(self) -> None:
        q = self.random_quaternions()
        self.assert_matrices_close(rot.quaternion_to_matrix(q), rot.quaternion_to_matrix(-q))

    def test_slerp_endpoints_unit_norm_and_shortest_branch(self) -> None:
        q0 = rot.axis_angle_to_quaternion([0.0, 0.0, 0.0])
        q1 = rot.axis_angle_to_quaternion([0.0, 0.0, 2.0 * np.pi / 3.0])
        samples = rot.quaternion_slerp(q0, q1, np.linspace(0.0, 1.0, 7))
        np.testing.assert_allclose(np.linalg.norm(samples, axis=-1), 1.0, atol=1e-12)
        self.assert_matrices_close(rot.quaternion_to_matrix(samples[0]), rot.quaternion_to_matrix(q0))
        self.assert_matrices_close(rot.quaternion_to_matrix(samples[-1]), rot.quaternion_to_matrix(q1))
        angles = np.linalg.norm(rot.quaternion_to_axis_angle(samples), axis=-1)
        np.testing.assert_allclose(angles, np.linspace(0.0, 2.0 * np.pi / 3.0, 7), atol=1e-12)
        self.assert_matrices_close(
            rot.quaternion_to_matrix(rot.quaternion_slerp(q0, -q1, 0.5)),
            rot.quaternion_to_matrix(samples[3]),
        )

    def test_rotation_preserves_vector_norm(self) -> None:
        matrices = rot.quaternion_to_matrix(self.random_quaternions())
        vectors = self.rng.normal(size=(512, 3))
        rotated = rot.rotate_vectors(matrices, vectors)
        np.testing.assert_allclose(np.linalg.norm(rotated, axis=-1), np.linalg.norm(vectors, axis=-1), atol=2e-14)

    def test_project_noisy_and_reflected_matrices_to_so3(self) -> None:
        base = rot.quaternion_to_matrix(self.random_quaternions(128))
        noisy = base + self.rng.normal(scale=0.02, size=base.shape)
        reflected = base.copy()
        reflected[..., :, -1] *= -1
        projected = rot.project_to_so3(np.concatenate((noisy, reflected)))
        orthogonality, determinant = rot.rotation_matrix_error(projected)
        self.assertLess(float(orthogonality.max()), 4e-15)
        self.assertLess(float(determinant.max()), 4e-15)

    def test_known_z_rotation_example(self) -> None:
        matrix = rot.axis_angle_to_matrix([0.0, 0.0, np.pi / 2.0])
        result = rot.rotate_vectors(matrix, [2.0, 0.0, 3.0])
        np.testing.assert_allclose(result, [0.0, 2.0, 3.0], atol=1e-12)

    def test_invalid_shapes_and_zero_quaternion_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            rot.quaternion_to_matrix([1.0, 0.0, 0.0])
        with self.assertRaises(ValueError):
            rot.normalize_quaternion([0.0, 0.0, 0.0, 0.0])
        with self.assertRaises(ValueError):
            rot.matrix_to_quaternion(np.eye(4))


if __name__ == "__main__":
    unittest.main()
