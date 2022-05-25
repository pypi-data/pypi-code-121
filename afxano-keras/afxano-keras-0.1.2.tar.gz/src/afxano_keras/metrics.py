from tensorflow import keras


class AvgMetric(keras.metrics.Metric):
    """Meta class for computing metrics, averaging over a dataset"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.val = self.add_weight(name="val", initializer="zero")
        self.steps = self.add_weight(name="step", initializer="zero")

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.val = self.val.assign_add(self(y_true, y_pred, sample_weight))
        self.steps = self.steps.assign_add(tf.cast(tf.shape(y_pred)[0], "float32"))

    def result(self):
        return self.val / self.steps

    def reset_state(self):
        self.val.assign(0)
        self.steps.assign(0)

    def __call__(self, y_true, y_pred, sample_weight=None):
        raise NotImplementedError()


class PSNR(AvgMetric):
    """Calculate the PSNR -- Signal to Noise Ratio, averaging over the dataset."""

    def __init__(self, name="psnr", max_val: float = 1.0, **kwargs):
        super().__init__(name=name, **kwargs)
        self.max_val = max_val

    def __call__(self, y_true, y_pred, sample_weight=None):
        del sample_weight
        return tf.reduce_sum(tf.image.psnr(y_true, y_pred, max_val=self.max_val))


class SSIM(AvgMetric):
    """Calculate the SSIM, averaging over the dataset."""

    def __init__(self, name="ssim", max_val: float = 1.0, **kwargs) -> None:
        super().__init__(name=name, **kwargs)
        self.max_val = max_val

    def __call__(self, y_true, y_pred, sample_weight=None):
        del sample_weight
        return tf.reduce_sum(tf.image.ssim(y_true, y_pred, self.max_val))


class MAE(AvgMetric):
    def __init__(self, name="mae", **kwargs) -> None:
        super().__init__(name=name, **kwargs)

    def __call__(self, y_true, y_pred, sample_weight=None):
        del sample_weight
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.cast(y_pred, tf.float32)
        return tf.reduce_mean(keras.metrics.mean_absolute_error(y_true, y_pred))
