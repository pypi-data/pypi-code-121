from abc import ABC
from typing import Union


class Variable(ABC):
    COUNTER = 0

    def __init__(self, name: str = None):
        Variable.COUNTER += 1
        if name is None:
            name = f"var_{self.COUNTER}"
        self.name = name


class DiscreteVariable(Variable):

    def __init__(self, items: Union[list, tuple], name: str = None):
        self.items = items
        super().__init__(name)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        if len(self) < 5:
            items = self.items
        else:
            items = self.items[:3] + ["..."]
        return f"{self.name} = {len(self)}; {items}"

    def __getattr__(self, index_: Union[int, slice]):
        return self.items[index_]

    def __iter__(self):
        return self.items


class ContinuousVariable(Variable):

    def __init__(self, min_: Union[int, float], max_: Union[int, float], type_: type = float, name: str = None):
        self.min_ = min_
        self.max_ = max_
        self.type_ = type_
        super().__init__(name)

    def __repr__(self):
        return f"{self.name} = [{self.min_}, {self.max_}]"
