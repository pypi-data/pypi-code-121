from mlplatform_lib.predefinedai.predefinedai_data_config import PredefinedAIDataConfig, DataConfig, DataConfigurationType, ColumnDict, Column
from mlplatform_lib.predefinedai.predefinedai_model_config import PredefinedAIModelConfig
from mlplatform_lib.predefinedai.predefinedai_stage_config import PredefinedAIStageConfig
import yaml
import argparse
from typing import List, Union, Dict
from inspect import signature
from inflection import underscore, camelize
from dataclasses import is_dataclass
from enum import EnumMeta
import json


class PredefinedAIConfigParser:
    def __init__(self, data_config_path=None, model_config_path=None, stage_config_path=None):
        parser = argparse.ArgumentParser()
        parser.add_argument("--data_config", type=str, default=None)
        parser.add_argument("--model_config", type=str, default=None)
        parser.add_argument("--stage_config", type=str, default=None)
        _args = parser.parse_args()

        if _args.data_config is not None:
            data_config_dict = json.loads(_args.data_config)
        elif data_config_path is not None:
            with open(data_config_path) as data_config_file:
                data_config_dict = yaml.safe_load(data_config_file)
        else:
            raise ValueError('data_config must be in args')

        if _args.model_config is not None:
            model_config_dict = json.loads(_args.model_config)
        elif model_config_path is not None:
            with open(model_config_path) as model_config_file:
                model_config_dict = yaml.safe_load(model_config_file)
        else:
            raise ValueError('model_config must be in args')

        if _args.stage_config is not None:
            stage_config_dict = json.loads(_args.stage_config)
        elif stage_config_path is not None:
            with open(stage_config_path) as stage_config_file:
                stage_config_dict = yaml.safe_load(stage_config_file)
        else:
            raise ValueError('stage_config must be in args')

        self.data_config: PredefinedAIDataConfig = from_dict(PredefinedAIDataConfig, data_config_dict)
        # self.data_config_list: List[PredefinedAIDataConfig] = [from_dict(PredefinedAIDataConfig, data_config_d) for
        #                                                        data_config_d in data_config_dict]
        self.model_config: PredefinedAIModelConfig = from_dict(PredefinedAIModelConfig, model_config_dict)
        self.stage_config: PredefinedAIStageConfig = from_dict(PredefinedAIStageConfig, stage_config_dict)

    def get_data_config_from_data_key(self, data_key) -> DataConfig:
        try:
            return list(filter(lambda x: x.__getattribute__('key') == data_key, self.data_config.data_configs))[0]
        except IndexError:
            raise ValueError(f'data_key "{data_key}" do not exist in data_config')

    def get_data_config_dict_from_data_key(self, data_key) -> Dict[str, Union[ColumnDict, List[ColumnDict]]]:
        data_config_dict = {}
        data_config = self.get_data_config_from_data_key(data_key)
        for config in data_config.configurations:
            if config.type == DataConfigurationType.Column:
                if config.value is None:
                    data_config_dict[config.key] = None
                else:
                    data_config_dict[config.key] = {'name': config.value.name, 'type': config.value.type}
            elif config.type == DataConfigurationType.Columns:
                data_config_dict[config.key] = []
                if config.value is None:
                    continue
                for value in config.value:
                    data_config_dict[config.key].append({'name': value.name, 'type': value.type})
        return data_config_dict

    def get_all_data_config_dict(self) -> Dict[str, Dict[str, Union[ColumnDict, List[ColumnDict]]]]:
        all_data_config_dict = {}
        data_keys = [data_config.key for data_config in self.data_config.data_configs]
        for data_key in data_keys:
            all_data_config_dict[data_key] = self.get_data_config_dict_from_data_key(data_key)
        return all_data_config_dict

    def get_model_name(self) -> str:
        return self.model_config.key

    def get_sub_model_name_list(self) -> List[str]:
        return [mc.key for mc in self.model_config.model_configs]

    def get_model_hyperparameters_dict(self, model_name: str) -> dict:
        return self.model_config._get_model_hyperparameters_dict(model_name)

    def get_train_args_dict(self) -> dict:
        return self._get_stage_args_dict('train')

    def get_retrain_args_dict(self) -> dict:
        return self._get_stage_args_dict('retrain')

    def get_inference_args_dict(self) -> dict:
        return self._get_stage_args_dict('inference')

    def get_serving_args_dict(self) -> dict:
        return self._get_stage_args_dict('serving')

    def _get_stage_args_dict(self, stage) -> dict:
        return self.stage_config._get_args_dict(stage)


def from_dict(dataclass, dictionary):
    if dictionary is None:
        return None
    temp_dict = {}
    sig = signature(dataclass)
    for key, value in dictionary.items():
        key = underscore(key)
        assert key in sig.parameters.keys(), \
            f'key ({key}) dose not exist in {dataclass.__name__} keys ({dataclass.__annotations__.keys()}), ' \
            f'({dataclass.__name__}: {dictionary})'
        key_class = sig.parameters[key].annotation
        if is_dataclass(key_class):
            temp_dict[key] = from_dict(key_class, value)
        elif (
            hasattr(key_class, '__origin__') and
            key_class.__origin__ == list
        ):
            # temp_dict[key] = [from_dict(key_class.__args__[0], v) for v in value]
            if is_dataclass(key_class.__args__[0]):
                temp_dict[key] = [
                    from_dict(key_class.__args__[0], v) for v in value
                ]
            elif (
                hasattr(key_class.__args__[0], '__origin__') and
                key_class.__args__[0].__origin__ == Union
            ):
                def union_mapping(union_classes, value):
                    for union_class in union_classes.__args__:
                        if value is None or set(union_class.__annotations__.keys()) == {underscore(v_k) for v_k in value.keys()}:
                            try:
                                return from_dict(union_class, value)
                            except AssertionError:
                                continue
                    raise ValueError(f'value ({value}) dose not fit in dataclasses ({union_classes.__args__})')
                temp_dict[key] = [union_mapping(key_class.__args__[0], v) for v in value]
        elif (
            hasattr(key_class, '__origin__') and key_class.__origin__ == Union
        ):
            def union_mapping(union_classes, value):
                for union_class in union_classes.__args__:
                    if value is None or set(union_class.__annotations__.keys()) == {underscore(v_k) for v_k in value.keys()}:
                        try:
                            return from_dict(union_class, value)
                        except AssertionError:
                            continue
                raise ValueError(f'value ({value}) dose not fit in dataclasses ({union_classes.__args__})')
            if type(value) == list:
                temp_dict[key] = [union_mapping(key_class, v) for v in value]
            else:
                temp_dict[key] = union_mapping(key_class, value)
        elif isinstance(key_class, EnumMeta):
            temp_dict[key] = key_class(value)
        else:
            assert isinstance(value, dataclass.__annotations__[key]), \
                    f'{key} type must be {dataclass.__annotations__[key]} (type: {type(value)}, value: {value}))'
            temp_dict[key] = value
    return dataclass(**temp_dict)
