import tensorflow as tf


def heaviside(x, n: float = 0.5):
    return tf.cast(x >= n, tf.float32)


def differentiable_binary(x, gamma: int = 20, T: float = 0.5):
    """Approximately binarize the input with a differentiable function.

    Contour Loss for Instance Segmentation via k-step Distance
    Transformation Image, Guo et al., 2021

    Parameters
    ----------
    x : tf.Tensor
        The input to binarize.
    gamma : int
        The slope.
    T : float
        Threshold value.

    Returns
    -------
    tf.Tensor

    Examples
    --------
    FIXME: Add docs.
    """
    return 1. / (1 + tf.math.exp(-gamma * (x - T)))

