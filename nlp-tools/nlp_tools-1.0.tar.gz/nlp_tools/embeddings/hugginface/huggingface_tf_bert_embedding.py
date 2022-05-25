#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
# author:fanfanfeng
# contact: 544855237@qq.com
# datetime:2022/3/7 下午11:31
'''
from transformers.models.bert.modeling_tf_bert import TFBertPreTrainedModel,TFBertMainLayer,TFBertModel
from transformers.models.bert.configuration_bert import BertConfig

class HuggingfaceTFBertModel(TFBertModel):
    def __init__(self, config: BertConfig, *inputs, **kwargs):
        super(TFBertPreTrainedModel,self).__init__(config, *inputs, **kwargs)

        self.bert = TFBertMainLayer(config, name="bert",add_pooling_layer=False)




if __name__ == '__main__':
    b = BertConfig()
    a  = HuggingfaceTFBertModel(b)