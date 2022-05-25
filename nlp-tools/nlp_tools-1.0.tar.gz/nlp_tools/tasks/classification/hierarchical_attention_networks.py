from typing import Dict,Any
from tensorflow import keras
from tensorflow.keras import Sequential
from nlp_tools.layers import L
from nlp_tools.tasks.classification.abc_model import ABCClassificationModel
from tensorflow.keras.layers import *
from nlp_tools.layers.normal_attention import NormalAttentionLayer


class HierarchicalAttentionNetworks(ABCClassificationModel):
    @classmethod
    def default_hyper_parameters(cls) -> Dict[str, Dict[str, Any]]:
        return {
            'sentence_attention':{
                'attention_dim': 128
            },
            'layer_bi_lstm': {
                'units': 10,
                'return_sequences': True
            },
            'layer_output': {

            },

            'dco_attention':{
                'attention_dim': 128
            },
        }

    def build_model_arc(self) -> None:
        output_dim = self.label_processor.vocab_size

        config = self.hyper_parameters
        embed_model = self.embedding.embed_model


        # build model structure in sequent way

        # sentEncoder = Sequential()
        # sentEncoder.add(embed_model)
        # sentEncoder.add(L.Bidirectional(L.GRU(**config['layer_bi_lstm'])))
        # sentEncoder.add(NormalAttentionLayer(name="sentence_attention",**config['sentence_attention']))
        # # sentence_bilstm = L.Bidirectional(L.LSTM(**config['layer_bi_lstm']))(embed_model.output)
        # # sentence_attention = NormalAttentionLayer(name="sentence_attention",**config['sentence_attention'])(sentence_bilstm)
        # # sentEncoder = keras.Model(self.embedding.embed_model.inputs, sentence_attention)
        #
        # review_input = L.Input(shape=(20, None), dtype='int32')
        #
        # review_encoder = L.TimeDistributed(sentEncoder)(review_input)
        #
        #
        #
        # doc_bilstm = L.Bidirectional(L.GRU(name='doc_lstm',**config['layer_bi_lstm']),name='doc_bi_lstm')(review_encoder)
        # doc_attention = NormalAttentionLayer(name="doc_attention",**config['dco_attention'])(doc_bilstm)
        # dense_output = L.Dense(output_dim, **config['layer_output'])(doc_attention)
        # final_output = self._activation_layer()(dense_output)

        from tensorflow.keras import Model
        MAX_SENT_LENGTH = None
        from nlp_tools.layers.normal_attention import NormalAttentionLayer as AttLayer
        sentence_input = Input(shape=(MAX_SENT_LENGTH,), dtype='int32')
        embedded_sequences = embed_model(sentence_input)
        l_lstm = Bidirectional(GRU(100, return_sequences=True))(embedded_sequences)
        l_att = AttLayer(100)(l_lstm)
        sentEncoder = Model(sentence_input, l_att)

        review_input = Input(shape=(20, MAX_SENT_LENGTH), dtype='int32')
        review_encoder = TimeDistributed(sentEncoder)(review_input)

        # review_encoder = HierarchicalAttentionMaskingLayer(input_masking=review_input)(review_encoder)
        l_lstm_sent = Bidirectional(GRU(100, return_sequences=True))(review_encoder)
        l_att_sent = AttLayer(100)(l_lstm_sent)
        preds = Dense(output_dim, activation='softmax')(l_att_sent)
        #model = Model(review_input, preds)

        self.tf_model: keras.Model = keras.Model(review_input, preds)


    def compile_model(self,
                      loss: Any = None,
                      optimizer: Any = None,
                      metrics: Any = None,
                      **kwargs: Any) -> None:

        if loss is None:
            from nlp_tools.loss import multi_category_focal_loss2_fixed
            from tensorflow.keras.losses import CategoricalCrossentropy
            loss = 'categorical_crossentropy'
            #loss = multi_category_focal_loss2_fixed



        optimizer = 'adam'
        if metrics is None:
            metrics = ['accuracy']

        self.tf_model.compile(loss=loss,
                              optimizer=optimizer,
                              metrics=metrics,
                              **kwargs)
