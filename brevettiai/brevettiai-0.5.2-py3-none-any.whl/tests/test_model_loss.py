import unittest
import tensorflow as tf
import h5py
from io import BytesIO

from brevettiai.model.losses import WeightedLossFactory, WeightedLoss


class TestModelLoss(unittest.TestCase):
    loss_settings = {
        "label_smoothing": .05,
        "sample_weights": [[1.0], [1.0], [0.2]],
        "sample_weights_bias": [0.0]}
    y_true = tf.eye(4, 3)[None, None]
    y_pred = tf.ones((4, 3))[None, None] * .3

    def test_weighted_loss(self):
        loss_configurator = WeightedLossFactory.parse_obj(self.loss_settings)
        loss_fun = loss_configurator.get_loss(reduction='NONE')
        mm = tf.keras.models.Sequential(tf.keras.layers.InputLayer(input_shape=self.y_true.shape[1:]))
        mm.compile("adam", loss_fun)
        h5_file = BytesIO()
        with h5py.File(h5_file, "w") as fp:
            mm.save(fp)
        with h5py.File(h5_file, "r") as fp:
            deserialized = tf.keras.models.load_model(fp, custom_objects={"WeightedLoss": WeightedLoss})

        loss = deserialized(self.y_true, self.y_pred)
        assert(loss.shape[-1] == 3 and loss.shape[-2] == 4)


if __name__ == '__main__':
    unittest.main()
