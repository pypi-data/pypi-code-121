import tensorflow as tf
from tensorflow.keras.layers import Input

from kolibri.backend.tensorflow.embeddings import Embedding
from kolibri.backend.tensorflow.layers.behdanau_attention import BahdanauAttention


class AttGRUDecoder(tf.keras.Model):
    def __init__(self,
                 embedding: Embedding,
                 vocab_size: int,
                 hidden_size: int = 1024):
        super(AttGRUDecoder, self).__init__()
        self.embedding = embedding
        self.hidden_size = hidden_size
        self.gru = tf.keras.layers.GRU(hidden_size,
                                       return_sequences=True,
                                       return_state=True,
                                       recurrent_initializer='glorot_uniform')
        self.fc = tf.keras.layers.Dense(vocab_size)

        # For attention
        self.attention = BahdanauAttention(hidden_size)

    def call(self, x, hidden, enc_output):
        # enc_output shape == (batch_size, max_length, hidden_size)
        context_vector, attention_weights = self.attention(hidden, enc_output)

        # x shape after passing through embedding == (batch_size, 1, embedding_dim)
        x = self.embedding.embed_model(x)

        # x shape after concatenation == (batch_size, 1, embedding_dim + hidden_size)
        x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)

        # passing the concatenated vector to the GRU
        output, state = self.gru(x)

        # output shape == (batch_size * 1, hidden_size)
        output = tf.reshape(output, (-1, output.shape[2]))

        # output shape == (batch_size, vocab)
        x = self.fc(output)

        return x, state, attention_weights

    def model(self):
        x1 = Input(shape=(None,))
        x2 = Input(shape=(self.hidden_size,))
        x3 = Input(shape=(self.hidden_size,))
        return tf.keras.Model(inputs=[x1, x2, x3],
                              outputs=self.call(x1, x2, x3),
                              name='AttGRUDecoder')


if __name__ == "__main__":
    pass
