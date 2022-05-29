from . import utils as utils
import copy

class Node(object):
    
    def __init__(self, name, config_dict, parent=None):
        object.__setattr__(self, "_xpipe_name", name)
        object.__setattr__(self, "_xpipe_config_dict", config_dict)
        object.__setattr__(self, "_xpipe_parent", parent)
        self._xpipe_construct(name, config_dict)

    def _xpipe_construct(self, name, config_dict):
        raise NotImplementedError("This function has to be implemented")

    def _xpipe_check_valid(self, name, config_dict):
        if isinstance(name, str):
            utils.valid_var_name(name)
        return True
    
    def __str__(self) -> str:
        return self.__repr__()