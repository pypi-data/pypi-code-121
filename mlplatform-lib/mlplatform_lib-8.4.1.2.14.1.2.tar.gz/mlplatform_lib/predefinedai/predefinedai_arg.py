from dataclasses import dataclass
from enum import Enum
import abc
from typing import List


class StrEnum(str, Enum):
    def __repr__(self):
        return str(self.name)

    def __str__(self):
        return str(self.name)


class PredefinedAIArgType(StrEnum):
    String = 'String'
    Integer = 'Integer'
    Float = 'Float'
    Categorical = 'Categorical'
    MultipleOf2 = 'MultipleOf2'
    Bool = 'Bool'


class PredefinedAIArg:
    @abc.abstractmethod
    def get_key(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_value(self):
        raise NotImplementedError


class ArgGroup(StrEnum):
    Arg = 'Arg'
    AlgorithmHyperparameter = 'AlgorithmHyperparameter'
    ModelHyperparameter = 'ModelHyperparameter'
    SamplingHyperparameter = 'SamplingHyperparameter'
    MetricHyperparameter = 'MetricHyperparameter'


@dataclass
class PredefinedAIStringArg(PredefinedAIArg):
    key: str
    display_name: str
    description: str
    value: str
    group: ArgGroup = ArgGroup.Arg
    type: PredefinedAIArgType = PredefinedAIArgType.String

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value


@dataclass
class PredefinedAIBoolArg(PredefinedAIArg):
    key: str
    display_name: str
    description: str
    value: bool
    group: ArgGroup = ArgGroup.Arg
    type: PredefinedAIArgType = PredefinedAIArgType.Bool

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value


@dataclass
class PredefinedAIIntegerArg(PredefinedAIArg):
    key: str
    display_name: str
    description: str
    min: int
    max: int
    value: int
    unit_step: int
    group: ArgGroup = ArgGroup.Arg
    type: PredefinedAIArgType = PredefinedAIArgType.Integer

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value


@dataclass
class PredefinedAIFloatArg(PredefinedAIArg):
    key: str
    display_name: str
    description: str
    min: float
    max: float
    value: float
    unit_step: float
    group: ArgGroup = ArgGroup.Arg
    type: PredefinedAIArgType = PredefinedAIArgType.Float

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value


@dataclass
class PredefinedAIMultipleOf2Arg(PredefinedAIArg):
    key: str
    display_name: str
    description: str
    min: int
    max: int
    value: int
    unit_step: int
    group: ArgGroup = ArgGroup.Arg
    type: PredefinedAIArgType = PredefinedAIArgType.MultipleOf2

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value


@dataclass
class PredefinedAICategoricalValue:
    key: str
    display_name: str
    description: str


@dataclass
class PredefinedAICategoricalArg(PredefinedAIArg):
    key: str
    display_name: str
    description: str
    values: List[PredefinedAICategoricalValue]
    value: PredefinedAICategoricalValue
    group: ArgGroup = ArgGroup.Arg
    type: PredefinedAIArgType = PredefinedAIArgType.Categorical

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value.key