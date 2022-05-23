import operator
from typing import List, Dict, Any
import tempfile
import numpy as np
from sklearn import metrics as sklearn_metrics

import kolibri
from kolibri.data.text.generators import DataGenerator
from kolibri.backend.tensorflow.tasks.structured.base_model import BaseStructuredModel
from kolibri.backend.tensorflow.embeddings import DefaultEmbedding
from kolibri.backend.tensorflow.layers import L
from kolibri.logger import get_logger

logger = get_logger(__name__)

from kdmt.ml.metrics.multi_label_classification import multi_label_classification_report


class BaseTextClassificationModel(BaseStructuredModel):
    """
    Abstract Classification Model
    """

    __task__ = 'regression'

    def __init__(self,  sequence_length=None, hyper_parameters=None):
        """

        Args:
            embedding: embedding object
            sequence_length: target sequence length_train
            hyper_parameters: hyper_parameters to overwrite
            multi_label: is multi-label classification
            content_indexer: text processor
            label_indexer: label processor
        """
        super().__init__( sequence_length, hyper_parameters)

    def build_model(self,
                    x_train,
                    y_train):
        """
        Build Model with x_data and y_data

        This function will setup a :class:`CorpusGenerator`,
         then call py:meth:`BaseTextClassificationModel.build_model_gen` for preparing processor and model

        Args:
            x_train:
            y_train:

        Returns:

        """

        train_gen = DataGenerator(x_train, y_train)
        self.build_model_generator([train_gen])

    def build_model_generator(self, generators):

        if self.tf_model is None:
            self.build_model_arc()
            self.compile_model()

    @classmethod
    def get_default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        raise NotImplementedError

    def build_model_arc(self):
        raise NotImplementedError


    def predict(self, x_data, *,
                top_k=5,
                batch_size: int = 32,
                truncating: bool = False,
                multi_label_threshold: float = 0.5,
                predict_kwargs: Dict = None):
        """
        Generates output predictions for the input samples.

        Computation is done in batches.

        Args:
            x_data: The input texts, as a Numpy array (or list of Numpy arrays if the model has multiple inputs).
            batch_size: Integer. If unspecified, it will default to 32.
            truncating: remove values from sequences larger than `model.embedding.sequence_length`
            multi_label_threshold:
            predict_kwargs: arguments passed to ``predict()`` function of ``tf.keras.Model``

        Returns:
            array(s) of predictions.
        """
        if predict_kwargs is None:
            predict_kwargs = {}
        with kolibri.backend.tensorflow.custom_object_scope():

            logger.debug(f'predict input shape {np.array(tensor).shape}')
            pred = self.tf_model.predict(tensor, batch_size=batch_size, **predict_kwargs)
            logger.debug(f'predict output shape {pred.shape}')
            sorted_indices = np.fliplr(np.argsort(pred, axis=1))
            labels=np.array([self.label_indexer.inverse_transform(p) for p in sorted_indices])






        return labels, pred[np.arange(pred.shape[0])[:, None], sorted_indices]


    def evaluate(self, x_data, y_data, *,
                 batch_size: int = 32,
                 digits: int = 4,
                 multi_label_threshold: float = 0.5,
                 truncating: bool = False, ):
        y_pred = self.predict(x_data,
                              batch_size=batch_size,
                              truncating=truncating,
                              multi_label_threshold=multi_label_threshold)


        original_report = sklearn_metrics.classification_report(y_data,
                                                                    y_pred[0][:,0],
                                                                    output_dict=True,
                                                                    digits=digits)
        print(sklearn_metrics.classification_report(y_data,
                                                        y_pred[0][:,0],
                                                        output_dict=False,
                                                        digits=digits))
        report = {
                'detail': original_report,
                **original_report['weighted avg']
            }
        return report


if __name__ == "__main__":
    pass
