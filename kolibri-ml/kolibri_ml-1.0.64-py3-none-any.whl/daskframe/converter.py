import numpy as np

from kdmt.infer import is_dict, is_dict_of_one_element, is_list_value, is_list_of_one_element


def tuple_to_dict(value):
    """
    Convert tuple to dict
    :param value: tuple to be converted
    :return:
    """

    return dict((x, y) for x, y in value)


def format_dict(_dict, tidy=True):
    """
    This function format a dict. If the main dict or a deep dict has only on element
     {"col_name":{0.5: 200}} we get 200
    :param _dict: dict to be formatted
    :param tidy:
    :return:
    """

    if tidy is True:
        levels = 2
        while (levels>=0):
            levels -= 1
            if is_list_of_one_element(_dict):
                _dict = _dict[0]
            elif is_dict_of_one_element(_dict):
                _dict = next(iter(_dict.values()))
            else:
                return _dict
                
    else:
        if is_list_of_one_element(_dict):
            return _dict[0]
        else:
            return _dict

def convert_numpy(value):
    if isinstance(value, (dict,)):
        for key in value:
            value[key] = convert_numpy(value[key])
        return value
    elif isinstance(value, (list, set, tuple)):
        return value.__class__(map(convert_numpy, value))
    elif isinstance(value, (np.generic,)):
        return np.asscalar(value)
    elif hasattr(value, "to_pydatetime"):
        return value.to_pydatetime()
    else:
        return value


def pandas_to_dask_dataframe(pdf, n_partitions=1):
    from dask import dataframe as dd
    return dd.from_pandas(pdf, npartitions=n_partitions)


