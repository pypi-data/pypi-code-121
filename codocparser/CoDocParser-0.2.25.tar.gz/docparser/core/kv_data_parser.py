import re

from docparser.config.excel import enums
from docparser.core.tools import Tools
from docparser.core.data_parser_base import DataParserBase
from docparser.core.action_data_parser import ActionDataParser


class KvDataParser(DataParserBase):

    def check_config(self, config, key):
        """
        检查键值对配置文件
        :param config: 配置
        :param key: 键
        :return: 检查失败返回False，反之True
        """
        key = Tools.get_key(self.parent_key, key)
        self._check_config_action(config)

        err_count = len(self.errors)

        cell_count = Tools.len_table_cell_count(self.sheet)
        if "position_pattern" not in config:
            self.errors[Tools.get_key(key, "value_pattern")] = r"<key: value_pattern; 缺少配置或者为空>"
        else:
            for i, pattern in enumerate(config["position_pattern"]):
                if pattern.strip() == "":
                    self.errors[Tools.get_key(key, "value_pattern", str(i))] = r"<value_pattern不能为空>"
        if "repeat_count" in config:
            if config["repeat_count"] <= 0:
                config["repeat_count"] = 1
            elif config["repeat_count"] > cell_count:
                config["repeat_count"] = cell_count
        else:
            config["repeat_count"] = 1
        if "is_split_cell" in config and config["is_split_cell"] == 1:
            if Tools.check_regex_group(config["split_pattern"]):
                self.errors[Tools.get_key(key, "split_pattern")] = r"<key: split_pattern; 缺少分列的捕获组>"
        if "value_pattern" not in config:
            self.errors[Tools.get_key(key, "value_pattern")] = r"<key: value_pattern; 缺少配置>"
        else:
            for j, _re in enumerate(config["value_pattern"]):
                if config["separator_mode"] != enums.SeparatorMode.split.name and Tools.check_regex_group(_re):
                    self.errors[
                        Tools.get_key(key, "value_pattern", str(j))] = r"<key: value_pattern; regex: %s; 缺少捕获组>" % _re

        for i,action in enumerate(config["action"]):
            if "key" not in action:
                action["key"] = i

        return len(self.errors) == err_count

    def _parse(self, config, key):
        """
        解析键值对数据
        :param config: 键值对解析配置
        :param key: 键
        :return:
        """
        regex = Tools.init_regex(config["position_pattern"])
        row_index = col_index = 0
        for repl in range(config["repeat_count"]):
            row_index, col_index = self._fixed_position_key(regex, row_index, col_index)
            if row_index == -1:
                self.errors[Tools.get_key(self.parent_key, key, "fixed_position_key")] = r"<没有定位到有效位置>"
                return

            find_mode = config["find_mode"]
            separator_mode = config["separator_mode"]

            is_split_cell = config["is_split_cell"]
            split_pattern = config["split_pattern"]
            if is_split_cell == 1:
                self._split_cell(row_index, col_index, key, split_pattern)

            group_dict, value, row_index, col_index = self._fixed_position_value(find_mode, separator_mode,
                                                                                 config["value_pattern"], row_index,
                                                                                 col_index)
            if config["repeat_count"] > 1 and find_mode == enums.FindMode.default.name and row_index > -1:
                row_index, col_index = Tools.table_data_next(self.sheet, row_index, col_index)

            for i, action in enumerate(config["action"]):
                v = None
                if group_dict:
                    if "key" not in action:
                        action["key"] = i
                    if "action_type" not in action:
                        action["action_type"] = "add"

                    if isinstance(action["key"], str) and action["key"] in group_dict:
                        v = group_dict[action["key"]]
                    elif isinstance(action["key"], int) and action["key"] < len(group_dict):
                        v = Tools.get_dict_for_index(group_dict, action["key"])

                    if "table-" not in action["keyword"] and action["keyword"] not in self.data:
                        self.data.update({action["keyword"]: ""})
                v = v if v else ""
                action_parser = ActionDataParser(action, value, v, Tools.get_key(self.parent_key, key))
                action_parser.change(self.data, self.errors, group_dict)

    def _split_cell(self, row_index, col_index, key, split_pattern):
        """
        拆分单元
        :param row_index: 单元格所在行号
        :param col_index: 单元格所在列号
        :return:
        """
        group_dict = Tools.match_value(self.sheet[row_index][col_index], Tools.init_regex(split_pattern))
        if group_dict:
            arr = group_dict.values()
            self.sheet[row_index].pop(col_index)
            for i, v in enumerate(arr):
                self.sheet[row_index].insert(row_index + i, v)
        else:
            self.errors[Tools.get_key(self.parent_key, key, "split_cell")] = r"<没有定位到有效位置>"

    def _fixed_position_value(self, find_mode, separator_mode, value_pattern, start_row_index, start_col_index):
        """
        定位值
        :param find_mode: 查找方向
        :param separator_mode: 分割膜式
        :param value_pattern: 正则表达式组
        :param start_row_index 开始行索引
        :param start_col_index 开始列索引
        :return: 匹配值， 原始值
        """
        row_index = start_row_index
        col_index = start_col_index
        cell_value = None
        cell_count = Tools.len_table_cell_count(self.sheet)
        for i in range(cell_count):
            if (find_mode == enums.FindMode.default.name and i == 0) or (
                    find_mode != enums.FindMode.default.name and i > 0):
                value = self.sheet[row_index][col_index]
                if separator_mode == enums.SeparatorMode.split.name:
                    cell_value = re.split(r'[%s]' % "".join(value_pattern), value, re.I)
                else:
                    cell_value = Tools.match_value(value, Tools.init_regex(value_pattern))
            if cell_value:
                return cell_value, value, row_index, col_index
            else:
                mode = find_mode == enums.FindMode.h.name
                if find_mode != enums.FindMode.default.name:
                    row_index, col_index = Tools.table_data_next(self.sheet, row_index, col_index, mode)
                    if row_index == -1:
                        row_index = 0
                        col_index = 0
                else:
                    break

        return None, None, -1, -1
