from typing import Dict,Any
from tensorflow import keras
from nlp_tools.layers import L
from nlp_tools.tasks.classification.abc_model import ABCClassificationModel
class BiLSTM_Model(ABCClassificationModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'layer_bi_lstm': {
                'units': 128,
                'return_sequences': False
            },
            'layer_output': {

            }
        }

    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size

        config = self.hyper_parameters
        embed_model = self.embedding.embed_model

        # build model structure in sequent way
        layer_stack = [
            L.Bidirectional(L.LSTM(**config['layer_bi_lstm'])),
            L.Dense(output_dim, **config['layer_output']),
            self._activation_layer()
        ]

        tensor = embed_model.output
        for layer in layer_stack:
            tensor = layer(tensor)

        self.tf_model: keras.Model = keras.Model(embed_model.inputs, tensor)
