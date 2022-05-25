from enum import Enum

class M3U8_STATUS(Enum):
    SUCCESS= 1
    ERROR= 0
    WAIT= 2 # 等待
    TYPE_ERROR= 1000 #文件类型错误
    GET_M3U8_PLAYLIST= 1001