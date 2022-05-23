# encoding: utf-8

# author: BrikerMan
# contact: eliyar917@gmail.com
# blog: https://eliyar.biz

# file: base_embedding.py
# time: 2:43 下午

import json
from typing import Dict, List, Any, Optional

import numpy as np
import tensorflow as tf
import tqdm

import kolibri.backend
from kolibri.indexers.base_indexer import BaseIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)

L = tf.keras.layers


class Embedding:
    def to_dict(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            'embedding_size': self.embedding_size,
            'max_position': self.max_position,
            **self.kwargs
        }
        return {
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'config': config,
            'embed_model': json.loads(self.embed_model.to_json())
        }

    def __init__(self,
                 embedding_size: int = 100,
                 max_position: int = None,
                 **kwargs: Any):

        self.embed_model: tf.keras.Model = None

        self.kwargs = kwargs

        self.embedding_size: int = embedding_size  # type: ignore
        self.max_position: int = max_position  # type: ignore
        self.token2idx = self.load_embed_vocab()
        self.indexer: Optional[BaseIndexer] = None

    def _override_load_model(self, config: Dict) -> None:
        embed_model_json_str = json.dumps(config['embed_model'])
        self.embed_model = tf.keras.models.model_from_json(embed_model_json_str,
                                                           custom_objects=kolibri.backend.tensorflow.custom_objects)

    def setup_text_processor(self, indexer):
        self.indexer = indexer
        self.build_embedding_model(vocab_size=indexer.vocab_size)
        if self.token2idx:
            self.indexer.token2idx = self.token2idx
            self.indexer.idx2token = dict([(v, k) for k, v in self.token2idx.items()])

    def get_seq_length_from_corpus(self,
                                   generators,
                                   *,
                                   use_label: bool = False,
                                   cover_rate: float = 0.95) -> int:
        """
        Calculate proper sequence length_train according to the corpus

        Args:
            generators:
            use_label:
            cover_rate:

        Returns:

        """
        seq_lens = []
        for gen in generators:
            for sentence, label in tqdm.tqdm(gen, desc="Calculating sequence length_train"):
                if use_label:
                    seq_lens.append(len(label))
                else:
                    seq_lens.append(len(sentence))
        if cover_rate == 1.0:
            target_index = -1
        else:
            target_index = int(cover_rate * len(seq_lens))
        sequence_length = sorted(seq_lens)[target_index]
        logger.debug(f'Calculated sequence length_train = {sequence_length}')
        print('Calculated sequence length_train = {}'.format(sequence_length))
        return sequence_length

    def load_embed_vocab(self) -> Optional[Dict[str, int]]:
        """
        Load vocab dict from embedding layer

        Returns:
            vocab dict or None
        """
        raise NotImplementedError

    def build_embedding_model(self,
                              *,
                              vocab_size: int = None,
                              force: bool = False,
                              **kwargs: Dict) -> None:
        raise NotImplementedError

    def embed(self,
              sentences: List[List[str]],
              *,
              debug: bool = False) -> np.ndarray:
        """
        batch embed sentences

        Args:
            sentences: Sentence list to embed
            debug: show debug info
        Returns:
            vectorized sentence list
        """
        if self.indexer is None:
            raise ValueError('Need to setup the `embedding.setup_text_processor` before calling the embed function.')

        tensor_x = self.indexer.transform(sentences)
        if debug:
            logger.debug(f'sentence tensor: {tensor_x}')
        embed_results = self.embed_model.predict(tensor_x)
        return embed_results

if __name__ == "__main__":
    pass
