from typing import Dict, Optional, Tuple, Union

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers as L

from transformers import TFRobertaPreTrainedModel, TFRobertaMainLayer, RobertaConfig, RobertaTokenizer
from transformers.file_utils import add_start_docstrings_to_model_forward, add_code_sample_docstrings
from transformers.modeling_tf_outputs import TFSequenceClassifierOutput
from transformers.modeling_tf_utils import TFSequenceClassificationLoss, get_initializer, TFModelInputType, \
    input_processing

from transformers.models.roberta.modeling_tf_roberta import ROBERTA_INPUTS_DOCSTRING,_TOKENIZER_FOR_DOC,_CHECKPOINT_FOR_DOC,_CONFIG_FOR_DOC


from nlp_tools.utils.prompt.prefix_encoder import PrefixEncoder,get_prompt_values

class TFRobertaPrefixForSequenceClassification(TFRobertaPreTrainedModel):
    _keys_to_ignore_on_load_unexpected = [r"mlm___cls", r"nsp___cls", r"cls.predictions", r"cls.seq_relationship"]
    _keys_to_ignore_on_load_missing = [r"dropout"]

    def __init__(self, config: RobertaConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.config = config



        self.n_layer = config.num_hidden_layers
        self.n_head = config.num_attention_heads
        self.n_embd = config.hidden_size // config.num_attention_heads
        self.pre_seq_len = 8#config.pre_seq_len
        config.pre_seq_len = 8
        config.prefix_projection = True
        config.prefix_hidden_size = 512

        self.dropout = tf.keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.prefix_tokens = np.arange(self.pre_seq_len).reshape((-1,self.pre_seq_len)).tolist()
        self.prefix_encoder = PrefixEncoder(config)

        self.roberta = TFRobertaMainLayer(config,name="roberta")


    def get_prompt(self, batch_size):
        prefix_tokens = tf.convert_to_tensor(self.prefix_tokens,dtype=tf.int32)
        prefix_tokens = tf.tile(prefix_tokens,multiples=[batch_size,1])

        past_key_values = self.prefix_encoder(prefix_tokens)
        past_key_values = tf.reshape(past_key_values,
            shape=(batch_size,self.pre_seq_len,self.n_layer * 2, self.n_head,self.n_embd))
        past_key_values = self.dropout(past_key_values)
        past_key_values = tf.transpose(past_key_values,[2, 0, 3, 1, 4])
        past_key_values = tf.split(past_key_values,self.n_layer)
        return past_key_values






    @add_start_docstrings_to_model_forward(ROBERTA_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    @add_code_sample_docstrings(
        processor_class=_TOKENIZER_FOR_DOC,
        checkpoint=_CHECKPOINT_FOR_DOC,
        output_type=TFSequenceClassifierOutput,
        config_class=_CONFIG_FOR_DOC,
    )
    def call(
            self,
            input_ids: Optional[TFModelInputType] = None,
            attention_mask: Optional[Union[np.ndarray, tf.Tensor]] = None,
            token_type_ids: Optional[Union[np.ndarray, tf.Tensor]] = None,
            position_ids: Optional[Union[np.ndarray, tf.Tensor]] = None,
            head_mask: Optional[Union[np.ndarray, tf.Tensor]] = None,
            inputs_embeds: Optional[Union[np.ndarray, tf.Tensor]] = None,
            output_attentions: Optional[bool] = None,
            output_hidden_states: Optional[bool] = None,
            return_dict: Optional[bool] = None,
            training: Optional[bool] = False,
            **kwargs,
    ) -> Union[TFSequenceClassifierOutput, Tuple[tf.Tensor]]:
        r"""
                labels (:obj:`tf.Tensor` or :obj:`np.ndarray` of shape :obj:`(batch_size,)`, `optional`):
                    Labels for computing the sequence classification/regression loss. Indices should be in :obj:`[0, ...,
                    config.num_labels - 1]`. If :obj:`config.num_labels == 1` a regression loss is computed (Mean-Square loss),
                    If :obj:`config.num_labels > 1` a classification loss is computed (Cross-Entropy).
                """
        batch_size = tf.shape(input_ids['input_ids'])[0] # 4
        past_key_values = self.get_prompt(batch_size=batch_size) # shape=[2,4,16,8,64]
        prefix_attention_mask = tf.ones((batch_size, self.pre_seq_len),dtype=tf.int32)
        attention_mask = L.concatenate((prefix_attention_mask, attention_mask), axis=1) # shape [4,136]


        inputs = input_processing(
            func=self.call,
            config=self.config,
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
            kwargs_call=kwargs,
            past_key_values=past_key_values,
        )








        outputs = self.roberta(
            input_ids=inputs["input_ids"],
            attention_mask=attention_mask,
            token_type_ids=inputs["token_type_ids"],
            position_ids=inputs["position_ids"],
            head_mask=inputs["head_mask"],
            inputs_embeds=inputs["inputs_embeds"],
            output_attentions=inputs["output_attentions"],
            output_hidden_states=inputs["output_hidden_states"],
            return_dict=inputs["return_dict"],
            #training=inputs["training"],
            past_key_values=inputs["past_key_values"],
        )

        pooled_output = outputs[1]
        pooled_output = self.dropout(inputs=pooled_output, training=inputs["training"])
        logits = self.classifier(inputs=pooled_output)
        loss = None if inputs["labels"] is None else self.compute_loss(labels=inputs["labels"], logits=logits)
        if not inputs["return_dict"]:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output

        return TFSequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )



if __name__ == '__main__':



    model_name = "roberta-large"

    config = RobertaConfig.from_pretrained(model_name)
    model = TFRobertaPrefixForSequenceClassification(config)
    from transformers import BertTokenizer
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    tf_batch = tokenizer(
        ['we are very happy to show you the transformers library.',
         "we hope you don't hate it.",
         ],
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors='tf',
    )
    #tf_outputs = model(tf_batch)
    tf_outputs = model(tf_batch, attention_mask = tf_batch['attention_mask'],labels=tf.constant([1, 0]))
    print(tf_outputs)