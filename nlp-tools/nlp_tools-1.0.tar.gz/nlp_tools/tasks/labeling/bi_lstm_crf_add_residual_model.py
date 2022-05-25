from typing import Dict, Any

from tensorflow import keras
from nlp_tools.layers import L, KConditionalRandomField
from nlp_tools.tasks.labeling.bi_lstm_crf_model import BiLSTM_CRF_Model




class BiLstmCrfAddResidualModel(BiLSTM_CRF_Model):

    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'layer_blstm': {
                'units': 64,
                'return_sequences': True
            },

            'layer_dropout': {
                'rate': 0.5
            },
            'layer_time_distributed': {},
        }


    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size

        config = self.hyper_parameters
        embed_model = self.embedding.embed_model

        crf = KConditionalRandomField()



        layer_stack = [
            L.Dropout(**config['layer_dropout'], name='layer_dropout'),
            L.Dense(output_dim, **config['layer_time_distributed']),
            crf
        ]

        dirct_output = L.Dense(config['layer_blstm']['units'] * 2)(embed_model.output)
        lstm_output  = L.Bidirectional(L.LSTM(**config['layer_blstm']), name='layer_blstm')(embed_model.output)

        # lstm output和bert output直接相加，类似与residual效果
        tensor = L.concatenate([lstm_output ,dirct_output])

        tensor = L.Dropout(**config['layer_dropout'])(tensor)
        for layer in layer_stack:
            tensor = layer(tensor)

        self.tf_model = keras.Model(embed_model.inputs, tensor)
        self.crf_layer = crf










