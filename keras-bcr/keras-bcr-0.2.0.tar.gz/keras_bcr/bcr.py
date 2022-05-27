import tensorflow as tf


def batch_corr(a, b, tol: float = 1e-8):
    """ Average of absolute correlations coefficients
         for each neuron across a batch.

    Parameters:
    -----------
    a : tf.tensor
        The output of the ResNet layer before the skip connection

    b : tf.tensor
        The input for the ResNet Layer

    Example:
    --------
    import numpy as np
    BATCH_SIZE = 100
    NUM_NEURONS = 1024
    a = np.random.random((BATCH_SIZE, NUM_NEURONS))
    b = np.random.random((BATCH_SIZE, NUM_NEURONS))
    bcr = batch_corr(a, b)
    """
    # compute pearson' rhos
    mu_a = tf.reduce_mean(a, axis=0)
    mu_b = tf.reduce_mean(b, axis=0)
    centered_a = a - mu_a
    centered_b = b - mu_b
    nomin = tf.reduce_sum(tf.multiply(centered_a, centered_b), axis=0)
    denom1 = tf.math.sqrt(tf.reduce_sum(tf.math.pow(centered_a, 2), axis=0))
    denom2 = tf.math.sqrt(tf.reduce_sum(tf.math.pow(centered_b, 2), axis=0))
    rhos = nomin / (denom1 * denom2 + tol)
    # take the mean of absolute rhos
    return tf.math.reduce_mean(tf.math.abs(rhos))


class BatchCorrRegularizer(tf.keras.layers.Layer):
    """ Batch Correlation Regularizer

    Parameters:
    -----------
    bcr_rate : float (Default: 1e-6)
        The factor how much BCR regularization contributes to the loss function

    Example:
    --------
    The BatchCorrRegularizer must be integrated within a ResNet block. It
      cannot be attached between ResNet layers. Here is an example how to
      design a ResNet block using the Keras Functional API

    def ...(self, inputs, ...):
        h = tf.keras.Dense(...)(h)
        h = h = tf.keras.layers.Activation(...)(h)
        h = tf.keras.layers.Dropout(...)(h)
        h = BatchCorrRegularizer(bcr_rate)([h, inputs])
        outputs = tf.keras.layers.Add(...)([h, inputs])
        return outputs
    """
    def __init__(self, bcr_rate: float = 1e-6):
        super(BatchCorrRegularizer, self).__init__()
        self.bcr_rate = bcr_rate

    def call(self, inputs):
        lout, linp = inputs
        loss = self.bcr_rate * batch_corr(
            tf.keras.layers.Flatten()(lout),
            tf.keras.layers.Flatten()(linp)
        )
        self.add_loss(loss)
        self.add_metric(loss, name="batch_corr_regularizer")
        return lout
