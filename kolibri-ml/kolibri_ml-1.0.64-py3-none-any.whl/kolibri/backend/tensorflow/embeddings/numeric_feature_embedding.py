# encoding: utf-8

# author: BrikerMan
# contact: eliyar917@gmail.com
# blog: https://eliyar.biz

# file: numeric_feature_embedding.py
# time: 2019-05-23 09:04


from typing import Union, Optional, Tuple, List

import numpy as np
from tensorflow import keras
from keras.preprocessing.sequence import pad_sequences

import kolibri.backend
from kolibri.backend.tensorflow.embeddings.base_embedding import Embedding

# from kolibri.indexers import BaseIndexer

L = keras.layers


# Todo: A better name for this class
class NumericFeaturesEmbedding(Embedding):
    """Embedding layer without pre-training, train embedding layer while training model"""

    def info(self):
        info = super(NumericFeaturesEmbedding, self).info()
        info['config'] = {
            'feature_count': self.feature_count,
            'feature_name': self.feature_name,
            'sequence_length': self.sequence_length,
            'embedding_size': self.embedding_size
        }
        return info

    def __init__(self,
                 feature_count: int,
                 feature_name: str,
                 sequence_length: Union[str, int] = 'auto',
                 embedding_size: int = None,
                 indexer=None,
                 from_saved_model: bool = False):
        """
        Init bare embedding (embedding without pre-training)

        Args:
            sequence_length: ``'auto'``, ``'variable'`` or integer. When using ``'auto'``, use the 95% of corpus length_train
                as sequence length_train. When using ``'variable'``, model input shape will set to None, which can handle
                various length_train of input, it will use the length_train of max sequence in every batch for sequence length_train.
                If using an integer, let's say ``50``, the input output sequence length_train will set to 50.
            embedding_size: Dimension of the dense embedding.
        """
        # Dummy Type
        task = kolibri.backend.CLASSIFICATION
        if embedding_size is None:
            embedding_size = feature_count * 8
        super(NumericFeaturesEmbedding, self).__init__(task=task,
                                                       sequence_length=sequence_length,
                                                       embedding_size=embedding_size,
                                                       indexer=indexer,
                                                       from_saved_model=from_saved_model)
        self.feature_count = feature_count
        self.feature_name = feature_name
        if not from_saved_model:
            self._build_model()

    def _build_model(self, **kwargs):
        input_tensor = L.Input(shape=(self.sequence_length,),
                               name=f'input_{self.feature_name}')
        layer_embedding = L.Embedding(self.feature_count + 1,
                                      self.embedding_size,
                                      name=f'layer_embedding_{self.feature_name}')

        embedded_tensor = layer_embedding(input_tensor)
        self.embed_model = keras.Model(input_tensor, embedded_tensor)

    def analyze_corpus(self,
                       x: Union[Tuple[List[List[str]], ...], List[List[str]]],
                       y: Union[List[List[str]], List[str]]):
        pass

    def process_x_dataset(self,
                          data: List[List[str]],
                          subset: Optional[List[int]] = None) -> Tuple[np.ndarray, ...]:
        """
        batch process feature texts while training

        Args:
            data: label dataset_train
            subset: subset index list

        Returns:
            vectorized feature tensor
        """
        if subset is not None:
            numerized_samples = kolibri.backend.tensorflow.utils.get_list_subset(data, subset)
        else:
            numerized_samples = data

        return pad_sequences(numerized_samples, self.sequence_length, padding='post', truncating='post')


if __name__ == "__main__":
    e = NumericFeaturesEmbedding(2, feature_name='is_bold', sequence_length=10)
    e.embed_model.summary()
    print(e.embed_one([1, 2]))
    print("Hello world")
