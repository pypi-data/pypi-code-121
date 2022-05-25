from typing import Dict,Any

from tensorflow.keras.layers import Flatten
from tensorflow.keras import layers
from tensorflow import keras
from tensorflow.keras import backend as K

from nlp_tools.layers import L
from nlp_tools.tasks.classification.abc_model import ABCClassificationModel
import tensorflow as tf
class ClassificationEntityLevel(ABCClassificationModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {}


    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size

        config = self.hyper_parameters
        embed_model = self.embedding.embed_model


        entity_positon_inputs = L.Input(shape=(None,), dtype='int32')



        tensor = embed_model.output
        tensor = tf.gather(tensor, entity_positon_inputs, batch_dims=K.ndim(entity_positon_inputs) - 1)
        tensor = layers.Dropout(rate=0.3)(tensor)

        output_net = 'lstm'
        if output_net == "lstm":
            tensor = layers.LSTM(units=128)(tensor)#layers.Bidirectional(layers.LSTM(units=128))(tensor)
        else:
            #tensor = layers.GlobalAveragePooling1D()(tensor)
            tensor = layers.GlobalMaxPool1D()(tensor)


        #import tensorflow.keras.backend as K
        tensor = layers.Dropout(rate=0.3)(tensor)
        tensor = layers.Dense(128, activation=tf.nn.relu ,name="FC/Dense")(tensor)
        tensor = L.Dense(output_dim, **config['layer_output'],name="FC/Dense_classify")(tensor)
        output = self._activation_layer()(tensor)
        self.tf_model = keras.Model(embed_model.inputs + [entity_positon_inputs], output)


