# Copyright (C) 2021- 2022 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pandas


class ParameterSet(dict):
    """
    A ParameterSet consist of a set of parameters, stored as a dictionary containing names of parameters and their values.
    The keys of the dictionary are strings representing the name of each parameter, and the values are python datatypes representing the corresponding value of a parameter (it may be a string, a float, an int, a bool, a list, a dict or a combination of these).
    Throughout the library a ParameterSet can be used interchangeably with a standard Python dictionary, since a ParameterSet is simply a dictionary. This class is mostly used for documentation purpose.

    Example
    -------

    {'param1': 1, 'param2': 1.5, 'param3': [1,2,4], 'param4': "option1", 'param5': {'a':1, 'b':2}}
    """

    @staticmethod
    def flatten(obj):
        output = {}
        flattened = True
        for key, val in obj.items():
            if isinstance(val, (tuple, list)):
                flattened = False
                new_dict = {
                    "{old_key}.{new_key}".format(old_key=key, new_key=i): v
                    for (i, v) in enumerate(val)
                }
                output.update(new_dict)
            elif isinstance(val, dict):
                flattened = False
                new_dict = {
                    "{old_key}.{new_key}".format(old_key=key, new_key=k): v
                    for (k, v) in val.items()
                }
                output.update(new_dict)
            else:
                output.update({key: val})

        if flattened:
            return output
        else:
            return ParameterSet.flatten(output)

    @staticmethod
    def to_dataframe(data):
        return pandas.DataFrame(
            [ParameterSet.flatten(parameterset) for parameterset in data]
        )
