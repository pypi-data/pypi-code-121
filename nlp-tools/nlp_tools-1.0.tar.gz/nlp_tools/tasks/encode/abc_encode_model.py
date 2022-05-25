#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
# author:fanfanfeng
# contact: 544855237@qq.com
# datetime:2022/3/1 下午11:02
'''

from nlp_tools.tasks.abs_task_model import ABCTaskModel

from typing import Dict,Any,List
from keras.api._v2.keras.optimizers import Adam
import nlp_tools

class AbcEncodeModel(ABCTaskModel):

    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
        }

    def build_model_arc(self) -> None:
        pass

    def __init__(self, text_processor, label_processor, pooler_type='cls', output_size=512, **kwargs):
        super().__init__(text_processor, label_processor,**kwargs)
        self.pooler_type = pooler_type
        self.output_size = output_size
        self. training_model = None
        assert self.pooler_type in ["cls", "cls_before_pooler", "avg", "avg_top2",
                                    "avg_first_last"], "unrecognized pooling type %s" % self.pooler_type





    def compile_model(self,
                      loss: Any = None,
                      optimizer: Any = None,
                      metrics: Any = None,
                      **kwargs: Any) -> None:

        if loss is None:
            loss = 'sparse_categorical_crossentropy'
        if optimizer is None:
            optimizer = Adam(learning_rate=1e-5)
        if metrics is None:
            metrics = ['accuracy']

        self.training_model.compile(loss=loss,
                              optimizer=optimizer,
                              metrics=metrics,
                              **kwargs)

    def encode(self,
                    x_data:List[str],
                    *,
                    batch_size: int = 32,
                    truncating: bool = True,
                    predict_kwargs: Dict = None
                ) :
        if predict_kwargs is None:
            predict_kwargs = {}

        with nlp_tools.utils.custom_object_scope():
            if truncating:
                seq_length = self.max_sequence_length
            else:
                seq_length = None
            tensor = self.text_processor.transform(x_data,seq_length=seq_length)
            encode_ts = self.tf_model.predict(tensor, batch_size=batch_size, **predict_kwargs)
        return encode_ts




    def fit_generator(self,
                      train_sample_gen,
                      valid_sample_gen,
                      epochs: int = 5,
                      callbacks = None,
                      fit_kwargs: Dict = None) -> 'tf.keras.callbacks.History':
        self.build_model_generator([g for g in [train_sample_gen, valid_sample_gen] if g])
        return self.training_model.fit(train_sample_gen.forfit(),
                                 steps_per_epoch=len(train_sample_gen),
                                 epochs=epochs,
                                 callbacks=callbacks,
                                 **fit_kwargs)