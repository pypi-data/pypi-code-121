from typing import Dict, Any, Callable
from abc import abstractmethod

# Point base class
class BasePoint(object):

    def __init__(self, point_source: str, point_writable: bool, point_name: str, point_description: str = '', point_sample_value: Any = None):
        self.point_writable = point_writable
        self.point_source = point_source
        self.point_name = point_name
        self.point_description = point_description
        self.point_sample_value = point_sample_value
        self.point_value = None

    # get point_source
    @property
    def get_point_source(self):
        return self.point_source

    # get point_description
    @property
    def get_point_description(self):
        return self.point_description

    # get point_name
    @property
    def get_point_name(self):
        return self.point_name

    # get point_writable
    @property
    def get_point_writable(self):
        return self.point_writable

PointTableDict = Dict[str, Dict[str, Any]]

class BaseDriver(object):

    def __init__(self, dict_config: dict, dict_point: PointTableDict):
        self.dict_config = dict_config
        self.dict_point = dict_point
        self.callbacks = {}

    def __del__(self):
        self.exit()

    def exit(self):
        pass

    @abstractmethod
    def get_points(self, dict_point: dict = {}) -> tuple:
        pass

    def set_points(self, dict_points: dict) -> dict:
        pass

    def reset_config(self, dict_config: dict):
        self.dict_config = dict_config

    def reset_point(self, dict_point: dict):
        self.dict_point = dict_point

    def ping_target(self):
        return True

    @abstractmethod
    def configure(self):
        pass

    def search_points(self) -> dict:
        return {}

    def enable_logging(self, enable_log: bool, callback: Callable = None):
        if enable_log is True:
            self.callbacks['debug_log'] = callback
        else:
            self.callbacks['debug_log'] = None

    def set_call_result(self, call_method: str, **kwargs):
        if isinstance(self.callbacks, dict):
            call_method = self.callbacks.get(call_method)
            if isinstance(call_method, Callable):
                call_method(**kwargs)