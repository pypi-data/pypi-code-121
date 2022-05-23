# -*- coding: UTF-8 -*-
import re
import json

from sensorsabtesting.ab_const import *

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2


from sensorsanalytics import SensorsAnalytics

from sensorsabtesting.cache import LRUCache, TTLCache
from datetime import datetime, timedelta

SDK_VERSION = "0.0.2"
VERSION_KEY = "abtest_lib_version"
PLATFORM = "platform"
PYTHON = "Python"

ab_enablg_log = False


class SensorsABException(Exception):
    pass


class SensorsABIllegalDataException(SensorsABException):
    """
    数据格式有误时，SDK会抛出此异常，用户应当捕获并处理。
    """

    pass


class SensorsABIllegalArgumentsException(SensorsABException):
    """
    参数有误时，SDK会抛出此异常，用户应当捕获并处理。
    """

    pass


class SensorsABTest:

    NAME_PATTERN = re.compile(
        r"^((?!^distinct_id$|^original_id$|^time$|^properties$|^id$|^first_id$|^second_id$|^users$|^events$|^event$|^user_id$|^date$|^datetime$|^device_id$|^user_group|^user_tag|^[0-9])[a-zA-Z0-9_]{0,99})$",
        re.I,
    )

    """
    要求 property 里面的 value 长度不得超过 1024
    """
    MAX_PROPERTY_LENGTH = 1024

    def __init__(
        self,
        base_url,
        sa,
        event_cache_time=1440,
        event_cache_size=4096,
        experiment_cache_size=4096,
        experiment_cache_time=1440,
        enable_event_cache=True,
        enable_log=False,
    ):
        """
        初始化 SDK
        :param base_url: AB 地址
        :param sa: SA SDK 对象
        :param event_cache_time:事件缓存时间，单位为分钟
        :param event_cache_size: 事件缓存条数
        :param experiment_cache_size: 试验缓存条数
        :param experiment_cache_time: 试验缓存时间，单位为分钟
        :param enable_event_cache: 是否自动触发 $ABTestTrigger 事件
        :param enable_log: 开启日志
        """
        if not base_url:
            raise SensorsABIllegalArgumentsException("base_url is Empty, init failed")
        if not isinstance(sa, SensorsAnalytics):
            raise SensorsABIllegalArgumentsException(
                "sa type is not SensorsAnalytics, init failed"
            )

        self._base_url = base_url
        self._sa = sa
        self._enable_event_cache = enable_event_cache
        if experiment_cache_size < 0:
            self._experiment_cache_size = 4096
        else:
            self._experiment_cache_size = int(experiment_cache_size)
        if experiment_cache_time < 0 or experiment_cache_time > 1440:
            self._experiment_cache_time = 1440
        else:
            self._experiment_cache_time = int(experiment_cache_time)
        if event_cache_time < 0 or event_cache_time > 1440:
            self._event_cache_time = 1440
        else:
            self._event_cache_time = int(event_cache_time)
        if event_cache_size < 0:
            self._event_cache_size = 4096
        else:
            self._event_cache_size = int(event_cache_size)
        global ab_enablg_log
        ab_enablg_log = enable_log

        self._experiment_cache_manager = ExperimentCacheManager(
            self._experiment_cache_time, self._experiment_cache_size
        )
        self._event_cache = EventCacheManager(
            self._event_cache_time, self._event_cache_size
        )
        self._track_day = None

    def async_fetch_ab_test(
        self,
        distinct_id,
        is_login_id,
        param_name,
        default_value,
        enable_auto_track_event=True,
        timeout_seconds=3.0,
        custom_ids={},
        properties={},
    ):
        """
        立即从服务端请求，忽略内存缓存
        :param distinct_id: 用户 ID
        :param is_login_id: 是否为登录 ID
        :param param_name: 试验变量名称
        :param default_value: 未命中试验，返回默认值（支持数据类型：int｜bool｜str｜dict）
        :param enable_auto_track_event: 是否 SDK 自动触发事件
        :param timeout_seconds:网络请求超时等待事件，单位为秒
        :param custom_ids:自定义主体
        :param properties:自定义属性
        :return: Experiment
        """
        return self.__fetch_ab(
            distinct_id,
            is_login_id,
            param_name,
            default_value,
            enable_auto_track_event,
            timeout_seconds,
            custom_ids,
            False,
            properties,
        )

    def fast_fetch_ab_test(
        self,
        distinct_id,
        is_login_id,
        param_name,
        default_value,
        enable_auto_track_event=True,
        timeout_seconds=3.0,
        custom_ids={},
        properties={},
    ):
        """
        优先从内存获取试验
        :param distinct_id: 用户 ID
        :param is_login_id: 是否为登录 ID
        :param param_name: 试验变量名称
        :param default_value: 未命中试验，返回默认值（支持数据类型：int｜bool｜str｜dict）
        :param enable_auto_track_event: 是否 SDK 自动触发事件
        :param timeout_seconds:网络请求超时等待事件，单位为秒
        :param custom_ids:自定义主体
        :param properties:自定义属性
        :return: Experiment
        """
        return self.__fetch_ab(
            distinct_id,
            is_login_id,
            param_name,
            default_value,
            enable_auto_track_event,
            timeout_seconds,
            custom_ids,
            True,
            properties,
        )

    def track_ab_test_trigger(self, experiment, custom_ids=None, properties={}):
        """
        触发 $ABTestTrigger 事件
        :param experiment: 请求返回结果
        :param custom_ids: 自定义主体
        :param properties: 自定义属性
        :return:
        """
        if not experiment or (not isinstance(experiment, Experiment)):
            SensorsABTest.ab_log(
                "The track ABTest event experiment result is null or type is not Experiment."
            )
            return
        if experiment.is_white_list or (not experiment.ab_experiment_id):
            SensorsABTest.ab_log(
                "The track ABTest event user not hit experiment or in the whiteList."
            )
            return
        if self._event_cache.is_event_exist(
            experiment.distinct_id,
            experiment.is_login_id,
            experiment.ab_experiment_id,
            custom_ids,
        ):
            SensorsABTest.ab_log("The event has been triggered.")
            return
        if not properties:
            properties = {}
        properties[EXPERIMENT_ID] = experiment.ab_experiment_id
        properties[EXPERIMENT_GROUP_ID] = experiment.ab_experiment_group_id
        if self.__is_day_first():
            version = [AB_TEST_EVENT_LIB_VERSION + ":" + SDK_VERSION]
            properties[LIB_PLUGIN_VERSION] = version
        self._sa.track(
            experiment.distinct_id, EVENT_TYPE, properties, experiment.is_login_id
        )
        if self._enable_event_cache:
            self._event_cache.set_cache(
                experiment.distinct_id,
                experiment.is_login_id,
                experiment.ab_experiment_id,
                custom_ids,
            )

    def __fetch_ab(
        self,
        distinct_id,
        is_login_id,
        param_name,
        default_value,
        enable_auto_track_event=True,
        timeout_seconds=3.0,
        custom_ids={},
        enable_cache=False,
        properties={},
    ):
        if not distinct_id or not isinstance(distinct_id, str):
            raise SensorsABIllegalArgumentsException("distinct_id is empty or not str")
        if not param_name or not isinstance(param_name, str):
            raise SensorsABIllegalArgumentsException("param_name is empty or not str")
        if not (
            isinstance(default_value, int)
            or isinstance(default_value, bool)
            or isinstance(default_value, dict)
            or isinstance(default_value, str)
        ):
            SensorsABTest.ab_log(
                "the type of defaultValue is not int,str,bool,dict return default value"
            )
            return Experiment(
                distinct_id, is_login_id=is_login_id, result=default_value
            )
        if self.__assert_custom_ids(custom_ids):
            return Experiment(
                distinct_id, is_login_id=is_login_id, result=default_value
            )
        r_timeout = timeout_seconds
        if (
            not timeout_seconds
            or timeout_seconds <= 0
        ):
            r_timeout = 3
        if enable_cache:
            experiment = self._experiment_cache_manager.get_cache_experiment_result(
                distinct_id, is_login_id, custom_ids, param_name
            )
            if not experiment:
                experiment = self.__getABTestByHttp(
                    distinct_id,
                    is_login_id,
                    r_timeout,
                    custom_ids,
                    properties,
                    param_name,
                )
                if experiment:
                    self._experiment_cache_manager.set_cache_experiment_result(
                        distinct_id, is_login_id, custom_ids, experiment
                    )
        else:
            experiment = self.__getABTestByHttp(
                distinct_id,
                is_login_id,
                r_timeout,
                custom_ids,
                properties,
                param_name,
            )
        result = self.__convert_experiment(
            experiment,
            distinct_id,
            is_login_id,
            param_name,
            default_value,
        )
        if enable_auto_track_event:
            try:
                self.__track_ab_trigger(result, custom_ids)
            except Exception as e:
                print(e)
        return result

    def __convert_experiment(
        self,
        experiment,
        distinct_id,
        is_login_id,
        param_name,
        default_value,
    ):
        r_experiment = Experiment(
            distinct_id, is_login_id=is_login_id, result=default_value
        )

        if not experiment:
            return r_experiment

        if RESULTS_KEY in experiment and experiment[RESULTS_KEY] is not None:
            results = experiment[RESULTS_KEY]
            for value in results:
                variables = value[VARIABLES_KEY]
                for variable in variables:
                    h_value = self._hit_experiment_value(
                        variable, param_name, default_value
                    )
                    if h_value is not None:
                        r_experiment.ab_experiment_id = value[EXPERIMENT_ID_KEY]
                        r_experiment.ab_experiment_group_id = value[
                            EXPERIMENT_GROUP_ID_KEY
                        ]
                        r_experiment.is_control_group = value[IS_CONTROL_GROUP_KEY]
                        r_experiment.is_white_list = value[IS_WHITE_LIST_KEY]
                        r_experiment.result = h_value
                        return r_experiment
        SensorsABTest.ab_log("return default value,http result not contains experiment")
        return r_experiment

    def _hit_experiment_value(self, variable, param_name, default_value):
        if "name" in variable and variable["name"] == param_name:
            v_type = variable["type"]
            v_value = variable["value"]
            if v_type:
                if "STRING" == v_type and isinstance(default_value, str):
                    return v_value
                elif "INTEGER" == v_type and isinstance(default_value, int):
                    return int(v_value)
                elif "JSON" == v_type and isinstance(default_value, dict):
                    return eval(v_value)
                elif "BOOLEAN" == v_type and isinstance(default_value, bool):
                    if v_value.lower() == 'true':
                        return True
                    else:
                        return False
                else:
                    SensorsABTest.ab_log("The default value type should be " + v_type)
                    return None

    def __getABTestByHttp(
        self,
        distinct_id,
        is_login_id,
        timeout_seconds,
        custom_ids,
        properties,
        experiment_name,
    ):
        request_params = {}
        if is_login_id:
            request_params["login_id"] = distinct_id
        else:
            request_params["anonymous_id"] = distinct_id
        request_params[PLATFORM] = PYTHON
        request_params[VERSION_KEY] = SDK_VERSION
        request_params["properties"] = {}
        if custom_ids:
            request_params["custom_ids"] = custom_ids
        right_p = SensorsABTest._properties_handler(properties)
        if right_p:
            request_params["custom_properties"] = right_p
            request_params["param_name"] = experiment_name
        response = self.__do_request(request_params, timeout_seconds)
        if response:
            ret_code = response.code
            SensorsABTest.ab_log("SAABTesting request code = " + str(ret_code))
            if 200 <= ret_code <= 300:
                http_res = response.read().decode("utf-8")
                SensorsABTest.ab_log("SAABTesting request message = " + http_res)
                http_res_dict = SensorsABTest._json_loads_byteified(http_res)
                if (
                    http_res_dict
                    and STATUS_KEY in http_res_dict
                    and SUCCESS == http_res_dict[STATUS_KEY]
                    and RESULTS_KEY in http_res_dict
                ):
                    return http_res_dict
        return None

    @staticmethod
    def _json_loads_byteified(json_text):
        return SensorsABTest._byteify(
            json.loads(json_text, object_hook=SensorsABTest._byteify), ignore_dicts=True
        )

    @staticmethod
    def _byteify(data, ignore_dicts=False):
        if isinstance(data, str):
            return data

        # if this is a list of values, return list of byteified values
        if isinstance(data, list):
            return [SensorsABTest._byteify(item, ignore_dicts=True) for item in data]
        # if this is a dictionary, return dictionary of byteified keys and values
        # but only if we haven't already byteified it
        if isinstance(data, dict) and not ignore_dicts:
            return {
                SensorsABTest._byteify(key, ignore_dicts=True): SensorsABTest._byteify(
                    value, ignore_dicts=True
                )
                for key, value in data.items()  # changed to .items() for python 2.7/3
            }

        # python 3 compatible duck-typing
        # if this is a unicode string, return its string representation
        if str(type(data)) == "<type 'unicode'>":
            return data.encode("utf-8")

        # if it's anything else, return it in its original form
        return data

    def __do_request(self, request_params, timeout_seconds):
        try:
            json_data = json.dumps(request_params)
            a = json_data.encode("utf-8")
            request = urllib2.Request(
                url=self._base_url, data=a, headers={"Content-type": "application/json"}
            )
            response = urllib2.urlopen(request, timeout=timeout_seconds)
        except Exception as e:
            print(e)
            return None
        return response

    def __assert_custom_ids(slef, ids):
        if not ids:
            SensorsABTest.ab_log("request without custom_ids")
            return False
        for (key, value) in ids.items():
            if not key or len(key.strip()) == 0:
                SensorsABTest.ab_log(
                    "request with invalid custom_ids,the keys of custom_ids has null or empty"
                )
                return True
            if not SensorsABTest.NAME_PATTERN.match(key):
                SensorsABTest.ab_log("request with invalid custom_ids,the key mismatch")
                return True
            if not value or len(value.strip()) == 0:
                SensorsABTest.ab_log(
                    "request with invalid custom_ids,the value of customIds has null or empty"
                )
                return True
            if len(value) > SensorsABTest.MAX_PROPERTY_LENGTH:
                SensorsABTest.ab_log(
                    "request with invalid custom_ids,the value length is too long"
                )
                return True
        return False

    def __track_ab_trigger(self, result, custom_ids={}):
        if result is None:
            return
        if (
            result.is_white_list is None
            or result.is_white_list
            or result.ab_experiment_id is None
        ):
            return
        if self._event_cache.is_event_exist(
            result.distinct_id, result.is_login_id, result.ab_experiment_id, custom_ids
        ):
            return
        properties = {}
        properties[EXPERIMENT_ID] = result.ab_experiment_id
        properties[EXPERIMENT_GROUP_ID] = result.ab_experiment_group_id
        if self.__is_day_first():
            version = [AB_TEST_EVENT_LIB_VERSION + ":" + SDK_VERSION]
            properties[LIB_PLUGIN_VERSION] = version
        self._sa.track(result.distinct_id, EVENT_TYPE, properties, result.is_login_id)
        if self._enable_event_cache:
            self._event_cache.set_cache(
                result.distinct_id,
                result.is_login_id,
                result.ab_experiment_id,
                custom_ids,
            )

    def __is_day_first(self):
        if self._track_day and self._track_day == datetime.now().day:
            return False
        self._track_day = datetime.now().day
        return True

    @staticmethod
    def ab_log(msg):
        if ab_enablg_log:
            print("SA_AB:" + msg)

    @staticmethod
    def _properties_handler(properties):
        if not properties:
            return {}
        new_p = properties.copy()
        for key, value in properties.items():
            if not key:
                raise SensorsABIllegalDataException("The property name is null")
            if len(key) > 100:
                raise SensorsABIllegalDataException(
                    "The property name %s is too long, max length is 100" % str(key)
                )
            if not SensorsABTest.NAME_PATTERN.match(key):
                raise SensorsABIllegalDataException(
                    "The property name %s is invalid format" % str(key)
                )
            if not (
                isinstance(value, int)
                or isinstance(value, float)
                or isinstance(value, str)
                or isinstance(value, bool)
                or isinstance(value, list)
            ):
                raise SensorsABIllegalDataException(
                    "The property name %s should be a basic type: float, str, bool, list."
                    % str(key)
                )
            if isinstance(value, list):
                for lvalue in value:
                    if not isinstance(lvalue, str):
                        raise SensorsABIllegalDataException(
                            "The property name %s should be a list of str." % str(key)
                        )
                new_p[key] = str(value)
            if isinstance(value, str) and len(value) > 8192:
                raise SensorsABIllegalDataException(
                    "The property name %s of value is too long.max length is 8192"
                    % str(key)
                )
        return new_p


