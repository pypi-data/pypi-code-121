
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class FileWaterImageModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(FileWaterImageModel, self).__init__(FileWaterImage, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class FileWaterImage:

    def __init__(self):
        super(FileWaterImage, self).__init__()
        self.WaterImageID = ""  # 
        self.WaterImagePath = ""  # 水印地址
        self.WaterName = ""  # 水印名称

    @classmethod
    def get_field_list(self):
        return ['WaterImageID', 'WaterImagePath', 'WaterName']
        
    @classmethod
    def get_primary_key(self):
        return "WaterImageID"

    def __str__(self):
        return "cms_filewaterimage_tb"
    