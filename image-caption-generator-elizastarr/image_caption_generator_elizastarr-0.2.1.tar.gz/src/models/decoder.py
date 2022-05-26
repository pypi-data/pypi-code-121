from tensorflow.keras.layers import Input, Embedding, Dense, LSTM
import keras.backend as K
from tensorflow.keras import Model
import tensorflow as tf


class Decoder(Model):
    def __init__(
        self,
        max_caption_length: int,
        num_unique_words: int,
        image_representation_dim: int = 20480,
        embedding_dim: int = 512,
        lstm_dim: int = 500,
        lstm_dropout: float = 0.5,
        recurrent_dropout: float = 0.1,
        **kwargs
    ):

        super(Decoder, self).__init__(**kwargs)
        self.image_representation_dim = image_representation_dim
        self.max_caption_length = max_caption_length

        self.image_emb = Dense(embedding_dim, name="image_embedding")
        self.caption_emb = Embedding(
            num_unique_words,
            embedding_dim,
            input_length=max_caption_length,
            name="caption_embedding",
        )
        self.lstm = LSTM(
            lstm_dim,
            return_state=True,
            dropout=lstm_dropout,
            recurrent_dropout=recurrent_dropout,
            name="lstm",
        )
        self.dense_output = Dense(num_unique_words, activation="softmax", name="output")

    def call(self, inputs: tf.Tensor):
        image_embedding = self.image_emb(inputs)
        image_embedding = K.expand_dims(image_embedding, axis=1)  # (None, 512) -> (None, 1, 512)

        # Image is only inputted once
        lstm_out, initial_hidden_state, initial_cell_state = self.lstm(image_embedding)
        state = [initial_hidden_state, initial_cell_state]
        
        dense_out = self.dense_output(lstm_out)  # output: (None, num_unique_words)
        word = K.argmax(dense_out, axis=1)  # output: (None, )
        caption = [word]
        caption_embedding = self.caption_emb(word)  # output: 512D

        for i in range(self.max_caption_length):
            caption_embedding = K.expand_dims(caption_embedding, axis=1)
            lstm_out, hidden_state, cell_state = self.lstm(
                caption_embedding, initial_state=state
            )
            state = [hidden_state, cell_state]

            dense_out = self.dense_output(lstm_out)  # output: (None, num_unique_words)
            word = K.argmax(dense_out, axis=1)
            caption.append(word)
            caption_embedding = self.caption_emb(word)  # output: 512D

        return K.stack(caption, axis=1)

    def model_summary(self):
        x = Input(shape=(self.image_representation_dim,), name="image_input")
        model = Model(inputs=x, outputs=self.call(x))
        return model.summary()
