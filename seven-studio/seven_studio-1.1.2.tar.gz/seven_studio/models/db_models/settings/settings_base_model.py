
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class SettingsBaseModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(SettingsBaseModel, self).__init__(SettingsBase, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class SettingsBase:

    def __init__(self):
        super(SettingsBase, self).__init__()
        self.id = 0  # 自增id
        self.login_background = ""  # 登录页背景图
        self.login_logo = ""  # 登录页logo
        self.banner_logo = ""  # 首页顶部logo
        self.title = ""  # 标题

    @classmethod
    def get_field_list(self):
        return ['id', 'login_background', 'login_logo', 'banner_logo', 'title']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "cms_settings_base_tb"
    