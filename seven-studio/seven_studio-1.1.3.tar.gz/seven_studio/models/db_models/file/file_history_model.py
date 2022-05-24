
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class FileHistoryModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(FileHistoryModel, self).__init__(FileHistory, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class FileHistory:

    def __init__(self):
        super(FileHistory, self).__init__()
        self.FileHistoryID = 0  # 文件上传历史记录
        self.FileResourceID = ""  # 文件资源标识
        self.FileRestrictID = ""  # 限制码标识
        self.FileStoragePathID = ""  # 存储标识
        self.FileType = 0  # 1文件2图片3flash4mid
        self.FileTitle = ""  # 文件标题
        self.FileUrl = ""  # 文件路经
        self.FileStatus = 0  # 状态1正常
        self.CreateDate = "1900-01-01 00:00:00"  # 创建时间
        self.CreateUserID = 0  # 上传用户标识

    @classmethod
    def get_field_list(self):
        return ['FileHistoryID', 'FileResourceID', 'FileRestrictID', 'FileStoragePathID', 'FileType', 'FileTitle', 'FileUrl', 'FileStatus', 'CreateDate', 'CreateUserID']
        
    @classmethod
    def get_primary_key(self):
        return "FileHistoryID"

    def __str__(self):
        return "cms_filehistory_tb"
    