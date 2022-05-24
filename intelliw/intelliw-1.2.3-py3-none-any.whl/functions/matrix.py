import numpy as np

KEY_FACTOR = "factor"
KEY_DIMENSION = "dimension"
KEY_SHAPE = "shape"
KEY_AXIS = "axis"


def normalize(data, params):
    if type(data) is not np.ndarray:
        raise Exception("expected input data type numpy.ndarray in func normalize")
    value = params[KEY_FACTOR]
    return data / value


def reshape(data, params):
    if type(data) is not np.ndarray:
        data = np.array(data)
    if KEY_SHAPE not in params:
        raise Exception("expected param shape in matrix func reshape")
    shape = params[KEY_SHAPE]

    if len(data.shape) > len(shape):
        raise Exception("expected {} dimensions, but got array with shape {}".format(len(shape), data.shape))
    if len(data.shape) < len(shape):
        axis = []
        for index in range(len(shape)):
            if shape[index] == 1:
                axis.append(index)
        data = np.expand_dims(data, axis=axis)

    return np.reshape(data, shape)


def transpose(data, params):
    if type(data) is not np.ndarray:
        data = np.array(data)
    if KEY_SHAPE not in params:
        raise Exception("expected param shape in matrix func transpose")
    axes = params[KEY_SHAPE]
    if len(data.shape) != len(axes):
        raise Exception("expected {} dimensions, but got array with shape {}".format(len(axes), data.shape))
    return np.transpose(data, axes)


def argmax(data, params):
    axis = params[KEY_AXIS]
    return np.argmax(data, axis=axis)
