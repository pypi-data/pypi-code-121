import json
from typing import Dict, List, Any
import numpy as np
import tensorflow as tf
import nlp_tools


L = tf.keras.layers


class ABCEmbedding:
    def to_dict(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {
            'segment': self.segment,
            'embedding_size': self.embedding_size,
            'max_position': self.max_position,
            'bert_application':self.bert_application,
            **self.kwargs
        }
        return {
            '__class_name__': self.__class__.__name__,
            '__module__': self.__class__.__module__,
            'config': config,
            #'embed_model': json.loads(self.embed_model.to_json())
        }

    def __init__(self,
                 segment: bool = False,
                 embedding_size: int = 100,
                 max_position: int = None,
                 bert_application='encoder',
                 **kwargs: Any):

        self.embed_model: tf.keras.Model = None

        self.segment: bool = segment  # type: ignore
        self.kwargs = kwargs

        self.embedding_size: int = embedding_size  # type: ignore
        self.max_position: int = max_position  # type: ignore
        self.bert_application = bert_application

    def _override_load_model(self,config:Dict) -> None:
        pass
        # embed_model_json_str = json.dumps(config['embed_model'])
        # self.embed_model = tf.keras.models.model_from_json(embed_model_json_str,
        #                                                    custom_objects=nlp_tools.custom_objects)


    def build_embedding_model(self,
                              *,
                              vocab_size: int = None,
                              force: bool = False,
                              bert_application=None,
                              **kwargs: Dict) -> None:
        raise NotImplementedError

    def embed(self,tensor_x: List[List[List[int]]],) -> np.ndarray:
        """
        batch embed sentences

        Args:
            sentences: Sentence list to embed
            debug: show debug info
        Returns:
            vectorized sentence list
        """

        embed_results = self.embed_model.predict(tensor_x)
        return embed_results

