from nlp_tools.layers.non_masking_layer import NonMaskingLayer
from nlp_tools.layers.conditional_random_field import KConditionalRandomField
from nlp_tools.layers.kmax_pool_layer import KMaxPoolingLayer
from nlp_tools.layers.att_wgt_avg_layer import AttentionWeightedAverageLayer
from nlp_tools.layers.behdanau_attention import BahdanauAttention
from nlp_tools.loss.r_drop_loss import RDropLoss

from nlp_tools.loss import TextGenerateCrossEntropy
from typing import Dict, Any

from tensorflow import keras
L = keras.layers
L.BahdanauAttention = BahdanauAttention
L.KConditionalRandomField = KConditionalRandomField


L.TextGenerateCrossEntropy = TextGenerateCrossEntropy



from transformers import TFBertModel
def resigter_custom_layers(custom_objects: Dict[str, Any]) -> Dict[str, Any]:
    custom_objects['KConditionalRandomField'] = KConditionalRandomField
    custom_objects['BahdanauAttention'] = BahdanauAttention
    custom_objects['loss'] = KConditionalRandomField.loss

    custom_objects['TextGenerateCrossEntropy'] = TextGenerateCrossEntropy
    custom_objects['r_drop_loss'] = RDropLoss(loss_func=None)

    custom_objects['TFBertModel'] = TFBertModel


    return custom_objects