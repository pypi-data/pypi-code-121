import traceback, inspect, trace, sys, os

from dataclasses import copy
from core import core
from typing import List, Dict

import pandas as pd

from ._save import AlphaSave

LOG = core.get_logger("tests")

class AlphaTest:
    _test = True
    category = ""
    index = 0
    current_test_name = ""

    outputs: Dict[str, bool] = {}
    coverages: Dict[str, object] = {}

    def begin(self):
        pass

    def end(self):
        pass

    def test(self, name, coverage: bool = False):
        self.output = None
        self.partial_output = None

        status = False
        self.current_test_name = name
        fct = getattr(self, name)
        if fct is None:
            LOG.info(
                f"Failed to get testing function <{name}> in category <{self.category}>"
            )
            return False

        ignore_dirs = [
            sys.prefix,
            sys.exec_prefix,
            os.sep.join(sys.prefix.split(os.sep)[:-1]),
        ]  # TODO: log ignored
        tracer = trace.Trace(ignoredirs=ignore_dirs)

        self.begin()
        status = fct()
        self.end()
        if coverage:
            tracer.runfunc(fct)
            self.coverages[name] = tracer.results()
        if self.output is not None:
            status = self.output

        return status

    def save(self, name):
        fct = getattr(self, name)
        if fct is None:
            return False

        if inspect.unwrap(fct).__name__ == save_method_name:  # TODO: modify
            object_to_save = fct(get_return=True)
            object_name_to_save = fct(get_name=True)
            AlphaSave.save(object_to_save, object_name_to_save)

    def reverse(self):
        self.__reverse_output()

    def __reverse_output(self):
        self.output = not self.output
        self.partial_output = not self.partial_output
        return self.output

    def _set_output(self, status):
        if self.output is not None:
            self.output = status and self.output
        else:
            self.output = status
        self.partial_output = status
        return self.partial_output

    def assert_array_equal(self, a, b, conditions: List[bool] = [], msg:str='') -> bool:
        status = len(a) == len(b)
        if status:
            for i in range(len(a)):
                if a[i] != b[i]:
                    status = False
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: <{a}> and <{b}> are not equals")
        return self._assert(status, conditions)

    def _assert(self, status, conditions: List[bool] = [], msg:str='') -> bool:
        if len(conditions) != 0 and type(conditions) == list:
            status = status and all(conditions)
        return self._set_output(status)

    def assert_is_not_none(self, a, conditions: List[bool] = [], msg:str='') -> bool:
        status = a is not None
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: value is None")
        return self._assert(status, conditions)

    def assert_is_none(self, a, conditions: List[bool] = [], msg:str='') -> bool:
        status = a is None
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: value is not None")
        return self._assert(status, conditions)

    def assert_is_empty(self, a, conditions: List[bool] = [], msg:str='', attribute=None) -> bool:
        status = self.assert_is_not_empty(a, conditions=conditions, attribute=attribute, msg=msg)
        if status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: value is not empty")
        return self.__reverse_output()

    def assert_are_keys_in_model_attributes(
        self, a, model, attributes=[], conditions: List[bool] = [], msg:str=''
    ):
        status = self.assert_are_keys_in_models_attributes(
            a, [model], attributes=attributes, conditions=conditions
        )
        return status

    def assert_are_keys_in_models_attributes(
        self, a, models, attributes=[], conditions: List[bool] = [], msg:str=''
    ):
        self.assert_is_not_none(a, msg=msg)
        for model in models:
            attributes.extend(list(model.get_schema()._declared_fields.keys()))
        attributes = list(set(attributes))
        key_in = {x: x in attributes for x in a.keys()}
        status = all(key_in.values())
        if not status:
            LOG.info(
                f"{self.current_test_name} {msg} - Assert: missing keys in model: {','.join([x for x, y in key_in.items() if not y])}"
            )
        return self._assert(status, conditions)

    def assert_has_model_attributes(
        self, a, model, conditions: List[bool] = [], msg:str=''
    ) -> bool:
        self.assert_is_not_none(a, msg=msg)
        fields = list(model.get_schema()._declared_fields.keys())
        if not hasattr(a, "keys"):
            return self._assert(False, conditions)
        key_in = {x: x in a.keys() for x in fields}
        status = all(key_in.values())
        if not status:
            LOG.info(
                f"{self.current_test_name} {msg} - Assert: missing model keys: {','.join([x for x, y in key_in.items() if not y])}"
            )
        return self._assert(status, conditions)

    def assert_is_true(self, a, conditions: List[bool] = [], msg:str=''):
        status = a
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: value {a} is not True")
        return self._assert(status, conditions)

    def assert_is_false(self, a, conditions: List[bool] = [], msg:str=''):
        status = a
        if status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: value {a} is not False")
        return self._assert(not status, conditions)

    def assert_contains(self, container, element, conditions: List[bool] = [], msg:str=''):
        status = element in container
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: {container=} does not contain {element=}")
        return self._assert(status, conditions)

    def assert_is_not_empty(
        self, a, conditions: List[bool] = [], msg:str='', attribute=None
    ) -> bool:
        if attribute is not None:
            if not hasattr(a, attribute):
                LOG.info(
                    f"{self.current_test_name} {msg} - Object of type <{type(a)}> does not have an attribute named <{attribute}>"
                )
            status = a is not None and not len(getattr(a, attribute)) == 0
        elif isinstance(a, pd.DataFrame):
            status = a is not None and not a.empty
        else:
            status = a is not None and len(a) != 0
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: value is None")
        return self._assert(status, conditions)

    def assert_is_dict(self, a, conditions: List[bool] = [], msg:str=''):
        status = type(a) == dict
        if not type(a) == dict:
            LOG.info(f"{self.current_test_name} {msg} - Assert: value is not a dict")
        return self._assert(status, conditions)

    def assert_is_dict_not_empty(self, a, conditions: List[bool] = [], msg:str=''):
        self.assert_is_dict(a, msg=msg)
        status = self.assert_is_not_empty(a, msg=msg)
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: dict {a} is empty")
        return self._assert(status, conditions)

    def assert_is_dict_with_key(self, a, key, conditions: List[bool] = [], msg:str='') -> bool:
        self.assert_is_dict(a, msg=msg)
        status = key in a
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: dict has not key {key}")
        return self._assert(status, conditions)

    def assert_is_dict_with_key_not_empty(
        self, a, key, conditions: List[bool] = [], msg:str=''
    ) -> bool:
        self.assert_is_not_none(a, msg=msg)
        self.assert_is_dict_with_key(a, key, msg=msg)
        status = self.assert_is_not_empty(a, msg=msg)
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: dict {a} has no empty key {key}")
        return self._assert(status, conditions)

    def assert_is_dict_with_key_with_value(
        self, a, key, value, conditions: List[bool] = [], msg:str=''
    ) -> bool:
        status = self.assert_is_dict_with_key_not_empty(a, key, msg=msg)
        if status:
            status = self.assert_equal(a[key], value, msg=msg)
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: {a} does not contains a {key=} with {value=}")
        return self._assert(status, conditions)

    def assert_equal(self, a, b, conditions: List[bool] = [], msg:str='') -> bool:
        status = a == b
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: {a} and {b} are not equals")
        return self._assert(status, conditions)
    
    def assert_not_equal(self, a, b, conditions: List[bool] = [], msg:str='') -> bool:
        status = a != b 
        if not status:
            LOG.info(f"{self.current_test_name} {msg} - Assert: {a} and {b} are equals")
        return self._assert(status, conditions)

    def assert_length(
        self, a, length, conditions: List[bool] = [], msg:str='', strict: bool = False
    ) -> bool:
        status_not_none = self.assert_is_not_none(a, msg=msg)
        status = len(a) == length
        if strict:
            status = status and len(a) != 0
        if not status and status_not_none:
            LOG.info(f"{self.current_test_name} {msg} - Assert: length {len(a)} is not the {length} expected")
        return self._assert(status, conditions)

    def assert_transaction(self, tr, conditions: List[bool] = [], msg:str='') -> bool:
        status_not_none = self.assert_is_not_none(tr, msg=msg)
        status = tr is not None and tr != "timeout"
        if not status and status_not_none:
            LOG.info(f"{self.current_test_name} {msg} - Assert: object if not a transaction")
        return self._assert(status, conditions)

    def assert_api_answer(self, url:str, method:str, expected_output:dict, default_values:dict, params:dict={}, msg:str=''):
        raw_params = copy.copy(params)
        from ...libs import api_lib
        answer = api_lib.get_api_answer(url=url, method=method, params=params, no_log=True)
        
        self.partial_output = True
        real_output = {}
        if not self.assert_equal(answer.error,0):
            LOG.info("Answer is invalid")
        for x, y in answer.data.items():
            if x in expected_output:
                self.assert_equal(y, expected_output[x])
                real_output[x] = y
            elif x in default_values:
                self.assert_equal(y, default_values[x])
            else:
                self.assert_is_none(y)
        if not self.partial_output:
            LOG.info(f"{self.current_test_name} {msg} - Assert: {raw_params=} > {params=} does not provide an {expected_output=} but {real_output}")

    def assert_api_answer_fail(self, url:str, method:str, params:dict, expected_output:str, default_values:dict, msg:str=''):
        from ...libs import api_lib
        answer = api_lib.get_api_answer(url=url, method=method, params=params, no_log=True)

        self.partial_output = True
        self.assert_equal(answer.error,1)
        self.assert_equal(answer.status,expected_output)

        if not self.partial_output:
            LOG.info(f"{self.current_test_name} {msg} - Assert: {params=} does not provide an {expected_output=} but {answer.status}")