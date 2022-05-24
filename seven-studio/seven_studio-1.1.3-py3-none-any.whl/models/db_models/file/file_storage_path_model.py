
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class FileStoragePathModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(FileStoragePathModel, self).__init__(FileStoragePath, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class FileStoragePath:

    def __init__(self):
        super(FileStoragePath, self).__init__()
        self.FileStoragePathID = ""  # 存储标识
        self.StoragePathName = ""  # 存储名称
        self.StorageTypeID = 0  # 存储类型1本地存储2FTP3文件系统
        self.VirtualName = ""  # 虚目录
        self.StoragePath = ""  # 存储地址
        self.IPAddress = ""  # IP
        self.Account = ""  # 帐号
        self.Password = ""  # 密码
        self.Port = ""  # 端口
        self.StorageConfig = ""  # 配置文件

    @classmethod
    def get_field_list(self):
        return ['FileStoragePathID', 'StoragePathName', 'StorageTypeID', 'VirtualName', 'StoragePath', 'IPAddress', 'Account', 'Password', 'Port', 'StorageConfig']
        
    @classmethod
    def get_primary_key(self):
        return "FileStoragePathID"

    def __str__(self):
        return "cms_filestoragepath_tb"
    