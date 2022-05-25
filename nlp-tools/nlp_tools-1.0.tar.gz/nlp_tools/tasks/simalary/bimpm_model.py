from typing import Dict,Any
from tensorflow import keras
from nlp_tools.layers import L
from nlp_tools.tasks.simalary.abc_model import ABCSimilaryModel
from nlp_tools.layers.similary import MultiPerspective




class BimpmModel(ABCSimilaryModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "first_bilstm":{
                'units':128,
                'return_sequences':True,
                'dropout':0.3
            },
            'agg_left':{
                'units':128,
                'return_sequences':True,
                'dropout':0.3
            },
            'agg_right': {
                'units': 128,
                'return_sequences': True,
                'dropout': 0.3
            },
            'mp_dim':64,
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
        agg_bilstm_left_layer = L.Bidirectional(L.LSTM(**config["agg_left"]))
        agg_bilstm_right_layer = L.Bidirectional(L.LSTM(**config["agg_right"]))
        matching_layer = MultiPerspective(config['mp_dim'])

        mix_dropout_layer = L.Dropout(**config["mixed_dropout"])
        mlp_layer = L.Dense(**config['mlp_layer'])
        mlp_dropout = L.Dropout(**config['mlp_dropout'])


        # Left input and right input.
        input_left, input_right = self._make_inputs(self.sequence_length)
        input_left_embed ,input_right_embed = embedding_model(input_left),embedding_model(input_right)

        rep_left = first_bilstm_layer(input_left_embed)
        rep_right = first_bilstm_layer(input_right_embed)

        # ---------- Matching layer ---------- #
        matching_left = matching_layer([rep_left,rep_right])
        matching_right = matching_layer([rep_right,rep_left])

        # ---------- Aggregation Layer ---------- #
        agg_left = agg_bilstm_left_layer(matching_left)
        agg_right = agg_bilstm_right_layer(matching_right)

        aggregation = keras.layers.concatenate([agg_left, agg_right])
        aggregation = mix_dropout_layer(aggregation)

        # ---------- Classification layer ---------- #
        mlp_result = mlp_layer(aggregation)
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



