from typing import Dict, Any

from tensorflow import keras
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import Accuracy

from nlp_tools.tasks.labeling.abc_model import ABCLabelingModel
from nlp_tools.layers.position_layer import GloablPointerLayer
from nlp_tools.loss.multilabel_loss import global_pointer_crossentropy
from nlp_tools.metrics.ner.global_pointer import global_pointer_f1_score

from nlp_tools.utils.ner_utils import output_ner_results



class GlobalPointModel(ABCLabelingModel):

    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'global_point_layer': {
                'head_size': 64,
                'RoPE': True
            }
        }

    def build_model_arc(self) -> None:
        label_size = self.label_processor.vocab_size

        config = self.hyper_parameters
        embed_model = self.embedding.embed_model
        tensor = embed_model.output
        tensor = keras.layers.Dropout(0.5)(tensor)
        output = GloablPointerLayer(label_size,**config['global_point_layer'])(tensor)
        self.tf_model = keras.Model(embed_model.inputs, output)
        self.tf_model.summary()


    def compile_model(self,
                      loss: Any = None,
                      optimizer: Any = None,
                      metrics: Any = None,
                      **kwargs: Any) -> None:
        if loss is None:
            loss = global_pointer_crossentropy
        if metrics is None:
            metrics = global_pointer_f1_score

        if optimizer is None:
            optimizer = Adam(learning_rate=2e-5)

        self.tf_model.compile(loss=loss,
                              optimizer=optimizer,
                              metrics=metrics,
                              **kwargs)


    def predict(self,
                x_data,
                batch_size: int = 32,
                truncating: bool = False,
                predict_kwargs=None,
                return_max_entity=False) :
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
        pred = self.tf_model.predict(tensor, batch_size=batch_size, verbose=1, **predict_kwargs)

        x_data_mapping = [self.text_processor.text_tokenizer.rematch(x, x_tokens) for x, x_tokens in
                          zip(x_data, x_data_tokenized)]
        res = self.label_processor.inverse_transform(pred,lengths=lengths,mapping_list =x_data_mapping)
        return res


    def predict_entities(self,
                         x_data,
                         batch_size: int = 32,
                         truncating: bool = False,
                         predict_kwargs: Dict = None) :
        predict_result = self.predict(x_data,batch_size,truncating,predict_kwargs)

        result = output_ner_results(x_data,predict_result)
        return result

    def predict_max_entities(self,
                         x_data,
                         batch_size: int = 32,
                         truncating: bool = False,
                         predict_kwargs: Dict = None) :
        predict_result = self.predict(x_data,batch_size,truncating,predict_kwargs,return_max_entity=True)

        result = output_ner_results(x_data,predict_result)
        return result






