import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.layers import TimeDistributed, GRU
from tensorflow.keras.models import Model
from tensorflow.keras.regularizers import l2

from kolibri.backend.tensorflow.tasks.audio.base_model import BaseAudioClassificationModel
from kolibri.backend.tensorflow.layers import L
try:
    from kapre.composed import get_melspectrogram_layer
    Melspectrogram = get_melspectrogram_layer()
except:
    Melspectrogram=None
    pass




class Conv1D_KapreModel(BaseAudioClassificationModel):

    @classmethod
    def get_default_hyper_parameters(cls):
        return {
            'delta_time': 1.0,
            'layer_spectrogram': {
                'n_dft': 512,
                'n_hop': 160,
                'padding': 'same',
                'sr': 16000,
                'n_mels': 128,
                'fmin': 0.0,
                'fmax': 8000,
                'power_melgram': 2.0,
                'return_decibel_melgram': True,
                'trainable_fb': False,
                'trainable_kernel': False,
                'name': 'melbands'
            },
            'layer_dense': {
                'activation': 'softmax',
                'name': 'softmax'
            },
            'max_pool_2D_layer': {
                'pool_size': (2, 2)
            },
            'layer_time_distributed': {
                'filters': [8, 16, 32, 64, 128],
                'kernel_size': 4,
                'activation': 'relu',
                'padding': 'same'
            },
            'dense_layer': {

                'activity_regularizer': l2(0.001),
                'units': 64,
                'activation': 'relu',
            },
            'activation_layer': {
                'activation': 'softmax'
            },
            'multipooling': False,
            'dropout': 0.2
        }

    def build_model_arc(self):

        output_dim = self.label_indexer.vocab_size
        config = self.hyper_parameters

        filters = config['layer_time_distributed']['filters']

        i = L.Input(shape=(1, int(config['layer_spectrogram']['sr']) * int(config['delta_time'])), name='input')
        if Melspectrogram is None:
            raise Exception('A compoment is missing. Did you install "kapre" linrary?')

        layer_mel_spectrogram = Melspectrogram(**config['layer_spectrogram'])(i)
        norm = L.BatchNormalization(str_axis='batch', name='batch_norm')(layer_mel_spectrogram)
        permute = L.Permute((2, 1, 3), name='permute')(norm)

        # build model structure in sequent way
        filter_id = 0
        for filter_size in filters:
            if filter_id == 0:
                x = L.TimeDistributed(L.Conv1D(
                    filter_size,
                    kernel_size=config['layer_time_distributed']['kernel_size'],
                    padding=config['layer_time_distributed']['padding'],
                    activation=config['layer_time_distributed']['activation']))(permute)
                filter_id += 1
            else:
                x = L.TimeDistributed(L.Conv1D(
                    filter_size,
                    kernel_size=config['layer_time_distributed']['kernel_size'],
                    padding=config['layer_time_distributed']['padding'],
                    activation=config['layer_time_distributed']['activation']))(x)
                filter_id += 1
            if config['multipooling'] and filter_id < len(filters):
                x = L.MaxPooling2D(**config['max_pool_2D_layer'])(x)

        x = L.GlobalMaxPooling2D()(x)
        if config['dropout'] > 0:
            x = L.Dropout(config['dropout'])(x)
        #        x = L.Dense(64, activation='relu', activity_regularizer=l2(0.001), name='dense')(x)
        x = L.Dense(**config['dense_layer'])(x)
        tensor = L.Dense(output_dim, **config['activation_layer'])(x)

        self.tf_model = tf.keras.Model(i, tensor)


class GRU_model(BaseAudioClassificationModel):

    @classmethod
    def get_default_hyper_parameters(cls):
        return {
            'delta_time': 1.0,
            'n_features': 29,
            'feature_size': 13,
            'layer_gru': {
                'units': 20,
                'activation': 'linear',
                'droput': 0.2,
                'name': 'gru'
            },
            'layer_dense': {
                'activation': 'sigmoid'
            }
        }

    def build_model_arc(self):
        output_dim = self.label_indexer.vocab_size
        config = self.hyper_parameters
        i = L.Input(shape=(config['n_features'], config['feature_size']), name='input')

        gru = GRU(32)(i)

        tensor = L.Dense(output_dim, **config['layer_dense'])(gru)

        self.tf_model = tf.keras.Model(i, tensor)


