# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-16 14:38:22
:LastEditTime: 2022-03-07 14:05:19
:LastEditors: ChenXiaolei
:Description: 内容管理平台基础路由
"""

# 框架引用
from .handlers.system import *
from seven_framework.web_tornado.monitor import *

def seven_studio_route():
    return [
        (r"/monitor", MonitorHandler),
        # 登陆、注销
        (r"/Core/GetGeetestCode", core.GeetestCodeHandler),
        (r"/power/loginPlatform", core.LoginPlatformHandler),
        (r"/power/logout", core.LogoutHandler),
        (r"/core/uploadfiles", core.UploadFilesHandler),
        # 用户、角色
        (r"/power/GetUserInfo", power.GetUserInfoHandler),
        (r"/power/FocusPassword", power.FocusPasswordHandler),
        (r"/power/FocusChangeUserPw", power.FocusChangeUserPwHandler),
        (r"/power/ChangeCurrUserPw", power.ChangeCurrUserPwHandler),
        (r"/Power/SaveUser", power.SaveUserHandler),
        (r"/Power/SaveCurrUser", power.SaveCurrUserHandler),
        (r"/Power/GetUserList", power.GetUserListHandler),
        (r"/Power/GetUserProductList", power.GetUserProductListHandler),
        (r"/Power/GetRoleList", power.GetRoleListHandler),
        (r"/Power/GetUserRoleList", power.GetUserRoleListHandler),
        (r"/Power/GetRoleUserList", power.GetRoleUserListHandler),
        (r"/Power/SaveRole", power.SaveRoleHandler),
        (r"/Power/RemoveRoleUser", power.RemoveRoleUserHandler),
        (r"/Power/DeleteRole", power.DeleteRoleHandler),
        (r"/Power/DeleteUser", power.DeleteUserHandler),
        (r"/Power/ModifyUserStatus", power.ModifyUserStatusHandler),
        (r"/Power/CopyUserRole", power.CopyUserRoleHandler),
        (r"/Power/RemoveUserAllRole", power.RemoveUserAllRoleHandler),
        (r"/Power/ResetUserPassword", power.ResetUserPasswordHandler),
        (r"/Power/ResetUserFaildLoginCount",
         power.ResetUserFaildLoginCountHandler),
        # 产品管理
        (r"/Power/GetProductList", product.GetProductListHandler),
        (r"/Power/GetAllProductList", product.GetAllProductListHandler),
        (r"/Power/SaveProduct", product.SaveProductHandler),
        (r"/Power/DeleteProduct", product.DeleteProductHandler),
        # 文件管理
        (r"/File/GetStoragePathList", file.GetStoragePathListHandler),
        (r"/File/GetResourceList", file.GetResourceListHandler),
        (r"/File/GetRestrictList", file.GetRestrictListHandler),
        (r"/File/GetWaterImageList", file.GetWaterImageListHandler),
        (r"/File/GetHistoryList", file.GetHistoryListHandler),
        (r"/File/GetResourceInfo", file.GetResourceInfoHandler),
        (r"/File/GetStoragePathData", file.GetStoragePathDataHandler),
        (r"/File/GetWaterImageData", file.GetWaterImageDataHandler),
        (r"/File/SaveStoragePath", file.SaveStoragePathHandler),
        (r"/File/DeleteStoragePath", file.DeleteStoragePathHandler),
        (r"/File/SaveResource", file.SaveResourceHandler),
        (r"/File/DeleteResource", file.DeleteResourceHandler),
        (r"/File/SaveRestrict", file.SaveRestrictHandler),
        (r"/File/DeleteRestrict", file.DeleteRestrictHandler),
        (r"/File/SaveWaterImage", file.SaveWaterImageHandler),
        (r"/File/DeleteWaterImage", file.DeleteWaterImageHandler),
        (r"/File/DeleteHistory", file.DeleteHistoryHandler),
        # 菜单
        (r"/power/PowerPlatformMenu", menu.PowerPlatformMenuHandler),
        (r"/Power/GetMenuCoteSelect", menu.MenuCoteSelectHandler),
        (r"/Power/GetMenuCoteList", menu.MenuCoteListHandler),
        (r"/Power/PowerMenuTree", menu.PowerMenuTreeHandler),
        (r"/Power/MenuPowerInfo", menu.MenuPowerInfoHandler),
        (r"/Power/MenuTree", menu.MenuTreeHandler),
        (r"/Power/SaveFastMenu", menu.AddFastMenuHandler),
        (r"/Power/DeleteMenu", menu.DeleteMenuHandler),
        (r"/Power/SaveMenu", menu.SaveMenuHandler),
        (r"/Power/SaveCopyMenu", menu.SaveCopyMenuHandler),
        (r"/Power/MoveMenu", menu.MoveMenuHandler),
        (r"/Power/SaveMenuCote", menu.SaveMenuCoteHandler),
        (r"/Power/DeleteMenuCote", menu.DeleteMenuCoteHandler),
        (r"/Power/SyncSql", menu.SyncSqlHandler),
        (r"/Power/InsertSql", menu.InsertSqlHandler),
        (r"/Power/UpdateSql", menu.UpdateSqlHandler),
        # 配置
        (r"/settings/base", settings.BaseSettingsHandler),
    ]
