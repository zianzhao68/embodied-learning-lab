import unittest

import numpy as np

from embodied_vision import numpy as cam


class TestNumPyDepthCloud(unittest.TestCase):
    def setUp(self) -> None:
        self.k_small = cam.make_intrinsics(2.0, 2.0, 1.0, 1.0)
        self.k = cam.make_intrinsics(500.0, 500.0, 320.0, 240.0)

    def test_three_by_three_hand_calculation(self) -> None:
        depth = np.array([[1.0, 1.0, 1.0], [1.0, 2.0, 1.0], [1.0, 1.0, 1.0]])
        points, valid = cam.depth_image_to_points(depth, self.k_small)
        self.assertEqual(points.shape, (3, 3, 3))
        self.assertTrue(valid.all())
        np.testing.assert_allclose(points[1, 1], [0.0, 0.0, 2.0])
        np.testing.assert_allclose(points[1, 2], [0.5, 0.0, 1.0])
        np.testing.assert_allclose(points[0, 0], [-0.5, -0.5, 1.0])

    def test_flatten_preserves_row_major_pixel_order(self) -> None:
        points, valid = cam.depth_image_to_points(np.ones((2, 3)), self.k_small, flatten=True)
        self.assertEqual(points.shape, (6, 3))
        self.assertEqual(valid.shape, (6,))
        np.testing.assert_allclose(points[0], [-0.5, -0.5, 1.0])
        np.testing.assert_allclose(points[1], [0.0, -0.5, 1.0])
        np.testing.assert_allclose(points[3], [-0.5, 0.0, 1.0])

    def test_invalid_depth_keeps_organized_shape_and_mask(self) -> None:
        depth = np.array([[1.0, 0.0], [np.nan, -1.0]])
        points, valid = cam.depth_image_to_points(depth, self.k_small)
        np.testing.assert_array_equal(valid, [[True, False], [False, False]])
        self.assertTrue(np.isfinite(points[0, 0]).all())
        self.assertTrue(np.isnan(points[~valid]).all())

    def test_range_and_z_depth_are_different_off_axis(self) -> None:
        distance = np.ones((3, 3)) * 2.0
        range_points, valid = cam.range_image_to_points(distance, self.k_small)
        self.assertTrue(valid.all())
        self.assertAlmostEqual(np.linalg.norm(range_points[0, 0]), 2.0)
        self.assertLess(range_points[0, 0, 2], 2.0)
        np.testing.assert_allclose(range_points[1, 1], [0.0, 0.0, 2.0])

    def test_rescaled_intrinsics_rescale_projected_pixels(self) -> None:
        point = np.array([0.1, 0.05, 1.0])
        pixel, _ = cam.project_points(point, self.k)
        resized_k = cam.rescale_intrinsics(self.k, 0.5, 0.25)
        resized_pixel, _ = cam.project_points(point, resized_k)
        np.testing.assert_allclose(resized_pixel, pixel * [0.5, 0.25])
        np.testing.assert_allclose(resized_k, [[250.0, 0.0, 160.0], [0.0, 125.0, 60.0], [0.0, 0.0, 1.0]])

    def test_cropped_intrinsics_shift_projected_pixels(self) -> None:
        point = np.array([0.1, 0.05, 1.0])
        pixel, _ = cam.project_points(point, self.k)
        cropped_k = cam.crop_intrinsics(self.k, left=100.0, top=40.0)
        cropped_pixel, _ = cam.project_points(point, cropped_k)
        np.testing.assert_allclose(cropped_pixel, pixel - [100.0, 40.0])

    def test_batched_depth_images(self) -> None:
        depth = np.stack((np.ones((2, 2)), np.ones((2, 2)) * 2.0))
        k = cam.make_intrinsics([2.0, 4.0], [2.0, 4.0], [1.0, 1.0], [1.0, 1.0])
        points, valid = cam.depth_image_to_points(depth, k)
        self.assertEqual(points.shape, (2, 2, 2, 3))
        self.assertTrue(valid.all())
        np.testing.assert_allclose(points[:, 1, 1], [[0.0, 0.0, 1.0], [0.0, 0.0, 2.0]])

    def test_invalid_contract(self) -> None:
        with self.assertRaises(ValueError):
            cam.depth_image_to_points(np.ones(3), self.k)
        with self.assertRaises(ValueError):
            cam.range_image_to_points(np.ones(3), self.k)


if __name__ == "__main__":
    unittest.main()
