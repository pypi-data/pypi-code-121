# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-04-22 14:32:40
:LastEditTime: 2021-01-12 08:36:04
:LastEditors: HuangJingCan
:Description: 栏目扩展类
"""

from seven_framework.uuid import *
from seven_studio.utils.dict import *

from seven_studio.models.db_models.menu.menu_info_model import *
from seven_studio.models.enum import ButtonType
from seven_studio.models.enum import ButtonPlace


class MenuInfoDto():
    """
    :description: 自定义实体(栏目)
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    def __init__(self):
        self.MenuID = ""
        self.MenuIcon = ""
        self.MenuName = ""
        self.ParentID = ""
        self.IsShow = 0
        self.IsPower = 0
        self.IDPath = ""
        self.ShowCondition = ""
        self.CommandParms = ""
        self.ButtonColor = ""
        self.MenuCoteID = 0
        self.MenuCoteKey = ""
        self.ChildList = []
        self.MenuNamePath = ""
        self.ApiPath = ""
        self.ViewPath = ""
        self.ButtonPlace = 0
        self.CommandName = ""
        self.ActionType = 0
        self.ActionRender = 0
        self.MenuType = 0
        self.SortIndex = 0

    @classmethod
    def get_field_list(self):
        return ['MenuID', 'MenuIcon', 'MenuName', 'ParentID', 'IsShow', 'IsPower', 'IDPath', 'ShowCondition', 'CommandParms', 'ButtonColor', 'MenuCoteID', 'MenuCoteKey', 'ChildList', 'MenuNamePath', 'ApiPath', 'ViewPath', 'ButtonPlace', 'CommandName', 'ActionType', 'ActionRender', 'MenuType', 'SortIndex']


class MenuInfoEx(MenuInfo):
    def get_list_by_menu_list(self, menu_info_list):
        for menu_info in menu_info_list:
            menu_info = self.get_entity_by_menu_info(menu_info)
        return menu_info_list

    def get_entity_by_menu_info(self, menu_info):
        menu_info.MenuChildID = menu_info.MenuID + ":Child"
        menu_info.ApiPathValue = "/" + menu_info.MenuID + menu_info.ApiPath

        view_path_find_index = menu_info.ViewPath.find("/:")
        if view_path_find_index > 0:
            menu_info.ViewPathValue = menu_info.ViewPath[0:view_path_find_index]
        else:
            menu_info.ViewPathValue = menu_info.ViewPath

        menu_cote_key = "$" + menu_info.MenuCoteKey if menu_info.MenuCoteKey.strip() != "" else ""

        menu_info.RedirctPathValue = f"/{menu_info.MenuID}{menu_cote_key}{menu_info.ViewPathValue.lower()}"

        if menu_info.ViewPath.strip() != "":
            menu_info.RoutePathValue = f"/{menu_info.MenuID}{menu_cote_key}{menu_info.ViewPath.lower()}"
        else:
            menu_info.RoutePathValue = ""

        return menu_info


