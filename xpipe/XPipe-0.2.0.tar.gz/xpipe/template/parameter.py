class Parameters():

    def __init__(self, obj, dict_param):
        self.dict_param = dict_param
        self.obj = obj

        needed_keys = ["type", "params"]
        for key in needed_keys:
            if key not in dict_param:
                raise IndexError(f"No {key} provided for '{self.obj}'")

        for k, v in self.dict_param:
            setattr(self, k, v)

    def match_with(self, dict):
        raise NotImplementedError()

    def __call__(self):
        pass
        