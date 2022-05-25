from nlp_tools.tokenizer.base_tokenizer import ABCTokenizer
from nlp_tools.utils.data import load_vocab
from typing import Dict,Any



class WhiteSpaceTokenizer(ABCTokenizer):
    """white space tokenizer
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(WhiteSpaceTokenizer, self).to_dict()
        data['config']['token_dict'] = self.token_dict
        return data

    def __init__(self, token_dict=None,max_position = 512):
        if not token_dict:
            token_dict = {}
        self.token_dict = token_dict
        # startswith = ['[PAD]', '[UNK]', '[CLS]', '[SEP]']
        if type(token_dict) != dict:
            self.token_dict = load_vocab(
                dict_path=token_dict
            )

        self.max_position = max_position
        self.id_to_token_dict = {id:key for key,id in self.token_dict.items()}

        self._token_pad_id = self.token_dict['[PAD]']
        self._token_start_id = self.token_dict['[CLS]']
        self._token_end_id = self.token_dict['[SEP]']
        self._token_mask_id = self.token_dict['[UNK]']
        self._vocab_size = len(self.token_dict)


    def tokenize(self, text, maxlen=None, **kwargs):
        if not maxlen:
            maxlen = self.max_position
        elif maxlen > self.max_position:
            maxlen = self.max_position

        if type(text) == str:
            text = text.split(" ")
            text = [t for t in text if t !=""]
            if len(text) > maxlen:
                text = text[:maxlen - 2]
        elif type(text) == list:
            if len(text) > maxlen - 2:
                text = text[:maxlen - 2]

        # 如果不以cls开头，则需要补充cls
        if text[0] != '[CLS]':
            text = ['[CLS]'] + text + ['[SEP]']
        return text


    def encode(self,
                text,
                second_text=None,
                maxlen=None,
                pattern='S*E*E',
                truncate_from='right'):
        assert type(text) in [list, str]
        if maxlen and maxlen > self.max_position:
            maxlen = self.max_position

        text_tokens = self.tokenize(text,maxlen=maxlen)
        token_ids = self.tokens_to_ids(text_tokens)
        first_segment_ids = [0] * len(token_ids)
        return token_ids, first_segment_ids
    
    def id_to_token(self, id):
        return self.id_to_token_dict[id]

    def tokens_to_ids(self,tokens):
        return [self.token_dict.get(token,1) for token in tokens]

