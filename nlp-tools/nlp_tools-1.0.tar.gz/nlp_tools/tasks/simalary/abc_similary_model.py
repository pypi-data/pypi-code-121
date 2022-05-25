#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
# author:fanfanfeng
# contact: 544855237@qq.com
# datetime:2022/3/1 下午11:02
'''

from nlp_tools.tasks.abs_task_model import ABCTaskModel

from typing import Dict,Any

class AbcSimilaryModel(ABCTaskModel):

    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
        }

    def build_model_arc(self) -> None:
        pass

    def __init__(self,pooler_type='cls',output_size=512):
        self.pooler_type = pooler_type
        self.output_size = output_size
        assert self.pooler_type in ["cls", "cls_before_pooler", "avg", "avg_top2",
                                    "avg_first_last"], "unrecognized pooling type %s" % self.pooler_type

