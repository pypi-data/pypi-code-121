from typing import Dict,Any,Optional

import numpy as np
from gensim.models import KeyedVectors
from tensorflow import keras

from nlp_tools.embeddings.abc_embedding import  ABCEmbedding
from nlp_tools.logger import logger

L = keras.layers


class WordEmbedding(ABCEmbedding):
    def to_dict(self) -> Dict[str, Any]:
        info_dic = super(WordEmbedding, self).to_dict()
        info_dic['config']['w2v_path'] = self.w2v_path
        info_dic['config']['w2v_kwargs'] = self.w2v_kwargs
        return info_dic

    def __init__(self,
                 w2v_path: str,
                 *,
                 w2v_kwargs: Dict[str, Any] = None,
                 **kwargs: Any):
        """
        Args:
            w2v_path: Word2Vec file path.
            w2v_kwargs: params pass to the ``load_word2vec_format()`` function
              of `gensim.models.KeyedVectors <https://radimrehurek.com/gensim/models/keyedvectors.html#module-gensim.models.keyedvectors>`_
            kwargs: additional params
        """
        if w2v_kwargs is None:
            w2v_kwargs = {}

        self.w2v_path = w2v_path
        self.w2v_kwargs = w2v_kwargs

        self.embedding_size = None
        self.w2v_matrix: np.ndarray = None



        super(WordEmbedding, self).__init__(**kwargs)

        self.vocab2idx = self.load_embed_vocab()

    def load_embed_vocab(self) -> Optional[Dict[str, int]]:
        w2v = KeyedVectors.load_word2vec_format(self.w2v_path, **self.w2v_kwargs)

        token2idx = {
            '[PAD]': 0,
            '[UNK]': 1,
            #'[CLS]': 2,
            #'[SEP]': 3
        }

        # if '[CLS]' not in w2v.vocab:
        #     token2idx['[CLS]'] = len(token2idx)
        #
        # if '[SEP]' not in w2v.vocab:
        #     token2idx['[SEP]'] = len(token2idx)

        for token in w2v.index2word:
            token2idx[token] = len(token2idx)

        vector_matrix = np.zeros((len(token2idx), w2v.vector_size))
        vector_matrix[1] = np.random.rand(w2v.vector_size)
        vector_matrix[2:] = w2v.vectors

        self.embedding_size = w2v.vector_size
        self.w2v_matrix = vector_matrix
        w2v_top_words = w2v.index2entity[:50]

        logger.debug('------------------------------------------------')
        logger.debug("Loaded gensim word2vec model's vocab")
        logger.debug('model        : {}'.format(self.w2v_path))
        logger.debug('word count   : {}'.format(len(self.w2v_matrix)))
        logger.debug('Top 50 words : {}'.format(w2v_top_words))
        logger.debug('------------------------------------------------')

        return token2idx

    def build_embedding_model(self,
                              *,
                              vocab_size: int = None,
                              force: bool = False,
                              **kwargs: Dict) -> None:
        if self.embed_model is None:
            input_tensor = L.Input(shape=(None,),
                                   name=f'input')
            layer_embedding = L.Embedding(len(self.vocab2idx),
                                          self.embedding_size,
                                          weights=[self.w2v_matrix],
                                          mask_zero=True,
                                          trainable=True,
                                          name=f'layer_embedding')

            embedded_tensor = layer_embedding(input_tensor)
            self.embed_model = keras.Model(input_tensor, embedded_tensor)


if __name__ == '__main__':
    word_vec_path = '/home/qiufengfeng/nlp/nlp_project/gitee_my/nlp_tools/example/pretraining/word2vec/model.vec'
    a = WordEmbedding(w2v_path=word_vec_path)


