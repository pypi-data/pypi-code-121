import json
import os
import pathlib
from typing import Any, Dict

import numpy as np
import tensorflow as tf
import tqdm

import kolibri
from kolibri.data.text.generators import DataGenerator, Seq2SeqDataSet
from kolibri.backend.tensorflow.autoencoder.decoders.att_gru_decoder import AttGRUDecoder
from kolibri.backend.tensorflow.autoencoder.encoders.gru_encoder import GRUEncoder
from kolibri.backend.tensorflow.embeddings import DefaultEmbedding
from kolibri.backend.tensorflow.embeddings import Embedding
from kolibri.indexers import SequenceIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)


class Seq2Seq:
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tf_version': tf.__version__,  # type: ignore
            'kolibri_version': kolibri.__version__,
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'config': {
                'encoder_seq_length': self.encoder_seq_length,  # type: ignore
                'decoder_seq_length': self.decoder_seq_length,  # type: ignore
                'hidden_size': self.hidden_size
            },
            'encoder_embedding': self.encoder_embedding.to_dict(),  # type: ignore
            'decoder_embedding': self.decoder_embedding.to_dict(),
            'encoder_processor': self.encoder_processor.to_dict(),
            'decoder_processor': self.decoder_processor.to_dict(),
        }

    def __init__(self,
                 encoder_embedding: Embedding = None,
                 decoder_embedding: Embedding = None,
                 encoder_seq_length: int = None,
                 decoder_seq_length: int = None,
                 hidden_size: int = 1024,
                 **kwargs: Any):
        """
        Init Labeling Model

        Args:
            embedding: embedding object
            sequence_length: target sequence length_train
            hyper_parameters: hyper_parameters to overwrite
            **kwargs:
        """
        logger.warning("Seq2Seq API is experimental. It may be changed in the future without notice.")
        if encoder_embedding is None:
            encoder_embedding = DefaultEmbedding(embedding_size=256)  # type: ignore

        self.encoder_embedding = encoder_embedding

        if decoder_embedding is None:
            decoder_embedding = DefaultEmbedding(embedding_size=256)  # type: ignore

        self.decoder_embedding = decoder_embedding

        self.encoder_processor = SequenceIndexer(min_count=1)
        self.decoder_processor = SequenceIndexer(build_vocab_from_labels=True, min_count=1)

        self.encoder: GRUEncoder = None
        self.decoder: AttGRUDecoder = None

        self.hidden_size: int = hidden_size

        self.encoder_seq_length = encoder_seq_length
        self.decoder_seq_length = decoder_seq_length

        self.optimizer = tf.keras.optimizers.Adam()
        self.loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True, reduction='none')

    # @tf.function
    def loss_function(self, real: tf.Tensor, pred: tf.Tensor) -> tf.Tensor:
        mask = tf.math.logical_not(tf.math.equal(real, 0))
        loss_ = self.loss_object(real, pred)

        mask = tf.cast(mask, dtype=loss_.dtype)
        loss_ *= mask

        return tf.reduce_mean(loss_)

    def build_model(self,
                    x_train, y_train):
        train_gen = DataGenerator(x_train, y_train)
        self.build_model_generator(train_gen)

    def _build_encoder_decoder(self) -> None:
        self.encoder = GRUEncoder(self.encoder_embedding, hidden_size=self.hidden_size)
        self.decoder = AttGRUDecoder(self.decoder_embedding,
                                     hidden_size=self.hidden_size,
                                     vocab_size=self.decoder_processor.vocab_size)
        try:
            self.encoder.model().summary()
            self.decoder.model().summary()
        except:
            pass

    def build_model_generator(self,
                              train_gen) -> None:
        """
        Build model with a generator, This function will do:

        1. setup processor's vocab if the vocab is empty.
        2. calculate the sequence length_train if `sequence_length` is None.
        3. build up model architect.
        4. compile the ``tf_model`` with default loss, optimizer and metrics.

        Args:
            train_gen: train texts generator

        """
        if self.encoder is None:
            self.encoder_processor.build_vocab_generator([train_gen])
            self.decoder_processor.build_vocab_generator([train_gen])
            self.encoder_embedding.setup_text_processor(self.encoder_processor)
            self.decoder_embedding.setup_text_processor(self.decoder_processor)

            if self.encoder_seq_length is None:
                self.encoder_seq_length = self.encoder_embedding.get_seq_length_from_corpus([train_gen],
                                                                                            cover_rate=1.0)
                logger.info(f"calculated encoder sequence length_train: {self.encoder_seq_length}")

            if self.decoder_seq_length is None:
                self.decoder_seq_length = self.decoder_embedding.get_seq_length_from_corpus([train_gen],
                                                                                            use_label=True,
                                                                                            cover_rate=1.0)
                logger.info(f"calculated decoder sequence length_train: {self.decoder_seq_length}")

            self._build_encoder_decoder()

    # @tf.function
    def train_step(self,  # type: ignore
                   input_seq,
                   target_seq,
                   enc_hidden):
        loss = 0

        with tf.GradientTape() as tape:
            enc_output, enc_hidden = self.encoder(input_seq, enc_hidden)

            dec_hidden = enc_hidden

            bos_token_id = self.encoder_processor.token2idx[self.encoder_processor.token_bos]
            dec_input = tf.expand_dims([bos_token_id] * target_seq.shape[0], 1)

            # Teacher forcing - feeding the target as the next input
            for t in range(1, target_seq.shape[1]):
                # pass enc_output to the decoder
                predictions, dec_hidden, _ = self.decoder(dec_input, dec_hidden, enc_output)
                loss += self.loss_function(target_seq[:, t], predictions)
                # using teacher forcing
                dec_input = tf.expand_dims(target_seq[:, t], 1)

        batch_loss = (loss / int(target_seq.shape[1]))
        variables = self.encoder.trainable_variables + self.decoder.trainable_variables
        gradients = tape.gradient(loss, variables)
        self.optimizer.apply_gradients(zip(gradients, variables))

        return batch_loss

    def fit(self,
            x_train, y_train,
            *,
            batch_size: int = 64,
            epochs: int = 5,
            callbacks=None):
        train_gen = DataGenerator(x_train, y_train)
        self.build_model_generator(train_gen)

        train_dataset = Seq2SeqDataSet(train_gen,
                                       batch_size=batch_size,
                                       encoder_processor=self.encoder_processor,
                                       encoder_seq_length=self.encoder_seq_length,
                                       decoder_processor=self.decoder_processor,
                                       decoder_seq_length=self.decoder_seq_length)

        if callbacks is None:
            callbacks = []
        history_callback = tf.keras.callbacks.History()
        callbacks.append(history_callback)

        for c in callbacks:
            c.set_model(self)
            c.on_train_begin()

        for epoch in range(epochs):
            for c in callbacks:
                c.on_epoch_begin(epoch=epoch)
            enc_hidden = tf.zeros((batch_size, self.hidden_size))
            total_loss = []

            with tqdm.tqdm(total=len(train_dataset)) as p_bar:
                for (inputs, targets) in train_dataset:
                    p_bar.update(1)
                    batch_loss = self.train_step(inputs, targets, enc_hidden)
                    total_loss.append(batch_loss.numpy())
                    info = f"Epoch {epoch + 1}/{epochs} | Epoch Loss: {np.mean(total_loss):.4f} " \
                           f"Batch Loss: {batch_loss.numpy():.4f}"
                    p_bar.set_description_str(info)
            logs = {'loss': np.mean(total_loss)}
            for c in callbacks:
                c.on_epoch_end(epoch=epoch, logs=logs)

        return history_callback

    def save(self, model_path: str) -> str:
        """
        Save model
        Args:
            model_path:
        """
        pathlib.Path(model_path).mkdir(exist_ok=True, parents=True)
        model_path = os.path.abspath(model_path)

        with open(os.path.join(model_path, 'model_config.json'), 'w') as f:
            f.write(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))
            f.close()

        self.encoder_embedding.embed_model.save_weights(os.path.join(model_path, 'encoder_embed_weights.h5'))
        self.decoder_embedding.embed_model.save_weights(os.path.join(model_path, 'decoder_embed_weights.h5'))
        self.encoder.save_weights(os.path.join(model_path, 'encoder_weights.h5'))
        self.decoder.save_weights(os.path.join(model_path, 'decoder_weights.h5'))
        logger.info('model saved to {}'.format(os.path.abspath(model_path)))
        return model_path

    @classmethod
    def load_model(cls, model_path: str) -> 'Seq2Seq':
        from kolibri.backend.tensorflow.utils import load_data_object
        model_config_path = os.path.join(model_path, 'model_config.json')
        model_config = json.loads(open(model_config_path, 'r').read())
        model = load_data_object(model_config)

        # Load indexers and embeddings
        model.encoder_processor = load_data_object(model_config['encoder_processor'])
        model.decoder_processor = load_data_object(model_config['decoder_processor'])
        model.encoder_embedding = load_data_object(model_config['encoder_embedding'])
        model.decoder_embedding = load_data_object(model_config['decoder_embedding'])

        model._build_encoder_decoder()
        # Load Model Weights
        model.encoder_embedding.embed_model.load_weights(os.path.join(model_path, 'encoder_embed_weights.h5'))
        model.decoder_embedding.embed_model.load_weights(os.path.join(model_path, 'decoder_embed_weights.h5'))
        model.encoder.built = True
        model.encoder.load_weights(os.path.join(model_path, 'encoder_weights.h5'))
        model.decoder.built=True
        model.decoder.load_weights(os.path.join(model_path, 'decoder_weights.h5'))

        return model

    def predict(self, x_data):
        results = []
        attentions = []

