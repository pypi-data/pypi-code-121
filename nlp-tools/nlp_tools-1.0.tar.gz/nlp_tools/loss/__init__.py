from tensorflow import keras
import tensorflow as tf
#import tensorflow.keras.backend as K
import numpy as np

#from bert4keras.layers import Loss
#from bert4keras.backend import search_layer

import tensorflow.python.keras.backend as K



def contrastive_loss(y_true, y_pred):
    '''Contrastive loss from Hadsell-et-al.'06
        http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf
        '''
    margin = 1
    sqaure_pred = tf.square(y_pred)
    margin_square = tf.square(tf.maximum(margin - y_pred, 0))
    return tf.reduce_mean(y_true * sqaure_pred + (1 - y_true) * margin_square)


class TextGenerateCrossEntropy():#(Loss):
    """交叉熵作为loss，并mask掉输入部分
     """
    def compute_loss(self, inputs, mask=None):
        y_true, y_mask, y_pred = inputs
        y_true = y_true[:, 1:]  # 目标token_ids
        y_mask = y_mask[:, 1:]  # segment_ids，刚好指示了要预测的部分
        y_pred = y_pred[:, :-1]  # 预测序列，错开一位
        loss = K.sparse_categorical_crossentropy(y_true, y_pred)
        loss = K.sum(loss * y_mask) / K.sum(y_mask)
        return loss


def categorical_focal_loss(alpha=0.25, gamma=2.):
    """
        Softmax version of focal loss.
        When there is a skew between different categories/labels in your data set, you can try to apply this function as a
        loss.
               m
          FL = ∑  -alpha * (1 - p_o,c)^gamma * y_o,c * log(p_o,c)
              c=1
          where m = number of classes, c = class and o = observation
        Parameters:
          alpha -- the same as weighing factor in balanced cross entropy. Alpha is used to specify the weight of different
          categories/labels, the size of the array needs to be consistent with the number of classes.
          gamma -- focusing parameter for modulating factor (1-p)
        Default value:
          gamma -- 2.0 as mentioned in the paper
          alpha -- 0.25 as mentioned in the paper
        References:
            Official paper: https://arxiv.org/pdf/1708.02002.pdf
            https://www.tensorflow.org/api_docs/python/tf/keras/backend/categorical_crossentropy
        Usage:
         model.compile(loss=[categorical_focal_loss(alpha=[[.25, .25, .25]], gamma=2)], metrics=["accuracy"], optimizer=adam)
        """
    alpha = np.array(alpha, dtype=np.float32)

    def categorical_focal_loss_fixed(y_true, y_pred):
        """
            :param y_true: A tensor of the same shape as `y_pred`
            :param y_pred: A tensor resulting from a softmax
            :return: Output tensor.
            """
        bh = K.prod(K.shape(y_pred)[:-1])
        y_true = K.reshape(y_true, (bh, -1))
        y_pred = K.reshape(y_pred, (bh, -1))


        # Clip the prediction value to prevent NaN's and Inf's
        epsilon = K.epsilon()
        y_pred = K.clip(y_pred,epsilon,1. - epsilon)

        # Calculate Cross Entropy
        y_true = K.cast(y_true,K.floatx())
        cross_entropy = -y_true * K.log(y_pred)

        # Calculate Focal Loss
        loss =  K.pow(1 - y_pred, gamma) * cross_entropy

        # Compute mean loss in mini_batch
        return K.mean(K.sum(loss,axis=-1))

    return categorical_focal_loss_fixed


class mutilplyLoss():
    __name__ = "mutilplyLoss"
    def __init__(self,loss_funs, epsilon=1):
        self.epsilon = epsilon
        self.loss_funs = loss_funs

    def __call__(self,y_true, y_pred):
        """带梯度惩罚的loss
        """
        loss = self.loss_funs(y_true, y_pred)
        embeddings = search_layer(y_pred, 'Embedding-Token').embeddings
        gp = K.sum(K.gradients(loss, [embeddings])[0].values ** 2)
        return loss + 0.5 * self.epsilon * gp


def loss_with_gradient_penalty(model,loss_func,epsilon=1):
    def loss_with_gradient_penalty_2(y_true, y_pred):
        loss = tf.math.reduce_mean(loss_func(y_true, y_pred))
        embeddings = search_layer(model, 'Embedding-Token').embeddings
        gp = tf.math.reduce_sum(tf.gradients(loss, [embeddings])[0].values**2)
        return loss + 0.5 * epsilon * gp
    return loss_with_gradient_penalty_2


def multi_category_focal_loss2(gamma=2., alpha=1):
    """
    focal loss for multi category of multi label problem
    适用于多分类或多标签问题的focal loss
    alpha控制真值y_true为1/0时的权重
        1的权重为alpha, 0的权重为1-alpha
    当你的模型欠拟合，学习存在困难时，可以尝试适用本函数作为loss
    当模型过于激进(无论何时总是倾向于预测出1),尝试将alpha调小
    当模型过于惰性(无论何时总是倾向于预测出0,或是某一个固定的常数,说明没有学到有效特征)
        尝试将alpha调大,鼓励模型进行预测出1。
    Usage:
     model.compile(loss=[multi_category_focal_loss2(alpha=0.25, gamma=2)], metrics=["accuracy"], optimizer=adam)
    """
    epsilon = 1.e-7
    gamma = float(gamma)
    alpha = tf.constant(alpha, dtype=tf.float32)

    def multi_category_focal_loss2_fixed(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.clip_by_value(y_pred, epsilon, 1. - epsilon)

        alpha_t = y_true * alpha + (tf.ones_like(y_true) - y_true) * (1 - alpha)
        y_t = tf.multiply(y_true, y_pred) + tf.multiply(1 - y_true, 1 - y_pred)
        ce = -K.log(y_t)
        weight = tf.pow(tf.subtract(1., y_t), gamma)
        fl = tf.multiply(tf.multiply(weight, ce), alpha_t)
        loss = tf.reduce_mean(fl)
        return loss

    return multi_category_focal_loss2_fixed


def multi_category_focal_loss2_fixed(y_true, y_pred):
    epsilon = 1.e-7
    gamma=2.
    alpha = tf.constant(0.5, dtype=tf.float32)

    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.clip_by_value(y_pred, epsilon, 1. - epsilon)

    alpha_t = y_true*alpha + (tf.ones_like(y_true)-y_true)*(1-alpha)
    y_t = tf.multiply(y_true, y_pred) + tf.multiply(1-y_true, 1-y_pred)
    ce = -K.log(y_t)
    weight = tf.pow(tf.subtract(1., y_t), gamma)
    fl = tf.multiply(tf.multiply(weight, ce), alpha_t)
    loss = tf.reduce_mean(fl)
    return loss
