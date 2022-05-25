import re
from docparser.core.tools import Tools
from docparser.config.excel import enums
from docparser.core.action_data_parser import ActionDataParser


class BehaviorDataParser:
    """
    表格行为解析器
    """

    def __init__(self, config, row_start_index, col_start_index, separator, find_mode, separator_mode, table_key,
                 parent_key):
        """
        初始化
        :param config: 行为配置
        :param row_start_index: 匹配开始行索引
        :param col_start_index: 匹配开始列索引
        :param separator: 分割符
        :param find_mode: 查找方向
        :param separator_mode: 取值方式
        :param table_key: 表名
        :param parent_key 父级键
        """
        self.configs = config
        for i in range(len(self.configs)):
            v = self.configs[i]
            v["re"] = Tools.init_regex(v["value_pattern"])
            if "value_format" in v:
                v["re_format"] = Tools.init_regex(v["value_format"])
        self.repl_separator = " " if "repl_separator" not in config else config["repl_separator"]
        self.row_start = row_start_index
        self.col_start = col_start_index
        self.separator = separator
        self.find_mode = find_mode
        self.separator_mode = separator_mode
        self.table_key = table_key
        self.parent_key = parent_key

    def match(self, data, errors, sheet):
        """
        执行赋值行为
        :param data: 结果字典
        :param errors: 错误字典
        :param sheet: 表单
        :return:
        """
        row_start = self.row_start
        col_start = self.col_start
        table = data[self.table_key]
        index = 0
        config = self.configs[index]
        is_break = False
        for i in range(row_start, len(sheet)):
            for j in range(col_start, len(sheet[i])):
                if is_break and j > 0:
                    is_break = False
                    break
                for x in range(len(self.configs)):
                    if self.find_mode != enums.FindMode.v.name:
                        state = self.__horizontal(config, table, data, errors, sheet[i])
                    else:
                        state = self.__vertical(config, table, data, errors, sheet[i][j], j)

                    if state == enums.OverAction.end.name:
                        return
                    elif self.find_mode == enums.FindMode.v.name and state is not None:
                        break
                    elif state == enums.OverAction.skip.name or self.find_mode != enums.FindMode.v.name:
                        is_break = True
                        break
                    elif state is None:
                        index = 0 if index + 1 >= len(self.configs) else index + 1
                        config = self.configs[index]

    def __horizontal(self, config, table, data, errors, row):
        """
        横列模式解析
        :param config: 解析配置
        :param table: 结果字典中的目标表格
        :param data: 结果字典
        :param errors: 错误列表
        :param row: 被搜索的行
        :return:
        """
        value = self.separator.join(row)
        group_dict = None
        if "loop" in config and config["loop"] == 1 and config["over_action"] == enums.OverAction.row.name:
            group_dict = Tools.match_find_all(value, config["re"])
            if group_dict:
                for i in range(len(group_dict)):
                    if not isinstance(group_dict[i], str):
                        table["rows"].append(list(group_dict[i]))
                    else:
                        table["rows"].append([group_dict[i]])
                    for action in config["action"]:
                        if isinstance(action["key"], int):
                            ActionDataParser(action, group_dict[action["key"]], value,
                                             "%s.Behavior.%s" % (self.parent_key, config["over_action"])).change(data,
                                                                                                                 errors,
                                                                                                                 group_dict)
            else:
                return None
        else:
            group_dict, groups = Tools.match_value2(value, config["re"])
            if group_dict:
                if config["over_action"] == enums.OverAction.row.name:
                    row = []
                    for i in range(len(table["column"])):
                        row.append(group_dict["col_%s" % (i + 1)])
                    table["rows"].append(row)
                    for action in config["action"]:
                        ActionDataParser(action, group_dict[action["key"]], value,
                                         "%s.Behavior.%s" % (self.parent_key, config["over_action"])).change(data,
                                                                                                             errors,
                                                                                                             group_dict)
            else:
                return None

        return config["over_action"]

    def __vertical(self, config, table, data, errors, col, find_col_index):
        """
        纵列模式
        :param config: 解析配置
        :param table: 结果字典中的目标表格
        :param data: 结果字典
        :param errors: 错误列表
        :param col: 被搜索的列
        :param find_col_index: 若配置正则没有搜索到正确列索引，即列值为空时，则认为是被搜索的列索引是当前列索引
        :return:
        """

        group_dict, groups = Tools.match_value2(col, config["re"])
        if group_dict:
            if config["over_action"] == enums.OverAction.row.name:
                col_index = col_insert_index = 0
                col_list = []
                for k, v in group_dict.items():
                    if v and v.strip() != "":
                        col_index = int(k.split("_")[1]) - 1
                        v = self.__format_col(v, config)
                        col_list = v.split(self.separator)
                        break

                if len(col_list) == 0:
                    return None

                # 如果找到空匹配，默认当前列索引
                # if len(col_list) == 0:
                #     col_list.append("")
                #     col_index = find_col_index

                rows = table["rows"]
                row_count = len(rows)
                col_count = len(table["column"])

                # 首次添加
                if row_count == 0:
                    rows.append([col_index])
                    for i in range(len(col_list)):
                        rows.append([col_list[i]])
                else:
                    # 找哪一行缺列
                    # 缺列行的索引
                    row_insert_index = 0
                    # 有几列
                    incomplete_len = 0
                    for i in range(row_count):
                        if col_count > len(rows[i]):
                            incomplete_len = len(rows[i])
                            row_insert_index = i
                            break
                    # 首行加标记列
                    if row_insert_index == 0:
                        col_list.insert(0, col_index)

                    # 当前列数量
                    now_col_count = len(col_list)

                    # 找到当前列所在位置
                    for i in range(len(rows[0])):
                        if col_index > rows[0][i]:
                            col_insert_index = i + 1
                        elif col_index == rows[0][i]:
                            col_insert_index = i

                    # 当前准备赋值的列与拥有最大行数的列比较，得到需要补齐的行数.
                    diff = row_count - row_insert_index - now_col_count
                    # 存在缺列行才需要补

                    if incomplete_len > 0:
                        for i in range(abs(diff)):
                            if diff > 0:
                                # 当前列小于其他列长度，补全自己
                                col_list.append("")
                            else:
                                # 当前列大于其他列长度，补全行
                                rows.append([])

                    for i in range(row_insert_index, len(rows)):
                        # 对齐缺行列
                        for j in range(incomplete_len):
                            if len(rows[i]) < incomplete_len:
                                rows[i].append("")
                        rows[i].insert(col_insert_index, col_list.pop(0))

                for action in config["action"]:
                    ActionDataParser(action, group_dict[action["key"]], col,
                                     "%s.Behavior.%s" % (self.parent_key, config["over_action"])).change(data, errors,
                                                                                                         group_dict)
            return config["over_action"]
        elif groups:
            return config["over_action"]
        return None

    def __format_col(self, value, config):
        """
        格式化
        :param value: 捕获之后的纵列值
        :param config: 配置
        :return: 格式化后的字符串
        """
        if "re_format" in config:
            arr = config["re_format"].split(value)
            arr = [s.replace(self.separator, self.repl_separator) for s in arr if
                   s != "" and s != self.separator and s != self.repl_separator]
            value = self.separator.join(arr)
        return value
