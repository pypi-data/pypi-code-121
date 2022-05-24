from copy import deepcopy

class EnvVars:
    def __init__(self, dict_func):
        self._dict_func = dict_func
        self._gen = None
        self._env_dict = lambda: None
        self._reload()
    
    def __repr__(self):
        return str(self._env_dict())
        
    def __call__(self, *args, **kwargs):
        return self._env_dict()
    
    def _get_generator(self):
        d = deepcopy(self._dict_func())
        while True:
            yield d

    def _reload(self):  # for easy unit testing only
        gen = self._get_generator()
        self._env_dict = lambda: next(gen)
