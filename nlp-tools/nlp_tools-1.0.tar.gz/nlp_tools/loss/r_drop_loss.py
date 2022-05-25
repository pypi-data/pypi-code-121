from tensorflow.keras.losses import kullback_leibler_divergence as kld
from tensorflow.keras import backend as K
import tensorflow as tf


class RDropLoss():
    # https://spaces.ac.cn/archives/8496
    __name__ ="r_drop_loss"
    def __init__(self,loss_func=None):
        self.loss_func = loss_func

    def __call__(self,y_true, y_pred,alpha=4):
        """配合上述生成器的R-Drop Loss
            其实loss_kl的除以4，是为了在数量上对齐公式描述结果。
            """
        loss = self.loss_func(y_true, y_pred)  # 原来的loss
        loss_kl = kld(y_pred[::2], y_pred[1::2]) + kld(y_pred[1::2], y_pred[::2])
        return loss + K.mean(loss_kl) / 4 * alpha

