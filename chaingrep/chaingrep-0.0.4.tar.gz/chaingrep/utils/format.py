from datetime import datetime


class DotDict(dict):
    # dot.notation access to dictionary attributes
    # pylint: disable=no-method-argument
    def __getattr__(*args):
        value = dict.get(*args)
        if isinstance(value, dict):
            return DotDict(value)
        if isinstance(value, list):
            return [DotDict(elem) for elem in value]

        return value

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def standardize_response(response):
    if isinstance(response, dict):
        response_keys = response.keys()
        # Time to datetime object
        if "time" in response_keys:
            unix_timestamp = response.get("time").get("unix_timestamp")
            datetime_object = datetime.fromtimestamp(unix_timestamp)
            datetime_object = {"datetime": datetime_object}
            response["time"] = {**response.get("time"), **datetime_object}

    elif isinstance(response, list):
        return [DotDict(standardize_response(elem)) for elem in response]

    return DotDict(response)
