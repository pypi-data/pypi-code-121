import random
import os
from abc import ABC
import numpy as np
from typing import List,Dict,Any,Union
from tensorflow import keras

import nlp_tools
from nlp_tools.embeddings import BertEmbedding
from nlp_tools.generators import BertGeneratorDataSet,CorpusGenerator
from nlp_tools.logger import logger
from nlp_tools.tasks.abs_task_model import ABCTaskModel
from nlp_tools.types import TextSamplesVar,ClassificationLabelVar,MultiLabelClassificationLabelVar
from nlp_tools.loss import TextGenerateCrossEntropy
from nlp_tools.tokenizer.bert_tokenizer import BertTokenizer
from nlp_tools.processors.sequence_processor import SequenceProcessor
from tensorflow.keras.optimizers import Adam



class BertGeneratorModel(ABCTaskModel,ABC):
    """
    Abstract Classification Model
    """

    __task__ = 'generator'

    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            }

    def to_dict(self) -> Dict:
        info = super(BertGeneratorModel, self).to_dict()
        info['config']['bert_model_path'] = self.bert_model_path
        info['config']['sequence_length'] = self.sequence_length
        info['config']['hyper_parameters'] = self.hyper_parameters
        info['config']['bert_application'] = self.bert_application
        info['config']['bert_token_simplified'] = self.bert_token_simplified
        return info

    def __init__(self,
                 bert_model_path ,
                 text_processor = None,
                 sequence_length: int = None,
                 hyper_parameters: Dict[str, Dict[str, Any]] = None,
                 bert_application='unilm',
                 bert_token_simplified=True):
        """
        Args:
            sequence_length: target sequence length
            hyper_parameters: hyper_parameters to overwrite
            text_processor: text processor
        """
        super(BertGeneratorModel, self).__init__()

        if text_processor == None:

            bert_vocab_path = os.path.join(bert_model_path,'vocab.txt')
            text_tokenizer = BertTokenizer(token_dict=bert_vocab_path,simplified=bert_token_simplified)
            text_processor = SequenceProcessor(text_tokenizer=text_tokenizer)

        if type(text_processor.text_tokenizer) != BertTokenizer:
            raise("bert Embedding must use bertTokenizer")

        self.embedding = BertEmbedding(model_folder=bert_model_path,
                                       bert_application=bert_application,
                                       keep_tokens=text_processor.text_tokenizer.keep_tokens,
                                       simplified=text_processor.text_tokenizer.simplified)  # type: ignore
        self.bert_model_path = bert_model_path
        self.sequence_length = sequence_length
        self.bert_application = bert_application
        self.text_processor = text_processor
        self.label_processor = text_processor
        self.hyper_parameters = hyper_parameters
        self.bert_token_simplified = bert_token_simplified


    def build_model(self,
                    x_train: TextSamplesVar,
                    y_train: TextSamplesVar) -> None:
        train_gen = CorpusGenerator(x_train, y_train)
        self.build_model_generator([train_gen])

    def build_model_generator(self,
                              generators: List[CorpusGenerator]) -> None:
        if not self.text_processor.vocab2idx:
            self.text_processor.build_vocab_generator(generators)
        self.embedding.setup_text_processor(self.text_processor)

        if self.sequence_length is None:
            self.sequence_length = self.text_processor.get_max_seq_length_from_corpus(generators)

        if self.tf_model is None:
            self.build_model_arc()
            self.compile_model()

    def build_model_arc(self) -> None:
        output = TextGenerateCrossEntropy(2)(self.embedding.embed_model.inputs + self.embedding.embed_model.outputs)
        self.tf_model = keras.Model(self.embedding.embed_model.inputs, output)

    def compile_model(self,
                      optimizer: Any = None,
                      **kwargs: Any) -> None:
        if optimizer is None:
            optimizer = Adam(1e-5)

        self.tf_model.compile( optimizer=optimizer, **kwargs)

    def fit(self,
            x_train: TextSamplesVar,
            y_train: TextSamplesVar,
            x_validate: TextSamplesVar = None,
            y_validate: Union[ClassificationLabelVar, MultiLabelClassificationLabelVar] = None,
            *,
            batch_size: int = 64,
            epochs: int = 5,
            callbacks: List['keras.callbacks.Callback'] = None,
            fit_kwargs: Dict = None) -> 'keras.callbacks.History':
        train_gen = CorpusGenerator(x_train, y_train)
        if x_validate is not None:
            valid_gen = CorpusGenerator(x_validate,y_validate)
        else:
            valid_gen = None
        return self.fit_generator(train_sample_gen=train_gen,
                                  valid_sample_gen=valid_gen,
                                  batch_size=batch_size,
                                  epochs=epochs,
                                  callbacks=callbacks,
                                  fit_kwargs=fit_kwargs)

    def fit_generator(self,
                      train_sample_gen: CorpusGenerator,
                      valid_sample_gen: CorpusGenerator = None,
                      *,
                      batch_size: int = 64,
                      epochs: int = 5,
                      callbacks: List['keras.callbacks.Callback'] = None,
                      fit_kwargs: Dict = None) -> 'keras.callbacks.History':
        self.build_model_generator([g for g in [train_sample_gen, valid_sample_gen] if g])
        model_summary = []
        self.tf_model.summary(print_fn=lambda x: model_summary.append(x))
        logger.debug('\n'.join(model_summary))

        train_set = BertGeneratorDataSet(train_sample_gen,
                                 text_processor=self.text_processor,
                                 segment=self.embedding.segment,
                                 seq_length=self.sequence_length,
                                 batch_size=batch_size)

        if fit_kwargs is None:
            fit_kwargs = {}

        if valid_sample_gen:
            valid_gen = BertGeneratorDataSet(valid_sample_gen,
                                     text_processor=self.text_processor,
                                     segment=self.embedding.segment,
                                     seq_length=self.sequence_length,
                                     batch_size=batch_size)
            fit_kwargs['validation_data'] = valid_gen.take()
            fit_kwargs['validation_steps'] = len(valid_gen)

        if "steps_per_epoch" not in fit_kwargs:
            fit_kwargs["steps_per_epoch"] = len(train_set)
        return self.tf_model.fit(train_set.take(),
                                 #steps_per_epoch=len(train_set),
                                 epochs=epochs,
                                 callbacks=callbacks,
                                 **fit_kwargs)



