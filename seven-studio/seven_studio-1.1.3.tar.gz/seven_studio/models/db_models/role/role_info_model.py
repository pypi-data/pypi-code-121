
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class RoleInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(RoleInfoModel, self).__init__(RoleInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class RoleInfo:

    def __init__(self):
        super(RoleInfo, self).__init__()
        self.RoleID = ""  # 角色标识
        self.RoleName = ""  # 角色名称
        self.Summary = ""  # 简介
        self.ModifyDate = "1900-01-01 00:00:00"  # 修改时间
        self.ModifyUserID = ""  # 修改人
        self.ChiefUserID = ""  # 直属用户ID

    @classmethod
    def get_field_list(self):
        return ['RoleID', 'RoleName', 'Summary', 'ModifyDate', 'ModifyUserID', 'ChiefUserID']
        
    @classmethod
    def get_primary_key(self):
        return "RoleID"

    def __str__(self):
        return "cms_roleinfo_tb"
    