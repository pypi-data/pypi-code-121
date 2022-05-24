
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class RoleUserModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(RoleUserModel, self).__init__(RoleUser, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class RoleUser:

    def __init__(self):
        super(RoleUser, self).__init__()
        self.RoleUserID = 0  # 权限标识
        self.RoleID = ""  # 角色标识
        self.UserID = ""  # 用户标识
        self.CreateDate = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['RoleUserID', 'RoleID', 'UserID', 'CreateDate']
        
    @classmethod
    def get_primary_key(self):
        return "RoleUserID"

    def __str__(self):
        return "cms_roleuser_tb"
    