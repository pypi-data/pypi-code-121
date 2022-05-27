import unittest
import tensorflow as tf
import tensorflow_addons as tfa

from brevettiai.tests import get_resource


from brevettiai.data.image import ImagePipeline, ImageLoader, CropResizeProcessor
from brevettiai.data.tf_types import BBOX

SAMPLE_IMAGE_PATH = "0_1543413266626.bmp"

class TestImageLoaderBbox(unittest.TestCase):
    test_image_path = get_resource(SAMPLE_IMAGE_PATH)
    bbox = BBOX(x1=10, x2=210, y1=30, y2=130)

    def test_loader_with_bbox(self):
        bbox_loader = ImageLoader(interpolation_method="nearest")
        image_bbox, _ = bbox_loader.load(self.test_image_path, bbox=self.bbox)
        image_raw, _ = ImageLoader(interpolation_method="nearest").load(self.test_image_path)

        # Test that image_bbox is correct region
        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(
            image_bbox -
            image_raw[self.bbox.y1:self.bbox.y2 + 1, self.bbox.x1:self.bbox.x2 + 1])), 1e-4)


class TestCropResizeProcessor(unittest.TestCase):
    test_image_path = get_resource(SAMPLE_IMAGE_PATH)

    def test_loader_affine_transform(self):
        image_loader = ImageLoader()
        image, _ = image_loader.load(self.test_image_path)

        processor = CropResizeProcessor(output_height=120, output_width=150,
                                        roi_vertical_offset=45, roi_horizontal_offset=37,
                                        interpolation="bilinear")

        output_shape = image_loader.output_shape()
        image_loader.postprocessor = processor
        output_shape_postproc = image_loader.output_shape()
        assert output_shape[-2] is None and output_shape_postproc[-2] == 150

        # Run on processor
        img_out = processor.process(image)

        # Run with tfa.image.transform
        input_height, input_width = tf.shape(image)[:2]
        tr = tfa.image.transform_ops.matrices_to_flat_transforms(processor.affine_transform(input_height, input_width))
        img2 = tfa.image.transform(tf.cast(image, tf.float32), tf.cast(tr, tf.float32), processor.interpolation,
                                   output_shape=processor.output_size(input_height, input_width))

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(img_out - img2)), 1e-4)


class TestImagePipelineToImageLoaderConversion(unittest.TestCase):
    test_image_path = get_resource(SAMPLE_IMAGE_PATH)

    def test_ensure_default_settings(self):
        ip = ImagePipeline()

        sample = {"path": tf.constant([self.test_image_path])}
        ip_image = ip(sample)["img"][0]

        loader_image, _ = ip.to_image_loader().load(self.test_image_path)

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(loader_image-ip_image)), 0.0)

    def test_ensure_target_size(self):
        ip = ImagePipeline(target_size=(120, 150))

        sample = {"path": tf.constant([self.test_image_path])}
        ip_image = ip(sample)["img"][0]

        loader_image, _ = ip.to_image_loader().load(self.test_image_path)

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(loader_image-ip_image)), 2.0)

    def test_ensure_roi(self):
        ip = ImagePipeline(rois=(((10, 10), (50, 70)),))

        sample = {"path": tf.constant([self.test_image_path])}
        ip_image = ip(sample)["img"][0]

        loader_image, _ = ip.to_image_loader().load(self.test_image_path)

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(loader_image - ip_image)), 1e-5)

    def test_ensure_roi_and_target_size(self):
        ip = ImagePipeline(rois=(((10, 10), (50, 70)),), target_size=(90, 70))

        sample = {"path": tf.constant([self.test_image_path])}
        ip_image = ip(sample)["img"][0]

        loader_image, _ = ip.to_image_loader().load(self.test_image_path)

        tf.debugging.assert_less_equal(tf.reduce_mean(tf.abs(loader_image-ip_image)), 2.0)


if __name__ == '__main__':
    unittest.main()