#        bos_token_id = self.decoder_processor.token2idx[self.decoder_processor.token_bos]
#        eos_token_id = self.decoder_processor.token2idx[self.decoder_processor.token_eos]

        for sample in x_data:
            input_seq = self.encoder_processor.transform([sample], seq_length=self.encoder_seq_length)
            enc_hidden = tf.zeros((1, self.hidden_size))
            enc_output, enc_hidden = self.encoder(input_seq, enc_hidden)
            dec_hidden = enc_hidden

            attention_plot = np.zeros((self.decoder_seq_length, self.encoder_seq_length))
            token_out = []

            dec_input = tf.expand_dims([bos_token_id], 0)

            for t in range(self.decoder_seq_length):
                predictions, dec_hidden, att_weights = self.decoder(dec_input, dec_hidden, enc_output)
                # storing the attention weights to plot later on
                attention_weights = tf.reshape(att_weights, (-1,))
                attention_plot[t] = attention_weights.numpy()

                next_tokens = tf.argmax(predictions[0]).numpy()
                token_out.append(next_tokens)
                if next_tokens == eos_token_id:
                    break
                dec_input = tf.expand_dims([next_tokens], 0)
            r = self.decoder_processor.inverse_transform([token_out])[0]
            results.append(r)
            attentions.append(attention_plot)
        return results, np.array(attentions)


if __name__ == "__main__":
    from kolibri.data.text.corpus import CONLL2003ENCorpus
    import logging

    logging.basicConfig(level='INFO', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    corpus = CONLL2003ENCorpus('valid')
    x, y = corpus.get_data()
    x, y = x[:100], y[:100]

    seq2seq = Seq2Seq(hidden_size=256)
    seq2seq.build_model(x, y)
    model_path=seq2seq.save('./seq2seq_model')

    s = Seq2Seq.load_model(model_path)
    res, att = seq2seq.predict(x[:10])
    res2, att2 = s.predict(x[:10])
    print(res == res2)
    print((att == att2).all())
