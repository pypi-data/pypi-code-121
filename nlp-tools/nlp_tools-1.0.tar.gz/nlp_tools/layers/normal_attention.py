from tensorflow.keras.layers import Layer
from tensorflow.keras.initializers import TruncatedNormal
import tensorflow.keras.backend  as K
import tensorflow as tf



class NormalAttentionLayer(Layer):
    def __init__(self,attention_dim,**kwargs):
        self.init = TruncatedNormal()
        self.supports_masking = True
        self.attention_dim = attention_dim
        super(NormalAttentionLayer, self).__init__(**kwargs)


    def build(self, input_shape):
        #assert len(input_shape) == 3
        self.W = self.add_weight(name='W',
                                 shape=(input_shape[-1],self.attention_dim),
                                 dtype=K.floatx(),
                                 initializer=self.init,
                                 trainable=True
                                 )

        self.b = self.add_weight(name='b',
                                 shape=(self.attention_dim,),
                                 dtype=K.floatx(),
                                 initializer=self.init,
                                 trainable=True
                                 )

        self.u = self.add_weight(name='u',
                                 shape=(self.attention_dim,1),
                                 dtype=K.floatx(),
                                 initializer=self.init,
                                 trainable=True
                                 )
        super(NormalAttentionLayer, self).build(input_shape)

    def compute_mask(self, inputs, mask=None):
        if mask != None:
            mask = K.cast(mask, tf.int32)
            mask_sum = K.sum(mask, axis=-1)
            mask_new = K.cast(mask_sum > 0, tf.bool)  # sentence mask
            return mask_new
        else:
            return mask

    def call(self,x,mask=None):
        # size of x :[batch_size, sel_len, attention_dim]
        # size of u :[batch_size, attention_dim]
        uit = K.tanh(K.bias_add(K.dot(x,self.W),self.b))
        ait = K.dot(uit,self.u)
        ait = K.squeeze(ait,-1)

        ait = K.exp(ait)

        if mask is not None:
            ait *= K.cast(mask,K.floatx())

        ait /= K.cast(K.sum(ait,axis=-2,keepdims=True) + K.epsilon(), K.floatx())
        ait = K.expand_dims(ait)

        weighted_input = x * ait
        output = K.sum(weighted_input, axis=1)

        return output

    def compute_output_shape(self, input_shape):
        return (input_shape[0],input_shape[-1])

    def get_config(self):
        config = {
            'attention_dim':self.attention_dim
        }
        base_config = super(NormalAttentionLayer,self).get_config()
        return dict(list(base_config.items()) + list(config.items()))



