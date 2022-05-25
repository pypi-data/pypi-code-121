import inspect
import os
import sys

import pandas as pd
from pandas.io.excel import ExcelFile
import numpy as np
import re
import importlib
import importlib.util
from docparser.core.document_parser_base import DocumentParserBase
from docparser.core.kv_data_parser import KvDataParser
from docparser.core.table_data_parser import TableDataParser
from docparser.core.tools import Tools
import logging

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',
                    level=logging.ERROR)


class Excel2DocumentParser(DocumentParserBase):
    """
    excel文档解析器
    """

    def __init__(self, file_path, config):
        """
        初始化excel文档解析器
        :param file_path: excel文件位置
        :param config: excel解析匹配
        """
        self.file = file_path
        self.configs = config
        self._table_dict = {}
        self.data = []
        self.errors = []
        self.behaviors = []

        self.__loader_plugins()

        if not os.path.exists(file_path):
            raise FileNotFoundError

    def __read_excel(self, single_page=True):
        """
        读取excel文档
        :return: 原始表数据字典
        """
        data_xls = ExcelFile(self.file)
        # data = {"default": data_xls}
        # self.sheet_names = ["default"]
        data = {}
        self.sheet_names = data_xls.sheet_names
        if single_page:
            data[self.sheet_names[0]] = pd.read_excel(data_xls, sheet_name=self.sheet_names[0], header=None)
            return data

        for name in data_xls.sheet_names:
            df = pd.read_excel(data_xls, sheet_name=name, header=None)
            data[name] = df

        return data

    def __convert_to_table(self, single_page=True):
        """
        转化表单成二维列表
        :return: 处理之后的数据字典
        """
        data_list = self.__read_excel(single_page)
        sheets = {}
        for name, data in data_list.items():
            data = np.array(data).astype("str")
            len_data = len(data)
            execl_list = []
            for row_index in range(len_data):
                row = list(filter(lambda x: not (x == "nan" or x == "NaT"), data[row_index]))
                if len(row) > 0:
                    execl_list.append(row)
            sheets[name] = execl_list
        self._table_dict = sheets

    def __ues_extends(self, sheet, config):
        """
        创建解析器
        :param sheet: 被解析的表
        :param config: 解析配置
        :return: 解析器
        """
        extends_name = os.path.splitext(os.path.split(self.file)[1])[0].split("_")[0]
        _class = None
        if re.match(r'^[a-z][a-zA-Z0-9]*$', extends_name, re.I):
            try:
                module_name = 'docparser.extends.%s_data_parser' % extends_name.lower()
                class_name = '%sDataParser' % extends_name.capitalize()
                data_parser_module = importlib.import_module(module_name)
                cls = getattr(data_parser_module, class_name)
                _class = cls(sheet, config)
            except ModuleNotFoundError:
                pass

        return _class

    def parse(self):
        """
        根据匹配解析数据
        :return: 返回解析后的数据，单个表单页
        """
        self.__convert_to_table()
        return self._extract(self.sheet_names[0], self.configs)

    # def parse_multi_page(self):
    #     """
    #     根据匹配解析数据，存在多个配置时,通用配置，设置键为default,非通用键应该对应excel文档单表名
    #     :return:
    #     """
    #     result = {}
    #     self.__convert_to_table(False)
    #     for name, sheet in self._table_dict.items():
    #         config_name = name if name in self.configs else "default"
    #         result[name] = self._extract(name, self.configs[config_name], config_name)
    #     return result

    def _extract(self, key, config, name="default"):
        """
        合成提取数据字典
        :param key: 需要提取源数据的键
        :param config: 解析配置
        :param config: 配置名称
        :return: 数据字典，错误字典
        """
        multi_page_sheet = [self._table_dict[key]]
        if "multi_page" in self.configs:
            if "page_pattern" not in self.configs:
                self.errors.append(f"<{name}分页配置没有设置分页标识>")
                return self.data, self.errors
            else:
                multi_page_sheet = self._split_sheet(self._table_dict[key])

        for i in range(len(multi_page_sheet)):
            data, errors = self._get_data(multi_page_sheet[i], config, name)
            self.data.append(data)
            self.errors.append(errors)
            if len(errors) > 0:
                break

        return self.data, self.errors

    def _split_sheet(self, sheet):
        """
        分页
        :param sheet: 解析源数据
        :return: 多个数据集
        """
        multi_page_sheet = []
        page_index = -1
        re_page = Tools.init_regex(self.configs["page_pattern"])
        for i in range(len(sheet)):
            row = '\t'.join(sheet[i])
            if Tools.match_find(row, re_page):
                multi_page_sheet.append([])
                page_index += 1
            if page_index > -1:
                multi_page_sheet[page_index].append(sheet[i])
        return multi_page_sheet

    def _get_data(self, sheet, config, name="default"):
        """
        提取数据字典
        :param config: 解析配置
        :param config: 配置名称
        :return: 数据字典，错误字典
        """
        data = {}
        errors = {}
        _class = self.__ues_extends(sheet, config)
        if _class:
            data, errors = _class.parse()
        else:
            if "kv" in config:
                for k, v in config["kv"].items():
                    data_parser = KvDataParser(sheet, data, errors, name)
                    if not data_parser.check_config(v, "kv.%s" % k):
                        return data, errors
                    else:
                        data_parser.parse(v, "kv.%s" % k)
            if "table" in config:
                for k, v in config["table"].items():
                    data_parser = TableDataParser(sheet, data, errors, name)
                    if not data_parser.check_config(v, "table.%s" % k):
                        return data, errors
                    else:
                        try:
                            data_parser.parse(v, "table.%s" % k)
                        except:
                            pass
            additional = {}
            for cls in self.behaviors:
                try:
                    additional = cls().data_processing(sheet, data, errors, config, logging, additional)
                except Exception as ex:
                    if "BehaviorsError" not in errors:
                        errors["BehaviorsError"] = []
                    errors["BehaviorsError"].append(ex.args)

        return data, errors

    def __loader_plugins(self):
        """
        加载解析后的处理行为
        """
        module_name = "docparser.plugins"
        if module_name in sys.modules:
            module = sys.modules["docparser.plugins"]
        elif (spec := importlib.util.find_spec(module_name)) is not None:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        else:
            return None

        plugins = list(filter(lambda x: x.endswith("_behavior.py"), os.listdir(module.__path__[0])))
        for file in plugins:
            module_file = os.path.splitext(os.path.basename(file))[0]
            module = importlib.import_module(f"{module_name}.{module_file}")
            cls = getattr(module,
                          ''.join([s.capitalize() for s in os.path.splitext(os.path.basename(file))[0].split('_')]))
            if inspect.isclass(cls):
                self.behaviors.append(cls)
        if len(self.behaviors) > 0:
            self.behaviors = sorted(self.behaviors, key=lambda x: x.class_index)
