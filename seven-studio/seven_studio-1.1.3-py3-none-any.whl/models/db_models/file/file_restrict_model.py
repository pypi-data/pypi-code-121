
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class FileRestrictModel(BaseModel):
    def __init__(self, db_connect_key='db_sevenstudio', sub_table=None, db_transaction=None):
        super(FileRestrictModel, self).__init__(FileRestrict, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction

    #方法扩展请继承此类
    
class FileRestrict:

    def __init__(self):
        super(FileRestrict, self).__init__()
        self.FileRestrictID = ""  # 文件限制标识
        self.FileStoragePathID = ""  # 存储路经标识
        self.FileResourceID = ""  # 文件资源标识
        self.AccessModeCodeType = 0  # 文件访问方式
        self.PathFormatCodeType = 0  # 目录存储格式
        self.ResourceCode = ""  # 资源代码
        self.RestrictName = ""  # 限制名称
        self.RestrictCode = ""  # 限制码
        self.FileType = 0  # 1文件2图片3flash4mid
        self.FileExtension = ""  # 文件扩展名
        self.FileMaxSize = 0  # 大小限制单位(K)0不限制
        self.IsReturnSize = 0  # 是否返回尺寸
        self.IsMd5 = 0  # 是否Md5
        self.IsHistory = 0  # 是否记录文件记录
        self.IsWaterMark = 0  # 是否创建水印
        self.IsFormatJpeg = 0  # 是否格式化成Jpeg
        self.WatermarkText = ""  # 水印文字
        self.HorizontalAlign = 0  # 水平位置
        self.VerticalAlign = 0  # 垂直位置
        self.ImageWidth = 0  # 图片宽度
        self.ImageHeight = 0  # 图片高度
        self.QualityValue = 0  # 质量压缩
        self.WatermarkType = 0  # 水印类型
        self.WaterImageID = ""  # 水印标识

    @classmethod
    def get_field_list(self):
        return ['FileRestrictID', 'FileStoragePathID', 'FileResourceID', 'AccessModeCodeType', 'PathFormatCodeType', 'ResourceCode', 'RestrictName', 'RestrictCode', 'FileType', 'FileExtension', 'FileMaxSize', 'IsReturnSize', 'IsMd5', 'IsHistory', 'IsWaterMark', 'IsFormatJpeg', 'WatermarkText', 'HorizontalAlign', 'VerticalAlign', 'ImageWidth', 'ImageHeight', 'QualityValue', 'WatermarkType', 'WaterImageID']
        
    @classmethod
    def get_primary_key(self):
        return "FileRestrictID"

    def __str__(self):
        return "cms_filerestrict_tb"
    