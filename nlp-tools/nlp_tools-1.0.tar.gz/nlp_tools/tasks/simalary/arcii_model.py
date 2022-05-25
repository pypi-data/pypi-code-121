from typing import Dict,Any
from tensorflow import keras
from nlp_tools.layers import L
from nlp_tools.tasks.simalary.abc_model import ABCSimilaryModel
import tensorflow as tf
from nlp_tools.layers.similary import MatchingLayer







class ArciiModel(ABCSimilaryModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "conv_1d_layer":{
                'filters':64,
                'kernel_size': 3,
                'padding':'same',
            },
            'matching_layer':{
                "normalize":True,
                'matching_type':'dot'
            },
            'num_blocks':3,
            'conv_block_1':{
                'filters': 32,
                'kernel_size': 3,
                'strides': 1,
                'padding': 'same',
                'activation': 'relu',
            },
            'pool_block_1':{
                "pool_size":2
            },
            'conv_block_2':{
                'filters': 64,
                'kernel_size': 3,
                'strides': 1,
                'padding': 'same',
                'activation': 'relu',
            },
            'pool_block_2': {
                "pool_size": 2
            },
            'conv_block_3':{
                'filters': 64,
                'kernel_size': 3,
                'strides': 1,
                'padding': 'same',
                'activation': 'relu',
            },
            'pool_block_3': {
                "pool_size": 2
            },
            'flatten_layer':{

            },
            "flatten_dropout":{
                'rate':0.5
            }
    }


    def make_inputs(self,seq_length) -> list:
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

        conv1d_layer = L.Conv1D(**config["conv_1d_layer"])
        matching_layer = MatchingLayer(**config['matching_layer'])
        flatten_layer = L.Flatten(**config["flatten_layer"])
        flatten_dropout = L.Dropout(**config['flatten_dropout'])




        # Left input and right input.
        input_left,input_right = self.make_inputs(self.sequence_length)
        input_left_embed ,input_right_embed = embedding_model(input_left),embedding_model(input_right)

        input_left_conv1d = conv1d_layer(input_left_embed)
        input_right_conv1d = conv1d_layer(input_right_embed)

        embed_cross = matching_layer([input_left_conv1d,input_right_conv1d])

        for i in range(1,int(config['num_blocks']) +1):
            conv2d_layer = L.Conv2D(**config['conv_block_'+ str(i)])
            pool2d_layer = L.MaxPooling2D(**config["pool_block_"+str(i)])
            embed_cross = conv2d_layer(embed_cross)
            embed_cross = pool2d_layer(embed_cross)

        embed_flat = flatten_layer(embed_cross)
        embed_flat = flatten_dropout(embed_flat)


        output = self.make_output_layer(output_dim)(embed_flat)


        self.tf_model = keras.Model([input_left,input_right],output)






