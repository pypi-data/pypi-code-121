
import tensorflow
from tensorflow.python.keras.layers import Layer

custom_objects = tensorflow.keras.utils.get_custom_objects()


class NonMaskingLayer(Layer):
    """
    fix convolutional 1D can't receive masked input, detail: https://github.com/keras-team/keras/issues/4978
    thanks for https://github.com/jacoxu
    """

    def __init__(self, **kwargs):
        self.supports_masking = True
        super(NonMaskingLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        pass

    def compute_mask(self, inputs, input_mask=None):
        # do not pass the mask to the next layers
        return None

    def call(self, x, mask=None):
        return x


custom_objects['NonMaskingLayer'] = NonMaskingLayer

if __name__ == "__main__":
    print("Hello world")
