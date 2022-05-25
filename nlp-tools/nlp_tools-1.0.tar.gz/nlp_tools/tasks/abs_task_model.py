import json
import os
import pathlib
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING, Union
import functools

import tensorflow as tf

import nlp_tools
from nlp_tools.embeddings import ABCEmbedding
from nlp_tools.logger import logger
from nlp_tools.utils import load_data_object
from nlp_tools.utils.training_tips import creat_FGM
from nlp_tools.generators import CorpusGenerator, BatchGenerator



class ABCTaskModel(ABC):

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
        super(ABCTaskModel, self).__init__()
        if hyper_parameters is None:
            hyper_parameters = self.default_hyper_parameters()

        self.tf_model = None
        self.embedding = embedding
        self.hyper_parameters = hyper_parameters


        self.text_processor = text_processor
        self.label_processor = label_processor

        self.max_sequence_length = max_sequence_length
        self.train_max_sequence_length = max_sequence_length
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

        self.model_node_names = {}






    def to_dict(self) -> Dict[str, Any]:
        #model_json_str = self.tf_model.to_json()

        save_json = {
            'tf_version': tf.__version__,
            'nlp_tools_version':nlp_tools.__version__,
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'config': {
                'hyper_parameters': self.hyper_parameters,
                'max_sequence_length': self.max_sequence_length,
                'use_FGM':self.use_FGM,
                'use_rdrop':self.use_rdrop
            },
            'label_processor': self.label_processor.to_dict(),
            #'tf_model': json.loads(model_json_str),
            'model_node_names':self.model_node_names
        }

        if self.embedding:
            save_json['embedding'] = self.embedding.to_dict()

        if self.text_processor:
            save_json['text_processor'] = self.text_processor.to_dict()

        return save_json

    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        raise NotImplementedError

    def save(self, model_path: str) -> str:
        pathlib.Path(model_path).mkdir(exist_ok=True, parents=True)
        model_path = os.path.abspath(model_path)

        # 将inputs和outputs 节点的name保存下来
        self.model_node_names = self.get_input_and_output_names_from_model()

        if(hasattr(self.text_processor.text_tokenizer,"change_model_path")):
            self.text_processor.text_tokenizer.change_model_path(os.path.join(model_path,'text_tokenizer'))

        with open(os.path.join(model_path,'model_config.json'), 'w',encoding='utf-8') as f:
            f.write(json.dumps(self.to_dict(),indent=2,ensure_ascii=False))
            f.close()

        tf.keras.models.save_model(self.tf_model,os.path.join(model_path,'model_weights'),include_optimizer=False)

        logger.info('model saved to {}'.format(os.path.abspath(model_path)))
        return model_path

    @classmethod
    def load_model(cls,model_path:str,**kwargs):
        model_config_path = os.path.join(model_path,'model_config.json')
        model_config = json.loads(open(model_config_path,'r',encoding='utf-8').read())


        if 'model_path' in model_config['text_processor']['text_tokenizer']['config']:
            model_config['text_processor']['text_tokenizer']['config']['model_path'] = os.path.join(model_path,'text_tokenizer')

        model_config['config']['text_processor'] = load_data_object(model_config['text_processor'])
        model_config['config']['label_processor'] = load_data_object(model_config['label_processor'])
        #model_config['config']['embedding'] = load_data_object(model_config['embedding'])
        model = load_data_object(model_config)
        model.tf_model = tf.keras.models.load_model(os.path.join(model_path,'model_weights'),custom_objects=nlp_tools.custom_objects)
        #model.tf_model = tf.keras.models.load_model(os.path.join(model_path, 'model_weights'))
        return model


    def build_model(self,
                    x_data: Any,
                    y_data: Any) -> None:
        train_gen = CorpusGenerator(x_data, y_data)
        self.build_model_generator([train_gen])



    def build_model_arc(self) -> None:
        raise NotImplementedError

    def compile_model(self) -> None:
        raise NotImplementedError

    def build_model_generator(self,generators) -> None:

        self.label_processor.build_vocab_generator(generators)
        # if self.train_max_sequence_length is None and self.text_processor:
        #     self.train_max_sequence_length = self.text_processor.get_max_seq_length_from_corpus(generators,cover_rate=1.0)
        #
        # if self.train_sequece_length_as_max_sequence_length:
        #     self.max_sequence_length = self.train_sequece_length_as_max_sequence_length

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


    def get_input_and_output_names_from_model(self):
        '''从模型中获取到输入和输出的node 的名称'''
        input_names = [node.name for node in self.tf_model.inputs]
        output_names = [node.name for node in self.tf_model.outputs]
        node_names_dict = {}
        node_names_dict['inputs'] = input_names
        node_names_dict['outputs'] = output_names
        return node_names_dict


    def fit(self,
            train_data,
            validate_data=None,
            batch_size: int = 64,
            epochs: int = 5,
            callbacks = None,
            fit_kwargs: Dict = None,
            generator=None) -> 'tf.keras.callbacks.History':

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
                      callbacks = None,
                      fit_kwargs: Dict = None) -> 'tf.keras.callbacks.History':
        self.build_model_generator([g for g in [train_sample_gen, valid_sample_gen] if g])
        return self.tf_model.fit(train_sample_gen.forfit(),
                                 steps_per_epoch=len(train_sample_gen),
                                 epochs=epochs,
                                 callbacks=callbacks,
                                 **fit_kwargs)