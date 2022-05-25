from typing import Dict, Any

from tensorflow import keras

from nlp_tools.layers import L
from nlp_tools.tasks.labeling.abc_model import ABCLabelingModel


class BiLSTM_Model(ABCLabelingModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'layer_blstm': {
                'units': 128,
                'return_sequences': True
            },
            'layer_dropout': {
                'rate': 0.4
            },
            'layer_time_distributed': {},
        }

    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size

        config = self.hyper_parameters
        embed_model = self.embedding.embed_model

        layer_stack = [
            L.Bidirectional(L.LSTM(**config['layer_blstm']), name='layer_blstm'),
            L.Dropout(**config['layer_dropout'], name='layer_dropout'),
            L.Dense(output_dim, **config['layer_time_distributed']),
        ]
        tensor = embed_model.output
        for layer in layer_stack:
            tensor = layer(tensor)

        self.tf_model = keras.Model(embed_model.inputs, tensor)
