from datetime import datetime


class Model(object):
    """通用字段"""
    # 主键 id
    id: int = None

    columns = dict()

    def __init__(self, res: dict = None, *args, **kwargs) -> None:
        '''
        构造器
        :param res:
        :param kwargs:
        '''
        self.load(res)

    def load(self, res: dict): ...

    @property
    def to_string(self) -> str: return str(self.columns)

    def equels(self, d) -> str: ...


class DownloadTaskMain(Model):
    def load(self, res: dict):
        self.columns = res
        '''
            字段 ：id
            类型 ：bigint(20) unsigned
            是否可以为空 ：NO
            默认值 ：None
            备注 ：
        '''
        self.id: int = res.get('id')

        '''
            字段 ：org_id
            类型 ：bigint(6) unsigned
            是否可以为空 ：NO
            默认值 ：None
            备注 ：
        '''
        self.org_id: int = res.get('org_id')

        '''
            字段 ：task_name
            类型 ：varchar(64)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：任务名称
        '''
        self.task_name: str = res.get('task_name')

        '''
            字段 ：platform
            类型 ：int(4)
            是否可以为空 ：NO
            默认值 ：None
            备注 ： 生成平台 ， 1 ：cfg , 2:cti , 3 : open , 4: crm 
        '''
        self.platform: int = res.get('platform')

        '''
            字段 ：type
            类型 ：int(4)
            是否可以为空 ：NO
            默认值 ：None
            备注 ：导出类型 1: 导出联系人 ， 2 ：公司对账单导出 3 ： 导出 计划item 4 ：导出 通话记录统计分析 5 ： 录音下载 6 ：信修下载 7 .通话记录加录音下载
        '''
        self.type: int = res.get('type')

        '''
            字段 ：sub_type
            类型 ：int(4)
            是否可以为空 ：NO
            默认值 ：None
            备注 ：导出子类型 导出类型下 分出来的子类型 
        '''
        self.sub_type: int = res.get('sub_type')

        '''
            字段 ：description
            类型 ：varchar(255)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：描述
        '''
        self.description: str = res.get('description')

        '''
            字段 ：data
            类型 ：varchar(1024)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：序列化字段
        '''
        self.data: str = res.get('data')

        '''
            字段 ：status
            类型 ：int(4)
            是否可以为空 ：YES
            默认值 ：0
            备注 ： 0 :任务创建中 , 1 : 文件上传中 ，2 ：文件上传完成 ,-1 :文件上传失败 3 : 任务失效  4：取消任务
        '''
        self.status: int = res.get('status')

        '''
            字段 ：notify
            类型 ：tinyint(4)
            是否可以为空 ：YES
            默认值 ：0
            备注 ：是否通知 0：否 1：是
        '''
        self.notify: int = res.get('notify')

        '''
            字段 ：remark
            类型 ：varchar(256)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：备注
        '''
        self.remark: str = res.get('remark')

        '''
            字段 ：created_by
            类型 ：bigint(20)
            是否可以为空 ：YES
            默认值 ：0
            备注 ：创建人 , agent org id 
        '''
        self.created_by: int = res.get('created_by')

        '''
            字段 ：created_time
            类型 ：timestamp(3)
            是否可以为空 ：NO
            默认值 ：CURRENT_TIMESTAMP(3)
            备注 ：创建时间
        '''
        self.created_time: datetime = res.get('created_time')

        '''
            字段 ：last_updated_time
            类型 ：timestamp(3)
            是否可以为空 ：NO
            默认值 ：CURRENT_TIMESTAMP(3)
            备注 ：最后更新时间
        '''
        self.last_updated_time: datetime = res.get('last_updated_time')


class DownloadItem(Model):
    def load(self, res: dict):
        self.columns = res
        '''
            字段 ：id
            类型 ：bigint(20) unsigned
            是否可以为空 ：NO
            默认值 ：None
            备注 ：主键 
        '''
        self.id: int = res.get('id')

        '''
            字段 ：task_id
            类型 ：bigint(20)
            是否可以为空 ：NO
            默认值 ：None
            备注 ：主任务id
        '''
        self.task_id: int = res.get('task_id')

        '''
            字段 ：org_id
            类型 ：bigint(6) unsigned
            是否可以为空 ：NO
            默认值 ：None
            备注 ： 公司ID 
        '''
        self.org_id: int = res.get('org_id')

        '''
            字段 ：type
            类型 ：int(4)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：下载类型。一般跟 task的 子类型相同 
        '''
        self.type: int = res.get('type')

        '''
            字段 ：file_name
            类型 ：varchar(256)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：文件名称
        '''
        self.file_name: str = res.get('file_name')

        '''
            字段 ：target_id
            类型 ：bigint(20)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：关联id
        '''
        self.target_id: int = res.get('target_id')

        '''
            字段 ：expire_time
            类型 ：timestamp
            是否可以为空 ：YES
            默认值 ：None
            备注 ：过期时间
        '''
        self.expire_time: datetime = res.get('expire_time')

        '''
            字段 ：download_times
            类型 ：int(2)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：下载次数
        '''
        self.download_times: int = res.get('download_times')

        '''
            字段 ：url
            类型 ：varchar(1024)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：文件下载地址
        '''
        self.url: str = res.get('url')

        '''
            字段 ：status
            类型 ：int(4)
            是否可以为空 ：YES
            默认值 ：0
            备注 ：0 :未开始 ， 1: 进行中 ，2:已完成 ，3 ：失效(针对下载次数超限) -1 :任务失败  4：取消任务
        '''
        self.status: int = res.get('status')

        '''
            字段 ：data
            类型 ：varchar(1024)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：序列化字段
        '''
        self.data: str = res.get('data')

        '''
            字段 ：remark
            类型 ：varchar(256)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：备注
        '''
        self.remark: str = res.get('remark')

        '''
            字段 ：md5_value
            类型 ：varchar(45)
            是否可以为空 ：YES
            默认值 ：None
            备注 ：文件MD5
        '''
        self.md5_value: str = res.get('md5_value')

        '''
            字段 ：created_time
            类型 ：timestamp(3)
            是否可以为空 ：NO
            默认值 ：CURRENT_TIMESTAMP(3)
            备注 ：创建时间
        '''
        self.created_time: datetime = res.get('created_time')

        '''
            字段 ：last_updated_time
            类型 ：timestamp(3)
            是否可以为空 ：NO
            默认值 ：CURRENT_TIMESTAMP(3)
            备注 ：最后更新时间
        '''
        self.last_updated_time: datetime = res.get('last_updated_time')
