from docparser.core.data_parser_base import DataParserBase
from docparser.core.tools import Tools
from docparser.core.behavior_data_parser import BehaviorDataParser
from docparser.config.excel import enums


class TableDataParser(DataParserBase):

    def check_config(self, config, key):
        """
        检查配置文件
        :param config: 配置
        :param key: 表名
        :return: 检查失败返回False，反之True
        """
        key = Tools.get_key(self.parent_key, key)
        err_count = len(self.errors)

        for k, v in config.items():
            if isinstance(v, str) and v == "":
                self.errors[Tools.get_key(key, k)] = r"<key: %s; 配置错误，不能为空>" % k

        if "column" not in config or len(config["column"]) == 0:
            self.errors[Tools.get_key(key, "column")] = r"<key: column; 表头至少需要一个列>"
        if "position_pattern" not in config:
            self.errors[Tools.get_key(key, "position_pattern")] = r"<key: position_pattern; 缺少配置>"
        if "behaviors" not in config:
            self.errors[Tools.get_key(key, "behaviors")] = r"<key: behaviors; 缺少配置>"
        for i, _config in enumerate(config["behaviors"]):
            if "over_action" not in _config:
                self.errors[Tools.get_key(key, "behaviors", "over_action")] = r"<key: over_action; 缺少配置>"
            if "value_pattern" not in _config:
                self.errors[Tools.get_key(key, "behaviors", "value_pattern")] = r"<key: value_pattern; 缺少配置>"
            if "value_format" in _config and Tools.check_regex_group(_config["value_format"]):
                self.errors[Tools.get_key(key, "behaviors", "value_format")] = r"<key: value_format; 正则表达式需要捕获组>"
            else:
                for j, _re in enumerate(_config["value_pattern"]):
                    if _config["over_action"] != enums.OverAction.row.name and Tools.check_regex_group(_re):
                        self.errors[Tools.get_key(key, "behaviors", "value_pattern", str(j),
                                                  _config["over_action"])] = r"<pattern: %s; 正则表达式需要捕获组>" % _re
                    elif _config["over_action"] == enums.OverAction.row.name and len(
                            config["column"]) > Tools.get_regex_group_count(_re):
                        self.errors[Tools.get_key(key, "behaviors", "value_pattern", str(j),
                                                  "row")] = r"<pattern: %s; 正则表达式的命名组格式不正确，或者数量与列数量不一致>" % _re

        return len(self.errors) == err_count

    def _parse(self, config, key):
        """
        解析表格数据
        :param config: 表格解析配置
        :param key: 表名
        :return:
        """
        regex = Tools.init_regex(config["position_pattern"])
        row_index, col_index = self._fixed_position_key(regex)
        if row_index == -1:
            self.errors["%s.%s" % (self.parent_key, key)] = r"<key:%s; 没有定位到有效位置>" % key
            return

        column = config["column"]
        separator = config["separator"]
        find_mode = config["find_mode"]
        separator_mode = config["separator_mode"]

        # 初始化表格
        table_key = key.split(".")[1]
        self.data[table_key] = {"column": column, "rows": []}
        behavior = BehaviorDataParser(config["behaviors"], row_index, col_index, separator, find_mode, separator_mode,
                                      table_key, "%s.%s" % (self.parent_key, key))
        behavior.match(self.data, self.errors, self.sheet)
        if len(self.data[table_key]["rows"]) > 0 and find_mode == enums.FindMode.v.name:
            self.data[table_key]["rows"].pop(0)
