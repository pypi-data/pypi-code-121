# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-12-07 19:12:00
:LastEditTime: 2021-06-30 19:12:45
:LastEditors: HuangJingCan
:Description: 
"""
class DictUtil:
    @classmethod
    def merge_dict_list(self, source_dict_list, source_key, merge_dict_list, merge_key, merge_columns_names):
        """
        :description: 两个字典列表合并
        :param source_dict_list：源字典表
        :param source_key：源表用来关联的字段
        :param merge_dict_list：需要合并的字典表
        :param merge_key：需要合并的字典表用来关联的字段
        :param merge_columns_names：需要合并的字典表中需要展示的字段
        :return: 
        :last_editors: HuangJingCan
        """
        result = []
        for source_dict in source_dict_list:
            info_list = [i for i in merge_dict_list if source_dict[source_key]!="" and i[merge_key] == source_dict[source_key]]
            if info_list:
                list_key = list(merge_columns_names.split(","))
                source_dict = dict(source_dict, **dict.fromkeys(list_key))
                for item in list_key:
                    source_dict[item] = info_list[0].get(item)
            else:
                list1 = list(merge_columns_names.split(","))
                source_dict = dict(source_dict, **dict.fromkeys(list1))
            result.append(source_dict)
        return result

    @classmethod
    def auto_mapper(self, model, map_dict=None):
        """
        :description: 对象映射（把map_dict值赋值到实体model中）
        :param model：需要映射的实体对象
        :param map_dict：被映射的实体字典
        :return: 映射后的实体model
        """
        if map_dict:
            field_list = model.get_field_list()
            for filed in field_list:
                if filed in map_dict.keys():
                    setattr(model, filed, map_dict[filed])
        return model
