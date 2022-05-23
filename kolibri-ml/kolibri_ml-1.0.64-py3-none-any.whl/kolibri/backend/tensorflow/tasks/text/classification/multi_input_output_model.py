import json
import os
from abc import abstractmethod
from typing import Dict, Any

import tensorflow as tf

from kolibri.data.text.corpus.generators import DataGenerator
from kolibri.backend.tensorflow.tasks.base_model import TaskBaseModel
from kolibri.backend.tensorflow.callbacks.connl_callBack import ConllCallback
from kolibri.backend.tensorflow.embeddings import DefaultEmbedding
from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.indexers.multi_content_indexer import MultiContentIndexer
from kolibri.indexers.multi_target_indexer import MultiTargetIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)


class MultiInputBaseModel(TaskBaseModel):
    """
    Model for multi-channel input. The default is a channel for words and channel for characters
    """

    def __init__(self, embeddings=None, sequence_length=None, hyper_parameters=None,
                 content_indexers=None, label_indexers=None):

        if sequence_length is None:
            sequence_length = []

        if not isinstance(sequence_length, list):
            raise Exception("sequence length need to ba a list of integrers")

        super().__init__(sequence_length, hyper_parameters, False, None)

        if embeddings is None:
            embeddings = []
            embeddings.append(DefaultEmbedding())  # type: ignore

        self.content_indexer = MultiContentIndexer()

        self.label_indexer = MultiTargetIndexer()

        if content_indexers is not None and isinstance(content_indexers, list):
            self.content_indexer.content_indexers = content_indexers

        if label_indexers is not None and isinstance(label_indexers, list):
            self.label_indexer.label_indexers = label_indexers

        self.embeddings = embeddings

    def to_dict(self):
        model_json_str = self.tf_model.to_json()
        base_dict = super(MultiInputBaseModel, self).to_dict()
        cont_dict = self.content_indexer.to_dict()
        base_dict.update({
            'embeddings': [embedding.to_dict() for embedding in self.embeddings],  # type: ignore
            'content_indexer': self.content_indexer.to_dict(),
            'label_indexer': self.label_indexer.to_dict(),
            'tf_model': json.loads(model_json_str)
        })
        return base_dict

    def update_hyper_parameters(self, parameters):
        if self.hyper_parameters is None:
            return

        for k, v in parameters.items():
            if k in self.hyper_parameters:
                self.hyper_parameters[k] = v

    @classmethod
    def get_default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        raise NotImplementedError

    def fit(self, x_train, y_train, x_validate=None, y_validate=None,
            *,
            batch_size: int = 64,
            epochs: int = 5,
            callbacks=None,
            fit_kwargs: Dict = None):
        """
        Trains the model for a given number of epochs with given texts set list.
        """

        train_gen = DataGenerator(x_train, y_train)
        if x_validate is not None:
            valid_gen = DataGenerator(x_validate, y_validate)
        else:
            valid_gen = None

        return self.fit_generator(train_sample_gen=train_gen,
                                  valid_sample_gen=valid_gen,
                                  batch_size=batch_size,
                                  epochs=epochs,
                                  callbacks=callbacks,
                                  fit_kwargs=fit_kwargs)

    def build_model_generator(self, generators):
        for content_indexer in self.content_indexer.content_indexers:
            if not content_indexer.token2idx:
                content_indexer.build_vocab_generator(generators)

        for label_indexer in self.label_indexer.label_indexers:
            label_indexer.build_vocab_generator(generators)

        for i, embedding in enumerate(self.embeddings):
            embedding.setup_text_processor(self.content_indexer.content_indexers[i])

        if self.tf_model is None:
            self.build_model_arc()
        self.compile_model()

    def fit_generator(self, train_sample_gen, valid_sample_gen=None,
                      *,
                      batch_size: int = 64,
                      epochs=10,
                      callbacks=None,
                      fit_kwargs):

        self.build_model_generator([g for g in [train_sample_gen, valid_sample_gen] if g])

        model_summary = []
        self.tf_model.summary(print_fn=lambda x: model_summary.append(x))
        logger.debug('\n'.join(model_summary))

        train_set = train_sample_gen
        train_set.set_batch_size(batch_size)
        train_set.label_indexer = self.label_indexer
        train_set.content_indexer = self.content_indexer

        if fit_kwargs is None:
            fit_kwargs = {}
        valid_gen = None
        if valid_sample_gen:
            valid_gen = valid_sample_gen
            valid_gen.set_batch_size(batch_size)
            valid_gen.label_indexer = self.label_indexer
            valid_gen.content_indexer = self.content_indexer

            fit_kwargs['validation_data'] = valid_gen
            fit_kwargs['validation_steps'] = len(valid_gen)

        conll_cb = ConllCallback(valid_gen, batch_size=batch_size)
        if callbacks is None:
            callbacks = [conll_cb]
        else:
            callbacks.append(conll_cb)

        return super(MultiInputBaseModel, self).fit(train_set, valid_gen, callbacks, fit_kwargs)

    @abstractmethod
    def build_model(self,
                    x_data: Any,
                    y_data: Any) -> None:
        raise NotImplementedError

    def save(self, model_path: str) -> str:
        """
        Save model
        Args:
            model_path:
        """

        super(MultiInputBaseModel, self).save(model_path)
        for i, embedding in enumerate(self.embeddings):
            embedding.embed_model.save_weights(os.path.join(model_path, 'embed_model_{}_weights.h5'.format(str(i))))

        logger.info('embedding file saved to {}'.format(os.path.abspath(model_path)))
        return model_path

    @classmethod
    def load_model(cls, model_path):
        from kolibri.backend.tensorflow.layers.crf import ConditionalRandomField
        model_config_path = os.path.join(model_path, 'model_config.json')
        with open(model_config_path, 'r') as f:
            model_config = json.loads(f.read())
        model = load_data_object(model_config)

        model.embeddings = [load_data_object(emb) for emb in model_config['embeddings']]
        model.content_indexer = load_data_object(model_config['content_indexer'])
        model.label_indexer = load_data_object(model_config['label_indexer'])
        model.epoch = model_config['epoch']
        tf_model_str = json.dumps(model_config['tf_model'])
        model.tf_model = tf.keras.models.model_from_json(tf_model_str,
                                                         {'ConditionalRandomField': ConditionalRandomField})

        if isinstance(model.tf_model.layers[-1], ConditionalRandomField):
            model.crf = model.tf_model.layers[-1]

        model.tf_model.load_weights(os.path.join(model_path, 'model_weights.h5'))
        for i, embedding in enumerate(model.embeddings):
            embedding.embed_model.load_weights(os.path.join(model_path, 'embed_model_{}_weights.h5'.format(str(i))))
        return model
