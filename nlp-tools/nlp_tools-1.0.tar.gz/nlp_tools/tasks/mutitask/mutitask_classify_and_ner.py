# encoding: utf-8

# author: BrikerMan
# contact: eliyar917@gmail.com
# blog: https://eliyar.biz

# file: abc_model.py
# time: 4:30 下午

from abc import ABC
from typing import List, Dict, Any, Union, Optional

import numpy as np
import tensorflow as tf

import nlp_tools
from nlp_tools.embeddings import ABCEmbedding, BareEmbedding,TransformerEmbedding,BertEmbedding
from nlp_tools.generators import CorpusGenerator, BatchGenerator
from nlp_tools.logger import logger
from nlp_tools.metrics.sequence_labeling import get_entities
from nlp_tools.metrics.sequence_labeling import sequence_labeling_report
from nlp_tools.processors import SequenceProcessor
from nlp_tools.tasks.abs_task_model import ABCTaskModel
from nlp_tools.types import TextSamplesVar
from nlp_tools.optimizer import MultiOptimizer

from tensorflow.keras.optimizers import Adam
from nlp_tools.utils.ner_utils import output_ner_results
from nlp_tools.utils.training_tips import creat_FGM
from nlp_tools.loss.r_drop_loss import RDropLoss
from sklearn.model_selection._split import StratifiedKFold,KFold
from tensorflow.keras import backend as K
import functools
import os



class MutitaskClassifyAndNer(ABCTaskModel, ABC):
    """
    Abstract Labeling Model
    """

    def __init__(self,
                 **kwargs):
        """

        Args:
            embedding: embedding object
            max_sequence_length: target sequence length
            hyper_parameters: hyper_parameters to overwrite
        """
        super(MutitaskClassifyAndNer, self).__init__(**kwargs)





    def build_model_arc(self) -> None:
        raise NotImplementedError

    def compile_model(self,
                      loss: Any = None,
                      optimizer: Any = None,
                      metrics: Any = None,
                      **kwargs: Any) -> None:

        if loss is None:
            loss = 'sparse_categorical_crossentropy'


        if type(self.embedding) in [TransformerEmbedding,BertEmbedding] :
            total_layers = self.tf_model.layers
            transfomer_layers = self.embedding.embed_model.layers
            no_transformer_layers = [layer for layer in total_layers if layer not in transfomer_layers]
            optimizer_list = [
                Adam(learning_rate=1e-5),
                Adam(learning_rate=2e-5)
            ]
            optimizers_and_layers = [(optimizer_list[0], no_transformer_layers), (optimizer_list[1], transfomer_layers)]
            optimizer = MultiOptimizer(optimizers_and_layers)




        if optimizer is None:
            optimizer = Adam(learning_rate=1e-5)
        if self.use_rdrop:
            if type(loss) == list:
                loss = [RDropLoss(i) for i in loss]
            else:
                loss = RDropLoss(loss)


        if metrics is None:
            metrics = ['accuracy']

        self.tf_model.compile(loss=loss,
                              optimizer=optimizer,
                              metrics=metrics,
                              **kwargs)


