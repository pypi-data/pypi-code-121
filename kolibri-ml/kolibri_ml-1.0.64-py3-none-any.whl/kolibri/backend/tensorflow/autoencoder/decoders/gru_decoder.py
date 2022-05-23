import tensorflow as tf

from kolibri.backend.tensorflow.embeddings import Embedding


class GRUDecoder(tf.keras.Model):
    def __init__(self,
                 embedding: Embedding,
                 hidden_size: int,
                 vocab_size: int):
        super(GRUDecoder, self).__init__()
        self.embedding = embedding

        self.gru = tf.keras.layers.GRU(hidden_size,
                                       return_sequences=True,
                                       return_state=True,
                                       recurrent_initializer='glorot_uniform')
        self.fc = tf.keras.layers.Dense(vocab_size)

    def call(self, dec_input, dec_hidden, enc_output):
        # The shape of x after passing through the embedding layer == (batch size, 1, embedding dimension)
        decoder_embedding = self.embedding.embed_model(dec_input)

        s = self.gru(decoder_embedding, initial_state=dec_hidden)
        decoder_outputs, decoder_state = s

        # Output shape == (batch size * 1, hidden layer size)
        output = tf.reshape(decoder_outputs, (-1, decoder_outputs.shape[2]))

        # Output shape == (batch size, vocab)
        x = self.fc(output)
        return x, decoder_state, None


if __name__ == "__main__":
    pass
