#! -*- coding: utf-8 -*-
# 预训练脚本，多GPU版/TPU版本

import os

os.environ['TF_KERAS'] = '1'  # 必须使用tf.keras

from bert4keras.models import build_transformer_model
from bert4keras.backend import keras, K
from bert4keras.optimizers import Adam
from bert4keras.optimizers import extend_with_weight_decay
from bert4keras.optimizers import extend_with_layer_adaptation
from bert4keras.optimizers import extend_with_piecewise_linear_lr
from bert4keras.optimizers import extend_with_gradient_accumulation
from keras.layers import Input, Lambda
from keras.models import Model
from keras.callbacks import Callback


def build_transformer_model_with_mlm(config_path,data_dtype):
    """带mlm的bert模型
    """
    bert = build_transformer_model(
        config_path, with_mlm='linear', return_keras_model=False
    )
    proba = bert.model.output

    # 辅助输入
    token_ids = Input(shape=(None,), dtype='int64', name='token_ids')  # 目标id
    is_masked = Input(shape=(None,), dtype=data_dtype, name='is_masked')  # mask标记

    def mlm_loss(inputs):
        """计算loss的函数，需要封装为一个层
        """
        y_true, y_pred, mask = inputs
        loss = K.sparse_categorical_crossentropy(
            y_true, y_pred, from_logits=True
        )
        loss = K.sum(loss * mask) / (K.sum(mask) + K.epsilon())
        return loss

    def mlm_acc(inputs):
        """计算准确率的函数，需要封装为一个层
        """
        y_true, y_pred, mask = inputs
        y_true = K.cast(y_true, data_dtype)
        acc = keras.metrics.sparse_categorical_accuracy(y_true, y_pred)
        acc = K.sum(acc * mask) / (K.sum(mask) + K.epsilon())
        return acc

    mlm_loss = Lambda(mlm_loss, name='mlm_loss')([token_ids, proba, is_masked])
    mlm_acc = Lambda(mlm_acc, name='mlm_acc')([token_ids, proba, is_masked])

    train_model = Model(
        bert.model.inputs + [token_ids, is_masked], [mlm_loss, mlm_acc]
    )

    loss = {
        'mlm_loss': lambda y_true, y_pred: y_pred,
        'mlm_acc': lambda y_true, y_pred: K.stop_gradient(y_pred),
    }

    return bert, train_model, loss


def build_transformer_model_with_lm(config_path,data_dtype):
    """带lm的bert模型
    """
    bert = build_transformer_model(
        config_path,
        with_mlm='linear',
        application='lm',
        return_keras_model=False
    )
    token_ids = bert.model.inputs[0]
    proba = bert.model.output

    def lm_loss(inputs, mask=None):
        """计算loss的函数，需要封装为一个层
        """
        y_true, y_pred = inputs
        y_true, y_pred = y_true[:, 1:], y_pred[:, :-1]

        if mask is None:
            mask = 1.0
        else:
            mask = K.cast(mask[1][:, 1:], data_dtype)

        loss = K.sparse_categorical_crossentropy(
            y_true, y_pred, from_logits=True
        )
        loss = K.sum(loss * mask) / (K.sum(mask) + K.epsilon())
        return loss

    def lm_acc(inputs, mask=None):
        """计算准确率的函数，需要封装为一个层
        """
        y_true, y_pred = inputs
        y_true, y_pred = K.cast(y_true[:, 1:], data_dtype), y_pred[:, :-1]

        if mask is None:
            mask = 1.0
        else:
            mask = K.cast(mask[1][:, 1:], data_dtype)

        acc = keras.metrics.sparse_categorical_accuracy(y_true, y_pred)
        acc = K.sum(acc * mask) / (K.sum(mask) + K.epsilon())
        return acc

    lm_loss = Lambda(lm_loss, name='lm_loss')([token_ids, proba])
    lm_acc = Lambda(lm_acc, name='lm_acc')([token_ids, proba])

    train_model = Model(bert.model.inputs, [lm_loss, lm_acc])

    loss = {
        'lm_loss': lambda y_true, y_pred: y_pred,
        'lm_acc': lambda y_true, y_pred: K.stop_gradient(y_pred),
    }

    return bert, train_model, loss


