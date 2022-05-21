# Copyright (C) 2020-Present the hyssop authors and contributors.
#
# This module is part of hyssop and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

'''
File created: August 21st 2020

Modified By: hsky77
Last Updated: August 27th 2020 12:55:07 pm
'''


from typing import Dict, List, Any, Tuple

from .localization import BaseLocal
from .constants import LocalCode_Not_HierarchyElementMeta_Subclass, LocalCode_No_Parameters, LocalCode_Parameters_No_Key


class HierarchyElementMeta(type):
    def set_cls_parameters(cls, *cls_parameters) -> None:
        for cls_parameter in cls_parameters:
            if not hasattr(cls, '_cls_parameters'):
                cls._cls_parameters = {}

            if issubclass(type(cls), HierarchyElementMeta):
                cls._cls_parameters[cls_parameter.__name__] = cls_parameter
            else:
                raise TypeError(BaseLocal.get_message(
                    LocalCode_Not_HierarchyElementMeta_Subclass, cls))

    def get_cls_parameter(cls, key_routes: str, delimeter='.') -> type:
        routes = key_routes.split(delimeter)
        temp = cls
        for key in routes:
            if hasattr(temp, '_cls_parameters'):
                if key in temp._cls_parameters:
                    temp = temp._cls_parameters[key]
                else:
                    raise KeyError(BaseLocal.get_message(
                        LocalCode_Parameters_No_Key, temp, key))
            else:
                raise AttributeError(BaseLocal.get_message(
                    LocalCode_No_Parameters, temp))

        return temp
