from typing import Dict,Any
from tensorflow import keras
from nlp_tools.layers import L
from nlp_tools.tasks.simalary.abc_model import ABCSimilaryModel
import tensorflow as tf
from nlp_tools.layers.kmax_pool_layer import KMaxPoolingLayer


class mvlstm_layer(keras.layers.Layer):
    def __init__(self,config,**kwargs):
        self.config = config
        self.layers = [
            L.Bidirectional(L.LSTM(**config['bilstm'])),

        ]
        super(mvlstm_layer, self).__init__(**kwargs)


    def call(self,x,mask=None):
        output = x
        for layer_ in self.layers:
            output = layer_(output)
        return output

class SimilaryMlpLayer(L.Layer):
    def __init__(self,config,**kwargs):
        self.config = config
        self.layers = [
            L.Dense(**config['mlp_layer']),
        ]
        super(SimilaryMlpLayer, self).__init__(**kwargs)


    def call(self,x,mask=None):
        output = x
        for layer_ in self.layers:
            output = layer_(output)
        return output

class MvLstmModel(ABCSimilaryModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "bilstm":{
                'units':300,
                'dropout': 0.3,
                'return_sequences':True,
            },
            'kmaxpooling':{
                "k":50,
            },
            'mlp_layer': {
                "units": 128,
                'activation': 'relu'
            },
            "mlp_dropout":{
                'rate':0.3
            }
    }


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

        bilstm_layer = L.Bidirectional(L.LSTM(**config["bilstm"]))
        normal_layer = L.Lambda(lambda x:tf.math.l2_normalize(x,axis=2))
        matching_layer = L.Dot(axes=[2,2],normalize=False)
        reshape_layer = L.Reshape((-1,))
        mlp_layer = SimilaryMlpLayer(config)
        mlp_dropout = L.Dropout(**config['mlp_dropout'])
        top_k_layer = L.Lambda(lambda x:tf.nn.top_k(x, **config["kmaxpooling"], sorted=True, name=None)[0])


        # Left input and right input.
        input_pairs = self._make_inputs(self.sequence_length)
        #input_left_embed ,input_right_embed = embedding_model(input_left),embedding_model(input_right)

        embed_input_pairs = []
        for input in input_pairs:
            input = embedding_model(input)
            input = bilstm_layer(input)
            input = normal_layer(input)
            embed_input_pairs.append(input)

        matching_result = matching_layer(embed_input_pairs)
        matching_result = reshape_layer(matching_result)
        matching_result = top_k_layer(matching_result)

        mlp_result = mlp_layer(matching_result)
        mlp_result = mlp_dropout(mlp_result)

        output = self.make_output_layer(output_dim)(mlp_result)


        self.tf_model = keras.Model(input_pairs,output)






