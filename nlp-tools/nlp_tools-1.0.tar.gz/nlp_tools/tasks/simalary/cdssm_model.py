from typing import Dict,Any
from tensorflow import keras
from nlp_tools.layers import L
from nlp_tools.tasks.simalary.abc_model import ABCSimilaryModel
from tensorflow.keras.losses import cosine_similarity

class dssm_layer(keras.layers.Layer):
    def __init__(self,config,**kwargs):
        self.config = config
        self.layers = [
            L.Conv1D(**self.config['conv1']),
            L.Dropout(**self.config['dropout']),
            L.GlobalMaxPool1D(**self.config['global_pool']),
            L.Dense(**self.config['mlp_layer']),
            L.Dense(**self.config['out_layer']),
        ]
        super(dssm_layer, self).__init__(**kwargs)


    def call(self,x,mask=None):
        output = x
        for layer_ in self.layers:
            output = layer_(output)
        return output


class CDssmModel(ABCSimilaryModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "conv1":{
                'filters':300,
                'kernel_size': 3,
                'strides': 1,
                'padding': 'same',
                'activation':'relu',
                "kernel_initializer":"random_uniform",
                "bias_initializer":"zeros"
            },
            'dropout':{
                'rate':0.2
            },
            'global_pool':{

            },
            'mlp_layer':{
                "units":128,
                'activation':'relu'
            },
            'out_layer':{
                "units": 128,
                'activation': 'relu'
            }
    }

    def _create_base_network(self):
        def _wrapper(x):
            embedding_model = self.embedding.embed_model
            config = self.default_hyper_parameters()

            layers = [
                embedding_model,
                L.Conv1D(**config['conv1']),
                L.Dropout(**config['dropout']),
                L.GlobalMaxPool1D(**config['global_pool']),
                L.Dense(**config['mlp_layer']),
                L.Dense(**config['out_layer']),
            ]
            output  = x
            for layer_ in layers:
                output = layer_(output)
            return output
        return _wrapper





    def base_encode_block(self,config):
        layer =  L.Bidirectional(L.LSTM(**config['layer_bi_lstm']))
        return layer

    def _make_inputs(self,seq_length) -> list:
        input_left = keras.layers.Input(
            name='text_left',
            shape=(seq_length,)
        )
        input_right = keras.layers.Input(
            name='text_right',
            shape=(seq_length,)
        )
        return [input_left, input_right]

    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size
        config = self.hyper_parameters
        embedding_model = self.embedding.embed_model
        base_network = dssm_layer(config)


        # Left input and right input.
        input_left, input_right = self._make_inputs(self.sequence_length)
        input_left_embed ,input_right_embed = embedding_model(input_left),embedding_model(input_right)
        # Process left & right input.
        x = [base_network(input_left_embed),
             base_network(input_right_embed)]

        # Dot product with cosine similarity.
        x = L.Dot(axes=[1, 1], normalize=True)(x)

        output = L.Dense(output_dim, activation='softmax')(x)

        self.tf_model = keras.Model([input_left,input_right],output)


    def compile_model(self,
                      loss:Any = None,
                      optimizer: Any=None,
                      metrics:Any=None,
                      **kwargs:Any) -> None:
        if loss is None:
            loss = 'sparse_categorical_crossentropy'

        if optimizer is None:
            optimizer = 'adam'

        if metrics is None:
            metrics=["cosine_similarity"]

        self.tf_model.compile(loss=loss,
                              optimizer=optimizer,
                              metrics=metrics,
                              **kwargs)



