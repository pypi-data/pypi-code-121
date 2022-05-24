import numpy as np

KEY_AXIS = "axis"
KEY_CHAR_SET = "char_set"


def argmax(data, params):
    if type(data) is not np.ndarray:
        data = np.array(data)
    if KEY_AXIS not in params:
        raise Exception("expected param axis in post func argmax")
    axis = params[KEY_AXIS]
    return np.argmax(data, axis=axis).reshape(data.shape[1])


def post_process(data, params):
    if KEY_CHAR_SET not in params:
        raise Exception("expected param char_set in post func post_process")
    char_set = params[KEY_CHAR_SET]
    res = {'data': ""}
    for index in data:
        res['data'] += char_set[index]
    res['status'] = 1
    return res
