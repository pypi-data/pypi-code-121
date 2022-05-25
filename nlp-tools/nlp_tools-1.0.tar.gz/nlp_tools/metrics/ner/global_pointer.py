from tensorflow.keras import backend as K
from tensorflow.python.keras.metrics import MeanMetricWrapper
import tensorflow as tf

@tf.keras.utils.register_keras_serializable(package='nlp_tools',name='GlobalPointerF1Score')
def global_pointer_f1_score(y_true, y_pred):
    """给GlobalPointer设计的F1
    """
    y_pred = K.cast(K.greater(y_pred, 0), K.floatx())
    return 2 * K.sum(y_true * y_pred) / K.sum(y_true + y_pred)

# @tf.keras.utils.register_keras_serializable(package='nlp_tools',name='GlobalPointerF1Score')
# class GlobalPointerF1Score():
#     def __init__(self, name='global_pointer_f1_score', dtype=None):
#         super(GlobalPointerF1Score, self).__init__(global_pointer_f1_score, name, dtype=dtype)

