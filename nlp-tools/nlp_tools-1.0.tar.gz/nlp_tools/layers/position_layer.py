from tensorflow.keras.layers import Layer,Dense
import tensorflow.keras.backend as K
import tensorflow as tf

from nlp_tools.utils.keras_utils import sequence_masking

class SinusoidalPositionEmbedding(Layer):
    """定义Sin-Cos位置Embedding
        """
    def __init__(self
                 ,output_dim,merge_mode='add',custom_position_ids = False,**kwargs):
        super(SinusoidalPositionEmbedding,self).__init__(**kwargs)
        self.output_dim = output_dim
        self.merge_mode = merge_mode
        self.custom_position_ids = custom_position_ids

    def call(self,inputs,**kwargs):
        """如果custom_position_ids，那么第二个输入为自定义的位置id
                """
        if self.custom_position_ids:
            seq_len = K.shape(inputs)[1]
            inputs,position_ids = inputs
            if 'float' not in K.dtype(position_ids):
                position_ids = K.cast(position_ids, K.floatx())
        else:
            input_shape = K.shape(inputs)
            batch_size, seq_len = input_shape[0], input_shape[1]
            position_ids = K.arange(0,seq_len,dtype=K.floatx())[None]

        indices = K.arange(0,self.output_dim // 2, dtype=K.floatx())
        indices = K.pow(10000.0, -2 * indices / self.output_dim)
        embeddings = tf.einsum('bn,d->bnd',position_ids,indices)
        embeddings = K.stack([K.sin(embeddings),K.cos(embeddings)],axis=-1)
        embeddings = K.reshape(embeddings,(-1,seq_len,self.output_dim))

        if self.merge_mode == 'add':
            return inputs + embeddings
        elif self.merge_mode == 'mul':
            return inputs * (embeddings + 1.0)
        elif self.merge_mode == 'zero':
            return embeddings
        else:
            if not self.custom_position_ids:
                embeddings = K.tile(embeddings,[batch_size,1,1])
            return K.concatenate([inputs,embeddings])

    def compute_output_shape(self, input_shape):
        if self.custom_position_ids:
            input_shape = input_shape[0]

        if self.merge_mode in ['add','mul','zero']:
            return input_shape[:2] + (self.output_dim,)
        else:
            return input_shape[:2] + (input_shape[2] + self.output_dim,)

    def get_config(self):
        config = {
            'output_dim': self.output_dim,
            'merge_mode': self.merge_mode,
            'custom_position_ids': self.custom_position_ids
        }
        base_config = super(SinusoidalPositionEmbedding, self).get_config()
        return  dict(list(base_config.items()) + list(config.items()))



class GloablPointerLayer(Layer):
    """全局指针模块
        将序列的每个(start, end)作为整体来进行判断
        """
    def __init__(self,heads, head_size,RoPE =True,**kwargs):
        super(GloablPointerLayer,self).__init__(**kwargs)
        self.heads = heads
        self.head_size = head_size
        self.RoPE = RoPE

    def build(self,input_shape):
        super(GloablPointerLayer,self).build(input_shape)
        self.dense = Dense(self.head_size * self.heads * 2)

    def compute_mask(self, inputs, mask=None):
        return None

    def call(self, inputs, mask=None):
        inputs = self.dense(inputs)
        inputs = tf.split(inputs,self.heads, axis=-1)
        inputs = K.stack(inputs,axis=-2)
        qw,kw = inputs[...,:self.head_size],inputs[...,self.head_size:]

        # RoPE编码
        if self.RoPE:
            pos = SinusoidalPositionEmbedding(self.head_size,'zero')(inputs)
            cos_pos = K.repeat_elements(pos[...,None,1::2],2,-1)
            sin_pos = K.repeat_elements(pos[...,None,::2],2,-1)
            qw2 = K.stack([-qw[...,1::2],qw[...,::2]],4)
            qw2 = K.reshape(qw2,K.shape(qw))
            qw = qw * cos_pos + qw2 * sin_pos

            kw2 = K.stack([-kw[...,1::2],kw[...,::2]],4)
            kw2 = K.reshape(kw2,K.shape(kw))
            kw  = kw * cos_pos + kw2 * sin_pos

        # 计算内积
        logits = tf.einsum('bmhd,bnhd->bhmn',qw,kw)

        # 排除padding
        logits = sequence_masking(logits,mask,'-inf',2)
        logits = sequence_masking(logits,mask,'-inf',3)

        # 排除下三角
        mask = tf.linalg.band_part(K.ones_like(logits),0,-1)
        logits = logits - ( 1 - mask) * 1e12

        # scale返回
        return logits / self.head_size ** 0.5

    def compute_output_shape(self, input_shape):
        return (input_shape[0] , self.heads,input_shape[1] ,input_shape[1])

    def get_config(self):
        config = {
            'heads': self.heads,
            'head_size': self.head_size,
            'RoPE':self.RoPE
        }
        base_config = super(GloablPointerLayer,self).get_config()
        return dict(list(base_config.items()) + list(config.items()))





if __name__ == '__main__':
    import numpy as np
    a = np.arange(0,10).reshape((2,1,1,5))
    print(np.repeat(a,2,-1).shape)
