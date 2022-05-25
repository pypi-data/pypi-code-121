import tensorflow.keras.backend as K
import tensorflow as tf


@tf.keras.utils.register_keras_serializable(package='nlp_tools')
def multilabel_categorical_crossentropy(y_true,y_pred):
    """多标签分类的交叉熵
        说明：
            1. y_true和y_pred的shape一致，y_true的元素非0即1，
               1表示对应的类为目标类，0表示对应的类为非目标类；
            2. 请保证y_pred的值域是全体实数，换言之一般情况下
               y_pred不用加激活函数，尤其是不能加sigmoid或者
               softmax；
            3. 预测阶段则输出y_pred大于0的类；
            4. 详情请看：https://kexue.fm/archives/7359 。
        """

    y_pred = (1 -2 *y_true) * y_pred
    y_pred_neg = y_pred - y_true * 1e12
    y_pred_pos = y_pred - (1 - y_true) * 1e12
    zeros = K.zeros_like(y_pred[...,:1])
    y_pred_neg = K.concatenate([y_pred_neg,zeros],axis=-1)
    y_pred_pos = K.concatenate([y_pred_pos,zeros],axis=-1)
    neg_loss = tf.reduce_logsumexp(y_pred_neg,axis=-1)
    pos_loss = tf.reduce_logsumexp(y_pred_pos,axis=-1)
    return neg_loss + pos_loss

@tf.keras.utils.register_keras_serializable(package='nlp_tools')
def global_pointer_crossentropy(y_true,y_pred):
    """给GlobalPointer设计的交叉熵
        其实就是将多维度的多分类【B,N，R,C】 变成 【B*N*R,C】，然后在调用multilabel_categorical_crossentropy
        """
    bh = K.prod(K.shape(y_pred)[:2])
    y_true = K.reshape(y_true,(bh, -1))
    y_pred = K.reshape(y_pred,(bh, -1))
    return K.mean(multilabel_categorical_crossentropy(y_true,y_pred))

