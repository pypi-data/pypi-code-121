import collections
import operator
from typing import Dict,List,Any,Optional,Union

import numpy as np
import tqdm
from tensorflow.keras.preprocessing.sequence import pad_sequences

from nlp_tools.generators import CorpusGenerator
from nlp_tools.logger import  logger
from nlp_tools.processors.abc_processor import ABCProcessor
from nlp_tools.types import TextSamplesVar


class SimilarySequenceProcessor(ABCProcessor):
    """
        Generic processors for the sequence samples.
        """

    def to_dict(self) -> Dict[str,Any]:
        data = super(SimilarySequenceProcessor,self).to_dict()
        data['config'].update({
            'build_in_vocab':self.build_in_vocab,
            'min_count':self.min_count,
            'conbime_sentence':False
        })
        return data

    def __init__(self,
                 build_in_vocab: str = 'text',
                 min_count: int = 3,
                 conbime_sentence:bool = False,
                 **kwargs: Any) -> None:
        """
                Args:
                    vocab_dict_type: initial vocab dict type, one of `text` `labeling`.
                    **kwargs:
                """
        super(SimilarySequenceProcessor,self).__init__(**kwargs)

        self.build_in_vocab = build_in_vocab
        self.min_count = min_count
        self.conbime_sentence = conbime_sentence

        if build_in_vocab == 'text':
            self._initial_vocab_dict = {
                self.token_pad: 0,
                self.token_unk: 1,
                self.token_bos: 2,
                self.token_eos: 3
            }
        else:
            self._initial_vocab_dict = {}

        self._showed_seq_len_warning = False

    def build_vocab_generator(self,generators: List[CorpusGenerator]) -> None:
        if not self.vocab2idx:
            vocab2idx = self._initial_vocab_dict

            token2count: Dict[str,int] = {}

            for gen in generators:
                for sentence,label in tqdm.tqdm(gen,desc="Preparing text vocab dict"):
                    target_1,target_2 = sentence
                    for token in self.tokenizer.tokenize(target_1):
                        count = token2count.get(token,0)
                        token2count[token] = count+ 1

                    for token in self.tokenizer.tokenize(target_2):
                        count = token2count.get(token,0)
                        token2count[token] = count+ 1



            sorted_token2count = sorted(token2count.items(),
                                        key=operator.itemgetter(1),
                                        reverse=True)
            token2count = collections.OrderedDict(sorted_token2count)

            for token,token_count in token2count.items():
                if token not in vocab2idx and token_count >= self.min_count:
                    vocab2idx[token] = len(vocab2idx)
            self.vocab2idx = vocab2idx
            self.idx2vocab = dict([(v,k) for k,v in self.vocab2idx.items()])

            top_k_vocab = [k for (k,v) in list(self.vocab2idx.items())[:10]]
            logger.debug(f"--- Build vocab dict finished, Total: {len(self.vocab2idx)} ---")
            logger.debug(f"Top-10: {top_k_vocab}")

    def transform(self,
                  samples: TextSamplesVar,
                  *,
                  seq_length: int = None,
                  max_position: int = None,
                  segment: bool = False ) -> np.ndarray:
        tokenized_sentences = []
        for pair in samples:
            seq_1,seq_2 = pair
            tokenized_sentences.append([self.tokenizer.tokenize(seq_1),self.tokenizer.tokenize(seq_2)])


        seq_length_from = ""
        if seq_length is None:
            seq_length_from = 'max length of the samples'
            seq_1_list = [i[0] for i in tokenized_sentences]
            seq_2_list = [i[1] for i in tokenized_sentences]

            max_1 = max([len(i) for i in seq_1_list])
            max_2 = max([len(i) for i in seq_2_list])
            if self.conbime_sentence:
                seq_length = max_1 + max_2
            else:
                seq_length = max(max_1,max_2)
        if max_position is not None and max_position < seq_length:
            seq_length_from = 'max embedding seq length'
            seq_length = max_position

        if seq_length_from and not self._showed_seq_len_warning:
            logger.warning(
                f'Sequence length is None, will use the {seq_length_from}, which is {seq_length}')
            self._showed_seq_len_warning = True

        numerized_samples = []
        segment_ids = []

        if self.conbime_sentence:
            for seq in samples:
                seq_tokens,seq_segment_ids = self.tokenizer.encode(seq[0],seq[1],maxlen=seq_length)

                numerized_samples.append(seq_tokens)
                segment_ids.append(seq_segment_ids)

            token_ids = pad_sequences(numerized_samples, seq_length, padding='post', truncating='post')
            segment_ids = pad_sequences(segment_ids, seq_length, padding='post', truncating='post')
        else:
            seq_list_1 = []
            seq_list_2 = []
            for seq in samples:
                if hasattr(self.tokenizer,"encode"):
                    seq_tokens_1, seq_segment_ids_1 = self.tokenizer.encode(seq[0],maxlen=seq_length)
                    seq_tokens_2, seq_segment_ids_2 = self.tokenizer.encode(seq[1], maxlen=seq_length)
                else:
                    seq_tokens_1,seq_tokens_2 = seq
                    seq_tokens_1, seq_tokens_2 = self.tokenizer.tokenize(seq_tokens_1),self.tokenizer.tokenize(seq_tokens_2)

                    if self.token_bos in self.vocab2idx:
                        seq_tokens_1 = [self.token_bos] + seq_tokens_1 + [self.token_eos]
                        seq_tokens_2 = [self.token_bos] + seq_tokens_2 + [self.token_eos]
                    else:
                        seq_tokens_1 = [self.token_pad] + seq_tokens_1 + [self.token_pad]
                        seq_tokens_2 = [self.token_pad] + seq_tokens_2 + [self.token_pad]

                    if self.token_unk in self.vocab2idx:
                        unk_index = self.vocab2idx[self.token_unk]
                        seq_tokens_1 = [self.vocab2idx.get(token, unk_index) for token in seq_tokens_1]
                        seq_tokens_2 = [self.vocab2idx.get(token, unk_index) for token in seq_tokens_2]
                    else:
                        seq_tokens_1 = [self.vocab2idx[token] for token in seq_tokens_1]
                        seq_tokens_2 = [self.vocab2idx[token] for token in seq_tokens_2]
                seq_list_1.append(seq_tokens_1)
                seq_list_2.append(seq_tokens_2)


            seq_list_1 = pad_sequences(seq_list_1, seq_length, padding='post', truncating='post')
            seq_segment_ids_1  = np.zeros(seq_list_1.shape,dtype=np.int32)
            seq_list_2 = pad_sequences(seq_list_2, seq_length, padding='post', truncating='post')
            seq_segment_ids_2  = np.zeros(seq_list_2.shape,dtype=np.int32)


            #numerized_samples.append([seq_list_1,seq_list_2])
            segment_ids.append([seq_segment_ids_1,seq_segment_ids_2])
            token_ids = [seq_list_1,seq_list_2]
            segment_ids = [seq_segment_ids_1,seq_segment_ids_2]



        if segment:
            return token_ids,segment_ids
        else:
            return token_ids

    def inverse_transform(self,
                          labels: Union[List[List[int]], np.ndarray],
                          *,
                          lengths: List[int] = None,
                          threshold: float = 0.5,
                          **kwargs: Any) -> List[List[str]]:
        result = []
        for index,seq in enumerate(labels):
            labels_ = []
            for idx in seq:
                labels_.append(self.idx2vocab[idx])

            if lengths is not None:
                labels_ = labels_[1:lengths[index] + 1]
            else:
                labels_ = labels_[1:-1]
            result.append(labels_)
        return result