def Conv1D(N_CLASSES=10, SR=16000, DT=1.0):
    i = layers.Input(shape=(1, int(SR * DT)), name='input')
    x = Melspectrogram(n_dft=512, n_hop=160,
                       padding='same', sr=SR, n_mels=128,
                       fmin=0.0, fmax=SR / 2, power_melgram=2.0,
                       return_decibel_melgram=True, trainable_fb=False,
                       trainable_kernel=False,
                       name='melbands')(i)
    x = BatchNormalization(str_axis='batch', name='batch_norm')(x)
    x = layers.Permute((2, 1, 3), name='permute')(x)
    x = TimeDistributed(layers.Conv1D(8, kernel_size=(4), activation='tanh'), name='td_conv_1d_tanh')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name='max_pool_2d_1')(x)
    x = TimeDistributed(layers.Conv1D(16, kernel_size=(4), activation='relu'), name='td_conv_1d_relu_1')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name='max_pool_2d_2')(x)
    x = TimeDistributed(layers.Conv1D(32, kernel_size=(4), activation='relu'), name='td_conv_1d_relu_2')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name='max_pool_2d_3')(x)
    x = TimeDistributed(layers.Conv1D(64, kernel_size=(4), activation='relu'), name='td_conv_1d_relu_3')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), name='max_pool_2d_4')(x)
    x = TimeDistributed(layers.Conv1D(128, kernel_size=(4), activation='relu'), name='td_conv_1d_relu_4')(x)
    x = layers.GlobalMaxPooling2D(name='global_max_pooling_2d')(x)
    x = layers.Dropout(rate=0.1, name='dropout')(x)
    x = layers.Dense(64, activation='relu', activity_regularizer=l2(0.001), name='dense')(x)
    o = layers.Dense(N_CLASSES, activation='softmax', name='softmax')(x)

    model = Model(inputs=i, outputs=o, name='1d_convolution')
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model


def Conv2D(N_CLASSES=10, SR=16000, DT=1.0):
    i = layers.Input(shape=(1, int(SR * DT)), name='input')
    x = Melspectrogram(n_dft=512, n_hop=160,
                       padding='same', sr=SR, n_mels=128,
                       fmin=0.0, fmax=SR / 2, power_melgram=2.0,
                       return_decibel_melgram=True, trainable_fb=False,
                       trainable_kernel=False,
                       name='melbands')(i)
    x = Normalization2D(str_axis='batch', name='batch_norm')(x)
    x = layers.Conv2D(8, kernel_size=(7, 7), activation='tanh', padding='same', name='conv2d_tanh')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), padding='same', name='max_pool_2d_1')(x)
    x = layers.Conv2D(16, kernel_size=(5, 5), activation='relu', padding='same', name='conv2d_relu_1')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), padding='same', name='max_pool_2d_2')(x)
    x = layers.Conv2D(16, kernel_size=(3, 3), activation='relu', padding='same', name='conv2d_relu_2')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), padding='same', name='max_pool_2d_3')(x)
    x = layers.Conv2D(32, kernel_size=(3, 3), activation='relu', padding='same', name='conv2d_relu_3')(x)
    x = layers.MaxPooling2D(pool_size=(2, 2), padding='same', name='max_pool_2d_4')(x)
    x = layers.Conv2D(32, kernel_size=(3, 3), activation='relu', padding='same', name='conv2d_relu_4')(x)
    x = layers.Flatten(name='flatten')(x)
    x = layers.Dropout(rate=0.2, name='dropout')(x)
    x = layers.Dense(64, activation='relu', activity_regularizer=l2(0.001), name='dense')(x)
    o = layers.Dense(N_CLASSES, activation='softmax', name='softmax')(x)

    model = Model(inputs=i, outputs=o, name='2d_convolution')
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model


def LSTM(N_CLASSES=10, SR=16000, DT=1.0):
    i = layers.Input(shape=(1, int(SR * DT)), name='input')
    x = Melspectrogram(n_dft=512, n_hop=160,
                       padding='same', sr=SR, n_mels=128,
                       fmin=0.0, fmax=SR / 2, power_melgram=2.0,
                       return_decibel_melgram=True, trainable_fb=False,
                       trainable_kernel=False,
                       name='melbands')(i)
    x = Normalization2D(str_axis='batch', name='batch_norm')(x)
    x = layers.Permute((2, 1, 3), name='permute')(x)
    x = TimeDistributed(layers.Reshape((-1,)), name='reshape')(x)
    s = TimeDistributed(layers.Dense(64, activation='tanh'),
                        name='td_dense_tanh')(x)
    x = layers.Bidirectional(layers.LSTM(32, return_sequences=True),
                             name='bidirectional_lstm')(s)
    x = layers.concatenate([s, x], axis=2, name='skip_connection')
    x = layers.Dense(64, activation='relu', name='dense_1_relu')(x)
    x = layers.MaxPooling1D(name='max_pool_1d')(x)
    x = layers.Dense(32, activation='relu', name='dense_2_relu')(x)
    x = layers.Flatten(name='flatten')(x)
    x = layers.Dropout(rate=0.2, name='dropout')(x)
    x = layers.Dense(32, activation='relu',
                     activity_regularizer=l2(0.001),
                     name='dense_3_relu')(x)
    o = layers.Dense(N_CLASSES, activation='softmax', name='softmax')(x)

    model = Model(inputs=i, outputs=o, name='long_short_term_memory')
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model


def get_model(model_type, hyper_parameters=None):
    if model_type == 'conv_1d':
        return Conv1D_KapreModel(hyper_parameters=hyper_parameters)
    elif model_type == 'gru':
        return GRU_model(hyper_parameters=hyper_parameters)
    else:
        raise Exception('Model does not exist in the library of audio classification models')
