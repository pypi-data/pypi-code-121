import collections
import operator
from typing import Dict, Any

import tqdm
from tensorflow.keras.preprocessing.sequence import pad_sequences

from kolibri.indexers.base_indexer import BaseIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)


class SequenceIndexer(BaseIndexer):
    """
    Generic indexers for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(SequenceIndexer, self).to_dict()
        data['config'].update({
            'build_in_vocab': self.build_in_vocab,
            'min_count': self.min_count,
            'seq_length': self.seq_length,
            'index': self.index
        })
        return data

    def __init__(self,
                 build_in_vocab: str = 'text',
                 min_count: int = 0,
                 build_vocab_from_labels: bool = False,
                 index=None,
                 **kwargs: Any):
        """

        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """
        super(SequenceIndexer, self).__init__(**kwargs)

        self.build_in_vocab = build_in_vocab
        self.min_count = min_count
        self.build_vocab_from_labels = build_vocab_from_labels
        self.index = index
        self.seq_length = 0
        if 'seq_length' in kwargs:
            self.seq_length = kwargs['seq_length']

        if build_in_vocab == 'text':
            self._initial_vocab_dic = {
                self.token_pad: 0,
                self.token_unk: 1,
                #                self.token_bos: 2,
                #                self.token_eos: 3
            }
        elif build_in_vocab == 'labeling':
            self._initial_vocab_dic = {
                self.token_pad: 0
            }
        else:
            self._initial_vocab_dic = {}

        self._showed_seq_len_warning = False

    def build_vocab_generator(self, generators):
        if not self.token2idx:
            vocab2idx = self._initial_vocab_dic
            max_len = 0
            token2count: Dict[str, int] = {}

            for gen in generators:
                for sentence, label in tqdm.tqdm(gen, desc="Preparing text vocab dict"):
                    if self.build_vocab_from_labels:
                        target = label
                    else:
                        target = sentence
                    if self.index is not None:
                        target = target[self.index]
                    max_len = max(max_len, len(target))

                    self.seq_length = max(self.seq_length, len(target))
                    for token in target:
                        count = token2count.get(token, 0)
                        token2count[token] = count + 1
            #            self.seq_length += 2
            sorted_token2count = sorted(token2count.items(),
                                        key=operator.itemgetter(1),
                                        reverse=True)
            token2count = collections.OrderedDict(sorted_token2count)

            for token, token_count in token2count.items():
                if token not in vocab2idx and token_count >= self.min_count:
                    vocab2idx[token] = len(vocab2idx)
            self.token2idx = vocab2idx
            self.idx2token = dict([(v, k) for k, v in self.token2idx.items()])

            top_k_vocab = [k for (k, v) in list(self.token2idx.items())[:10]]
            logger.debug(f"--- Build vocab dict finished, Total: {len(self.token2idx)} ---")
            logger.debug(f"Top-10: {top_k_vocab}")
    def transform(self, samples):
        numerized_samples = []
        for seq in samples:
            if self.index is not None:
                seq = seq[self.index]

            #            if self.token_bos in self.token2idx:
            #                seq = [self.token_bos] + seq + [self.token_eos]
            #            else:
            #                seq = [self.token_pad] + seq + [self.token_pad]
            if self.token_unk in self.token2idx:
                unk_index = self.token2idx[self.token_unk]
                numerized_samples.append([self.token2idx.get(token, unk_index) for token in seq])
            else:
                numerized_samples.append([self.token2idx[token] for token in seq])

        sample_index = pad_sequences(numerized_samples, self.seq_length, padding='post', truncating='post')
        token_ids = sample_index

        return token_ids

    def inverse_transform(self, labels, *, lengths=None, threshold=0.5, **kwargs):
        result = []
        for index, seq in enumerate(labels):
            labels_ = []

            for idx in seq:
                labels_.append(self.idx2token[idx])
            if lengths is not None:
                labels_ = labels_[0:lengths[index]]

            result.append(labels_)
        return result


if __name__ == "__main__":
    pass
