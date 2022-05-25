from docparser.core.tools import Tools


class DataParserBase:

    def __init__(self, sheet, data, errors, parent_key):
        """
        初始化表格解析器
        :param sheet: 被解析的表单
        """
        self.sheet = sheet
        self.data = data
        self.errors = errors
        self.parent_key = parent_key

    def check_config(self, config):
        pass

    def _callback_action_check(self, key, value, dic, parent_key, *args):
        if key == "pattern_list":
            for pattern in value:
                if Tools.check_regex_group(pattern):
                    self.errors[Tools.get_key(self.parent_key,
                                              parent_key)] = "<key: pattern_list; regex: %s; 正则没有捕获组>" % pattern
        if key in "pattern" and not isinstance(value, list):
            dic[key] = [value]

    def _check_config_action(self, config):
        Tools.recursion_dict(config, self._callback_action_check, None)

    def parse(self, config, key):
        self._prev(config, key)
        self._parse(config, key)
        self._after(config, key)
        return True

    def _parse(self, config, key):
        pass

    def _prev(self, config, key):
        pass

    def _after(self, config, key):
        pass

    def _fixed_position_key(self, pattern_list: list, start_row_index=0, start_col_index=0) -> (int, int):
        """
        定位键位置
        :param pattern_list: 定位正则表达式列表
        :return:
        """
        is_first = False
        for row_index in range(start_row_index, len(self.sheet)):
            for col_index in range(len(self.sheet[row_index])):
                # 防止重复匹配时，查询重复的位置
                if start_row_index == row_index and start_col_index == col_index:
                    is_first = True
                if is_first:
                    if Tools.match_find(self.sheet[row_index][col_index], pattern_list):
                        return row_index, col_index
        return -1, -1
