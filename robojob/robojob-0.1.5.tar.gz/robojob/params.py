from typing import Any, Dict


class ParameterCollection:
    def __init__(self):
        self.parameters = dict()

    def normalize_name(self, name):
        return name.lower().replace("_", "").replace("@", "").replace("$", "")

    def __setitem__(self, name: str, value: Any) -> None:
        self.parameters[self.normalize_name(name)] = value

    def __getitem__(self, name: str) -> Any:
        normalized_name = self.normalize_name(name)
        if normalized_name in self.parameters:
            return self.parameters[normalized_name]
        else:
            raise KeyError(name)

    def update(self, input_dict : Dict) -> None:
        for key, value in input_dict.items():
            self[key] = value
            
    def get(self, name: str, default_value: Any=None) -> Any:
        normalized_name = self.normalize_name(name)
        if normalized_name in self.parameters:
            return self.parameters[normalized_name]
        else:
            return default_value
