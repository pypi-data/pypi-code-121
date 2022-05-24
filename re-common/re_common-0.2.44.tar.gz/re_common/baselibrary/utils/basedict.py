import copy
import sys


class BaseDicts(object):

    @classmethod
    def removeDictsNone(self, dicts: dict) -> dict:
        """
        去除字典中值为None的键值
        :param dicts:
        :return:
        """
        return {key: value for key, value in dicts.items() if value is not None}

    @classmethod
    def removeDictsStringNull(self, dicts: dict) -> dict:
        """
        去除字典中值为''的键值
        :param dicts:
        :return:
        """
        return {key: value for key, value in dicts.items() if value != ""}

    @classmethod
    def removeDictsAllNone(self, dicts: dict) -> dict:
        """
        去除字典中值为'' 和 None 的键值
        :param dicts:
        :return:
        """
        return {key: value for key, value in dicts.items() if value != "" and value is not None}

    @classmethod
    def sortkeys(self, dicts, reverse=False):
        """
        默认升序排序，加  reverse = True 指定为降序排序
        通过keys 对dicts 排序
        经过测试是新的列表
        :return:
        """
        return {k: dicts[k] for k in sorted(dicts.keys(), reverse=reverse)}

    @classmethod
    def sortvalues(self, dicts, reverse=False):
        """
        默认升序排序，加  reverse = True 指定为降序排序
        d[1] 为值　ｄ[0]　为键
        d 为元组　为dicts的键值
        通过　values 对dicts 排序
        :param dicts:
        :return:
        """
        return {k: v for k, v in sorted(dicts.items(), key=lambda d: d[1], reverse=reverse)}

    @classmethod
    def is_key_have(cls, dicts, key):
        """
        判断key 是否存在,但只能判断一个层次
        :param dicts:
        :param key:
        :return:
        """
        if key in dicts.keys():
            return True
        else:
            return False

    @classmethod
    def is_more_key_have(cls, dicts, keys=[]):
        """
        判断多个key 是否存在　可以有更深的层次
        :param dicts:
        :param keys: ["a.b","c.d"]
        :return:
        """
        for item in keys:
            if item.find("."):
                allstrings = ""
                for key in item.split("."):
                    allstrings = allstrings + '["{}"]'.format(key)
                try:
                    eval("dicts" + allstrings)
                except:
                    return False
            else:
                if item not in dicts.keys():
                    return False
        return True

    @classmethod
    def get_recursive_dict(cls, dict_a, key, call_back):
        if isinstance(dict_a, dict):
            for key, value in dict_a.items():
                if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, dict):
                    dict_a[key] = cls.get_recursive_dict(value, key, call_back)
                else:
                    dict_a[key] = call_back(key, value)

        elif isinstance(dict_a, list):
            # 如果列表中存在一个不是字典就不需要遍历了
            if dict_a == []:
                return call_back(key, dict_a)
            is_true = True
            for i in dict_a:
                if isinstance(i, dict):
                    is_true = True
                else:
                    is_true = False
                    continue
            if is_true:
                dict_temp = []
                for value in dict_a:
                    dict_temp.append(cls.get_recursive_dict(value, key, call_back))
                return dict_temp
            else:
                return call_back(key, dict_a)
        elif isinstance(dict_a, tuple):
            # 如果存在元组转成列表使用
            return cls.get_recursive_dict(list(dict_a), key, call_back)
        else:
            assert False, "传入类型错误：{}".format(type(dict_a))
        return dict_a

    @classmethod
    def is_dict_exit_key(cls, dicts, key_name, default=""):
        if dicts is not None and isinstance(dicts, dict):
            if dicts.get(key_name, 0) != 0:
                return dicts[key_name]
            else:
                return default
        else:
            return default
