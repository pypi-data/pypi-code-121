import numpy as np
import tensorflow as tf

from kolibri.backend.tensorflow.embeddings import Embedding
from kolibri.backend.tensorflow.layers import L


class LSTMEncoder(tf.keras.Model):
    def __init__(self, hidden_size: int = 1024, dropout=0.3):
        super(LSTMEncoder, self).__init__()
        self.hidden_size = hidden_size
        self.lstm = tf.keras.layers.LSTM(hidden_size,
                                       return_sequences=True,
                                       return_state=True,
                                        dropout=dropout,
                                       recurrent_initializer='glorot_uniform')

    def call(self, x: np.ndarray, hidden: np.ndarray, **kwargs):
        x = self.embedding.embed_model(x)
        output, state = self.lstm(x, initial_state=hidden)
        return output, state

    def model(self) -> tf.keras.Model:
        x1 = L.Input(shape=(None,))
        x2 = L.Input(shape=(self.hidden_size,))
        return tf.keras.Model(inputs=[x1, x2],
                              outputs=self.call(x1, x2),
                              name='LSTMEncoder')


if __name__ == "__main__":
    pass
