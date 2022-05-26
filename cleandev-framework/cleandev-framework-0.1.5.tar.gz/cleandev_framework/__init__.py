import re
from datetime import datetime
from generic_utils import CleanDevGenericUtils
from generic_utils import ReflectionClassUtilsImpl
from cleandev_framework.inmutables import DATA_CLASS_NAME
from cleandev_framework.config import _camel_case_enabled
from cleandev_framework.config import _parent_package_model
from cleandev_framework.inmutables import MODEL_BASE_CLASS_NAME

utils_reflec: ReflectionClassUtilsImpl = ReflectionClassUtilsImpl()
utils: CleanDevGenericUtils = CleanDevGenericUtils()

class DataClassAdapter:

    @staticmethod
    def _filter_attrs(instance) -> list:
        all_attr: list = list(dict(instance.__dict__).keys())
        filter_attrs: list = []
        for attr in all_attr:
            if not re.match('^_.*', attr):
                filter_attrs.append(attr)
        return filter_attrs

    @staticmethod
    def _check_is_model(instance: object):
        for class_ in instance.__class__.__bases__:
            if class_.__name__ == MODEL_BASE_CLASS_NAME:
                return True
        raise Exception

    @staticmethod
    def model_to_dataclass(instance):
        DataClassAdapter._check_is_model(instance)
        class_name: str = f"_{instance.__class__.__name__}{DATA_CLASS_NAME}"
        data_class_ = utils_reflec.get_class_from_package(_parent_package_model, class_name)
        attr_model_class: list = DataClassAdapter._filter_attrs(instance)
        json_model_adapter: dict = {}
        for attr in attr_model_class:
            json_model_adapter[attr] = getattr(instance, str(attr))
        return data_class_(**json_model_adapter)

    @staticmethod
    def list_models_to_list_dict(items: list) -> list:
        list_dict: list = []
        for row in items:
            model = DataClassAdapter.model_to_dataclass(row).__dict__

            if _camel_case_enabled == 'true':
                temp_json = {}
                for k in dict(model).keys():
                    temp_json[utils.to_camel_case(k)] = model[k]
                model = temp_json

            if 'date' in model:
                date: datetime.datetime = model['date']
                date_str: str = date.strftime("%m/%d/%Y, %H:%M:%S")
                model['date'] = date_str
            list_dict.append(model)
        return list_dict


class ModelAdapter:

    @staticmethod
    def _check_is_dataclass(instance: object):
        model_class: str = DATA_CLASS_NAME
        for class_ in instance.__class__.__bases__:
            if class_.__name__ == model_class:
                return True
        raise Exception


    @staticmethod
    def dataclass_to_model(instance):
        ModelAdapter._check_is_dataclass(instance)
        name_class_to_find = re.sub(f'{DATA_CLASS_NAME}$', '', re.sub('^_', '', instance.__class__.__name__))
        model_class_ = utils_reflec.get_class_from_package(_parent_package_model, name_class_to_find)
        model_class_ = model_class_()
        for key in dict(instance.__dict__).keys():
            value_to_set = getattr(instance, str(key))
            setattr(model_class_, key, value_to_set)
        return model_class_


