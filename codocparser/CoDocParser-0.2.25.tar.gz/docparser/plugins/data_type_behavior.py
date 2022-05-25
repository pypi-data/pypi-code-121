import re
import time
import traceback
from docparser.core.behavior_base import BehaviorBase


class DataTypeBehavior(BehaviorBase):
    """
    数据类型转换处理行为
    =================
    配置说明：主节点下

        "data_type_format": {
                     # table：对应表格模板中的column中的列名，
                     # data_type 对应执行转换方法
                     # format: 格式化的样式
                     # collect: 复杂情况使用正则表达式来处理，必须命名捕获组，且对应format的组名 例如：'{a}+{b}' '(?P<a>\\w*?,)afasdf(?P<a>\\d+)' 'hello,afasdf123123' => 'hello+123123'
                     # filter： 使用正则过滤当前值的干扰字符串
                     # default： 设置默认值的情况下，如果转换失败会使用默认值替换原值
                     "ESTIMATE ARRIVAL AT POD Country": {"table": "", "data_type": "time", "format": "%A, %d %b, %Y %I:%M %p", "filter": "(\\n)"},
                     "ESTIMATE ARRIVAL AT POD Time": {"table": "", "data_type": "time", "format": "%A, %d %b, %Y %I:%M %p", "filter": "(\\n)"},
        }
    """

    class_index = 1

    class TypeConverter:

        @classmethod
        def convert_str(cls, table, error, key, conf, values, collect, val_format, val_filter, default_val, logger):
            return values

        @classmethod
        def convert_time(cls, table, error, key, conf, values, collect, val_format, val_filter, default_val, logger):

            for i in range(len(values)):
                try:
                    values[i] = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(values[i], val_format))
                except ValueError:
                    if default_val:
                        values[i] = default_val
                    logger.getLogger(cls.__name__).error(
                        f'时间格式转换异常,原因: [{values[i]} | {val_format} | {default_val}] <{traceback.format_exc()}>')
                except Exception:
                    if default_val:
                        values[i] = default_val
                    logger.getLogger(cls.__name__).error(
                        f'时间格式转换异常,原因: [{values[i]} | {val_format} | {default_val}] <{traceback.format_exc()}>')

            return values

    def data_processing(self, ref_data, data: list, error: list, config: dict, logger, additional) -> dict:
        """
        数据处理行为
        :param ref_data: 源数据
        :param data: execl解析出数据
        :param error: execl解析出现的错误
        :param config: 解析配置
        :param logger: 日志工具
        :param additional: 附加数据
        """

        format_config = config.get("data_type_format")
        if data and len(data) > 0 and format_config is not None:
            cls = DataTypeBehavior.TypeConverter()
            for key, conf in format_config.items():

                table_name = conf.get("table")

                data_type = conf.get("data_type")
                fun_name = f"convert_{data_type.lower()}"
                if hasattr(DataTypeBehavior.TypeConverter, fun_name):
                    callback = getattr(cls, fun_name)
                else:
                    continue

                val_format = conf.get("format")
                collect = conf.get("collect")
                val_filter = conf.get("filter")
                default_val = conf.get("default")

                values = self._find_values(key, table_name, data)
                self.__filter(values, val_filter)
                self.__format(values, collect, val_format)
                callback(data, error, key, conf, values, collect, val_format, val_filter, default_val, logger)
                self._restore_values(key, table_name, data, values)

        return additional

    @classmethod
    def __filter(cls, values, rule):
        """
        过滤指定字符
        """
        regex = re.compile(rule)
        for i in range(len(values)):
            values[i] = regex.sub("", values[i])

    @classmethod
    def __format(cls, values, collect, val_format):
        if collect and collect.strip() != "":
            regex = re.compile(collect)
            for i in range(len(values)):
                if (match := regex.search(values[i])) is not None:
                    if (group_dict := match.groupdict()) is not None:
                        values[i] = val_format.format(**group_dict)
