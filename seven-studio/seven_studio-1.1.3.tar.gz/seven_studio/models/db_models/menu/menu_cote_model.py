
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class MenuCoteModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(MenuCoteModel, self).__init__(MenuCote, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class MenuCote:

    def __init__(self):
        super(MenuCote, self).__init__()
        self.MenuCoteID = 0  # 
        self.CoteTitle = ""  # 栏目名称
        self.CoteTableName = ""  # 栏目表名
        self.IDName = ""  # 主键名
        self.Name = ""  # 显示名称
        self.ParentIDName = ""  # 父节点标识
        self.IDPathName = ""  # ID路经名称
        self.ConnectionStringName = ""  # 链接字符串
        self.RootIDValue = ""  # 根节点ID值
        self.IDDataType = 0  # ID类型1整型2字符串
        self.IsParentUrl = 0  # 是否父节点链接
        self.SortExpression = ""  # 排序
        self.Condtion = ""  # 条件

    @classmethod
    def get_field_list(self):
        return ['MenuCoteID', 'CoteTitle', 'CoteTableName', 'IDName', 'Name', 'ParentIDName', 'IDPathName', 'ConnectionStringName', 'RootIDValue', 'IDDataType', 'IsParentUrl', 'SortExpression', 'Condtion']
        
    @classmethod
    def get_primary_key(self):
        return "MenuCoteID"

    def __str__(self):
        return "cms_menucote_tb"
    