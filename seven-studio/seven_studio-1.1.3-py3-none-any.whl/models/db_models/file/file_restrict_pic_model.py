
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class FileRestrictPicModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(FileRestrictPicModel, self).__init__(FileRestrictPic, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class FileRestrictPic:

    def __init__(self):
        super(FileRestrictPic, self).__init__()
        self.SystemFilePicID = ""  # 文件系统图片标识
        self.FileRestrictID = ""  # 存储路经标识
        self.SortIndex = 0  # 创建排序号
        self.IsCreateWaterMark = 0  # 是否创建水印
        self.WatermarkText = ""  # 水印文字
        self.HorizontalAlign = 0  # 水平位置
        self.VerticalAlign = 0  # 垂直位置
        self.ImageWidth = 0  # 图片宽度
        self.ImageHeight = 0  # 图片高度
        self.WatermarkType = 0  # 水印类型
        self.WaterImageID = ""  # 水印图标

    @classmethod
    def get_field_list(self):
        return ['SystemFilePicID', 'FileRestrictID', 'SortIndex', 'IsCreateWaterMark', 'WatermarkText', 'HorizontalAlign', 'VerticalAlign', 'ImageWidth', 'ImageHeight', 'WatermarkType', 'WaterImageID']
        
    @classmethod
    def get_primary_key(self):
        return "SystemFilePicID"

    def __str__(self):
        return "cms_filerestrictpic_tb"
    