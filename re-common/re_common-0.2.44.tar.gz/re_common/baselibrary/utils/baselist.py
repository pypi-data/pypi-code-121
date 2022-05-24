class BaseList(object):

    def remove_null(self, lists):
        """
        清除列表的所有空字符串
        :param lists:
        :return:
        """
        return [r for r in lists if r != ""]

    def remove_blank_space(self, lists):
        """
        清除列表的所有空格数据,有其他字符的不算
        ["a","     ","  b"],　比如清除中间的　不清除ｂ
        :return:
        """
        return [r for r in lists if not r.isspace()]

    def clean_space_first_end(self, lists):
        """
        清理列表里每个字符串前后的空格
        :param lists:
        :return:
        """
        return [r.strip() for r in lists]

    def get_index(self, lists, obj):
        """
        从列表中找出某个值第一个匹配项的索引位置
        :return:
        """
        return lists.index(obj)
