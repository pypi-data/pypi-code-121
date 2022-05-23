import logging
from typing import Dict, Any

import numpy as np
from seqeval.metrics.sequence_labeling import get_entities

import kolibri
from kolibri.data.text.corpus.generators import DataGenerator
from kolibri.backend.tensorflow.tasks.text.base_model import TextBaseModel
from kolibri.backend.tensorflow.embeddings import DefaultEmbedding
from kolibri.indexers.labeling_indexer import SequenceIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)

from kolibri.metrics.sequence_labeling import sequence_labeling_report


class BaseLabelingModel(TextBaseModel):
    """
    Abstract Labeling Model
    """

    def __init__(self, embedding=None, sequence_length: int = None, hyper_parameters: Dict[str, Dict[str, Any]] = None):
        """

        Args:
            embedding: embedding object
            sequence_length: target sequence length_train
            hyper_parameters: hyper_parameters to overwrite
        """
        #       super(BaseLabelingModel, self).__init__()
        super(BaseLabelingModel, self).__init__(embedding, sequence_length, hyper_parameters)
        if self.embedding is None:
            self.embedding = DefaultEmbedding()  # type: ignore

        if self.hyper_parameters is None:
            self.hyper_parameters = self.get_default_hyper_parameters()

        self.sequence_length = sequence_length
        self.content_indexer = SequenceIndexer()
        self.label_indexer = SequenceIndexer(build_in_vocab='labeling',
                                             min_count=1,
                                             build_vocab_from_labels=True)

    def build_model(self, x_data, y_data):
        """
        Build Model with x_data and y_data

        This function will setup a :class:`CorpusGenerator`,
         then call :meth:`BaseTextClassificationModel.build_model_gen` for preparing processor and model

        Args:
            x_data:
            y_data:

        Returns:

        """

        train_gen = DataGenerator(x_data, y_data)
        self.build_model_generator([train_gen])

    def build_model_generator(self, generators):
        if not self.content_indexer.token2idx:
            self.content_indexer.build_vocab_generator(generators)
        self.label_indexer.build_vocab_generator(generators)
        self.embedding.setup_text_processor(self.content_indexer)

        if self.sequence_length is None:
            self.sequence_length = self.embedding.get_seq_length_from_corpus(generators)

        if self.tf_model is None:
            self.build_model_arc()
            self.compile_model()

    def build_model_arc(self) -> None:
        raise NotImplementedError

    def compile_model(self,
                      loss: Any = None,
                      optimizer: Any = None,
                      metrics: Any = None,
                      **kwargs: Any) -> None:
        """
        Configures the model for training.
        call :meth:`tf.keras.Model.predict` to compile model with custom loss, optimizer and metrics
        """
        if loss is None:
            loss = 'sparse_categorical_crossentropy'
        if optimizer is None:
            optimizer = 'adam'
        if metrics is None:
            metrics = ['accuracy']

        self.tf_model.compile(loss=loss,
                              optimizer=optimizer,
                              metrics=metrics,
                              **kwargs)

    def predict(self,
                x_data,
                *,
                batch_size: int = 32,
                truncating: bool = False,
                predict_kwargs: Dict = None):
        """
        Generates output predictions for the input samples.

        Computation is done in batches.

        Args:
            x_data: The input texts, as a Numpy array (or list of Numpy arrays if the model has multiple inputs).
            batch_size: Integer. If unspecified, it will default to 32.
            truncating: remove values from sequences larger than `model.embedding.sequence_length`
            predict_kwargs: arguments passed to :meth:`tf.keras.Model.predict`

        Returns:
            array(s) of predictions.
        """
        if predict_kwargs is None:
            predict_kwargs = {}
        with kolibri.backend.custom_object_scope():
            if truncating:
                seq_length = self.sequence_length
            else:
                seq_length = None
            tensor = self.content_indexer.transform(x_data, seq_length=seq_length,
                                                    max_position=self.embedding.max_position)
            logger.debug('predict seq_length: {}, input: {}'.format(seq_length, np.array(tensor).shape))
            pred = self.tf_model.predict(tensor, batch_size=batch_size, **predict_kwargs)
            pred = pred.argmax(-1)
            lengths = [len(sen) for sen in x_data]

            res = self.label_indexer.inverse_transform(pred,  # type: ignore
                                                       lengths=lengths)
            logger.debug('predict output: {}'.format(np.array(pred).shape))
            logger.debug('predict output argmax: {}'.format(pred.argmax(-1)))
        return res

    def predict_entities(self,
                         x_data,
                         batch_size: int = 32,
                         join_chunk: str = ' ',
                         truncating: bool = False,
                         predict_kwargs: Dict = None):
        """Gets entities from sequence.

        Args:
            x_data: The input texts, as a Numpy array (or list of Numpy arrays if the model has multiple inputs).
            batch_size: Integer. If unspecified, it will default to 32.
            truncating: remove values from sequences larger than `model.embedding.sequence_length`
            join_chunk: str or False,
            predict_kwargs: arguments passed to :meth:`tf.keras.Model.predict`

        Returns:
            list: list of entity.
        """
        if isinstance(x_data, tuple):
            text_seq = x_data[0]
        else:
            text_seq = x_data
        res = self.predict(x_data,
                           batch_size=batch_size,
                           truncating=truncating,
                           predict_kwargs=predict_kwargs)
        new_res = [get_entities(seq) for seq in res]
        final_res = []
        for index, seq in enumerate(new_res):
            seq_data = []
            for entity in seq:
                res_entities = []
                for i, e in enumerate(text_seq[index][entity[1]:entity[2] + 1]):
                    # Handle bert tokenizer
                    if e.startswith('##') and len(res_entities) > 0:
                        res_entities[-1] += e.replace('##', '')
                    else:
                        res_entities.append(e)
                value = None
                if join_chunk is False:
                    value = res_entities
                else:
                    value = join_chunk.join(res_entities)

                seq_data.append({
                    "entity": entity[0],
                    "start": entity[1],
                    "end": entity[2],
                    "value": value,
                })

            final_res.append({
                'tokenized': x_data[index],
                'y_values': seq_data
            })
        return final_res

    def evaluate(self,
                 x_data, y_data,
                 batch_size: int = 32,
                 digits: int = 4,
                 truncating: bool = False) -> Dict:
        """
        Build a text report showing the main labeling metrics.
        """
        y_pred = self.predict(x_data,
                              batch_size=batch_size,
                              truncating=truncating)
        y_true = [seq[:len(y_pred[index])] for index, seq in enumerate(y_data)]

        new_y_pred = []
        for x in y_pred:
            new_y_pred.append([str(i) for i in x])
        new_y_true = []
        for x in y_true:
            new_y_true.append([str(i) for i in x])

        report = sequence_labeling_report(y_true, y_pred, digits=digits)
        return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    from kolibri.data.text.corpus import CONLL2003ENCorpus

    corpus = CONLL2003ENCorpus('train')
    train_x, train_y = corpus.get_data()
    valid_x, valid_y = CONLL2003ENCorpus('valid')

    train_x, train_y = train_x[:5120], train_y[:5120]

    model = None
    model.build_model(train_x[:100], train_y[:100])

    model.fit(train_x[:1000], train_y[:1000], epochs=10)

    model.evaluate(train_x[:20], train_y[:20])
    print("Hello world")
