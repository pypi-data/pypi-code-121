from abc import ABC
import numpy as np
from typing import List,Dict,Any,Union

from sklearn import metrics as sklearn_metrics
from tensorflow import keras

import nlp_tools
from nlp_tools.embeddings import ABCEmbedding,BareEmbedding
from nlp_tools.generators import CorpusGenerator
from nlp_tools.layers import L
from nlp_tools.logger import logger
from nlp_tools.processors import ClassificationProcessor
from nlp_tools.processors import SequenceProcessor
from nlp_tools.tasks.abs_task_model import  ABCTaskModel
from nlp_tools.types import TextSamplesVar,ClassificationLabelVar
from nlp_tools.generators import CorpusGenerator, BatchGenerator

from nlp_tools.utils.training_tips import creat_FGM
import functools

class ABCSimilaryModel(ABCTaskModel,ABC):
    '''
        Abstract Similary Model
    '''
    __task__ = 'encoder'

    def to_dict(self) -> Dict:
        info = super(ABCSimilaryModel,self).to_dict()
        info['config']['use_FGM'] = self.use_FGM
        info['config']['subtask'] = self.subtask
        return info

    def __init__(self,
                 embedding,
                 text_processor,
                 label_processor,
                 sequence_length: int = None,
                 hyper_parameters:Dict[str,Dict[str,Any]] = None,
                 subtask='Classification',
                 use_FGM=True,
                 train_sequece_length_as_max_sequence_length=None,
                 max_sequence_length=None):
        """
                        Args:
                            embedding: encoder object
                            sequence_length: target sequence length
                            hyper_parameters: hyper_parameters to overwrite
                            multi_label: is multi-label classification
                            text_processor: text processor
                            label_processor: label processor
                        """
        super(ABCSimilaryModel,self).__init__()


        if hyper_parameters is None:
            hyper_parameters = self.default_hyper_parameters()

        self.tf_model:keras.Model = None
        self.embedding = embedding
        self.hyper_parameters = hyper_parameters
        self.sequence_length = sequence_length

        self.text_processor = text_processor
        self.label_processor = label_processor

        self.subtask = subtask
        self.text_processor = text_processor
        self.label_processor = label_processor

        self.max_sequence_length = max_sequence_length
        self.train_max_sequence_length = None
        self.train_sequece_length_as_max_sequence_length = train_sequece_length_as_max_sequence_length
        self.use_FGM = use_FGM

        ## 如果分词器支持keep_tokens，且embedding也支持keep_tokens，则需要吧分词器的keep_tokens跟新到
        if self.text_processor:
            if hasattr(self.text_processor.text_tokenizer,
                       "keep_tokens") and self.text_processor.text_tokenizer.keep_tokens != "" and hasattr(
                    self.embedding, "keep_tokens"):
                self.embedding.keep_tokens = self.text_processor.text_tokenizer.keep_tokens

        self.embedding_max_position = None
        if self.embedding and hasattr(self.embedding, "max_position"):
            self.embedding_max_position = self.embedding.max_position

    def build_model(self,
                    x_train:TextSamplesVar,
                    y_train:ClassificationLabelVar) -> None:
        """
                       Build Model with x_data and y_data
                       This function will setup a :class:`CorpusGenerator`,
                        then call py:meth:`ABCClassificationModel.build_model_gen` for preparing processor and model
                       Args:
                           x_train:
                           y_train:
                       Returns:
                       """
        train_gen = CorpusGenerator(x_train,y_train)
        self.build_model_generator([train_gen])

    def build_model_generator(self,
                              generators: List[CorpusGenerator]) -> None:

        self.label_processor.build_vocab_generator(generators)
        if self.train_max_sequence_length is None:
            self.train_max_sequence_length = self.text_processor.get_max_seq_length_from_corpus(generators,
                                                                                                cover_rate=1.0)

        if self.train_sequece_length_as_max_sequence_length:
            self.max_sequence_length = self.train_sequece_length_as_max_sequence_length

        #self.label_processor.update_length_info(embedding_max_position=self.embedding_max_position,
        #                                       max_sentence_length=self.max_sequence_length)
        self.text_processor.update_length_info(embedding_max_position=self.embedding_max_position,
                                               max_sentence_length=self.max_sequence_length)

        self.embedding.build_embedding_model()

        if self.tf_model is None:
            self.build_model_arc()
            self.compile_model()

            # 替换model.train_step 方法即可,并且删除原有的 train_function方法

            if self.use_FGM:
                # if self.tf_model.train_function is not None:
                #    self.tf_model.make_train_function()
                # old_train_function = self.tf_model.train_function
                train_step = creat_FGM()
                self.tf_model.train_step = functools.partial(train_step, self.tf_model)
                self.tf_model.train_function = None

    def build_model_arc(self) -> None:
        raise NotImplementedError

    def compile_model(self,
                      loss:Any = None,
                      optimizer: Any=None,
                      metrics:Any=None,
                      **kwargs:Any) -> None:
        """
                        Configures the model for training.
                        call :meth:`tf.keras.Model.predict` to compile model with custom loss, optimizer and metrics
                        Examples:
                            >>> model = BiLSTM_Model()
                            # Build model with corpus
                            >>> model.build_model(train_x, train_y)
                            # Compile model with custom loss, optimizer and metrics
                            >>> model.compile(loss='categorical_crossentropy', optimizer='rsm', metrics = ['accuracy'])
                        Args:
                            loss: name of objective function, objective function or ``tf.keras.losses.Loss`` instance.
                            optimizer: name of optimizer or optimizer instance.
                            metrics (object): List of metrics to be evaluated by the model during training and testing.
                            **kwargs: additional params passed to :meth:`tf.keras.Model.predict``.
                        """
        if loss is None:
            loss = 'sparse_categorical_crossentropy'

        if optimizer is None:
            optimizer = 'adam'

        if metrics is None:
            metrics=['accuracy']

        self.tf_model.compile(loss=loss,
                              optimizer=optimizer,
                              metrics=metrics,
                              **kwargs)


    def fit(self,
            train_data,
            validate_data=None,
            batch_size: int=64,
            epochs:int = 5,
            callbacks:List['keras.callbacks.Callback'] =None,
            fit_kwargs:Dict=None,
            generator=None) ->'keras.callbacks.History':
        if generator == None:
            generator = BatchGenerator

        train_generator = generator(train_data,
                                    text_processor=self.text_processor,
                                    label_processor=self.label_processor,
                                    seq_length=self.train_max_sequence_length,
                                    batch_size=batch_size)
        if validate_data:
            valid_generator = generator(validate_data,
                                        text_processor=self.text_processor,
                                        label_processor=self.label_processor,
                                        seq_length=self.train_max_sequence_length,
                                        batch_size=batch_size)
        else:
            valid_generator = None

        return self.fit_generator(train_sample_gen= train_generator,
                                  valid_sample_gen = valid_generator,
                                  batch_size=batch_size,
                                  epochs = epochs,
                                  callbacks=callbacks,
                                  fit_kwargs=fit_kwargs)

    def fit_generator(self,
                      train_sample_gen,
                      valid_sample_gen,
                      *,
                      batch_size:int=64,
                      epochs:int=5,
                      callbacks:List['keras.callbacks.Callback'] = None,
                      fit_kwargs:Dict=None) -> 'keras.callbacks.History':
        """
                        Trains the model for a given number of epochs with given data generator.
                        Data generator must be the subclass of `CorpusGenerator`
                        Args:
                            train_sample_gen: train data generator.
                            valid_sample_gen: valid data generator.
                            batch_size: Number of samples per gradient update, default to 64.
                            epochs: Number of epochs to train the model.
                                An epoch is an iteration over the entire `x` and `y` data provided.
                            callbacks: List of `tf.keras.callbacks.Callback` instances.
                                List of callbacks to apply during training.
                                See `tf.keras.callbacks`.
                            fit_kwargs: fit_kwargs: additional arguments passed to :meth:`tf.keras.Model.fit`
                        Returns:
                            A :py:class:`tf.keras.callback.History`  object. Its `History.history` attribute is
                            a record of training loss values and metrics values
                            at successive epochs, as well as validation loss values
                            and validation metrics values (if applicable).
                        """
        if fit_kwargs == None:
            fit_kwargs = {}

        self.build_model_generator([g for g in [train_sample_gen, valid_sample_gen] if g])
        return self.tf_model.fit(train_sample_gen.forfit(),
                                 steps_per_epoch=len(train_sample_gen),
                                 validation_data=valid_sample_gen.forfit(random=False),
                                 validation_steps=len(valid_sample_gen),
                                 epochs=epochs,
                                 callbacks=callbacks,
                                 **fit_kwargs)

    def predict(self,
                x_data:TextSamplesVar,
                *,
                batch_size:int=32,
                truncating:bool=False,
                label_threshold:float = 0.5,
                predict_kwargs:Dict = None) -> ClassificationLabelVar:
        """
                        Generates output predictions for the input samples.
                        Computation is done in batches.
                        Args:
                            x_data: The input data, as a Numpy array (or list of Numpy arrays if the model has multiple inputs).
                            batch_size: Integer. If unspecified, it will default to 32.
                            truncating: remove values from sequences larger than `model.encoder.sequence_length`
                            multi_label_threshold:
                            predict_kwargs: arguments passed to ``predict()`` function of ``tf.keras.Model``
                        Returns:
                            array(s) of predictions.
                        """
        if predict_kwargs is None:
            predict_kwargs = {}

        with nlp_tools.utils.custom_object_scope():
            if truncating:
                seq_length = self.sequence_length
            else:
                seq_length = None
            tensor = self.text_processor.transform(x_data,
                                                   segment=self.embedding.segment,
                                                   seq_length=seq_length,
                                                   max_position=self.embedding.max_position)
            logger.debug(f'predict input shape {np.array(tensor).shape} x: \n{tensor}')
            pred = self.tf_model.predict(tensor, batch_size=batch_size, **predict_kwargs)
            logger.debug(f'predict output shape {pred.shape}')
            pred_argmax = pred.argmax(-1)
            lengths = [len(sen) for sen in x_data]
            res = self.label_processor.inverse_transform(pred_argmax, lengths=lengths)
            logger.debug(f'predict output argmax: {pred_argmax}')
        return res

    def evaluate(self,
                 x_data: TextSamplesVar,
                 y_data: ClassificationLabelVar,
                 *,
                 batch_size: int = 32,
                 digits: int = 4,
                 label_threshold: float = 0.5,
                 truncating: bool = False) -> Dict:
        y_pred = self.predict(x_data,
                              batch_size=batch_size,
                              truncating=truncating,
                              label_threshold=label_threshold)


        original_report = sklearn_metrics.classification_report(y_data,
                                                                y_pred,
                                                                output_dict=True,
                                                                digits=digits)

        print(sklearn_metrics.classification_report(y_data,
                                                    y_pred,
                                                    output_dict=False,
                                                    digits=digits))
        report = {
            'detail': original_report,
            **original_report['weighted avg']
        }
        return report


    def make_output_layer(self,num_classes=0) -> keras.layers.Layer:
        """:return: a correctly shaped keras dense layer for model output."""
        if self.subtask == "Classification":
            return keras.layers.Dense(num_classes, activation='softmax')
        elif self.subtask == "Ranking":
            return keras.layers.Dense(1, activation='linear')
        else:
            raise ValueError(f"{self.subtask} is not a valid task type."
                             f"Must be in `Ranking` and `Classification`.")




