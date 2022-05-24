
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class RolePowerModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(RolePowerModel, self).__init__(RolePower, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class RolePower:

    def __init__(self):
        super(RolePower, self).__init__()
        self.RolePowerID = 0  # 权限标识
        self.RoleID = ""  # 角色标识
        self.MenuID = ""  # 菜单标识
        self.CoteID = ""  # 数据ID

    @classmethod
    def get_field_list(self):
        return ['RolePowerID', 'RoleID', 'MenuID', 'CoteID']
        
    @classmethod
    def get_primary_key(self):
        return "RolePowerID"

    def __str__(self):
        return "cms_rolepower_tb"
    