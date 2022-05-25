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



class ABCLabelingModel(ABCTaskModel, ABC):
    """
    Abstract Labeling Model
    """

    def __init__(self,
                 text_processor,
                 label_processor,
                 embedding: ABCEmbedding = None,
                 max_sequence_length: int = None,
                 hyper_parameters: Dict[str, Dict[str, Any]] = None,
                 train_sequece_length_as_max_sequence_length = False,
                 use_FGM = True,
                 use_rdrop=True):
        """

        Args:
            embedding: embedding object
            max_sequence_length: target sequence length
            hyper_parameters: hyper_parameters to overwrite
        """
        super(ABCLabelingModel, self).__init__()
        if hyper_parameters is None:
            hyper_parameters = self.default_hyper_parameters()

        self.tf_model: Optional[tf.keras.Model] = None
        self.embedding = embedding
        self.hyper_parameters = hyper_parameters


        self.text_processor = text_processor
        self.label_processor = label_processor

        self.max_sequence_length = max_sequence_length
        self.train_max_sequence_length = None
        self.train_sequece_length_as_max_sequence_length = train_sequece_length_as_max_sequence_length
        self.use_FGM = use_FGM
        self.use_rdrop = use_rdrop

        ## 如果分词器支持keep_tokens，且embedding也支持keep_tokens，则需要吧分词器的keep_tokens跟新到
        if self.text_processor:
            if hasattr(self.text_processor.text_tokenizer,"keep_tokens") and self.text_processor.text_tokenizer.keep_tokens != "" and hasattr(self.embedding,"keep_tokens"):
                self.embedding.keep_tokens = self.text_processor.text_tokenizer.keep_tokens


        self.embedding_max_position = None
        if self.embedding and  hasattr(self.embedding,"max_position"):
            self.embedding_max_position = self.embedding.max_position



    def build_model(self,
                    x_data: TextSamplesVar,
                    y_data: TextSamplesVar) -> None:
        """
        Build Model with x_data and y_data

        This function will setup a :class:`CorpusGenerator`,
         then call :meth:`ABCClassificationModel.build_model_gen` for preparing processor and model

        Args:
            x_data:
            y_data:

        Returns:

        """

        train_gen = CorpusGenerator(x_data, y_data)
        self.build_model_generator([train_gen])

    def build_model_generator(self,
                              generators: List[CorpusGenerator]) -> None:

        self.label_processor.build_vocab_generator(generators)
        if self.train_max_sequence_length is None and self.text_processor:
            self.train_max_sequence_length = self.text_processor.get_max_seq_length_from_corpus(generators,cover_rate=1.0)

        if self.train_sequece_length_as_max_sequence_length:
            self.max_sequence_length = self.train_sequece_length_as_max_sequence_length

        self.label_processor.update_length_info(embedding_max_position=self.embedding_max_position,max_sentence_length=self.max_sequence_length)

        if self.text_processor:
            self.text_processor.update_length_info(embedding_max_position=self.embedding_max_position,max_sentence_length=self.max_sequence_length)

        if self.embedding:
            self.embedding.build_embedding_model()


        if self.tf_model is None:
            self.build_model_arc()
            self.compile_model()

            # 替换model.train_step 方法即可,并且删除原有的 train_function方法
            if self.use_FGM:
                train_step = creat_FGM()
                self.tf_model.train_step = functools.partial(train_step, self.tf_model)
                self.tf_model.train_function = None


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



    def fit(self,
            train_data,
            validate_data=None,
            batch_size: int = 64,
            epochs: int = 5,
            callbacks: List[tf.keras.callbacks.Callback] = None,
            fit_kwargs: Dict = None,
            generator=None) -> 'tf.keras.callbacks.History':

        # 修正一下数据集，因为经过分词以后，实体的位置的index可能发现改变，需要修正一下
        train_data = self.ner_data_tokeninzed_and_change_label(train_data)
        if validate_data:
            validate_data = self.ner_data_tokeninzed_and_change_label(validate_data)

        if fit_kwargs is None:
            fit_kwargs = {}

        if generator == None:
            generator = BatchGenerator

        train_generator = generator(train_data,
                                   text_processor=self.text_processor,
                                   label_processor=self.label_processor,
                                   seq_length=self.train_max_sequence_length,
                                   batch_size=batch_size,
                                    use_rdrop=self.use_rdrop)
        if validate_data:
            valid_generator = generator(validate_data,
                                     text_processor=self.text_processor,
                                     label_processor=self.label_processor,
                                     seq_length=self.train_max_sequence_length,
                                     batch_size=batch_size,
                                     use_rdrop=self.use_rdrop)
            fit_kwargs['validation_data'] = valid_generator.forfit()
            fit_kwargs['validation_steps'] = len(valid_generator)
        else:
            valid_generator = None


        return self.fit_generator(train_sample_gen=train_generator,
                                  valid_sample_gen=valid_generator,
                                  epochs=epochs,
                                  callbacks=callbacks,
                                  fit_kwargs=fit_kwargs)

    def fit_generator(self,
                      train_sample_gen,
                      valid_sample_gen,
                      epochs: int = 5,
                      callbacks: List['tf.keras.callbacks.Callback'] = None,
                      fit_kwargs: Dict = None) -> 'tf.keras.callbacks.History':
        self.build_model_generator([g for g in [train_sample_gen, valid_sample_gen] if g])
        return self.tf_model.fit(train_sample_gen.forfit(),
                                 steps_per_epoch=len(train_sample_gen),
                                 epochs=epochs,
                                 callbacks=callbacks,
                                 **fit_kwargs)

    def predict(self,
                x_data: TextSamplesVar,
                batch_size: int = 32,
                truncating: bool = False,
                predict_kwargs: Dict = None) -> List[List[str]]:
        """
        Generates output predictions for the input samples.

        Computation is done in batches.

        Args:
            x_data: The input data, as a Numpy array (or list of Numpy arrays if the model has multiple inputs).
            batch_size: Integer. If unspecified, it will default to 32.
            truncating: remove values from sequences larger than `model.embedding.sequence_length`
            predict_kwargs: arguments passed to :meth:`tf.keras.Model.predict`

        Returns:
            array(s) of predictions.
        """
        if predict_kwargs is None:
            predict_kwargs = {}

        if truncating:
            seq_length = self.max_sequence_length
        else:
            seq_length = None

        if type(x_data[0]) == list:
            x_data = ["".join(x).replace("##","").replace('[CLS]',"").replace("[SEP]","") for x in x_data]
        x_data_tokenized = [self.text_processor.text_tokenizer.tokenize(x) for x in x_data]
        lengths = [len(x) for x in x_data_tokenized]

        tensor = self.text_processor.transform(x_data,seq_length=seq_length)
        logger.debug('predict seq_length: {}, input: {}'.format(seq_length, np.array(tensor).shape))
        pred = self.tf_model.predict(tensor, batch_size=batch_size, verbose=1, **predict_kwargs)
        pred = pred.argmax(-1)

        x_data_mapping = [self.text_processor.text_tokenizer.rematch(x, x_tokens) for x, x_tokens in
                          zip(x_data, x_data_tokenized)]

        res: List[List[str]] = self.label_processor.inverse_transform(pred,lengths=lengths,mapping_list=x_data_mapping)
        logger.debug('predict output: {}'.format(np.array(pred).shape))
        logger.debug('predict output argmax: {}'.format(pred))
        return res

    def predict_entities(self,
                         x_data,
                         batch_size: int = 32,
                         truncating: bool = False,
                         predict_kwargs: Dict = None):
        predict_result = self.predict(x_data, batch_size, truncating, predict_kwargs)

        result = output_ner_results(x_data, predict_result)
        return result

    def evaluate(self,data,
                 y_data,
                 batch_size: int = 32,
                 digits: int = 4,
                 truncating: bool = False) -> Dict:
        y_pred = self.predict(data,
                              batch_size=batch_size,
                              truncating=truncating)
        y_true = [seq[:len(y_pred[index])] for index, seq in enumerate(y_data)]

        new_y_pred = []
        for x in y_pred:
            new_y_pred.append([str(i) for i in x])
        new_y_true = []
        for x in y_true:
            new_y_true.append([str(i) for i in x])

        report = sequence_labeling_report(y_true, y_pred, digits=digits)
        return report

    def ner_data_tokeninzed_and_change_label(self,data):
        '''对训练数据分词处理，并跟新label的index'''
        if self.text_processor and hasattr(self.text_processor.text_tokenizer,'rematch'):
            tokenizer_data = []
            for (x, y) in data:
                item = []
                tokens = self.text_processor.text_tokenizer.tokenize(x)
                item.append(tokens)

                mapping = self.text_processor.text_tokenizer.rematch(x, tokens)
                start_mapping = {j[0]: i for i, j in enumerate(mapping) if j}
                end_mapping = {j[-1]: i for i, j in enumerate(mapping) if j}

                entities = []
                for start, end ,label in y:
                    if start in start_mapping and end in end_mapping:
                        start = start_mapping[start]
                        end = end_mapping[end]
                        entities.append((start,end,label))
                item.append(entities)

                tokenizer_data.append(item)
        else:
            tokenizer_data = data
        return tokenizer_data

    def smooth_labels(self, labels, factor=0.1):
        # smooth the labels
        labels *= (1 - factor)
        labels += (factor / labels.shape[1])

        return labels
