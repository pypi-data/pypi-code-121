import re

from docparser.core.tools import Tools
from docparser.config.excel import enums


class ActionDataParser:
    """
    行动解析器
    """

    def __init__(self, config, original_value, value, parent_key):
        self.config = config
        self.original_value = original_value
        self.value = value
        self.parent_key = parent_key
        self.keyword_list = config["keyword"]
        self.keyword = self.keyword_list[0] if isinstance(self.keyword_list, list) else self.keyword_list
        self.key = config["key"]
        self.action_type = "add" if "action_type" not in config else config["action_type"]
        self.pattern_list = [] if "pattern_list" not in config else config["pattern_list"]
        self.default = None if "default_value" not in config else config["default_value"]

    def __error(self, errors, reason=None):
        """
        组装错误信息
        :param errors:
        :param reason:
        :return:
        """
        error_message = "<keyword: %s; key: %s; type: %s; message:[%s]处理失败!%s;>" % (
            self.keyword, self.key, self.action_type, self.original_value, (reason or ""))
        key = "%s.%s" % (self.parent_key, self.keyword)
        errors[key] = error_message

    def __keyword_fixed_table(self, data):
        """
        通过keywor寻找表格单元格
        :param data: 结果字典
        :return: 行号，列号, 失败原因
        """
        arr = self.keyword.split("-")

        if len(arr) < 3:
            return -1, -1, "寻找表格位置失败,keyword的配置规则应为table-键-列号-行号,table-键-列号"

        table_key = arr[1]
        if table_key in data:
            column = data["column"]
            if len(column) >= int(arr[2]):
                other_row = data[table_key]["rows"]
                col_number = int(arr[2]) - 1
                if len(arr) == 4 and len(other_row) > 0:
                    row_number = int(arr[3]) - 1
                else:
                    row_number = -1
                return row_number, col_number, None
            else:
                return -1, -1, "被寻找的表格不符合配置的查找条件"

    def __loop_table(self, value, data, row_index, col_index, mode=True):
        """
        遍历表格
        :param value: 处理之后的原始值
        :param data: 结果字典中的具体表格
        :param row_index: 行索引
        :param col_index: 列索引
        :param mode: 添加模式，True：默认为覆盖模式， False: 追加模式
        :return:
        """
        if row_index > -1 and data[row_index][col_index].strip() == "":
            data[row_index][col_index] = value if mode else "%s%s" % (data[row_index][col_index], value)
        else:
            for i in range(len(data)):
                if len(data[i]) > col_index:
                    data[i][col_index] = value if mode else "%s%s" % (data[i][col_index], value)

    def __completion_table(self, data, value, values):
        """
        根据列值补全表格数据
        :param data: 结果字典
        :param value: 原始值
        :param values: 处理之后列值列表
        :return:
        """
        table_name = self.parent_key.split('.')[2]
        if table_name in data:
            col_index = int(self.key.split('_')[1]) - 1
            rows = data[table_name]["rows"]
            start_repl = False
            for i in range(1, len(rows)):
                if not start_repl and rows[i][col_index] in value:
                    start_repl = True
                if len(values) == 0:
                    return
                if start_repl:
                    rows[i][col_index] = values.pop(0)
        else:
            return "父级键的层级错误{%s}，没找到表格{%s}" % (self.parent_key, table_name)

    def change(self, data, errors, group_dict):
        """
        根据配置修改值
        :param data: 结果字典
        :param errors: 错误列表
        :param group_dict: 当前已完成匹配的捕获组
        :return:
        """
        value = ""
        if len(self.pattern_list) > 0:
            r_list = Tools.init_regex(self.pattern_list)
            gmatch = Tools.match_value(self.value, r_list)
            if gmatch:
                value = gmatch["value"]
        elif group_dict and self.key in group_dict:
            value = group_dict[self.key]
        else:
            value = self.value

        if self.default is not None and value is None:
            value = self.default
        elif value is None:
            self.__error(errors)

        row_index = col_index = -1
        if "table-" in self.keyword:
            row_index, col_index, msg = self.__keyword_fixed_table(data)
            if col_index == -1:
                self.__error(errors, msg)
                return
            else:
                data = data[self.keyword.split('-')[1]]["rows"]
        elif self.keyword in data and "column" in data[self.keyword]:
            self.__error(errors, "键值不能覆盖表格")
            return

        reason = None
        if self.action_type == enums.ActionType.add.name:
            self._add_mode(value, data, row_index, col_index)
        elif self.action_type == enums.ActionType.append.name:
            self._append_mode(value, data, row_index, col_index)
        elif self.action_type == enums.ActionType.cut.name:
            self._cut_mode(value, data)
        elif self.action_type == enums.ActionType.split.name:
            self._split_mode(value, data)
        if reason:
            self.__error(errors, reason)

    def _add_mode(self, value, data, row_index, col_index):
        """
        覆盖模式， 直接覆盖指定位置的值，没有则创建。 在表格模式下只覆盖空值列
        :param value: 处理之后的原始值
        :param data: 结果字典中的具体表格
        :param row_index: 行索引
        :param col_index: 列索引
        :return:
        """
        if col_index > -1:
            self.__loop_table(value, data, row_index, col_index, True)
        else:
            data.update({self.keyword: data[self.keyword] if value == "" and self.keyword in data else value})

    def _append_mode(self, value, data, row_index, col_index):
        """
        追加模式
        :param value: 处理之后的原始值
        :param data: 结果字典中的具体表格
        :param row_index: 行索引
        :param col_index: 列索引
        :return:
        """
        if col_index > -1:
            self.__loop_table(value, data, row_index, col_index, False)
        else:
            value = ("%s%s" % (data[self.keyword], value)) if self.keyword in data else value
            data.update({self.keyword: value})

    def _cut_mode(self, value, data):
        """
        裁剪模式
        :param value: 处理之后的原始值
        :param data: 结果字典
        :return:
        """
        if value.strip() != "":
            values = Tools.cut_value_to_string(value, self.keyword_list)
            self.__completion_table(data, self.value, values)

    def _split_mode(self, value, data):
        """
        分割模式
        :param value: 处理之后的原始值
        :param data: 结果字典
        :return:
        """
        if value.strip() != "":
            values = re.split(r"[%s]" % re.escape("".join(self.keyword_list)), value, re.I)
            self.__completion_table(data, self.value, values)
