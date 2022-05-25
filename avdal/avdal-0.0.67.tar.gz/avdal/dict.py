import json


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

        for k, v in self.items():
            if type(v) is dict:
                self[k] = AttrDict(v)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def from_file(filename):
        with open(filename, "r") as f:
            return AttrDict(json.load(f))
