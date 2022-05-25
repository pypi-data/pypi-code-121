#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
# author:fanfanfeng
# contact: 544855237@qq.com
# datetime:2022/3/1 下午11:09
'''
from nlp_tools.tasks.simalary.abc_similary_model import AbcSimilaryModel

class BertForContrastiveLearning(AbcSimilaryModel):
    def build_model_arc(self) -> None:
        config = self.hyper_parameters
        embed_model = self.embedding.embed_model

        tensor = embed_model.output

        if self.pooler_type == "cls":
            pass
