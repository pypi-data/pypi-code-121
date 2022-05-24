"""
:Author: HuangJingCan
:Date: 2020-04-15 09:56:24
:LastEditTime: 2021-06-30 19:46:55
:LastEditors: HuangJingCan
:Description: 权限角色栏目相关
"""
from asq.initiators import query
from seven_studio.utils.dict import *
from seven_framework.time import *

from seven_studio.models.db_models.role.role_power_model_ex import *
from seven_studio.models.db_models.role.role_user_model import *
from seven_studio.models.db_models.role.role_info_model import *
from seven_studio.models.db_models.menu.menu_info_model_ex import *
from seven_studio.models.db_models.menu.menu_cote_model import *
from seven_studio.models.db_models.user.user_info_model_ex import *
from seven_studio.models.db_models.product.product_user_model import *
from seven_studio.models.enum import ButtonPlace
from seven_studio.models.dto_model import *


class PowerModel():
    """
    :description: 权限相关操作类
    """
    def __init__(self, db_connect_key='db_sevenstudio', is_super=False, user_id="", product_id=0):
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.is_super = is_super
        self.user_id = user_id
        self.product_id = product_id

    ROLE_POWERS = []

    def get_power_menu_list(self):
        """
        :description: 获取栏目列表
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        manage_context_key = self.db_connect_key
        menu_info_list = []
        if self.is_super:
            menu_info_list = MenuInfoModel(manage_context_key).get_list(order_by="SortIndex ASC")
        else:
            role_user_list = RoleUserModel(manage_context_key).get_list("UserID=%s", params=self.user_id)
            if len(role_user_list) == 0:
                return menu_info_list
            # self.ROLE_POWERS = RolePowerModelEx(manage_context_key).get_role_power_list([i.RoleID for i in role_user_list])
            role_power_list = RolePowerModelEx(manage_context_key).get_role_power_list([i.RoleID for i in role_user_list])
            self.ROLE_POWERS = RolePowerEx().get_list_by_role_power_list(role_power_list)
            condition = "IsPower=0"
            if len(self.ROLE_POWERS) > 0:
                condition += " OR "
                condition += f"MenuID IN ({str([i.MenuID for i in self.ROLE_POWERS]).strip('[').strip(']')})"
            menu_info_list = MenuInfoModel(manage_context_key).get_list(condition, order_by="SortIndex ASC")

        return MenuInfoEx().get_list_by_menu_list(menu_info_list)

    def get_platform_power_menu_list(self):
        """
        :description: 获取权限菜单
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        menu_info_list = self.get_power_menu_list()
        menu_item_list = []

        # 平台管理权限
        # menu_info_list_plat = [i for i in menu_info_list if i.MenuType == 1 and i.MenuID == config.get_value("menu_id_platform")]
        menu_info_list_plat = [i for i in menu_info_list if i.MenuType == 1]
        for menu_info in menu_info_list_plat:
            curr_menu_item_dto = PowerMenuInfoDto()
            curr_menu_item_dto.MenuID = menu_info.MenuID
            curr_menu_item_dto.MenuName = menu_info.MenuName
            curr_menu_item_dto.MenuIcon = menu_info.MenuIcon
            curr_menu_item_dto.ApiPath = menu_info.ApiPathValue
            curr_menu_item_dto.ViewPath = menu_info.ViewPathValue
            hidden_power_menu_list = []
            self.__get_menu_item_dto_list(curr_menu_item_dto, menu_info_list, hidden_power_menu_list)
            if menu_info.MenuCoteID > 0:
                menu_list = self.__get_power_cote_menu_item(menu_info.MenuCoteID, curr_menu_item_dto, (self.is_super or menu_info.IsPower == 0))
                # if len(menu_list) > 0:
                if menu_list:
                    curr_menu_item_dto.MenuItemDtoList = menu_list
            menu_item_list.append(curr_menu_item_dto.__dict__)
        return menu_item_list

    def __get_menu_item_dto_list(self, menu_item, child_menu_infos, hidden_power_menu_list, depth=0):
        menu_info_list = [i for i in child_menu_infos if i.ParentID == menu_item.MenuID]
        for menu_info in menu_info_list:
            if menu_info.MenuType == 3 and menu_info.IsShow == 1:
                curr_menu_button_dto = PowerButtonDto()
                curr_menu_button_dto.ID = menu_info.MenuID
                curr_menu_button_dto.Title = menu_info.MenuName
                curr_menu_button_dto.Icon = menu_info.MenuIcon
                curr_menu_button_dto.ApiPath = menu_info.ApiPathValue
                curr_menu_button_dto.ViewPath = menu_info.ViewPathValue
                curr_menu_button_dto.Path = "" if menu_info.ViewPath.strip() == "" else menu_info.RedirctPathValue
                curr_menu_button_dto.CommandName = menu_info.CommandName
                curr_menu_button_dto.CommandParms = menu_info.CommandParms
                curr_menu_button_dto.IsHidden = menu_info.IsShow == 0
                curr_menu_button_dto.ButtonPlace = menu_info.ButtonPlace
                curr_menu_button_dto.ButtonColor = menu_info.ButtonColor
                curr_menu_button_dto.ShowCondition = menu_info.ShowCondition
                menu_item.MenuButtonDtoList.append(curr_menu_button_dto.__dict__)

            child_menu_info_list = [i for i in child_menu_infos if menu_info.MenuID in i.IDPath]
            if menu_info.ViewPath.strip() != "" or len([i for i in child_menu_info_list if i.MenuType == 2]) > 0:
                curr_menu_item_dto = PowerMenuInfoDto()
                curr_menu_item_dto.MenuID = menu_info.MenuID
                curr_menu_item_dto.MenuName = menu_info.MenuName
                curr_menu_item_dto.MenuIcon = menu_info.MenuIcon
                curr_menu_item_dto.ApiPath = menu_info.ApiPathValue
                curr_menu_item_dto.ViewPath = menu_info.ViewPathValue
                curr_menu_item_dto.Path = menu_info.RoutePathValue
                curr_menu_item_dto.IsHidden = True if menu_info.MenuType == 3 else menu_info.IsShow == 0

                self.__get_menu_item_dto_list(curr_menu_item_dto, child_menu_info_list, hidden_power_menu_list, depth + 1)

                list_count = len([i for i in child_menu_info_list if i.MenuType == 3 and i.ViewPath.strip() != ""])
                if (curr_menu_item_dto.ViewPath.strip() != "" and depth == 0) or (menu_info.MenuType != 3 and list_count > 0):
                    power_menu_info_dto_curr = PowerMenuInfoDto()
                    power_menu_info_dto_curr.MenuID = menu_info.MenuChildID
                    power_menu_info_dto_curr.MenuIcon = menu_info.MenuIcon
                    power_menu_info_dto_curr.MenuName = menu_info.MenuName
                    power_menu_info_dto_curr.ApiPath = menu_info.ApiPathValue
                    power_menu_info_dto_curr.ViewPath = menu_info.ViewPathValue
                    power_menu_info_dto_curr.Path = menu_info.RoutePathValue
                    power_menu_info_dto_curr.IsHidden = True
                    curr_menu_item_dto.MenuItemDtoList.insert(0, power_menu_info_dto_curr.__dict__)

                if (menu_info.MenuCoteID > 0):
                    is_power = self.is_super or menu_info.IsPower == 0
                    self.__get_power_cote_menu_item(menu_info.MenuCoteID, curr_menu_item_dto, is_power)

                menu_item.MenuItemDtoList.append(curr_menu_item_dto.__dict__)

    def __get_power_cote_menu_item(self, coteID, curr_menu_info, is_power):
        menu_item_list = curr_menu_info.MenuItemDtoList
        curr_menu_info.MenuItemDtoList = []
        cote_menu_info_list = []
        menu_item_dto_list = []
        if coteID > 0:
            menu_cote = MenuCoteModel(self.db_connect_key).get_entity_by_id(coteID)
            if not menu_cote:
                return menu_item_dto_list
            menu_cote_list = self.__get_cote_menu_data(menu_cote)
            menu_cote_id = curr_menu_info.MenuID + "$"

            for menu_cote_item in menu_cote_list:
                if not self.__check_menu_power(is_power, curr_menu_info.MenuID, menu_cote_item[menu_cote.IDName]):
                    continue
                cote_menu_info = MenuInfo()
                cote_menu_info.MenuID = menu_cote_id + str(menu_cote_item[menu_cote.IDName])
                cote_menu_info.MenuName = menu_cote_item[menu_cote.Name]
                cote_menu_info.ParentID = menu_cote_id + str(menu_cote_item[menu_cote.ParentIDName]) if menu_cote.ParentIDName.strip() != "" else menu_cote_id + menu_cote.RootIDValue
                cote_menu_info.IDPath = menu_cote_item[menu_cote.IDPathName] if menu_cote.IDPathName.strip() != "" else ""
                cote_menu_info.TargetUrl = str(menu_cote_item[menu_cote.IDName])
                cote_menu_info.ViewPath = curr_menu_info.ViewPath
                cote_menu_info = MenuInfoEx().get_entity_by_menu_info(cote_menu_info)
                cote_menu_info_list.append(cote_menu_info.__dict__)

            if len(cote_menu_info_list) == 1:
                curr_menu_info.MenuItemDtoList = []

            for menu_info in [i for i in cote_menu_info_list if i["ParentID"] == menu_cote_id + menu_cote.RootIDValue]:
                curr_menu_item_dto = PowerMenuInfoDto()
                curr_menu_item_dto.MenuID = menu_info["MenuID"]
                curr_menu_item_dto.MenuName = menu_info["MenuName"]
                curr_menu_item_dto.ViewPath = curr_menu_info.ViewPath
                curr_menu_item_dto.Path = menu_info["RoutePathValue"]
                curr_menu_item_dto.IsHidden = len(cote_menu_info_list) == 1

                if len(cote_menu_info_list) == 1:
                    childInfo = PowerMenuInfoDto()
                    childInfo.MenuID = str(curr_menu_item_dto.MenuID) + ":child"
                    childInfo.MenuName = menu_info["MenuName"]
                    childInfo.ViewPath = curr_menu_info.ViewPath
                    childInfo.Path = menu_info["RoutePathValue"]
                    childInfo.IsHidden = True
                    curr_menu_item_dto.MenuItemDtoList.append(childInfo.__dict__)
                else:
                    curr_menu_info.Path = curr_menu_item_dto.Path

                if [i for i in cote_menu_info_list if i["ParentID"] == menu_info["MenuID"]]:
                    self.__get_child_cote_menu_list(menu_item_list, curr_menu_info.MenuButtonDtoList, curr_menu_item_dto, cote_menu_info_list, is_power)
                else:
                    curr_menu_item_dto.MenuButtonDtoList.extend(curr_menu_info.MenuButtonDtoList)
                    if len(menu_item_list) > 1:
                        curr_menu_item_dto.MenuItemDtoList.extend(self.__to_cote_menu_list(menu_item_list, menu_info["TargetUrl"], is_power))

                curr_menu_info.MenuItemDtoList.append(curr_menu_item_dto.__dict__)

    def __get_cote_menu_data(self, menu_cote):
        field_parms = f"{menu_cote.IDName},{menu_cote.Name}"
        if menu_cote.ParentIDName.strip() != "":
            field_parms += f",{menu_cote.ParentIDName}"
        if menu_cote.IDPathName.strip() != "":
            field_parms += f",{menu_cote.IDPathName}"

        condition = ""
        if menu_cote.Condtion.strip() == "":
            condition = f" ORDER BY {menu_cote.SortExpression}"
        else:
            condition = f"{menu_cote.Condtion} ORDER BY {menu_cote.SortExpression}"

        sql = f"SELECT {field_parms} FROM {menu_cote.CoteTableName}{condition}"
        # list_row = MySQLHelper(config.get_value(self.db_connect_key)).fetch_all_rows(sql)
        list_row = MySQLHelper(config.get_value(menu_cote.ConnectionStringName)).fetch_all_rows(sql)
        return list_row

    def __check_menu_power(self, is_power, menu_id, cote_id):
        is_contains = [i for i in self.ROLE_POWERS if f"{i.MenuID}${i.CoteID}".lower() == f"{menu_id}${cote_id}".lower()]
        if is_power == 0 and not is_contains:
            return False
        return True

    def __get_child_cote_menu_list(self, root_power_menu_list, button_menu_dto_list, menu_item, menu_info_list, is_super):
        for curr_menu_info in [i for i in menu_info_list if i["ParentID"] == menu_item.MenuID]:
            curr_menu_item_dto = PowerMenuInfoDto()
            curr_menu_item_dto.MenuID = curr_menu_info["MenuID"]
            curr_menu_item_dto.MenuName = curr_menu_info["MenuName"]
            curr_menu_item_dto.ViewPath = curr_menu_info["ViewPathValue"]
            curr_menu_item_dto.Path = curr_menu_info["RoutePathValue"]

            if [i for i in menu_info_list if i["ParentID"] == curr_menu_info["MenuID"]]:
                self.__get_child_cote_menu_list(root_power_menu_list, button_menu_dto_list, curr_menu_item_dto, menu_info_list, is_super)
            else:
                for curr_power_button_dto in button_menu_dto_list:
                    if is_super or [i for i in self.ROLE_POWERS if i.MenuCoteID in (curr_power_button_dto['ID'] + "$" + curr_menu_info["TargetUrl"])]:
                        curr_menu_item_dto.MenuButtonDtoList.append(curr_power_button_dto)
                curr_menu_item_dto.MenuItemDtoList.extend(self.__to_cote_menu_list(root_power_menu_list, curr_menu_info["TargetUrl"], is_super))
                menu_item.MenuItemDtoList.extend(self.__to_cote_menu_list(root_power_menu_list, curr_menu_info["TargetUrl"], is_super, True))

            menu_item.MenuItemDtoList.append(curr_menu_item_dto.__dict__)
            if len(menu_item.MenuItemDtoList) == 1:
                childInfo = PowerMenuInfoDto()
                childInfo.MenuID = curr_menu_item_dto.MenuID + ":child"
                childInfo.MenuName = curr_menu_info["MenuName"]
                childInfo.ViewPath = curr_menu_info["ViewPathValue"]
                childInfo.Path = curr_menu_info["RoutePathValue"]
                childInfo.IsHidden = True
                curr_menu_item_dto.MenuItemDtoList.append(childInfo.__dict__)

    def __to_cote_menu_list(self, menu_info_list, menu_cote_key, is_super, is_hidden=False):
        menu_item_list = menu_info_list if is_super else query(menu_info_list).where(lambda x: query(self.ROLE_POWERS).select(lambda y: y["MenuCoteID"]).contains(str(x["MenuID"]) + "$" + menu_cote_key)).to_list()
        for curr_power_menu_info_dto in menu_item_list:
            curr_power_menu_info_dto['MenuID'] = curr_power_menu_info_dto['MenuID'] + "$" + menu_cote_key
            curr_power_menu_info_dto['Path'] = "/" + curr_power_menu_info_dto['MenuID'] + curr_power_menu_info_dto['ViewPath']

            if is_hidden:
                curr_power_menu_info_dto['MenuID'] = curr_power_menu_info_dto['ViewPath'] + "hidden"

            c_menu_list = curr_power_menu_info_dto['MenuButtonDtoList']
            curr_power_menu_info_dto['MenuButtonDtoList'] = c_menu_list if is_super else query(c_menu_list).where(lambda x: query(self.ROLE_POWERS).select(lambda y: y["MenuCoteID"]).contains(str(x["ID"]) + "$" + menu_cote_key)).to_list()

            curr_power_menu_info_dto['IsHidden'] = True if curr_power_menu_info_dto['IsHidden'] else is_hidden

            if len(curr_power_menu_info_dto['MenuItemDtoList']) == 1:
                curr_power_menu_info_dto['MenuItemDtoList'][0]['MenuID'] = curr_power_menu_info_dto['MenuID'] + ":Child"
                curr_power_menu_info_dto['MenuItemDtoList'][0]['Path'] = curr_power_menu_info_dto['Path']
            elif len(curr_power_menu_info_dto['MenuItemDtoList']) > 1:
                curr_power_menu_info_dto['MenuItemDtoList'] = self.__to_cote_menu_list(curr_power_menu_info_dto['MenuItemDtoList'], menu_cote_key, is_super, is_hidden)

        return menu_item_list

    def get_menu_item_tree(self, is_load_cote_menu=True):
        """
        :description: 获取栏目树
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        menu_info_list = self.get_power_menu_list()
        menu_item_list = []
        for menu_info in [i for i in menu_info_list if i.MenuType == 1 and i.ParentID == ""]:
            curr_menu_dto = DictUtil.auto_mapper(MenuInfoDto(), menu_info.__dict__)
            self.__get_child_menu_item_list(curr_menu_dto, menu_info_list, is_load_cote_menu)
            if is_load_cote_menu and menu_info.MenuCoteID > 0:
                curr_menu_dto.ChildList = self.__get_cote_menu_item(menu_info, curr_menu_dto.ChildList)
            menu_item_list.append(curr_menu_dto.__dict__)
        return menu_item_list

    def __get_child_menu_item_list(self, menu_item, menu_infos, is_load_cote_menu):
        menu_item_list = []
        for curr_menu_info in [i for i in menu_infos if i.ParentID == menu_item.MenuID]:
            curr_menu_dto = DictUtil.auto_mapper(MenuInfoDto(), curr_menu_info.__dict__)
            id_path_list = [i for i in menu_infos if curr_menu_info.MenuID in i.IDPath]
            self.__get_child_menu_item_list(curr_menu_dto, id_path_list, is_load_cote_menu)
            if is_load_cote_menu and curr_menu_info.MenuCoteID > 0:
                curr_menu_dto.ChildList = self.__get_cote_menu_item(curr_menu_info, curr_menu_dto.ChildList)
            if curr_menu_dto.MenuCoteKey != "":
                curr_menu_dto.MenuID = curr_menu_dto.MenuID + "$" + curr_menu_dto.MenuCoteKey
            menu_item.ChildList.append(curr_menu_dto.__dict__)
            menu_item_list.append(menu_item)

        return menu_item_list

    def __get_cote_menu_item(self, curr_menu_info, child_menu_info_list):
        menu_item_list = []
        cote_menu_info_list = []
        if curr_menu_info.MenuCoteID > 0:
            menu_cote = MenuCoteModel(self.db_connect_key).get_entity_by_id(curr_menu_info.MenuCoteID)
            if not menu_cote:
                return menu_item_list

            field = f"{menu_cote.IDName},{menu_cote.Name}{(',' + menu_cote.ParentIDName if menu_cote.ParentIDName!='' else '')}{(',' + menu_cote.IDPathName if menu_cote.IDPathName!='' else '')}"
            condition = f"{(' WHERE ' + menu_cote.Condtion if menu_cote.Condtion!='' else '')}{(' ORDER BY ' + menu_cote.SortExpression if menu_cote.SortExpression!='' else '')}"
            sql = f"SELECT {field} FROM {menu_cote.CoteTableName}{condition}"
            menu_cote_table = MySQLHelper(config.get_value(menu_cote.ConnectionStringName)).fetch_all_rows(sql)

            cote_id = curr_menu_info.MenuID + "$"
            for dr in menu_cote_table:
                if not self.__check_menu_power(self.is_super, curr_menu_info.MenuID, dr[menu_cote.IDName]):
                    continue
                cote_menu_info = MenuInfo()
                cote_menu_info.MenuID = cote_id + str(dr[menu_cote.IDName])
                cote_menu_info.MenuName = dr[menu_cote.Name]
                cote_menu_info.ParentID = cote_id + str(dr[menu_cote.ParentIDName]) if menu_cote.ParentIDName != "" else cote_id + menu_cote.RootIDValue
                cote_menu_info.IDPath = dr[menu_cote.IDPathName] if menu_cote.IDPathName != "" else ""
                cote_menu_info.TargetUrl = dr[menu_cote.IDName]
                cote_menu_info_list.append(cote_menu_info.__dict__)

            for menu_info in [i for i in cote_menu_info_list if i["ParentID"] == cote_id + menu_cote.RootIDValue]:
                curr_menu_dto = DictUtil.auto_mapper(MenuInfoDto(), menu_info)
                if len([i for i in cote_menu_info_list if i["ParentID"] == curr_menu_dto.MenuID]) > 0:
                    self.__get_child_cote_menu_item_list(curr_menu_dto, cote_menu_info_list, child_menu_info_list)
                else:
                    curr_child_menu_info = []
                    for c_menu_info_dto in child_menu_info_list:
                        new_c_menu_info_dto = MenuInfoDto()
                        new_c_menu_info_dto.MenuID = c_menu_info_dto['MenuID'] + "$" + str(menu_info['TargetUrl'])
                        new_c_menu_info_dto.MenuName = c_menu_info_dto['MenuName']
                        new_c_menu_info_dto.MenuIcon = c_menu_info_dto['MenuIcon']
                        new_c_menu_info_dto.ParentID = c_menu_info_dto['MenuID']
                        new_c_menu_info_dto.IDPath = c_menu_info_dto['IDPath']
                        new_c_menu_info_dto.ChildList = c_menu_info_dto['ChildList']
                        for info in new_c_menu_info_dto.ChildList:
                            info['MenuID'] = info['MenuID'] + "$" + curr_menu_info.TargetUrl
                            info['ParentID'] = str(info['ParentID']) + "$" + str(menu_info['TargetUrl'])
                            self.__revise_child_cote_menu_list(info, menu_info['TargetUrl'])

                        curr_child_menu_info.append(new_c_menu_info_dto.__dict__)

                    curr_menu_dto.ChildList.extend(curr_child_menu_info)

                menu_item_list.append(curr_menu_dto.__dict__)

        return menu_item_list

    def __revise_child_cote_menu_list(self, menu_info_dto, cote_key):
        if menu_info_dto['ChildList']:
            for info in menu_info_dto['ChildList']:
                info['MenuID'] = str(info['MenuID']) + "$" + str(cote_key)
                info['ParentID'] = str(info['ParentID']) + "$" + str(cote_key)
                self.__revise_child_cote_menu_list(info, cote_key)

    def __get_child_cote_menu_item_list(self, menu_item, menu_infos, child_menu_info_list):
        menu_item_list = []
        for curr_menu_info in [i for i in menu_infos if i['ParentID'] == menu_item.MenuID]:
            curr_child_menu_info = []
            curr_menu_dto = DictUtil.auto_mapper(MenuInfoDto(), curr_menu_info)
            child_menu_list = [i for i in menu_infos if i['ParentID'] == curr_menu_info['MenuID']]
            if not child_menu_list:
                for c_menu_info_dto in child_menu_info_list:
                    new_c_menu_info_dto = MenuInfoDto()
                    new_c_menu_info_dto.MenuID = str(c_menu_info_dto['MenuID']) + "$" + str(curr_menu_info['TargetUrl'])
                    new_c_menu_info_dto.MenuIcon = c_menu_info_dto['MenuIcon']
                    new_c_menu_info_dto.MenuName = c_menu_info_dto['MenuName']
                    new_c_menu_info_dto.ParentID = str(curr_menu_info['MenuID']) + "$" + str(curr_menu_info['TargetUrl'])
                    new_c_menu_info_dto.IDPath = c_menu_info_dto['IDPath']
                    new_c_menu_info_dto.ChildList = c_menu_info_dto['ChildList']
                    for info in c_menu_info_dto['ChildList']:
                        info['MenuID'] = str(info['MenuID']) + "$" + str(curr_menu_info['TargetUrl'])

                    curr_child_menu_info.append(new_c_menu_info_dto.__dict__)

                curr_menu_dto.ChildList.extend(curr_child_menu_info)
            else:
                self.__get_child_cote_menu_item_list(curr_menu_dto, child_menu_list, child_menu_info_list)

            menu_item.ChildList.append(curr_menu_dto.__dict__)
            menu_item_list.append(menu_item.__dict__)

        return menu_item_list

    def get_power_menu_role_list(self, menu_id):
        """
        :description: 根据栏目id获取角色和用户
        :param menu_id：栏目id
        :return: 角色用户列表
        :last_editors: HuangJingCan
        """
        menu_role_list = []
        rowle_power_list = RolePowerModelEx(self.db_connect_key).get_list("MenuID=%s", params=menu_id)
        if rowle_power_list:
            role_info_list = RoleInfoModel(self.db_connect_key).get_list("RoleID IN ("+','.join("'"+str(item.RoleID)+"'" for item in rowle_power_list)+")")
            role_user_list = RoleUserModel(self.db_connect_key).get_list("RoleID IN ("+','.join("'"+str(item.RoleID)+"'" for item in rowle_power_list)+")")
            user_info_list = UserInfoModel(self.db_connect_key).get_list("UserID IN ("+','.join("'"+str(item.UserID)+"'" for item in role_user_list)+")")
            for curr_role_info in role_info_list:
                curr_user_info_list = [i for j in [i.UserID for i in role_user_list if i.RoleID == curr_role_info.RoleID] for i in user_info_list if j in i.UserID]
                info = {}
                info["RoleID"] = curr_role_info.RoleID
                info["RoleName"] = curr_role_info.RoleName
                info["Summary"] = curr_role_info.Summary
                curr_user_dict = []
                for user_info in curr_user_info_list:
                    curr_user_dict.append(user_info.__dict__)
                info["UserInfoList"] = curr_user_dict
                menu_role_list.append(info)
        return menu_role_list

    def remove_role_user(self, role_id, user_id):
        """
        :description: 删除用户角色
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        role_user_model = RoleUserModel(self.db_connect_key)
        if self.is_super:
            role_user_model.del_entity("RoleID=%s and UserID=%s", [role_id, user_id])
        else:
            user_info = UserInfoModel().get_entity_by_id(user_id)
            if user_info and user_info.ChiefUserID == user_id:
                role_user_model.del_entity("RoleID=%s and UserID=%s", [role_id, user_id])

    def set_role(self, role_info, user_id_list, menu_id_list, is_add=False):
        """
        :description: 设置角色
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        role_info_model = RoleInfoModel(self.db_connect_key)
        user_id_list = [i for i in user_id_list if i != ""]
        menu_id_list = [i for i in menu_id_list if i != ""]

        if is_add:
            role_info_model.add_entity(role_info)
        else:
            role_info_model.update_entity(role_info)

        if len(user_id_list) > 0:
            self.add_role_user(role_info.RoleID, user_id_list)

        if len(menu_id_list) > 0:
            self.add_role_menu(role_info.RoleID, menu_id_list)

        result = DictUtil.auto_mapper(RoleUserDto(), role_info.__dict__)
        result.RoleUserIds = user_id_list
        result.RoleMenuIds = menu_id_list
        result.IsAdd = is_add
        return result

    def add_role_user(self, role_id, user_id_list):
        role_user_mode = RoleUserModel(self.db_connect_key)
        role_user_mode.del_entity("RoleID=%s", role_id)
        if len(user_id_list) > 0:
            role_user_list = []
            for user_id in user_id_list:
                role_user = RoleUser()
                role_user.RoleUserID = CryptoHelper.md5_encrypt_int(role_id + user_id)
                role_user.UserID = user_id
                role_user.RoleID = role_id
                role_user.CreateDate = TimeHelper.get_now_format_time()
                role_user_list.append(role_user)
            role_user_mode.add_list(role_user_list, True, True)

    def add_role_menu(self, role_id, menu_id_list):
        role_power_mode = RolePowerModel(self.db_connect_key)
        role_power_mode.del_entity("RoleID=%s", role_id)
        if len(menu_id_list) > 0:
            role_power_list = []
            for menu_id in menu_id_list:
                role_power = RolePower()
                role_power.RolePowerID = CryptoHelper.md5_encrypt_int(role_id + menu_id)
                cote_menu_array = menu_id.split("$")
                if len(cote_menu_array) > 1:
                    role_power.MenuID = cote_menu_array[0]
                    role_power.CoteID = cote_menu_array[1]
                else:
                    role_power.MenuID = menu_id
                role_power.RoleID = role_id
                role_power_list.append(role_power)

            role_power_mode.add_list(role_power_list, True)

    def set_user(self, user_info, role_id_list, product_id_list, password, change_pw=False, is_add=False):
        """
        :description: 
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        user_info_model = UserInfoModel(self.db_connect_key)
        base_user_info_model = UserInfoModel(config.get_value("base_manage_context_key"))
        role_id_list = [i for i in role_id_list if i != ""]
        product_id_list = [i for i in product_id_list if i != ""]
        update_field = ["IsSuper", "Account", "Email", "LoginIP", "PasswordQuestion", "PasswordAnswer", "IsLock", "FaildLoginCount", "FaildQuestionCount", "UserName", "NickName", "JobNo", "Avatar", "LoginDate", "Phone", "PersonalitySignature", "ChiefUserID"]

        if change_pw:
            update_field.append("Password")
        if is_add:
            base_user_info = base_user_info_model.get_entity("Account=%s", params=user_info.Account)
            if base_user_info:
                user_info.UserID = base_user_info.UserID
                user_info_model.add_entity(user_info, True)
            else:
                user_info.UserID = UUIDHelper.get_uuid()
                base_user_info_model.add_entity(user_info)
                user_info_model.add_entity(user_info, True)
            if change_pw:
                user_info.Password = UserInfoModelEx().sign_password(password, user_info.UserID)
            else:
                user_info.Password = UserInfoModelEx().sign_password(config.get_value("default_password"))
            user_info_model.update_entity(user_info, field_list=update_field)
            base_user_info_model.update_table("Password=%s", "UserID=%s", params=[user_info.Password, user_info.UserID])
        else:
            if change_pw:
                user_info.Password = UserInfoModelEx().sign_password(password, user_info.UserID)
            user_info_model.update_entity(user_info, field_list=update_field)
            base_user_info_model.update_table("Password=%s", "UserID=%s", params=[user_info.Password, user_info.UserID])

        if len(role_id_list) > 0:
            self.add_user_role(user_info.UserID, role_id_list)

        if len(product_id_list) > 0:
            self.add_product_user(user_info.UserID, product_id_list)

        self.set_base_user(user_info)

        result = DictUtil.auto_mapper(UserRoleDto(), user_info.__dict__)
        result.IsAdd = is_add
        return result

    def add_user_role(self, user_id, role_id_list):
        """
        :description: 添加用户角色
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        role_user_model = RoleUserModel(self.db_connect_key)
        role_user_model.del_entity("UserID=%s", user_id)
        if len(role_id_list) > 0:
            role_user_list = []
            for role_id in role_id_list:
                role_user = RoleUser()
                role_user.RoleUserID = CryptoHelper.md5_encrypt_int(role_id + user_id)
                role_user.UserID = user_id
                role_user.RoleID = role_id
                role_user.CreateDate = TimeHelper.get_now_format_time()
                role_user_list.append(role_user)
            role_user_model.add_list(role_user_list, True, True)

    def add_product_user(self, user_id, product_id_list):
        """
        :description: 添加产品用户
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        product_user_model = ProductUserModel(config.get_value("base_manage_context_key"))
        product_user_model.del_entity("UserID=%s", user_id)
        if len(product_id_list) > 0:
            product_user_list = []
            for product_id in product_id_list:
                product_user = ProductUser()
                product_user.UserID = user_id
                product_user.ProductID = product_id
                product_user_list.append(product_user)
            product_user_model.add_list(product_user_list, True, True)

    def set_base_user(self, user_info):
        """
        :description: 子产品将用户同步回主库之中
        :param {type} 
        :return: 
        :last_editors: HuangJingCan
        """
        if self.product_id > 0:
            base_user_info_model = UserInfoModel(config.get_value("base_manage_context_key"), "")
            base_product_user_model = ProductUserModel(config.get_value("base_manage_context_key"), "")

            base_product_user = base_product_user_model.get_entity("ProductID=%s and UserID=%s", params=[self.product_id, user_info.UserID])

            if not base_product_user:
                product_user = ProductUser()
                product_user.ProductID = self.product_id
                product_user.UserID = user_info.UserID
                base_product_user_model.add_entity(product_user)
                base_user_info_model.add_entity(user_info, True)
            else:
                base_user_info_model.update_entity(user_info, "Password")

    def export_sql(self, menu_id, mode=3):
        """
        :description: 导出sql语句
        :param menu_id：栏目id
        :param mode：模式类型（1-新增，2-更新，3-同步）
        :return: str
        :last_editors: HuangJingCan
        """
        sql = ""
        menu_info_model = MenuInfoModel(self.db_connect_key)
        menu_info = menu_info_model.get_entity_by_id(menu_id)

        if menu_info:
            model_list = menu_info_model.get_list(f"IDPath like '{menu_info.IDPath}%'")
            if mode == 1:
                sql = menu_info_model.build_add_sql(model_list, True)
            elif mode == 2:
                sql = menu_info_model.build_update_sql(model_list)
            else:
                sql = menu_info_model.build_data_sql(model_list)

        return sql

    def remove_user(self, curr_user_id, user_id):
        """
        :description: 删除用户
        :param {*}
        :return {*}
        :last_editors: HuangJingCan
        """
        user_info_model = UserInfoModel(self.db_connect_key)

        if self.is_super:
            user_info_model.del_entity("UserID=%s", user_id)
        else:
            user_info = user_info_model.get_entity_by_id(user_id)
            if user_info and user_info.ChiefUserID == curr_user_id:
                user_info_model.del_entity("UserID=%s", user_id)

    def copy_user_role(self, copy_user_id, user_id):
        """
        :description: 复制权限
        :param {*}
        :return {*}
        :last_editors: HuangJingCan
        """
        role_id_list = RoleUserModel(self.db_connect_key).get_list("UserID=%s", params=copy_user_id)
        role_id_list = [i.RoleID for i in role_id_list if i != ""]
        if len(role_id_list) > 0:
            self.add_user_role(user_id, role_id_list)