import tensorflow.keras.backend as K
import tensorflow as tf

class MaskLoss():
    def __init__(self,mask,loss_func):
        self.mask = mask
        self.loss_func = loss_func


    def __call__(self, y_true, y_pred):
        loss_ = self.loss_func(y_true,y_pred)
        mask = tf.cast(self.mask, dtype=loss_.dtype)  # 将前面统计的是否零转换成1，0的矩阵
        loss_ *= mask  # 将正常计算的loss加上mask的权重，就剔除了padding 0的影响
        loss_ = tf.math.divide_no_nan(tf.reduce_sum(loss_, axis=-1), tf.reduce_sum(mask, axis=-1))

        return  loss_