import tensorflow as tf
from tensorflow.python import keras
from tensorflow.python.keras import backend as K

custom_objects = tf.keras.utils.get_custom_objects()

L = keras.layers


class Highway(L.Layer):
    """
      codes from github: https://github.com/batikim09/Keras_highways/blob/master/src/conv2d_highway.py
    """
    activation = None
    transform_gate_bias = None

    def __init__(self, activation='relu', transform_gate_bias=-2, **kwargs):
        self.activation = activation
        self.transform_gate_bias = transform_gate_bias
        super(Highway, self).__init__(**kwargs)

    def build(self, input_shape):
        # Create a trainable weight variable for this layer.
        dim = input_shape[-1]
        self.dense_1 = L.Layer.Dense(units=dim, bias_initializer=L.Layer.Constant(self.transform_gate_bias))
        self.dense_1.build(input_shape)
        self.dense_2 = L.Layer.Dense(units=dim)
        self.dense_2.build(input_shape)
        self.trainable_weights = self.dense_1.trainable_weights + self.dense_2.trainable_weights
        super(Highway, self).build(input_shape)  # Be sure to call this at the end

    def call(self, x):
        dim = K.int_shape(x)[-1]
        transform_gate = self.dense_1(x)
        transform_gate = L.Layer.Activation("sigmoid")(transform_gate)
        carry_gate = L.Layer.Lambda(lambda x: 1.0 - x, output_shape=(dim,))(transform_gate)
        transformed_data = self.dense_2(x)
        transformed_data = L.Layer.Activation(self.activation)(transformed_data)
        transformed_gated = L.Layer.Multiply()([transform_gate, transformed_data])
        identity_gated = L.Layer.Multiply()([carry_gate, x])
        value = L.Layer.Add()([transformed_gated, identity_gated])
        return value

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):
        config = super().get_config()
        config['activation'] = self.activation
        config['transform_gate_bias'] = self.transform_gate_bias
        return config
