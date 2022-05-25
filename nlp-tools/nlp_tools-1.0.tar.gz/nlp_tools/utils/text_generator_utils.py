from bert4keras.snippets import AutoRegressiveDecoder
from tensorflow.keras.models import Model
import numpy as np

class AutoTitle(AutoRegressiveDecoder):
    """解码器
    """

    def __init__(self,generator_mode,tokenizer,max_generator_len,max_seq_len=32 ,**kwargs):
        kwargs["maxlen"] = max_generator_len
        super(AutoTitle,self).__init__(**kwargs)
        self.generate_mode = generator_mode
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len
        self.max_generator_len = max_generator_len


    @AutoRegressiveDecoder.wraps(default_rtype='probas')
    def predict(self, inputs, output_ids, states):
        token_ids, segment_ids = inputs
        token_ids = np.concatenate([token_ids, output_ids], 1)
        segment_ids = np.concatenate([segment_ids, np.ones_like(output_ids)], 1)
        if type(self.generate_mode) != Model:
            return self.last_token(self.generate_mode.tf_model).predict([token_ids, segment_ids])[:, -1]
        else:
            return self.last_token(self.generate_mode).predict([token_ids, segment_ids])[:, -1]

    def generate(self, text, topk=1):
        token_ids, segment_ids = self.tokenizer.encode(text, maxlen=self.max_seq_len)
        output_ids = self.beam_search([token_ids, segment_ids],
                                      topk=topk)  # 基于beam search
        return self.tokenizer.decode(output_ids)
