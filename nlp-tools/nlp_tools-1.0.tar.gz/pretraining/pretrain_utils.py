from bert4keras.models import build_transformer_model
from bert4keras.backend import keras, K
from bert4keras.optimizers import Adam
from bert4keras.optimizers import extend_with_weight_decay
from bert4keras.optimizers import extend_with_layer_adaptation
from bert4keras.optimizers import extend_with_piecewise_linear_lr
from bert4keras.optimizers import extend_with_gradient_accumulation
from keras.layers import Input, Lambda
from keras.models import Model

from tensorflow.keras import  backend as K


floatx = K.floatx()

def build_transformer_model_with_mlm(config_path):
    """带mlm的bert模型
    """
    bert = build_transformer_model(
        config_path, with_mlm='linear', return_keras_model=False
    )
    proba = bert.model.output

    # 辅助输入
    token_ids = Input(shape=(None,), dtype='int64', name='token_ids')  # 目标id
    is_masked = Input(shape=(None,), dtype=floatx, name='is_masked')  # mask标记

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
        y_true = K.cast(y_true, floatx)
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


def build_transformer_model_with_lm(config_path):
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
            mask = K.cast(mask[1][:, 1:], floatx)

        loss = K.sparse_categorical_crossentropy(
            y_true, y_pred, from_logits=True
        )
        loss = K.sum(loss * mask) / (K.sum(mask) + K.epsilon())
        return loss

    def lm_acc(inputs, mask=None):
        """计算准确率的函数，需要封装为一个层
        """
        y_true, y_pred = inputs
        y_true, y_pred = K.cast(y_true[:, 1:], floatx), y_pred[:, :-1]

        if mask is None:
            mask = 1.0
        else:
            mask = K.cast(mask[1][:, 1:], floatx)

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


def build_transformer_model_with_unilm(config_path):
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
            mask = K.cast(mask[1][:, 1:], floatx)

        segment_ids = K.cast(segment_ids, floatx)
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
        y_true, y_pred = K.cast(y_true[:, 1:], floatx), y_pred[:, :-1]

        if mask is None:
            mask = 1.0
        else:
            mask = K.cast(mask[1][:, 1:], floatx)

        segment_ids = K.cast(segment_ids, floatx)
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


def build_transformer_model_for_pretraining(model,model_config,model_ckpt):
    """构建训练模型，通用于TPU/GPU
    注意全程要用keras标准的层写法，一些比较灵活的“移花接木”式的
    写法可能会在TPU上训练失败。此外，要注意的是TPU并非支持所有
    tensorflow算子，尤其不支持动态（变长）算子，因此编写相应运算
    时要格外留意。
    """
    learning_rate = 0.00176
    weight_decay_rate = 0.01
    grad_accum_steps = 16  # 大于1即表明使用梯度累积
    which_optimizer = 'lamb'  # adam 或 lamb，均自带weight decay
    exclude_from_weight_decay = ['Norm', 'bias']
    exclude_from_layer_adaptation = ['Norm', 'bias']
    num_train_steps = 125000
    num_warmup_steps = 3125

    lr_schedule = {
        num_warmup_steps * grad_accum_steps: 1.0,
        num_train_steps * grad_accum_steps: 0.0,
    }

    if model == 'roberta':
        bert, train_model, loss = build_transformer_model_with_mlm(model_config)
    elif model == 'gpt':
        bert, train_model, loss = build_transformer_model_with_lm(model_config)
    elif model == 'unilm':
        bert, train_model, loss = build_transformer_model_with_unilm(model_config)
    else:
        raise ValueError("Not support")

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
    if model_ckpt is not None:
        bert.load_weights_from_checkpoint(model_ckpt)

    return bert,train_model