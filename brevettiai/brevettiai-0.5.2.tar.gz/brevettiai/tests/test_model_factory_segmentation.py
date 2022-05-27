import unittest
import tensorflow as tf

from brevettiai.model.factory.segmentation import SegmentationModelFactory
from brevettiai.model.factory.mobilenetv2_backbone \
    import lightning_segmentation_backbone
from brevettiai.model.factory.lraspp import LRASPP2SegmentationHead



class TestModelFactory(unittest.TestCase):
    segmentation_model_settings = dict(segmentation_model={"resize_output": True},
                                       backbone_factory=lightning_segmentation_backbone(),
                                       head_factory=LRASPP2SegmentationHead(),
                                       classes=["dummy1", "dummy2"])

    def test_model_factory(self):
        segmentation_model_factory = SegmentationModelFactory.parse_obj(self.segmentation_model_settings)
        segmentation_model = segmentation_model_factory.build(input_shape=(None, None, 3))
        assert(isinstance(segmentation_model, tf.keras.models.Model))


if __name__ == '__main__':
    unittest.main()

