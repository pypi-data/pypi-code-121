from typing import Dict, Any, Tuple
from collections import Counter
import sys, warnings, os
import tqdm
from multiprocessing import Pool
import tempfile, operator, collections


class BaseIndexer():
    def to_dict(self) -> Dict[str, Any]:
        return {
            'config': {
                'token_pad': self.token_pad,
                'token_unk': self.token_unk,
                'token_bos': self.token_bos,
                'token_eos': self.token_eos,
                'token2idx': self.token2idx
            },
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
        }

    def __init__(self,multi_label=False,index=None, **kwargs: Any) -> None:
        from sklearn.preprocessing import MultiLabelBinarizer

        self.token2idx = kwargs.get('token2idx', {})
        self.idx2token = dict([(v, k) for k, v in self.token2idx.items()])

        self.token_pad: str = kwargs.get('token_pad', '[PAD]')  # type: ignore
        self.token_unk: str = kwargs.get('token_unk', '[UNK]')  # type: ignore
        self.token_bos: str = kwargs.get('token_bos', '[CLS]')  # type: ignore
        self.token_eos: str = kwargs.get('token_eos', '[SEP]')  # type: ignore

        self.multi_label = multi_label
        self.index = index
        self.multi_label_binarizer = MultiLabelBinarizer(classes=self.token2idx)

    @property
    def vocab_size(self) -> int:
        return len(self.token2idx)

    def __getitem__(self, tokenid):
        """Get the string token that corresponds to `tokenid`.
        Parameters
        ----------
        tokenid : int
            Id of token.
        Returns
        -------
        str
            Token corresponding to `tokenid`.
        Raises
        ------
        KeyError
            If this Dictionary doesn't contain such `tokenid`.
        """

        return self.idx2token[tokenid]  # will throw for non-existent ids

    def __iter__(self):
        """Iterate over all tokens."""
        return iter(self.keys())

    # restore Py2-style dict API
    iterkeys = __iter__

    def keys(self):
        """Get all stored ids.
        Returns
        -------
        list of int
            List of all token ids.
        """
        return list(self.token2idx.values())

    def __len__(self):
        """Get number of stored tokens.
        Returns
        -------
        int
            Number of stored tokens.
        """
        return len(self.token2idx)


    @property
    def is_vocab_build(self) -> bool:
        return self.vocab_size != 0

    def build_vocab(self, x_data, y_data=None):
        raise NotImplementedError

    def build_vocab_generator(self, generators):
        from sklearn.preprocessing import MultiLabelBinarizer
        if self.token2idx:
            return

        vocab2idx: Dict[str, int] = {}
        token2count: Dict[str, int] = {}
        for generator in generators:
            if self.multi_label:
                for _, label in tqdm.tqdm(generator, desc="Preparing classification label vocab dict"):
                    if self.index is not None:
                        label = label[self.index]
                    for token in label:
                        count = token2count.get(token, 0)
                        token2count[token] = count + 1
            else:
                for _, label in tqdm.tqdm(generator, desc="Preparing classification label vocab dict"):
                    if self.index is not None:
                        label = label[self.index]

                    count = token2count.get(label, 0)
                    token2count[label] = count + 1

        sorted_token2count = sorted(token2count.items(),
                                    key=operator.itemgetter(1),
                                    reverse=True)
        token2count = collections.OrderedDict(sorted_token2count)

        for token, token_count in token2count.items():
            if token not in vocab2idx:
                vocab2idx[token] = len(vocab2idx)
        self.token2idx = vocab2idx
        self.idx2token = dict([(v, k) for k, v in self.token2idx.items()])
        self.multi_label_binarizer = MultiLabelBinarizer(classes=self.token2idx)

    def get_tensor_shape(self, batch_size: int, seq_length: int) -> Tuple:
        return batch_size, seq_length

    def transform(self, samples):
        raise NotImplementedError

    def inverse_transform(self, labels, lengths=None, threshold: float = 0.5, **kwargs):
        raise NotImplementedError

    def get_vocabulary(self, data, is_dict=False, num_workers=1):
        """Read text and return dictionary that encodes vocabulary
        """
        vocab = Counter()
        if is_dict:

            for i, line in enumerate( tqdm.tqdm(data)):
                try:
                    word, count = line.strip('\r\n ').split(' ')
                except:
                    print('Failed reading vocabulary file at line {0}: {1}'.format(i, line))
                    sys.exit(1)
                vocab[word] += int(count)
        elif num_workers == 1:
            if num_workers > 1:
                warnings.warn("In parallel mode, the input cannot be STDIN. Using 1 processor instead.")
            for i, line in enumerate( tqdm.tqdm(data)):
                for word in line.strip('\r\n ').split(' '):
                    if word:
                        vocab[word] += 1

        elif num_workers > 1:
            size = len(data)
            chunk_size = int(size / num_workers)
            offsets = [i*chunk_size for i in range(num_workers + 1)]
            offsets[-1]=size

            vocab_files = []
            pool = Pool(processes=num_workers)
            for i in range(num_workers):
                tmp = tempfile.NamedTemporaryFile(delete=False)
                tmp.close()
                vocab_files.append(tmp)
                pool.apply_async(self._get_vocabulary, (data, tmp.name, offsets[i], offsets[i + 1]))
            pool.close()
            pool.join()
            import pickle
            for i in range(num_workers):
                with open(vocab_files[i].name, 'rb', encoding='utf-8') as f:
                    vocab += pickle.load(f)
                os.remove(vocab_files[i].name)
        else:
            raise ValueError('`num_workers` is expected to be a positive number, but got {}.'.format(num_workers))
        return vocab
    def _get_vocabulary(self, data, outfile, begin, end):
        import pickle
        vocab = Counter()
        for line in  tqdm.tqdm(data[begin:end]):
            for word in line.strip('\r\n ').split(' '):
                if word:
                    vocab[word] += 1
        with open(outfile, 'wb') as f:
            pickle.dump(vocab, f)


if __name__ == "__main__":
    print("Hello world")
