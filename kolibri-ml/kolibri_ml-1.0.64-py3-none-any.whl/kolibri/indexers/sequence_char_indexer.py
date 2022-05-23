from typing import Dict, Any

import numpy as np
import tqdm
from tensorflow.keras.preprocessing.sequence import pad_sequences

from kolibri.indexers.sequence_indexer import SequenceIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)


class SequenceCharIndexer(SequenceIndexer):
    """
    Generic indexers for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(SequenceCharIndexer, self).to_dict()
        data['config'].update({
            'char_seq_length': self.char_seq_length
        })
        return data

    def __init__(self, build_in_vocab='text', min_count=0, build_vocab_from_labels=False, index=None,
                 char_seq_length=None, **kwargs: Any):
        """
        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """

        super(SequenceCharIndexer, self).__init__(**kwargs)

        self.build_in_vocab = build_in_vocab
        self.min_count = min_count
        self.build_vocab_from_labels = build_vocab_from_labels
        self.index = index
        self.char_seq_length = char_seq_length

        if build_in_vocab == 'text':
            self._initial_vocab_dic = {
                self.token_pad: 0,
                self.token_unk: 1
            }
        elif build_in_vocab == 'labeling':
            self._initial_vocab_dic = {
                self.token_pad: 0
            }
        else:
            self._initial_vocab_dic = {}

        self._showed_seq_len_warning = False

    def build_vocab(self, x_data, y_data=None):
        self.build_vocab_generator(zip(x_data, y_data))

    def build_vocab_generator(self, generators):
        if not self.token2idx:
            vocab2idx = self._initial_vocab_dic
            v_count = 2
            char_seq_length = 0
            for sentence, label in tqdm.tqdm(generators, desc="Preparing text vocab dict"):
                    if self.build_vocab_from_labels:
                        if self.index is not None:
                            target = label[self.index]
                        else:
                            target = label
                    else:
                        target = sentence
                    if self.index is not None:
                        target = target[self.index]

                    for token in target:
                        if isinstance(token, list):
                            for word in token:
                                char_seq_length = max(char_seq_length, len(word))
                                for ch in word:
                                    if ch not in vocab2idx:
                                        vocab2idx[ch] = v_count
                                        v_count += 1
                        else:
                            char_seq_length = max(char_seq_length, len(token))
                            for ch in token:
                                if ch not in vocab2idx:
                                    vocab2idx[ch] = v_count
                                    v_count += 1
                    self.seq_length = max(self.seq_length, len(target))
            #            self.seq_length += 2
            if self.char_seq_length is None:
                self.char_seq_length = char_seq_length
            self.token2idx = vocab2idx
            self.idx2token = dict([(v, k) for k, v in self.token2idx.items()])

    def transform(self,
                  samples,
                  *,
                  char_seq_length: int = None,
                  max_position: int = None):

        numerized_samples = []
        for seq in samples:
            numerized_sequences = []
            if self.index is not None:
                seq = seq[self.index]
            for i in range(0, self.seq_length):
                if i < len(seq):
                    word = seq[i]
                    if self.token_unk in self.token2idx:
                        unk_index = self.token2idx[self.token_unk]
                        word_ = [self.token2idx.get(ch, unk_index) for ch in word]
                    else:
                        word_ = [self.token2idx[ch] for ch in word]
                else:
                    word_ = np.zeros(self.char_seq_length)
                numerized_sequences.append(word_)

            numerized_samples.append(numerized_sequences)

        chars_vectors = [pad_sequences(seq, maxlen=self.char_seq_length, padding='post', truncating='post') for seq in
                         numerized_samples]
        #        chars_vectors = [pad_sequences(d, maxlen=self.seq_length, padding='post', truncating='post') for d   in numerized_samples]

        chars_vectors = np.array(chars_vectors)

        return chars_vectors

    def inverse_transform(self, data, *, lengths=None, threshold=0.5, **kwargs):
        raise NotImplementedError


if __name__ == "__main__":
    pass
