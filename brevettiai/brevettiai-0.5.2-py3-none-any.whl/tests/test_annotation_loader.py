import unittest
import json
import tensorflow as tf

from brevettiai.tests import get_resource
from brevettiai.data.image import ImageLoader, AnnotationLoader, CropResizeProcessor
from brevettiai.data.tf_types import BBOX
from brevettiai.io import io_tools


class TestAnnotationLoaderBbox(unittest.TestCase):
    test_image_path = get_resource("0_1543413266626.bmp")
    test_annotation_path = get_resource("1651574629796.json")
    bbox = BBOX(x1=10, x2=210, y1=30, y2=130)

    def test_loader_bbox_selection(self):
        classes = set([anno["label"] for anno in
                       json.loads(io_tools.read_file(self.test_annotation_path))["annotations"]])
        annotation_bbox, _ = AnnotationLoader(classes=classes).load(path=self.test_annotation_path, bbox=self.bbox)
        image_bbox, _ = ImageLoader(interpolation_method="nearest").load(self.test_image_path, bbox=self.bbox)
        image_raw, _ = ImageLoader(interpolation_method="nearest").load(self.test_image_path)
        annotation_raw, _ = AnnotationLoader(classes=classes).load(path=self.test_annotation_path,
                                                 metadata={"_image_file_shape": image_raw.shape})

        # Test that annotation is not empty
        tf.debugging.assert_greater(tf.reduce_mean(tf.abs(annotation_bbox)), 1e-4)

        # Test that image_bbox is correct region
        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(
            image_bbox -
            image_raw[self.bbox.y1:self.bbox.y2 + 1, self.bbox.x1:self.bbox.x2 + 1])), 1e-4)

        # Test that area outputs shape of output image
        tf.debugging.assert_less_equal(tf.cast(tf.abs(
            self.bbox.area - annotation_bbox.shape[0] * annotation_bbox.shape[1]), dtype=tf.int64),
            tf.constant(0, dtype=tf.int64))

        # Test that annotation_bbox is correct region
        tf.debugging.assert_less_equal(tf.reduce_sum(tf.abs(
            annotation_bbox -
            annotation_raw[self.bbox.y1:self.bbox.y2 + 1, self.bbox.x1:self.bbox.x2 + 1])), 25.0)

        tf.debugging.assert_less_equal(tf.reduce_sum(
            tf.abs(tf.convert_to_tensor(annotation_bbox.shape)[:2] - tf.convert_to_tensor(image_bbox.shape)[:2])), 0)


class TestAnnotationLoaderCropResize(unittest.TestCase):
    test_image_path = get_resource("0_1543413266626.bmp")
    test_annotation_path = get_resource("1651574629796.json")
    image_crop = CropResizeProcessor(roi_horizontal_offset=32,
                                     roi_vertical_offset=64,
                                     roi_width=160,
                                     roi_height=128)

    def test_loader_crop_resize(self):
        classes = sorted(set([anno["label"] for anno in
                         json.loads(io_tools.read_file(self.test_annotation_path))["annotations"]]))
        annotation_cropped, _ = AnnotationLoader(classes=classes, postprocessor=self.image_crop).load(
                                                 path=self.test_annotation_path)
        image_cropped, _ = ImageLoader(interpolation_method="nearest", postprocessor=self.image_crop).load(
                                       self.test_image_path)
        image_raw, _ = ImageLoader(interpolation_method="nearest").load(self.test_image_path)
        annotation_raw, _ = AnnotationLoader(classes=classes).load(path=self.test_annotation_path,
                                             metadata={"_image_file_shape": image_raw.shape})

        image_crop_copy = self.image_crop.copy().set_bbox(self.image_crop.bbox(100, 100))

        assert image_crop_copy.roi_width == self.image_crop.roi_width

        # Test that annotation is not empty
        tf.debugging.assert_greater(tf.reduce_mean(tf.abs(annotation_cropped)), 1e-4)

        # Test that annotation_bbox is correct region
        tf.debugging.assert_less_equal(tf.reduce_sum(tf.abs(
            annotation_cropped -
            annotation_raw[self.image_crop.roi_vertical_offset:self.image_crop.roi_vertical_offset +
                                                               self.image_crop.roi_height,
                           self.image_crop.roi_horizontal_offset:self.image_crop.roi_horizontal_offset +
                                                               self.image_crop.roi_width])), 25.0)

        # Test that annotation_bbox is correct region
        tf.debugging.assert_less_equal(tf.reduce_sum(tf.abs(
            annotation_cropped[30::70, 6::100] - tf.constant([[[0., 0., 0.],
                                                               [1., 0., 1.]],
                                                              [[1., 0., 0.],
                                                               [1., 0., 0.]]], dtype=tf.float32))), 1e-4)

        # test that bboxes match
        tf.debugging.assert_less_equal(tf.reduce_sum(
            tf.abs(tf.convert_to_tensor(annotation_cropped.shape)[:2] - tf.convert_to_tensor(image_cropped.shape)[:2])), 0)



if __name__ == '__main__':
    unittest.main()
