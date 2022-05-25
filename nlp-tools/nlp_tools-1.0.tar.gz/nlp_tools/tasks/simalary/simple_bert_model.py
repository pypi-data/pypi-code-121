from typing import Dict,Any
from tensorflow import keras
from nlp_tools.layers import L
from nlp_tools.tasks.simalary.abc_model import ABCSimilaryModel

class SimpleBertModel(ABCSimilaryModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'dropout':{'rate':0.1},
            'layer_output':{
                'activation':'softmax'
            }
        }

    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size
        config = self.hyper_parameters


        layer_stack = [
            L.Dropout(**config['dropout']),
            L.Dense(output_dim, **config['layer_output']),
        ]

        tensor = self.embedding.embed_model.output

        for layer in layer_stack:
            tensor = layer(tensor)

        self.tf_model = keras.Model(self.embedding.embed_model.inputs,tensor)


