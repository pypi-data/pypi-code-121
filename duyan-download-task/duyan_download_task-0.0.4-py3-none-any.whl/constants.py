from enum import IntEnum

UTF8 = 'UTF-8'
TASK_INFO_KEY = 'DOWNLOAD_TASK_INFO'
DEFAULT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class TaskStatus(IntEnum):
    FAIL = -1  # 任务失败
    READY = 0  # 任务创建中
    PROCESSING = 1  # 文件上传中
    VALID = 2  # 文件上传完成
    EXCEED = 3  # 任务失效
    CANCEL = 4  # 取消


class ItemStatus(IntEnum):
    FAIL = -1  # 任务失败
    READY = 0  # 未开始
    PROCESSING = 1  # 进行中
    VALID = 2  # 已完成
    EXCEED = 3  # 失效(针对下载次数超限)
