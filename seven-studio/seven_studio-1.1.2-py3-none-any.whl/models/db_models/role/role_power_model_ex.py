"""
:Author: HuangJingCan
:Date: 2020-03-24 19:48:05
:LastEditTime: 2020-04-15 10:08:00
:LastEditors: HuangJingCan
:Description: 角色权限扩展类
"""
from seven_studio.models.db_models.role.role_power_model import *


class RolePowerEx(RolePower):
    def get_list_by_role_power_list(self, role_power_list):
        for role_power in role_power_list:
            role_power = self.get_entity_by_role_power(role_power)
        return role_power_list

    def get_entity_by_role_power(self, role_power):
        role_power.MenuCoteID = role_power.MenuID + "$" + role_power.CoteID if role_power.CoteID.strip() != "" else role_power.MenuID
        return role_power


class RolePowerModelEx(RolePowerModel):
    def get_role_power_list(self, rowid_list):
        if not rowid_list or len(rowid_list) == 0:
            return []
        rowid_list_str = str(rowid_list).strip('[').strip(']')
        return self.get_list(f"RoleID IN({rowid_list_str})")