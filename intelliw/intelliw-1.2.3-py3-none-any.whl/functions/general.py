import base64

KEY_FIELD = "field"
KEY_BS64DECODE = "bs64decode"


def get_value(data, params):
    # get bs64 string
    if KEY_FIELD not in params:
        raise Exception("expected param field in general func get_value")
    field = params[KEY_FIELD]
    value_list = data[field]

    # turn bs64 string into numpy array
    if KEY_BS64DECODE in params and params[KEY_BS64DECODE]:
        # bs64_str = unquote(bs64_str)
        bs64_str = base64.b64decode("".join(value_list))
        return bs64_str
    else:
        return value_list


def convert_data(data, params):
    print("do convert_data")
    return data
