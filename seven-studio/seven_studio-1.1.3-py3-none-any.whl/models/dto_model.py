# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-10-20 10:15:03
:LastEditTime: 2020-12-09 14:45:37
:LastEditors: ChenXiaolei
:Description: 自定义实体
"""

from seven_studio.models.enum import ButtonPlace


class PowerButtonDto():
    """
    :description: 权限按钮
    """
    def __init__(self):
        self.ID = ""
        self.Title = ""
        self.Icon = ""
        self.ViewPath = ""
        self.ApiPath = ""
        self.Path = ""
        self.CommandName = ""
        self.CommandParms = ""
        self.ShowCondition = ""
        self.ButtonColor = ""
        self.ButtonPlace = ButtonPlace.Top


class PowerMenuInfoDto():
    """
    :description: 权限栏目
    """
    def __init__(self):
        self.MenuID = ""
        self.MenuIcon = ""
        self.MenuName = ""
        self.ViewPath = ""
        self.ApiPath = ""
        self.Path = ""
        self.IsHidden = False
        self.MenuItemDtoList = []
        self.MenuButtonDtoList = []


class RoleUserDto():
    """
    :description: 角色用户
    """
    def __init__(self):
        self.RoleID = ""
        self.RoleName = ""
        self.Summary = ""
        self.ModifyDate = ""
        self.ModifyUser = ""
        self.RoleUserIds = []
        self.RoleMenuIds = []
        self.IsAdd=True

    @classmethod
    def get_field_list(self):
        return ['RoleID', 'RoleName', 'Summary', 'ModifyDate', 'ModifyUser', 'RoleUserIds', 'RoleMenuIds', 'IsAdd']


class UserRoleDto():
    """
    :description: 用户角色
    """
    def __init__(self):
        self.UserID = ""
        self.IsSuper = 0
        self.Account = ""
        self.Email = ""
        self.Phone = ""
        self.UserName = ""
        self.NickName = ""
        self.JobNo = ""
        self.Avatar = ""
        self.IsLock = 0
        self.FaildLoginCount = 0
        self.ChiefUserName = ""
        self.LoginDate = ""
        self.UserRoleIds = []
        self.UserProductIds = []
        self.IsAdd = True

    @classmethod
    def get_field_list(self):
        return ['UserID', 'IsSuper', 'Account', 'Email', 'Phone', 'UserName', 'NickName', 'JobNo', 'Avatar', 'IsLock', 'FaildLoginCount', 'ChiefUserName', 'LoginDate', 'UserRoleIds', 'UserProductIds', 'IsAdd']


class LogAppDto():
    """
    :description: 日志
    """
    def __init__(self):
        self.AppID = 0
        self.AppCode = ""
        self.AppName = ""
        self.ParentID = 0
        self.IDPath = ""
        self.ErrorCount = 0
        self.FatalCount = 0
        self.NoticePhone = ""
        self.NoticeInterval = 0
        self.IsNotice = 0
        self.LogStoreInfo = ""
        self.NoticeCheckInfo = ""
        self.ChildList = []

    @classmethod
    def get_field_list(self):
        return ['AppID', 'AppCode', 'AppName', 'ParentID', 'IDPath', 'ErrorCount', 'FatalCount', 'NoticePhone', 'NoticeInterval', 'IsNotice', 'LogStoreInfo', 'NoticeCheckInfo', 'ChildList']
