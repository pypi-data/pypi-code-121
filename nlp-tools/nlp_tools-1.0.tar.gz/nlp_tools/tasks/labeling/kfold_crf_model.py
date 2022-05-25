from typing import Dict, Any

from tensorflow import keras
from tensorflow.keras import backend as K
from nlp_tools.layers import L, KConditionalRandomField
from nlp_tools.tasks.labeling.abc_model import ABCLabelingModel
from tensorflow.keras.preprocessing.sequence import  pad_sequences




class KfoldCrfModel(ABCLabelingModel):

    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {}


    def build_model_arc(self) -> None:
        label_size = self.label_processor.vocab_size

        crf = KConditionalRandomField()
        input = L.Input(shape=(None,label_size),dtype=K.floatx())
        input_masking = L.Input(shape=(None,))



        tensor = crf(input,input_masking)

        self.tf_model = keras.Model([input,input_masking], tensor)
        self.crf_layer = crf

    def compile_model(self,
                      loss: Any = None,
                      optimizer: Any = None,
                      metrics: Any = None,
                      **kwargs: Any) -> None:

        if loss is None:
            loss = self.crf_layer.loss
        if metrics is None:
            metrics = [self.crf_layer.accuracy]
        super(KfoldCrfModel, self).compile_model(loss=loss,
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

        sentences = []
        y_folds = []
        for item in x_data:
            sentences.append(item[0])
            y_folds.append(item[1])



        x_data_tokenized = [list(x) for x in sentences]
        lengths = [len(x) for x in x_data_tokenized]

        max_sequence_len = max(lengths)
        masking = []
        for seq in sentences:
            seq_masking = [1] * len(seq)
            masking.append(seq_masking)
        masking = pad_sequences(masking, max_sequence_len, padding='post', truncating='post')

        y_folds = self.label_processor.transform_kfold(y_folds, seq_length=max_sequence_len)



        pred = self.tf_model.predict((y_folds,masking), batch_size=batch_size, **predict_kwargs)
        pred = pred.argmax(-1)

        res = self.label_processor.inverse_transform(pred,lengths=lengths,mapping_list =None)
        return res


    def predict_entities(self,
                         x_data,
                         batch_size: int = 32,
                         truncating: bool = False,
                         predict_kwargs: Dict = None) :
        predict_result = self.predict(x_data,batch_size,truncating,predict_kwargs)

        return predict_result