class Experiment:
    def __init__(
        self,
        distinct_id,
        is_login_id,
        result=None,
        ab_experiment_id=None,
        ab_experiment_group_id=None,
        is_control_group=None,
        is_white_list=None,
    ):
        self.distinct_id = distinct_id
        self.is_login_id = is_login_id
        self.ab_experiment_id = ab_experiment_id
        self.ab_experiment_group_id = ab_experiment_group_id
        self.is_control_group = is_control_group
        self.is_white_list = is_white_list
        self.result = result

    def __str__(self):
        return (
            "distinct_id = %s,is_login_id = %s,result = %s,ab_experiment_id = %s,ab_experiment_group_id = %s,"
            "is_control_group = %s,is_white_list = %s"
            % (
                self.distinct_id,
                self.is_login_id,
                self.result,
                self.ab_experiment_id,
                self.ab_experiment_group_id,
                self.is_control_group,
                self.is_white_list,
            )
        )


class EventCacheManager:
    def __init__(self, time, size):
        if size != 0:
            self._cache = TTLCache(
                size, ttl=(timedelta(minutes=time)), timer=datetime.now
            )

    def is_event_exist(self, distinct_id, is_login_id, ab_experiment_id, custom_ids):
        if hasattr(self, "_cache"):
            return (
                self.__generate_key(
                    distinct_id, is_login_id, ab_experiment_id, custom_ids
                )
                in self._cache
            )
        else:
            return False

    def set_cache(self, distinct_id, is_login_id, ab_experiment_id, custom_ids):
        if hasattr(self, "_cache"):
            self._cache[
                self.__generate_key(
                    distinct_id, is_login_id, ab_experiment_id, custom_ids
                )
            ] = ""

    def __generate_key(self, distinct_id, is_login_id, ab_experiment_id, custom_ids):
        return "%s_%s_%s_%s" % (distinct_id, is_login_id, ab_experiment_id, custom_ids)


class ExperimentCacheManager:
    def __init__(self, cache_time, cache_size):
        if cache_size != 0:
            self._experiment_result_cache = TTLCache(
                cache_size, ttl=(timedelta(minutes=cache_time)), timer=datetime.now
            )

    def get_cache_experiment_result(
        self, distinct_id, is_login, custom_ids, experiment_name
    ):
        if hasattr(self, "_experiment_result_cache"):
            key = self.__generate_key(distinct_id, is_login, custom_ids)
            if key in self._experiment_result_cache:
                experiment_result = self._experiment_result_cache[key]
                result = experiment_result[RESULTS_KEY]
                for value in result:
                    v_var = value[VARIABLES_KEY]
                    for v in v_var:
                        if experiment_name == v["name"]:
                            SensorsABTest.ab_log("return cache")
                            return experiment_result
        return None

    def set_cache_experiment_result(
        self, distinct_id, is_login_id, custom_ids, experiment
    ):
        if hasattr(self, "_experiment_result_cache"):
            key = self.__generate_key(distinct_id, is_login_id, custom_ids)
            self._experiment_result_cache[key] = experiment

    def __generate_key(self, distinct_id, is_login, custom_ids):
        return distinct_id + "_" + str(is_login) + "_" + str(custom_ids)
