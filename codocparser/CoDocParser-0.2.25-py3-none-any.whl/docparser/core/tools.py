import re
import types


class Tools:
    """
    解析工具类
    """

    regex_check = re.compile(r'.*?[^(]*?\((?!\?[!#<>=(:])[^)]*?\)', re.I)
    regex_check_group = re.compile(r'.*?[^(]*?\(\?P<col_\d+>(?!\?[!#<=(:])[^)]*?\)', re.I)

    @staticmethod
    def init_regex(pattern_list):
        """
        预编译正则
        :param pattern_list: 正则列表
        :return:
        """
        if isinstance(pattern_list, list):
            if pattern_list and len(pattern_list) > 0:
                return [re.compile(regex, re.I) for regex in pattern_list]
            return []
        else:
            return re.compile(pattern_list, re.I)

    @staticmethod
    def match_value(value, pattern_list, default_value=None):
        """
        根据指定的正则表示列表,顺序解析指定的字符串,匹配成功后停止继续往下匹配.
        :param value: 需要匹配的字符串
        :param pattern_list: 正则表达式列表
        :param default_value: 解析失败后,返回默认值. 如果没有给默认参数,则输出None
        :return: 给定正则表达存在命名捕获组,返回dict.非命名捕获组,返回list
        """

        if len(value) > 0:
            for i, pattern in enumerate(pattern_list):
                match = pattern.match(value)
                if match:
                    group_list = match.groups()
                    group_dict = match.groupdict()
                    return group_dict if len(group_dict) > 0 else group_list
                else:
                    continue

        return default_value

    @staticmethod
    def match_value2(value, pattern_list):
        """
        根据指定的正则表示列表,顺序解析指定的字符串,匹配成功后停止继续往下匹配.
        :param value: 需要匹配的字符串
        :param pattern_list: 正则表达式列表
        :return: 同时返回dict，list
        """

        if len(value) > 0:
            for i, pattern in enumerate(pattern_list):
                match = pattern.match(value)
                if match:
                    group_list = match.groups()
                    group_dict = match.groupdict()
                    return group_dict, group_list
                else:
                    continue

        return None, None

    @staticmethod
    def match_find_all(value, pattern_list):
        """
        根据指定的正则表示列表,顺序解析指定的字符串,匹配成功后停止继续往下匹配.
        :param value: 需要匹配的字符串
        :param pattern_list: 正则表达式列表
        :return: 同时返回list(tuple)
        """

        if len(value) > 0:
            for i, pattern in enumerate(pattern_list):
                group_dict = pattern.findall(value)
                if group_dict is not None and len(group_dict) > 0:
                    return group_dict
                else:
                    continue
        return None

    @staticmethod
    def match_find(value, pattern_list):
        """
        根据指定正则表示列表,顺序解析指定的字符串,匹配成功后停止继续往下匹配.
        :param value: 需要匹配的字符串
        :param pattern_list: 正则表达式列表
        :return: 任意正则表达式匹成功,返回被捕获字符串.反之,返回None.
        """
        if len(value) > 0:
            for i, pattern in enumerate(pattern_list):
                match = pattern.match(value)
                if match:
                    return match.group(0)
        return False

    @staticmethod
    def table_data_next(data, row_index, col_index, next_cell=True):
        """
        获得表格下一个数据
        :param data: 源表格
        :param row_index: 查找开始的行
        :param col_index: 查找开始的列
        :param next_cell: True：下一个单元格，如果遇到行尾，则进去下一行的首列索引； False：仅找一下行的索引,列不变，如果下一行列索引超出，返回末尾列索引
        :return: 行索引，列索引 如果没有下一格则返回-1，-1
        """
        max_row_index = len(data) - 1

        if max_row_index >= row_index + 1 and not next_cell:
            max_col_index = len(data[row_index + 1]) - 1
            if max_col_index >= col_index:
                return row_index + 1, col_index
            else:
                return row_index + 1, len(data[row_index + 1]) - 1

        max_col_index = len(data[row_index]) - 1
        if max_col_index >= col_index + 1:
            return row_index, col_index + 1
        elif max_row_index >= row_index + 1:
            return row_index + 1, 0

        return -1, -1

    @staticmethod
    def cut_value_to_string(value, cut_list):
        """
        裁剪字符串
        :param value: 被裁剪的字符串
        :param cut_list: 固定值列表
        :return: 返回列表
        """

        arr = []
        value = value.lstrip()
        j = len(cut_list)
        index = 0

        for i in range(len(value)):
            _index = value.find(cut_list[index])
            if _index == 0:
                arr.append(cut_list[index])
                value = value[len(cut_list[index]):].rstrip().lstrip()
            else:
                index = 0 if index + 1 >= j else index + 1
            if len(value) == 0:
                break
        return arr

    @staticmethod
    def merge_cell(col_list):
        """
        合并列数据
        :param col_list: 列数据
        :return: 合并之后的二维列表
        """
        result = []
        max_row_size = max(len(i) for i in col_list)
        max_col_size = len(col_list)

        for j in range(max_row_size):
            lst = []
            for i in range(max_col_size):
                lst.append(col_list[i][j] if j < len(col_list[i]) else '')
            result.append(lst)

        return result

    @staticmethod
    def recursion_dict(dic, func, _type: type, parent_key="", *parameters):
        """
        递归字典，并对特定类型的值进行回调
        :param dic: 数据字典
        :param func: 回调函数 包含参数：当前键，当前值，父级对象，层级key,不定长参数
        :param _type: 特定类型
        :param parent_key: 父级的键 默认空字符串
        :param parameters: 不定长参数，默认传回回调函数
        :return: 无
        """
        if not isinstance(dic, dict) or (
                not isinstance(func, types.FunctionType) and not isinstance(func, types.MethodType)):
            return

        keys_list = list(dic.keys())

        for index in range(len(keys_list)):
            k = keys_list[index]
            v = dic[keys_list[index]]

            if _type is None or isinstance(v, _type):
                func(k, v, dic, parent_key, *parameters)
            if _type is None or not isinstance(v, _type):
                if isinstance(v, list):
                    for i in range(len(v)):
                        if isinstance(v[i], dict):
                            Tools.recursion_dict(v[i], func, _type, "%s.%s.%d" % (parent_key, k, i), *parameters)
                elif isinstance(v, dict):
                    Tools.recursion_dict(v, func, _type, "%s.%s" % (parent_key, k), *parameters)

    @staticmethod
    def check_regex_group(regex_str):
        """
        检查正则表达式是否存在捕获组
        :param regex_str: 正则表达式字符串 或 正则表达式列表
        :return: 存在返回False,反之返回True
        """
        if isinstance(regex_str, list):
            return not all(Tools.regex_check.match(_str) for _str in regex_str)
        return Tools.regex_check.match(regex_str) is None

    @staticmethod
    def get_regex_group_count(regex_str):
        """
        返回正则表达式中带有【col_数字】命名捕获组的数量
        :param regex_str: 正则表达式字符串
        :return: 存在返回True,反之返回False
        """

        match_all = Tools.regex_check_group.findall(regex_str)
        return len(match_all)

    @staticmethod
    def len_table_cell_count(table):
        """
        获得二维列表的单元格的数量
        :param table: 二维列表
        :return:
        """
        cell_count = 0
        for i in range(len(table)):
            cell_count += len(table[i])
        return cell_count

    @staticmethod
    def get_key(*args):
        """
        组合键名
        :param args: 键组
        :return: 键
        """
        return ".".join(args)

    @staticmethod
    def get_dict_for_index(dic, index):
        if isinstance(dic, dict):
            for i, value in enumerate(dic.values()):
                if i == index:
                    return value
        else:
            return dic[index]
