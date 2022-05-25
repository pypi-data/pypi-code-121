from keras.api.keras.layers import Layer,Dense,LayerNormalization,Concatenate

class PoolerInputLayer(Layer):
    def __init__(self, hidden_size,output_size):
        super(Layer, self).__init__()
        self.dense_0 = Dense(hidden_size,activation='tanh')
        self.LayerNorm = LayerNormalization()
        self.dense_1 = Dense( output_size)

    def __call__(self,inputs,mask=None, **kwargs):
        input = Concatenate()(inputs)
        x = self.dense_0(input)
        x = self.LayerNorm(x)
        x = self.dense_1(x)
        return x