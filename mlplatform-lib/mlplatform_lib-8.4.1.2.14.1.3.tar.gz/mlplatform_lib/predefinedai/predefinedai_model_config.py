from dataclasses import dataclass
from typing import List, Union
from .predefinedai_arg import PredefinedAIBoolArg, PredefinedAIIntegerArg, PredefinedAIFloatArg, PredefinedAIMultipleOf2Arg, PredefinedAICategoricalArg

@dataclass
class ModelConfig:
    key: str
    display_name: str
    description: str
    hyperparameters: List[
        Union[PredefinedAIBoolArg, PredefinedAIIntegerArg, PredefinedAIFloatArg, PredefinedAIMultipleOf2Arg, PredefinedAICategoricalArg]]

    def __post_init__(self):
        self.hyperparameter_dict = {}
        for hp in self.__getattribute__('hyperparameters'):
            self.hyperparameter_dict[hp.get_key()] = hp.get_value()


@dataclass
class PredefinedAIModelConfig:
    display_name: str
    key: str
    description: str
    model_configs: List[ModelConfig]

    def __post_init__(self):
        self.hyperparameter_dict = {}
        for model_config in self.model_configs:
            self.hyperparameter_dict[model_config.key] = {}
            for hp in model_config.hyperparameters:
                self.hyperparameter_dict[model_config.key][hp.get_key()] = hp.get_value()

    def _get_model_hyperparameters_dict(self, model_name) -> dict:
        if model_name in self.hyperparameter_dict.keys():
            return self.hyperparameter_dict[model_name]
        raise ValueError(f'model "{model_name}" dose not exist in model_configs')
