from dataclasses import dataclass
from typing import List, Union
from .predefinedai_arg import PredefinedAIStringArg, PredefinedAIBoolArg, PredefinedAIIntegerArg, PredefinedAIFloatArg, PredefinedAIMultipleOf2Arg, PredefinedAICategoricalArg


@dataclass
class StageConfig:
    args: List[
        Union[
            PredefinedAIStringArg, PredefinedAIBoolArg, PredefinedAIIntegerArg, PredefinedAIFloatArg, PredefinedAIMultipleOf2Arg, PredefinedAICategoricalArg]]
    envs: List[
        Union[
            PredefinedAIStringArg, PredefinedAIBoolArg, PredefinedAIIntegerArg, PredefinedAIFloatArg, PredefinedAIMultipleOf2Arg, PredefinedAICategoricalArg]]


@dataclass
class PredefinedAIStageConfig:
    train: StageConfig
    retrain: StageConfig
    inference: StageConfig
    serving: StageConfig

    def __post_init__(self):
        self.args_dict = {}
        for stage in ['train', 'retrain', 'inference', 'serving']:
            self.args_dict[stage] = {}
            for arg in self.__getattribute__(stage).__getattribute__('args'):
                self.args_dict[stage][arg.get_key()] = arg.get_value()

    def _get_args_dict(self, stage) -> dict:
        if stage in ['train', 'retrain', 'inference', 'serving']:
            return self.args_dict[stage]
        raise ValueError(f'stage "{stage}" dose not exist')