def build_transformer_model_with_unilm(config_path,data_dtype):
    """带unilm的bert模型
    """
    bert = build_transformer_model(
        config_path,
        with_mlm='linear',
        application='unilm',
        return_keras_model=False
    )
    token_ids = bert.model.inputs[0]
    segment_ids = bert.model.inputs[1]
    proba = bert.model.output

    def unilm_loss(inputs, mask=None):
        """计算loss的函数，需要封装为一个层
        """
        y_true, y_pred, segment_ids = inputs
        y_true, y_pred = y_true[:, 1:], y_pred[:, :-1]

        if mask is None:
            mask = 1.0
        else:
            mask = K.cast(mask[1][:, 1:], data_dtype)

        segment_ids = K.cast(segment_ids, data_dtype)
        mask = mask * segment_ids[:, 1:]

        loss = K.sparse_categorical_crossentropy(
            y_true, y_pred, from_logits=True
        )
        loss = K.sum(loss * mask) / (K.sum(mask) + K.epsilon())
        return loss

    def unilm_acc(inputs, mask=None):
        """计算准确率的函数，需要封装为一个层
        """
        y_true, y_pred, segment_ids = inputs
        y_true, y_pred = K.cast(y_true[:, 1:], data_dtype), y_pred[:, :-1]

        if mask is None:
            mask = 1.0
        else:
            mask = K.cast(mask[1][:, 1:], data_dtype)

        segment_ids = K.cast(segment_ids, data_dtype)
        mask = mask * segment_ids[:, 1:]

        acc = keras.metrics.sparse_categorical_accuracy(y_true, y_pred)
        acc = K.sum(acc * mask) / (K.sum(mask) + K.epsilon())
        return acc

    token_proba_segment = [token_ids, proba, segment_ids]
    unilm_loss = Lambda(unilm_loss, name='unilm_loss')(token_proba_segment)
    unilm_acc = Lambda(unilm_acc, name='unilm_acc')(token_proba_segment)

    train_model = Model(bert.model.inputs, [unilm_loss, unilm_acc])

    loss = {
        'unilm_loss': lambda y_true, y_pred: y_pred,
        'unilm_acc': lambda y_true, y_pred: K.stop_gradient(y_pred),
    }

    return bert, train_model, loss


def build_transformer_model_for_pretraining(config_path,data_dtype,which_optimizer,learning_rate,lr_schedule,weight_decay_rate,exclude_from_weight_decay,exclude_from_layer_adaptation,grad_accum_steps,checkpoint_path,pretrained_model_type):
    """构建训练模型，通用于TPU/GPU
    注意全程要用keras标准的层写法，一些比较灵活的“移花接木”式的
    写法可能会在TPU上训练失败。此外，要注意的是TPU并非支持所有
    tensorflow算子，尤其不支持动态（变长）算子，因此编写相应运算
    时要格外留意。
    """
    if pretrained_model_type == 'roberta':
        bert, train_model, loss = build_transformer_model_with_mlm(config_path,data_dtype)
    elif pretrained_model_type == 'gpt':
        bert, train_model, loss = build_transformer_model_with_lm(config_path,data_dtype)
    elif pretrained_model_type == 'unilm':
        bert, train_model, loss = build_transformer_model_with_unilm(config_path,data_dtype)

    # 优化器
    optimizer = extend_with_weight_decay(Adam)
    if which_optimizer == 'lamb':
        optimizer = extend_with_layer_adaptation(optimizer)
    optimizer = extend_with_piecewise_linear_lr(optimizer)
    optimizer_params = {
        'learning_rate': learning_rate,
        'lr_schedule': lr_schedule,
        'weight_decay_rate': weight_decay_rate,
        'exclude_from_weight_decay': exclude_from_weight_decay,
        'exclude_from_layer_adaptation': exclude_from_layer_adaptation,
        'bias_correction': False,
    }
    if grad_accum_steps > 1:
        optimizer = extend_with_gradient_accumulation(optimizer)
        optimizer_params['grad_accum_steps'] = grad_accum_steps
    optimizer = optimizer(**optimizer_params)

    # 模型定型
    train_model.compile(loss=loss, optimizer=optimizer)

    # 如果传入权重，则加载。注：须在此处加载，才保证不报错。
    if checkpoint_path is not None:
        bert.load_weights_from_checkpoint(checkpoint_path)

    return train_model,bert





class ModelCheckpoint(keras.callbacks.Callback):
    """自动保存最新模型
    """
    def __init__(self,model_saved_path,bert_instance):
        super(ModelCheckpoint,self).__init__()
        self.model_saved_path = model_saved_path
        self.bert_instance = bert_instance

    def on_epoch_end(self, epoch,logs=None):
        self.bert_instance.save_weights_as_checkpoint(self.model_saved_path)



