import tensorflow as tf
from kolibri.backend.tensorflow.tasks.structured.base_model import BaseStructuredModel




class LSTMModel(BaseStructuredModel):
    @classmethod
    def get_default_hyper_parameters(cls):
        return {
            'loss': 'mae',
            'input': {
                'embedding°size': 64,
            },

            'lstm1': {
                "units":100
            },
            'dense1':{
                'units':200,
                "activation": 'linear'
            },
            'dense2': {
                'units': 64,
                "activation": 'linear'
            },
            'dense3': {
                'units': 16,
                "activation": 'linear'
            },
            'output': {
                'units': 1,
                "activation": 'linear'
            },

            "dropout":{
                'rate': 0.02
            }
        }

    def build_model_arc(self, generators):
        config = self.hyper_parameters

        embeding_size=generators.x_values[0].shape[1]
        time_steps=generators.x_values[1].shape[1]
        n_features=generators.x_values[1].shape[2]
        X = tf.keras.Input(shape=(embeding_size,))

        F = tf.keras.Input(shape=(time_steps, n_features,))

        lstm = tf.keras.layers.LSTM( **config['lstm1'], input_shape=(time_steps, n_features,))

        out_lstm = lstm(F)
        temp = tf.keras.layers.Concatenate(axis=1)([X, out_lstm])

        dense1 = tf.keras.layers.Dense(**config["dense1"])
        dense1_output = dense1(temp)

        drop_out3 = tf.keras.layers.Dropout(**config["dropout"])
        dense1_output = drop_out3(dense1_output, training=True)

        dense2 = tf.keras.layers.Dense(**config["dense2"])
        dense2_output = dense2(dense1_output)
        # dense2_output = dense2(temp)

        drop_out4 = tf.keras.layers.Dropout(**config["dropout"])
        dense2_output = drop_out4(dense2_output, training=True)

        dense3 = tf.keras.layers.Dense(**config["dense3"])
        dense3_output = dense3(dense2_output)

        drop_out5 = tf.keras.layers.Dropout(**config["dropout"])
        dense3_output = drop_out5(dense3_output, training=True)

        dense4 = tf.keras.layers.Dense(**config["output"])
        dense4_output = dense4(dense3_output)

        self.tf_model = tf.keras.Model(inputs=[X, F], outputs=dense4_output)

        print(self.tf_model.summary())


def get_model(model_type, hyper_parameters=None):
    if model_type == 'lstm':
        return LSTMModel(hyper_parameters=hyper_parameters)

    else:
        raise Exception('Model does not exist in the library of audio classification models')
