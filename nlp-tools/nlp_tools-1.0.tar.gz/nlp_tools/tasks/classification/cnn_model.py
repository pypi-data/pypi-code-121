from typing import Dict,Any
from tensorflow import keras
from nlp_tools.layers import L
from nlp_tools.tasks.classification.abc_model import ABCClassificationModel
class ClassificationCnn(ABCClassificationModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'conv1d_layer': {
                'filters': 128,
                'kernel_size': 3,
                'activation': 'relu'
            },
            'max_pool_layer': {},
            'layer_output': {

            },
        }

    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size

        config = self.hyper_parameters
        embed_model = self.embedding.embed_model

        # build model structure in sequent way
        layer_stack = [
            L.Conv1D(**config['conv1d_layer']),
            L.GlobalMaxPool1D(**config['max_pool_layer']),
            L.Dense(output_dim, **config['layer_output']),
            self._activation_layer()
        ]

        tensor = embed_model.output
        for layer in layer_stack:
            tensor = layer(tensor)

        self.tf_model = keras.Model(embed_model.inputs, tensor)

