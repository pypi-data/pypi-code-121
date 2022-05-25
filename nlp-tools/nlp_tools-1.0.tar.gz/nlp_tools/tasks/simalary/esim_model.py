from typing import Dict,Any
from tensorflow import keras
from nlp_tools.layers import L
from nlp_tools.tasks.simalary.abc_model import ABCSimilaryModel
from nlp_tools.layers.similary import LocalInferenceLayer




class EsimModel(ABCSimilaryModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "first_bilstm":{
                'units':128,
                'return_sequences':True,
                'dropout':0.3
            },
            'composition_left':{
                'units':128,
                'return_sequences':True,
                'dropout':0.3
            },
            'composition_right': {
                'units': 128,
                'return_sequences': True,
                'dropout': 0.3
            },
            'mixed_dropout':{
                'rate':0.3
            },
            'mlp_layer': {
                "units": 128,
                'activation': 'relu'
            },
            "mlp_dropout": {
                'rate': 0.3
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

        first_bilstm_layer = L.Bidirectional(L.LSTM(**config["first_bilstm"]))
        composition_bilstm_left_layer = L.Bidirectional(L.LSTM(**config["composition_left"]))
        composition_bilstm_right_layer = L.Bidirectional(L.LSTM(**config["composition_right"]))
        mix_dropout_layer = L.Dropout(**config["mixed_dropout"])
        mlp_layer = L.Dense(**config['mlp_layer'])
        mlp_dropout = L.Dropout(**config['mlp_dropout'])


        # Left input and right input.
        input_left, input_right = self._make_inputs(self.sequence_length)
        input_left_embed ,input_right_embed = embedding_model(input_left),embedding_model(input_right)

        encoded_left = first_bilstm_layer(input_left_embed)
        encoded_right = first_bilstm_layer(input_right_embed)

        # ---------- Local inference layer ---------- #
        local_left,local_right = LocalInferenceLayer()([encoded_left,encoded_right])

        # ---------- Inference composition layer ---------- #
        composition_left = composition_bilstm_left_layer(local_left)
        composition_right = composition_bilstm_right_layer(local_right)

        avg_pool_left = L.GlobalAveragePooling1D()(composition_left)
        max_pool_left = L.GlobalMaxPooling1D()(composition_left)

        avg_pool_right = L.GlobalAveragePooling1D()(composition_right)
        max_pool_right = L.GlobalMaxPooling1D()(composition_right)

        mixed = L.concatenate([avg_pool_left,max_pool_left,avg_pool_right,max_pool_right])
        mixed = mix_dropout_layer(mixed)

        # ---------- Classification layer ---------- #
        mlp_result = mlp_layer(mixed)
        mlp_result = mlp_dropout(mlp_result)

        output = self.make_output_layer()(mlp_result)

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



