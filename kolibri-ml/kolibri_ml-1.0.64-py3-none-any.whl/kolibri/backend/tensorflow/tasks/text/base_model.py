import json
import os
from abc import abstractmethod
from typing import Dict, Any
import tensorflow as tf
from kolibri.indexers import LabelIndexer

from kolibri.data.text.generators import DataGenerator
from kolibri.backend.tensorflow.tasks.base_model import TaskBaseModel
from kolibri.backend.tensorflow.embeddings import DefaultEmbedding
from kolibri.backend.tensorflow.utils import load_data_object
from kolibri.indexers.sequence_indexer import SequenceIndexer
from kolibri.logger import get_logger

logger = get_logger(__name__)


class TextBaseModel(TaskBaseModel):

    def __init__(self, embedding=None, sequence_length=None, hyper_parameters=None, multi_label=False,
                 content_indexer=None, label_indexer=None):

        super().__init__(sequence_length, hyper_parameters)

        if embedding is None:
            embedding = DefaultEmbedding()  # type: ignore
        if content_indexer is None:
            content_indexer = SequenceIndexer()
        self.multi_label = multi_label
        if label_indexer is None:
            self.label_indexer = LabelIndexer(multi_label=multi_label)
        self.content_indexer = content_indexer
        self.embedding = embedding

    def to_dict(self):
        model_json_str = self.tf_model.to_json()
        base_dict = super(TextBaseModel, self).to_dict()
        base_dict.update({
            'embedding': self.embedding.to_dict(),  # type: ignore
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
            batch_size: int = 32,
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
                                  callbacks=callbacks,
                                  fit_kwargs=fit_kwargs)

    def build_model_generator(self, generators):
        raise NotImplementedError

    def fit_generator(self, train_sample_gen, valid_sample_gen=None,
                      *,
                      batch_size: int = 64,
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

        return super(TextBaseModel, self).fit(train_set, valid_gen, callbacks, fit_kwargs)

    @classmethod
    def load_model(cls, model_path):
        from kolibri.backend.tensorflow.layers.crf import ConditionalRandomField
        model_config_path = os.path.join(model_path, 'model_config.json')
        with open(model_config_path, 'r') as f:
            model_config = json.loads(f.read())
        model = load_data_object(model_config)

        model.embedding = load_data_object(model_config['embedding'])
        model.content_indexer = load_data_object(model_config['content_indexer'])
        model.label_indexer = load_data_object(model_config['label_indexer'])
        model.epoch = model_config['epoch']
        tf_model_str = json.dumps(model_config['tf_model'])
        model.tf_model = tf.keras.models.model_from_json(tf_model_str,
                                                         {'ConditionalRandomField': ConditionalRandomField})

        if isinstance(model.tf_model.layers[-1], ConditionalRandomField):
            model.layer_crf = model.tf_model.layers[-1]

        model.tf_model.load_weights(os.path.join(model_path, 'model_weights.h5'))
        model.embedding.embed_model.load_weights(os.path.join(model_path, 'embed_model_weights.h5'))
        return model

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

        super(TextBaseModel, self).save(model_path)
        self.embedding.embed_model.save_weights(os.path.join(model_path, 'embed_model_weights.h5'))
        logger.info('embedding file saved to {}'.format(os.path.abspath(model_path)))
        return model_path


if __name__ == "__main__":
    path = '/var/folders/x3/_dg9_drj42l_cc70tsqkpqrw0000gn/T/1590915853.4571211'
    m = TextBaseModel.load_model(path)
    m.tf_model.summary()
