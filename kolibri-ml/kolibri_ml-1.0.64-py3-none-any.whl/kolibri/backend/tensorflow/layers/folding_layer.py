import tensorflow as tf
from tensorflow.python import keras

custom_objects = tf.keras.utils.get_custom_objects()

L = tf.keras.layers
initializers = keras.initializers
InputSpec = L.InputSpec


class FoldingLayer(L.Layer):

    def __init__(self, **kwargs):
        super(FoldingLayer, self).__init__(**kwargs)
        self.input_spec = InputSpec(ndim=3)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1], int(input_shape[2] / 2))

    def call(self, x):
        input_shape = x.get_shape().as_list()

        # split the tensor along dimension 2 into dimension_axis_size/2
        # which will give us 2 tensors
        splits = tf.split(
            x, num_or_size_splits=int(
                input_shape[2] / 2), axis=2)

        # reduce sums of the pair of rows we have split onto
        reduce_sums = [tf.reduce_sum(split, axis=2) for split in splits]

        # stack them up along the same axis we have reduced
        row_reduced = tf.stack(reduce_sums, axis=2)
        return row_reduced
