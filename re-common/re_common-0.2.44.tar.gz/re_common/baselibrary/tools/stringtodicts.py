from re_common.baselibrary.utils.baselist import BaseList


class StringToDicts(object):

    def __init__(self):
        pass

    def string_to_dicts_by_equal(self, strings):
        """
        将string 按行分组 然后每组内使用等号分割 前面为字典的键 后面为字典的值
        strings = ```
        host = 192.168.31.209
        user = root
        passwd = vipdatacenter
        db = data_gather_record
        port = 3306
        chartset = utf8
        ```
        :param strings:
        :return:
        """
        baselistobj = BaseList()
        lists = strings.split("\n")
        lists = baselistobj.remove_null(lists)
        lists = baselistobj.remove_blank_space(lists)
        lists = baselistobj.clean_space_first_end(lists)
        dicts = {}
        for item in lists:
            key = item.split("=")[0].strip()
            values = item.split("=")[1].strip()
            dicts[key] = values
        return dicts
