
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ProductInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(ProductInfoModel, self).__init__(ProductInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class ProductInfo:

    def __init__(self):
        super(ProductInfo, self).__init__()
        self.ProductID = 0  # 产品ID
        self.ProductName = ""  # 产品名称
        self.ProductSubName = ""  # 产品简称
        self.ManageUrl = ""  # 业务地址
        self.PowerUrl = ""  # 权限地址
        self.Summary = ""  # 说明
        self.ImageUrl = ""  # 图片地址
        self.SuperID = ""  # 超管ID
        self.FileContextKey = ""  # 文件上下文配置
        self.LogContextKey = ""  # 日志上下文配置
        self.PlugWorkContextKey = ""  # 作业上下文配置
        self.ManageContextKey = ""  # 权限上下文配置
        self.IsRelease = 0  # 是否发布
        self.IsBrank = 0  # 是否新页面打开

    @classmethod
    def get_field_list(self):
        return ['ProductID', 'ProductName', 'ProductSubName', 'ManageUrl', 'PowerUrl', 'Summary', 'ImageUrl', 'SuperID', 'FileContextKey', 'LogContextKey', 'PlugWorkContextKey', 'ManageContextKey', 'IsRelease', 'IsBrank']
        
    @classmethod
    def get_primary_key(self):
        return "ProductID"

    def __str__(self):
        return "cms_productinfo_tb"
    