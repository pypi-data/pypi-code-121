import abc
import docparser.core.easy_cache
from docparser.core import easy_cache


class BehaviorBase:
    """
    数据处理行为基类
    """
    class_index = 1
    _cache = easy_cache

    def __init__(self):
        pass

    @abc.abstractmethod
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

    @classmethod
    def _find_values(cls, key, table_name, table):

        values = []
        if table_name and table_name.strip() != "":
            datatable = table.get(table_name)
            for i, x in enumerate(datatable["column"]):
                if x.lower() == key:
                    for j, row in enumerate(datatable["rows"]):
                        values.append(row[i])

        else:
            values.append(table.get(key))
        return values

    @classmethod
    def _find_col_index(cls, key, table_name, table):
        datatable = table.get(table_name)
        for i, x in enumerate(datatable["column"]):
            if x.lower() == key:
                return i


    @classmethod
    def _restore_values(cls, key, table_name, table, values):
        if len(values) == 0:
            return
        if table_name and table_name.strip() != "":
            datatable = table.get(table_name)
            val_len = len(values)
            table_len = len(datatable["rows"])
            for i, x in enumerate(datatable["column"]):
                if x.lower() == key:
                    for j, row in enumerate(datatable["rows"]):
                        if val_len >= table_len:
                            datatable["rows"][j][i] = values[j]
        else:
            table[key] = values[0]
