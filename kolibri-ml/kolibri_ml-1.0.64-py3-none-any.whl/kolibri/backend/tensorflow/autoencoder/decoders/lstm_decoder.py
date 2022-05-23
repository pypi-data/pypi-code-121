import tensorflow as tf

class Decoder():

    def to_dict(self):
        return {
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'input_shape': self.input_shape,  # type: ignore
            'dropout': self.dropout,

        }

    def __init__(self, input_shape, encoder_states, dropout=0.3):
        super(Decoder, self).__init__()

        self.input_shape=input_shape
        self.dropout=dropout
        self.decoder_input = tf.keras.Input(shape=self.input_shape)
        # gaussian_decoder_input = GaussianNoise(0.01)(decoder_input)

        decoder_lstm1 = tf.keras.layers.LSTM(64, return_sequences=True, return_state=True, dropout=self.dropout)
        decoder_output1, _, _ = decoder_lstm1(self.decoder_input, initial_state=encoder_states, training=True)

        decoder_lstm2 = tf.keras.layers.LSTM(200, return_state=True, dropout=self.dropout)
        decoder_output2, _, _ = decoder_lstm2(decoder_output1, training=True)

        decoder_dense = tf.keras.layers.Dense(4)
        self.decoder_output = decoder_dense(decoder_output2)
