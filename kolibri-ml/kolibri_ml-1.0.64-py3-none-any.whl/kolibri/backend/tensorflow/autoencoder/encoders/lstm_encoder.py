import tensorflow as tf


class Encoder():
    def to_dict(self):
        return {
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'input_shape': self.inout_shape,  # type: ignore
            'dropout': self.dropout,

        }

    def __init__(self, input_shape, dropout=0.3):
        super(Encoder, self).__init__( )
        # encoder
        self.inout_shape=input_shape
        self.dropout=dropout
        self.encoder_input = tf.keras.Input(shape=self.inout_shape)
        #gaussian_encoder_input = GaussianNoise(0.01)(encoder_input)

        encoder_lstm1 = tf.keras.layers.LSTM(200, return_state = True, return_sequences=True, dropout = self.dropout)
        encoder_output1,state_h1, state_c1 = encoder_lstm1(self.encoder_input, training = True)

        encoder_lstm2 = tf.keras.layers.LSTM(64, return_state = True, dropout = self.dropout)
        encoder_output2,state_h2, state_c2 = encoder_lstm2(encoder_output1, training = True)

        self.encoder_states = [state_h2, state_c2]

        # The encoder model outputs the cell state to provide features for the inference part
        self.encoder_model = tf.keras.Model(self.encoder_input, state_c2)

    def predict(self, input):
        return self.encoder_model.predict(input)
