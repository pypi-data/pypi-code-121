import collections
import operator
from typing import Dict, Any
from six import string_types, iteritems, itervalues
import tqdm
from collections import defaultdict

from kolibri.indexers.base_indexer import BaseIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)


class TextIndexer(BaseIndexer):
    """
    Generic indexers for the sequence samples.
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(TextIndexer, self).to_dict()
        data['config'].update({
            'min-count': self.min_count,
            'seq-length': self.seq_length,
            'index': self.index
        })
        return data

    def __init__(self,
                 min_count: int = 0,
                 build_vocab_from_labels: bool = False,
                 index=None,
                 **kwargs: Any):
        """

        Args:
            vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
            **kwargs:
        """
        super(TextIndexer, self).__init__(**kwargs)


        self.min_count = min_count
        self.build_vocab_from_labels = build_vocab_from_labels
        self.index = index
        self.seq_length = 0
        if 'seq_length' in kwargs:
            self.seq_length = kwargs['seq_length']

        self._initial_vocab_dic = {}

        self._showed_seq_len_warning = False

    def build_vocab(self, x_data, y_data=None):
        if not self.token2idx:
            token2id = self._initial_vocab_dic
            max_len = 0
            token2count: Dict[str, int] = {}


            for sentence in tqdm.tqdm(x_data, desc="Preparing text vocab dict"):
                target = sentence
                if self.index is not None:
                    target = target[self.index]
                max_len = max(max_len, len(target))

                self.seq_length = max(self.seq_length, len(target))
                for token in target:
                    count = token2count.get(token, 0)
                    token2count[token] = count + 1

            sorted_token2count = sorted(token2count.items(),
                                        key=operator.itemgetter(1),
                                        reverse=True)
            self.token2count = collections.OrderedDict(sorted_token2count)

            for token, token_count in token2count.items():
                if token not in token2id and token_count >= self.min_count:
                    token2id[token] = len(token2id)
            self.token2idx = token2id
            self.idx2token = dict([(v, k) for k, v in self.token2idx.items()])

            top_k_vocab = [k for (k, v) in list(self.token2idx.items())[:10]]
            logger.debug(f"--- Build vocab dict finished, Total: {len(self.token2idx)} ---")
            logger.debug(f"Top-10: {top_k_vocab}")

    def transform(self, samples):
        numerized_samples = []
        for seq in samples:
            if self.index is not None:
                seq = seq[self.index]

            #            if self.token_bos in self.token2id:
            #                seq = [self.token_bos] + seq + [self.token_eos]
            #            else:
            #                seq = [self.token_pad] + seq + [self.token_pad]
            if self.token_unk in self.token2idx:
                unk_index = self.token2idx[self.token_unk]
                numerized_samples.append([self.token2idx.get(token, unk_index) for token in seq])
            else:
                numerized_samples.append([self.token2idx[token] for token in seq])


        token_ids = numerized_samples

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

    def doc2bow(self, doc, allow_update=False, return_missing=False):
        """Convert `document` into the bag-of-words (BoW) format = list of `(token_id, token_count)` tuples.

        Parameters
        ----------
        doc : list of str
            Input document.
        allow_update : bool, optional
            Update self, by adding new tokens from `document` and updating internal corpus statistics.
        return_missing : bool, optional
            Return missing tokens (tokens present in `document` but not in self) with frequencies?

        Return
        ------
        list of (int, int)
            BoW representation of `document`.
        list of (int, int), dict of (str, int)
            If `return_missing` is True, return BoW representation of `document` + dictionary with missing
            tokens and their frequencies.

        """


        if isinstance(doc, string_types):
            raise TypeError("doc2bow expects an array of unicode tokens on input, not a single string")

        # Construct (word, frequency) mapping.
        counter = defaultdict(int)
        for w in doc:
            counter[w if isinstance(w, str) else str(w, 'utf-8')] += 1


        if allow_update or return_missing:
            missing = sorted(x for x in iteritems(counter) if x[0] not in self.token2idx)
            if allow_update:
                for w, _ in missing:
                    # new id = number of ids made so far;
                    # NOTE this assumes there are no gaps in the id sequence!
                    self.token2idx[w] = len(self.token2idx)
        result = {self.token2idx[w]: freq for w, freq in iteritems(counter) if w in self.token2idx}


        # return tokenids, in ascending id order
        result = sorted(iteritems(result))
        if return_missing:
            return result, dict(missing)
        else:
            return result


if __name__ == "__main__":
    pass
