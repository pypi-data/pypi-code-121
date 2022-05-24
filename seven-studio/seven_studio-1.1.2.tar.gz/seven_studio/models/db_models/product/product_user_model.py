
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ProductUserModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(ProductUserModel, self).__init__(ProductUser, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class ProductUser:

    def __init__(self):
        super(ProductUser, self).__init__()
        self.ProductUserID = 0  # ProductUserID
        self.ProductID = 0  # 产品ID
        self.UserID = ""  # 用户ID

    @classmethod
    def get_field_list(self):
        return ['ProductUserID', 'ProductID', 'UserID']
        
    @classmethod
    def get_primary_key(self):
        return "ProductUserID"

    def __str__(self):
        return "cms_productuser_tb"
    