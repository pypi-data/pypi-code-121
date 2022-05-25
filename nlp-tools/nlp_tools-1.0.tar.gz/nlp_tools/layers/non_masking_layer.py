from tensorflow.keras.layers import Layer
from tensorflow.keras import backend as K
import nlp_tools
import tensorflow as tf

class NonMaskingLayer(Layer):
    def __init__(self,**kwargs):
        self.supports_masking = True
        super(NonMaskingLayer,self).__init__(**kwargs)

    def build(self, input_shape):
        pass

    def compute_mask(self, inputs, mask=None):
        return None
    def call(self,x,mask=None):
        return x


class MaskingSaverLayer(Layer):
    def __init__(self,**kwargs):
        self.supports_masking = True
        self.mask = None
        self.loss_func = None
        super(MaskingSaverLayer,self).__init__(**kwargs)

    def build(self, input_shape):
        pass

    def compute_mask(self, inputs, mask=None):
        return None
    def call(self,x,mask=None):
        self.mask = mask
        return x
    def set_loss_func(self,loss_func):
        self.loss_func = loss_func
    def loss(self, y_true, y_pred):
        loss_ = self.loss_func(y_true, y_pred)
        mask = tf.cast(self.mask, dtype=loss_.dtype)  # 将前面统计的是否零转换成1，0的矩阵
        loss_ *= mask  # 将正常计算的loss加上mask的权重，就剔除了padding 0的影响
        loss_ = tf.math.divide_no_nan(tf.reduce_sum(loss_, axis=-1), tf.reduce_sum(mask, axis=-1))
        return loss_



nlp_tools.custom_objects['NonMaskingLayer'] = NonMaskingLayer
nlp_tools.custom_objects['MaskingSaverLayer'] = MaskingSaverLayer