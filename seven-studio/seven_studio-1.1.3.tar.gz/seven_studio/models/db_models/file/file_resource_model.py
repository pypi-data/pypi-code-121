
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class FileResourceModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(FileResourceModel, self).__init__(FileResource, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class FileResource:

    def __init__(self):
        super(FileResource, self).__init__()
        self.FileResourceID = ""  # 文件资源标识
        self.FileResourceName = ""  # 文件资源名称
        self.FileResourceCode = ""  # 文件资源代码
        self.CreateDate = "1900-01-01 00:00:00"  # 创建时间

    @classmethod
    def get_field_list(self):
        return ['FileResourceID', 'FileResourceName', 'FileResourceCode', 'CreateDate']
        
    @classmethod
    def get_primary_key(self):
        return "FileResourceID"

    def __str__(self):
        return "cms_fileresource_tb"
    