class MenuInfoModelEx(MenuInfoModel):
    """
    :description: 菜单扩展类
    :param {type} 
    :return: 
    :last_editors: HuangJingCan
    """
    def add_fast_menu(self, parent_id, suffix_name, button_type_str):
        """
        :description: 快速添加菜单
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        button_type_list = button_type_str.split(",")
        for button_Type in button_type_list:
            curr_button_type_enum = int(button_Type)
            curr_menu_info = MenuInfo()
            curr_menu_info.ButtonColor = "primary"
            curr_menu_info.ParentID = parent_id
            curr_menu_info.MenuType = 3
            curr_menu_info.IsShow = 1
            curr_menu_info.IsPower = 1
            if curr_button_type_enum == ButtonType.Add.value:
                curr_menu_info.ButtonPlace = ButtonPlace.Top.value
                curr_menu_info.CommandName = "create"
                curr_menu_info.MenuName = "新增"
                curr_menu_info.MenuIcon = "plus-circle"
            elif curr_button_type_enum == ButtonPlace.List.value:
                curr_menu_info.ButtonPlace = ButtonPlace.List.value
                curr_menu_info.CommandName = "delete"
                curr_menu_info.MenuName = "删除"
                curr_menu_info.MenuIcon = "trash-o"
                curr_menu_info.ButtonColor = "danger"
            elif curr_button_type_enum == ButtonType.Modify.value:
                curr_menu_info.ButtonPlace = ButtonPlace.List.value
                curr_menu_info.CommandName = "edit"
                curr_menu_info.MenuName = "修改"
                curr_menu_info.MenuIcon = "edit"
            elif curr_button_type_enum == ButtonType.Save.value:
                curr_menu_info.ButtonPlace = ButtonPlace.Top.value
                curr_menu_info.CommandName = "save"
                curr_menu_info.MenuName = "保存"
                curr_menu_info.MenuIcon = "save"
            elif curr_button_type_enum == ButtonType.Search.value:
                curr_menu_info.ButtonPlace = ButtonPlace.Top.value
                curr_menu_info.CommandName = "search"
                curr_menu_info.MenuName = "查询"
                curr_menu_info.MenuIcon = "search"
            elif curr_button_type_enum == ButtonType.View.value:
                curr_menu_info.ButtonPlace = ButtonPlace.List.value
                curr_menu_info.CommandName = "view"
                curr_menu_info.MenuName = "查看详细"
                curr_menu_info.ButtonColor = "info"
            elif curr_button_type_enum == ButtonType.Release.value:
                curr_menu_info.ButtonPlace = ButtonPlace.List.value
                curr_menu_info.CommandName = "release"
                curr_menu_info.MenuName = "发布"
            elif curr_button_type_enum == ButtonType.UnRelease.value:
                curr_menu_info.ButtonPlace = ButtonPlace.List.value
                curr_menu_info.CommandName = "unRelease"
                curr_menu_info.MenuName = "取消发布"
                curr_menu_info.ButtonColor = "info"
            elif curr_button_type_enum == ButtonType.Back.value:
                curr_menu_info.ButtonPlace = ButtonPlace.List.value
                curr_menu_info.CommandName = "back"
                curr_menu_info.MenuName = "返回"

            if curr_button_type_enum != ButtonType.Search.value:
                curr_menu_info.MenuName += suffix_name

            self.add(curr_menu_info)

    def add(self, menu_info):
        """
        :description: 添加方法
        :param menu_info：菜单实体
        :return: 
        :last_editors: HuangJingCan
        """
        menu_info.MenuID = UUIDHelper.get_uuid()
        self.add_entity(menu_info)
        parent_power_menu = self.get_entity_by_id(menu_info.ParentID)

        if parent_power_menu:
            parent_power_menu.HaveChild = 1
            self.update(parent_power_menu)
            menu_info.IDPath = "," + parent_power_menu.IDPath.strip(",") + "," + menu_info.MenuID + ","
            menu_info.MenuNamePath = parent_power_menu.MenuNamePath + "," + menu_info.MenuName
            menu_info.Depth = parent_power_menu.Depth + 1
            menu_info.SortIndex = int(self.get_total("ParentID=%s", params=menu_info.ParentID))

        else:
            menu_info.MenuType = 1
            menu_info.IDPath = menu_info.ParentID + "," + menu_info.MenuID + ","
            menu_info.Depth = 1
            menu_info.SortIndex = int(self.get_total("ParentID=%s", params=[menu_info.ParentID]))

        self.update(menu_info)

        return menu_info.MenuID

    def add_menu(self, menu_info):
        """
        :description: 添加菜单
        :param menu_info：菜单实体
        :return: 
        :last_editors: HuangJingCan
        """
        self.add(menu_info)
        return DictUtil.auto_mapper(MenuInfoDto(), menu_info.__dict__)

    def update(self, menu_info):
        """
        :description: 更新菜单
        :param menu_info：菜单实体
        :return: 
        :last_editors: HuangJingCan
        """
        if menu_info.MenuNamePath != "":
            menu_name_list = [i for i in menu_info.MenuNamePath.strip(",").split(",") if i != ""]
            menu_name_list.pop()
            if menu_name_list:
                menu_info.MenuNamePath = "," + ','.join(menu_name_list) + "," + menu_info.MenuName + ","
        menu_info.MenuNamePath = "," + menu_info.MenuName + "," if menu_info.MenuNamePath == "" else menu_info.MenuNamePath

        return self.update_entity(menu_info)

    def update_menu(self, menu_info):
        """
        :description: 更新菜单
        :param menu_info：菜单实体
        :return: 
        :last_editors: HuangJingCan
        """
        self.update(menu_info)
        return DictUtil.auto_mapper(MenuInfoDto(), menu_info.__dict__)

    def add_copy_menu(self, copy_menu_id, stick_menu_id):
        """
        :description: 粘贴菜单
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        menu_info_list = self.get_list(f"IDPath LIKE '%{copy_menu_id}%'")
        if menu_info_list:
            copy_menu_info = [i for i in menu_info_list if i.MenuID == copy_menu_id][0]
            copy_menu_info.MenuType = 2 if copy_menu_info.MenuType == 1 else copy_menu_info.MenuType
            copy_menu_info.MenuID = UUIDHelper.get_uuid()
            copy_menu_info.MenuName += "==复制"
            copy_menu_info.ParentID = stick_menu_id
            copy_menu_info.SortIndex = 0
            self.add(copy_menu_info)
            self.add_copy_child_menu(copy_menu_id, copy_menu_info.MenuID, menu_info_list)

    def add_copy_child_menu(self, old_parent_id, curr_parent_id, menu_info_list):
        """
        :description: 粘贴子节点
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        curr_menu_info_list = [i for i in menu_info_list if i.ParentID == old_parent_id]
        for curr_menu_info in curr_menu_info_list:
            curr_menu_id = curr_menu_info.MenuID
            curr_menu_info.MenuID = UUIDHelper.get_uuid()
            curr_menu_info.ParentID = curr_parent_id
            curr_menu_info.SortIndex = 0
            self.add(curr_menu_info)
            self.add_copy_child_menu(curr_menu_id, curr_menu_info.MenuID, [i for i in menu_info_list if i.ParentID == old_parent_id])

    def update_move(self, move_id, target_id):
        """
        :description: 移动菜单
        :param move_id：被移动的菜单id
        :param target_id：目的地菜单id
        :return: 
        :last_editors: HuangJingCan
        """
        move_menu_info = self.get_entity_by_id(move_id)
        if not move_menu_info or move_menu_info.ParentID == target_id or move_id == target_id:
            return

        old_parent_id = move_menu_info.ParentID
        id_path = move_menu_info.IDPath
        menu_name_path = move_menu_info.MenuNamePath
        depth = move_menu_info.Depth
        menu_info_list = self.get_list(f"IDPath LIKE '{id_path}%'")
        target_menu_info = self.get_entity_by_id(target_id)
        update_id_path = target_id + "," + move_id if not target_menu_info else target_menu_info.IDPath + move_id + ","
        update_name_path = "," + move_menu_info.MenuName if not target_menu_info else target_menu_info.MenuNamePath + move_menu_info.MenuName + ","
        update_depth = 1 if not target_menu_info else target_menu_info.Depth

        for power_menu in menu_info_list:
            power_menu.MenuNamePath = power_menu.MenuNamePath.replace(menu_name_path, update_name_path)
            power_menu.IDPath = power_menu.IDPath.replace(id_path, update_id_path)
            power_menu.Depth = power_menu.Depth - depth + 1 + update_depth
            if power_menu.MenuID == move_id:
                power_menu.ParentID = target_id
            self.update_entity(power_menu)

        self.update_table("HaveChild=1", "MenuID=%s", target_id)

        dict_total = self.get_total("ParentID=%s", params=old_parent_id)
        have_child = 0
        if dict_total and int(dict_total) > 0:
            have_child = 1
        self.update_table("HaveChild=%s", "MenuID=%s", [have_child, target_id])

    def update_after_before_move(self, move_id, target_id, top_field_name, condition="", is_after=True):
        """
        :description: 移动
        :param move_id：被移动的菜单id
        :param target_id：目的地菜单id
        :param top_field_name：排序字段名称
        :param condition：查询条件
        :param is_after：after是True，before是False
        :return: 
        :last_editors: HuangJingCan
        """
        move_menu_info = self.get_entity_by_id(move_id)
        target_menu_info = self.get_entity_by_id(target_id)
        if not move_menu_info or not target_menu_info:
            return
        if move_menu_info.ParentID != target_menu_info.ParentID:
            self.update_move(move_id, target_menu_info.ParentID)

        self.move_record(move_id, target_id, top_field_name, condition, is_after)

    def move_record(self, select_id, target_id, top_field_name, condition="", is_after=True):
        """
        :description: 向前或者向后移动菜单（通用方法，可移动到base_model）
        :param select_id：被移动的菜单id
        :param target_id：目的地菜单id
        :param top_field_name：排序字段名称
        :param condition：查询条件
        :param is_after：after是True，before是False
        :return: 执行行数
        :last_editors: HuangJingCan
        """
        reverse = False
        select_sort_id = 0
        primary_key = MenuInfo().get_primary_key()
        table_name = MenuInfo().__str__()
        dict_select_sort_id = self.get_dict(f"{primary_key}=%s", field=top_field_name, params=select_id)
        if dict_select_sort_id:
            select_sort_id = int(dict_select_sort_id[top_field_name])

        target_sort_id = 0
        dict_target_sort_id = self.get_dict(f"{primary_key}=%s", field=top_field_name, params=target_id)
        if dict_target_sort_id:
            target_sort_id = int(dict_target_sort_id[top_field_name])

        condition = "" if condition == "" else condition + " AND "
        if is_after:
            condition += f"{top_field_name}>{select_sort_id} AND {top_field_name}<={target_sort_id} ORDER BY {top_field_name}"
        else:
            reverse = True
            condition += f"{top_field_name}>={target_sort_id} AND {top_field_name}<{select_sort_id} ORDER BY {top_field_name}"
        dict_list = self.get_dict_list(condition)
        sort_info_list = self.get_sort_list(dict_list, top_field_name)

        if isinstance(select_id, int):
            sql = f"UPDATE {table_name} SET {top_field_name}={target_sort_id} WHERE {primary_key}={select_id};"
        else:
            sql = f"UPDATE {table_name} SET {top_field_name}={target_sort_id} WHERE {primary_key}='{select_id}';"
        sort_value = select_sort_id
        sort_info_list.sort(key=lambda x: x["sort_value"], reverse=reverse)
        for sort_info in sort_info_list:
            sort_id = sort_info["id"]
            if isinstance(select_id, int):
                sql += f"UPDATE {table_name} SET {top_field_name}={sort_value} WHERE {primary_key}={sort_id};"
            else:
                sql += f"UPDATE {table_name} SET {top_field_name}={sort_value} WHERE {primary_key}='{sort_id}';"
            sort_value = sort_info["sort_value"]

        sql_list = [i for i in sql.split(";") if i != ""]

        return self.transaction_execute(sql_list)

    def get_sort_list(self, dict_list, top_field_name):
        """
        :description: 列表加工后返回id和sort的列表
        :param dict_list：
        :param top_field_name：
        :return: 字典列表
        :last_editors: HuangJingCan
        """
        obj_list = []
        top_field_name = top_field_name.replace("`", "")
        primary_key = MenuInfo().get_primary_key()
        for dr in dict_list:
            sort_info = {}
            if dr[primary_key] != "":
                sort_info["id"] = dr[primary_key]
            if dr[top_field_name] != "":
                sort_info["sort_value"] = int(dr[top_field_name])
            obj_list.append(sort_info)
        return obj_list

    def delete(self, menu_id):
        """
        :description: 删除栏目
        :param menu_id:栏目id
        :return bool
        :last_editors: HuangJingCan
        """
        menu_info = self.get_entity_by_id(menu_id)
        if not menu_info:
            return 0
        count = self.del_entity("IDPath like '" + menu_info.IDPath + "%'")
        have_child = 1 if self.get_total("ParentID=%s", params=[menu_info.ParentID]) > 0 else 0
        self.update_table("HaveChild=%s", "ParentID=%s", [have_child, menu_info.ParentID])
        return count