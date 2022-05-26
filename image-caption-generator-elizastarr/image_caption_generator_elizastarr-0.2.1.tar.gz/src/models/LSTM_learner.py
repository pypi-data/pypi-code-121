from typing import List
from tensorflow.keras.layers import Input, Embedding, Dense, LSTM, concatenate
import keras.backend as K
from tensorflow.keras import Model


class LSTMLearner(Model):
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

        super(LSTMLearner, self).__init__(**kwargs)
        self.image_representation_dim = image_representation_dim
        self.max_caption_length = max_caption_length

        self.image_emb = Dense(embedding_dim, name="image_embedding")
        self.caption_emb = Embedding(num_unique_words, embedding_dim, name="caption_embedding")
        self.lstm = LSTM(
            lstm_dim,
            return_sequences=True,
            dropout=lstm_dropout,
            recurrent_dropout=recurrent_dropout,
            name="lstm",
        )
        self.dense_output = Dense(num_unique_words, activation="softmax", name="output")

    def call(self, inputs: List):
        input_image, input_caption = inputs
        # Map the images and captions to the same 512D space
        x_image = K.expand_dims(
            self.image_emb(input_image), axis=1
        )  # (None, 512) -> (None, 1, 512)
        x_caption = self.caption_emb(input_caption)

        # Concatenation: (None, 1, 512) + (None, 34, 512) -> (None, 35, 512)
        x = concatenate(
            [x_image, x_caption], axis=1, name="concatenation"
        )  
        x = self.lstm(x)
        return self.dense_output(x)

    def model_summary(self):
        x_image = Input(shape=(self.image_representation_dim,), name="image_input")
        x_caption = Input(
            shape=(self.max_caption_length - 1,), name="caption_input"
        )  # Removed last "_" from each caption
        model = Model(
            inputs=[x_image, x_caption], outputs=self.call([x_image, x_caption])
        )
        return model.summary()
