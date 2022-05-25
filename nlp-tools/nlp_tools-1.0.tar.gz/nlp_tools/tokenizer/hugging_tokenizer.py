from nlp_tools.tokenizer.base_tokenizer import ABCTokenizer
from typing import Dict,Any


from transformers import AutoTokenizer,BertTokenizer



class HuggingTokenizer(ABCTokenizer):
    """hugging tokenizer wrapper
    """

    def to_dict(self) -> Dict[str, Any]:
        data = super(HuggingTokenizer, self).to_dict()
        data['config']['model_path'] = self.model_path
        data['config']['need_attention_ids'] = self.need_attention_ids

        self.tokenizer.save_pretrained(self.model_path)
        return data

    def __init__(self, model_path, need_attention_ids=True):
        super().__init__()
        self.model_path = model_path
        self._tokenizer:BertTokenizer = AutoTokenizer.from_pretrained(model_path)

        self.need_attention_ids = need_attention_ids

    def change_model_path(self, new_model_path):
        self.model_path = new_model_path

    def tokenize(self, text, maxlen=None, add_special_tokens=True,**kwargs):
        text = self.tokenizer.tokenize(text,add_special_tokens=add_special_tokens,max_length=maxlen)
        return text


    def encode(self,
                text_or_list,
                second_text=None,
                maxlen=None,
                is_split_into_words=False,
                add_special_tokens=True,
               **kwargs):
        if type(text_or_list) == str:
            text_or_list = [text_or_list]


        tokener_dict = self.tokenizer(text_or_list,padding=True,truncation=True,return_tensors='np',max_length=maxlen,is_split_into_words=is_split_into_words,add_special_tokens=add_special_tokens,**kwargs)


        if not self.need_attention_ids:
            if 'attention_mask' in tokener_dict:
                del tokener_dict['attention_mask']
        return [value for key,value in tokener_dict.items()]
    


