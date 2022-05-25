from pretraining.pretraining import *
from pretraining.pretrain_data_utils import *

prtrained_model_type = 'roberta'

def load_training_tfrecord(pretrained_model_type,tf_corpus_paths,batch_size,grad_accum_steps,sequence_length):
    if pretrained_model_type == 'roberta':
        dataset = TrainingDatasetRoBERTa.load_tfrecord(
            record_names=tf_corpus_paths,
            sequence_length=sequence_length,
            batch_size=batch_size // grad_accum_steps,
        )

    elif pretrained_model_type == 'gpt':
        dataset = TrainingDatasetGPT.load_tfrecord(
            record_names=tf_corpus_paths,
            sequence_length=sequence_length,
            batch_size=batch_size // grad_accum_steps,
        )

    elif pretrained_model_type == 'unilm':

        dataset = TrainingDatasetUniLM.load_tfrecord(
            record_names=tf_corpus_paths,
            sequence_length=sequence_length,
            batch_size=batch_size // grad_accum_steps,
            token_sep_id=3,  # 这里需要自己指定[SEP]的id
        )
    else:
        raise ValueError("Not support")
    return dataset


def start_pretrained(
        model_saved_path,
        tf_record_path,
        bert_config_path,
        bert_checkpoint_path,# 如果从零训练，就设为None
        batch_size = 256,
        pretrained_model_type = 'roberta',
        tpu_address = None

):
    '''

    '''
    corpus_paths = []
    for file in os.listdir(tf_record_path):
        corpus_paths.append(os.path.join(tf_record_path, file))

    # 其他配置7
    sequence_length = 512
    learning_rate = 0.00176
    weight_decay_rate = 0.01
    num_warmup_steps = 3125
    num_train_steps = 125000
    steps_per_epoch = 10000
    grad_accum_steps = 16  # 大于1即表明使用梯度累积
    epochs = num_train_steps * grad_accum_steps // steps_per_epoch
    exclude_from_weight_decay = ['Norm', 'bias']
    exclude_from_layer_adaptation = ['Norm', 'bias']
    which_optimizer = 'lamb'  # adam 或 lamb，均自带weight decay
    lr_schedule = {
        num_warmup_steps * grad_accum_steps: 1.0,
        num_train_steps * grad_accum_steps: 0.0,
    }
    floatx = K.floatx()

    dataset = load_training_tfrecord(pretrained_model_type,corpus_paths,batch_size,grad_accum_steps,sequence_length)

    if tpu_address is None:
        # 单机多卡模式（多机多卡也类似，但需要硬软件配合，请参考https://tf.wiki）
        strategy = tf.distribute.MirroredStrategy()
    else:
        # TPU模式
        resolver = tf.distribute.cluster_resolver.TPUClusterResolver(
            tpu=tpu_address
        )
        tf.config.experimental_connect_to_host(resolver.master())
        tf.tpu.experimental.initialize_tpu_system(resolver)
        strategy = tf.distribute.experimental.TPUStrategy(resolver)

    with strategy.scope():
        train_model,bert_instance = build_transformer_model_for_pretraining(
            config_path=bert_config_path,
            data_dtype=floatx,
            which_optimizer=which_optimizer,
            learning_rate=learning_rate,
            lr_schedule=lr_schedule,
            weight_decay_rate=weight_decay_rate,
            exclude_from_weight_decay=exclude_from_weight_decay,
            exclude_from_layer_adaptation=exclude_from_layer_adaptation,
            grad_accum_steps=grad_accum_steps,
            checkpoint_path=bert_checkpoint_path,
            pretrained_model_type=pretrained_model_type
        )
        train_model.summary()

    # 保存模型
    checkpoint = ModelCheckpoint(model_saved_path=model_saved_path,bert_instance=bert_instance)
    # 记录日志
    csv_logger = keras.callbacks.CSVLogger('training.log')

    # 模型训练
    train_model.fit(
        dataset,
        steps_per_epoch=steps_per_epoch,
        epochs=epochs,
        callbacks=[checkpoint, csv_logger],
    )