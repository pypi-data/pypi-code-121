
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class MenuInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(MenuInfoModel, self).__init__(MenuInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class MenuInfo:

    def __init__(self):
        super(MenuInfo, self).__init__()
        self.MenuID = ""  # 菜单标识
        self.MenuName = ""  # 菜单名称
        self.ParentID = ""  # 父标识
        self.IDPath = ""  # ID路经
        self.MenuNamePath = ""  # 菜单路径
        self.Depth = 0  # 深度
        self.HaveChild = 0  # 是否有子结点
        self.SortIndex = 0  # 排序
        self.ApiPath = ""  # 接口地址
        self.ViewPath = ""  # 视图地址
        self.TargetUrl = ""  # 跳转地址
        self.IsShow = 0  # 是否显示0不显示1显示
        self.IsPower = 0  # 是否授权0不1是
        self.MenuIcon = ""  # 图标地址
        self.ButtonType = 0  # 按钮类型0无1新增2修改3删除4保存5返回6查询7查看
        self.ButtonPlace = 0  # 1顶部2列表3底部
        self.CommandName = ""  # 菜单命令
        self.CommandParms = ""  # 菜单参数
        self.MenuType = 0  # 菜单类型
        self.ShowCondition = ""  # 菜单显示条件
        self.ButtonColor = ""  # 按钮颜色
        self.MenuCoteID = 0  # 栏目数据ID
        self.MenuCoteKey = ""  # 栏目标识

    @classmethod
    def get_field_list(self):
        return ['MenuID', 'MenuName', 'ParentID', 'IDPath', 'MenuNamePath', 'Depth', 'HaveChild', 'SortIndex', 'ApiPath', 'ViewPath', 'TargetUrl', 'IsShow', 'IsPower', 'MenuIcon', 'ButtonType', 'ButtonPlace', 'CommandName', 'CommandParms', 'MenuType', 'ShowCondition', 'ButtonColor', 'MenuCoteID', 'MenuCoteKey']
        
    @classmethod
    def get_primary_key(self):
        return "MenuID"

    def __str__(self):
        return "cms_menuinfo_tb"
    