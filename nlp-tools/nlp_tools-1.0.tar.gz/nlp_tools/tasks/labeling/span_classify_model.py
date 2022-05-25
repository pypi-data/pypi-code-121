from typing import Dict, Any

from tensorflow import keras
from nlp_tools.layers import L
from nlp_tools.tasks.labeling.abc_model import ABCLabelingModel
from nlp_tools.layers.pool_layer import PoolerInputLayer
from nlp_tools.layers.non_masking_layer import MaskingSaverLayer
import tensorflow as tf




class SpanClassifyModel(ABCLabelingModel):

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
        self.mask_save_layer = MaskingSaverLayer()



        layers_starts_label_fc = L.Dense(output_dim)
        layers_ends_label_fc = PoolerInputLayer(128,output_dim)


        layer_stack = [
            L.Bidirectional(L.LSTM(**config['layer_blstm']), name='layer_blstm'),
            L.Dropout(**config['layer_dropout'], name='layer_dropout'),
        ]

        tensor = embed_model.output
        for layer in layer_stack:
            tensor = layer(tensor)

        tensor = self.mask_save_layer(tensor)

        starts_logits =  layers_starts_label_fc(tensor)
        ends_logits = layers_ends_label_fc([tensor,starts_logits])

        output_starts = tf.nn.softmax(starts_logits)
        output_ends = tf.nn.softmax(ends_logits)





        self.tf_model = keras.Model(embed_model.inputs, [output_starts,output_ends])


    def compile_model(self,
                      loss: Any = None,
                      optimizer: Any = None,
                      metrics: Any = None,
                      **kwargs: Any) -> None:

        if loss is None:
            self.mask_save_layer.set_loss_func(tf.keras.losses.sparse_categorical_crossentropy)
            loss = self.mask_save_layer.loss
        if metrics is None:
            metrics = 'accuracy'
        super(SpanClassifyModel, self).compile_model(loss=loss,
                                                    optimizer=optimizer,
                                                    metrics=metrics,
                                                    **kwargs)


    def predict(self,
                x_data,
                batch_size: int = 32,
                truncating: bool = False,
                predict_kwargs: Dict = None) :

        if predict_kwargs is None:
            predict_kwargs = {}

        if truncating:
            seq_length = self.max_sequence_length
        else:
            seq_length = None

        if type(x_data[0]) == list:
            x_data = ["".join(x).replace("##","").replace('[CLS]',"").replace("[SEP]","") for x in x_data]
        x_data_tokenized = [self.text_processor.text_tokenizer.tokenize(x) for x in x_data]
        lengths = [len(x) for x in x_data_tokenized]

        tensor = self.text_processor.transform(x_data,seq_length=seq_length)
        (starts_labels,ends_labels) = self.tf_model.predict(tensor, batch_size=batch_size, verbose=1, **predict_kwargs)
        #pred= self.tf_model.predict(tensor, batch_size=batch_size, verbose=1, **predict_kwargs)
        starts_labels = starts_labels.argmax(-1)
        ends_labels = ends_labels.argmax(-1)

        x_data_mapping = [self.text_processor.text_tokenizer.rematch(x, x_tokens) for x, x_tokens in
                          zip(x_data, x_data_tokenized)]

        res = self.label_processor.inverse_transform((starts_labels.tolist(),ends_labels.tolist()),lengths=lengths,mapping_list=x_data_mapping)
        return res

