import unittest

import numpy as np

from embodied_vision import numpy as cam


class TestNumPyCamera(unittest.TestCase):
    def setUp(self) -> None:
        self.k = cam.make_intrinsics(500.0, 500.0, 320.0, 240.0)
        self.rng = np.random.default_rng(20260901)

    def test_known_projection_with_units(self) -> None:
        pixels, valid = cam.project_points([0.1, 0.05, 1.0], self.k)
        self.assertTrue(bool(valid))
        np.testing.assert_allclose(pixels, [370.0, 265.0], atol=1e-12)

    def test_same_ray_has_same_pixel_and_depth_is_lost(self) -> None:
        points = np.array([[0.1, 0.05, 1.0], [0.2, 0.1, 2.0], [0.4, 0.2, 4.0]])
        pixels, valid = cam.project_points(points, self.k)
        self.assertTrue(valid.all())
        np.testing.assert_allclose(pixels, np.array([[370.0, 265.0]] * 3), atol=1e-12)

    def test_single_variable_comparisons(self) -> None:
        points = np.array([[0.1, 0.0, 1.0], [0.2, 0.0, 1.0], [0.1, 0.0, 2.0]])
        pixels, _ = cam.project_points(points, self.k)
        np.testing.assert_allclose(pixels[:, 0], [370.0, 420.0, 345.0])
        # Double X at fixed Z doubles the offset; double Z at fixed X halves it.
        np.testing.assert_allclose(pixels[:, 0] - 320.0, [50.0, 100.0, 25.0])

    def test_project_unproject_round_trip(self) -> None:
        points = self.rng.uniform([-0.4, -0.3, 0.2], [0.4, 0.3, 4.0], size=(2048, 3))
        pixels, projected = cam.project_points(points, self.k)
        reconstructed, unprojected = cam.unproject_pixels(pixels, points[:, 2], self.k)
        self.assertTrue(projected.all() and unprojected.all())
        np.testing.assert_allclose(reconstructed, points, atol=8e-16)

    def test_invalid_depth_is_explicit(self) -> None:
        pixels, valid = cam.project_points([[0.0, 0.0, 0.0], [0.1, 0.0, -1.0]], self.k)
        self.assertFalse(valid.any())
        self.assertTrue(np.isnan(pixels).all())
        points, depth_valid = cam.unproject_pixels([[320.0, 240.0]], [0.0], self.k)
        self.assertFalse(depth_valid.any())
        self.assertTrue(np.isnan(points).all())

    def test_center_ray_and_metric_unprojection(self) -> None:
        ray = cam.pixel_rays([320.0, 240.0], self.k)
        np.testing.assert_allclose(ray, [0.0, 0.0, 1.0])
        point, valid = cam.unproject_pixels([370.0, 265.0], 2.0, self.k)
        self.assertTrue(bool(valid))
        np.testing.assert_allclose(point, [0.2, 0.1, 2.0])

    def test_extrinsic_transform_then_projection(self) -> None:
        transform_camera_world = np.eye(4)
        transform_camera_world[0, 3] = -1.0
        pixel, valid = cam.project_world_points([1.0, 0.0, 3.0], transform_camera_world, self.k)
        self.assertTrue(bool(valid))
        np.testing.assert_allclose(pixel, [320.0, 240.0])

    def test_batched_intrinsics_and_points(self) -> None:
        k = cam.make_intrinsics([500.0, 800.0], [500.0, 800.0], [320.0, 640.0], [240.0, 360.0])
        points = np.array([[[0.1, 0.0, 1.0]], [[0.1, 0.0, 1.0]]])
        pixels, valid = cam.project_points(points, k)
        self.assertTrue(valid.all())
        np.testing.assert_allclose(pixels[:, 0], [[370.0, 240.0], [720.0, 360.0]])

    def test_fov_and_invalid_contracts(self) -> None:
        self.assertAlmostEqual(float(cam.focal_length_from_fov(640.0, np.pi / 2)), 320.0)
        with self.assertRaises(ValueError):
            cam.make_intrinsics(0.0, 500.0, 320.0, 240.0)
        with self.assertRaises(ValueError):
            cam.project_points([1.0, 2.0], self.k)
        with self.assertRaises(ValueError):
            cam.focal_length_from_fov(640.0, np.pi)


if __name__ == "__main__":
    unittest.main()
