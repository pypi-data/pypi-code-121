
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class UserLoginModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(UserLoginModel, self).__init__(UserLogin, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class UserLogin:

    def __init__(self):
        super(UserLogin, self).__init__()
        self.UserID = ""  # 用户ID
        self.UserIDMD5 = ""  # 用户IDMD5
        self.UserToken = ""  # UserToken
        self.ExpireTime = "1900-01-01 00:00:00"  # 过期时间

    @classmethod
    def get_field_list(self):
        return ['UserID', 'UserIDMD5', 'UserToken', 'ExpireTime']
        
    @classmethod
    def get_primary_key(self):
        return "UserID"

    def __str__(self):
        return "cms_userlogin_tb"
    