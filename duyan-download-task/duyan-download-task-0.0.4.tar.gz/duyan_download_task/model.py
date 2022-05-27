from datetime import datetime


class Column:
    def __init__(self, field_name):
        self.field_name = field_name
        self.instance_field_name = f'_{self.field_name}'

    def __set__(self, instance, value):
        setattr(instance, self.instance_field_name, value)

    def __get__(self, instance, owner):
        if hasattr(instance, self.instance_field_name):
            return getattr(instance, self.instance_field_name)
        return None


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
        if res:
            self.load(res)

    def load(self, res: dict): ...

    @property
    def to_string(self) -> str: return str(self.columns)

    def equels(self, d) -> str: ...


class DownloadTaskMain(Model):
    id = Column('id')
    org_id = Column('org_id')
    task_name = Column('task_name')
    platform = Column('platform')
    type = Column('type')
    sub_type = Column('sub_type')
    description = Column('description')
    data = Column('data')
    status = Column('status')
    notify = Column('notify')
    remark = Column('remark')
    created_by = Column('created_by')
    created_time = Column('created_time')
    last_updated_time = Column('last_updated_time')

    def load(self, res: dict):
        self.columns = res
        self.id: int = res.get('id')
        self.org_id: int = res.get('org_id')
        self.task_name: str = res.get('task_name')
        self.platform: int = res.get('platform')
        self.type: int = res.get('type')
        self.sub_type: int = res.get('sub_type')
        self.description: str = res.get('description')
        self.data: str = res.get('data')
        self.status: int = res.get('status')
        self.notify: int = res.get('notify')
        self.remark: str = res.get('remark')
        self.created_by: int = res.get('created_by')
        self.created_time: datetime = res.get('created_time')
        self.last_updated_time: datetime = res.get('last_updated_time')


class DownloadItem(Model):
    id = Column('id')
    task_id = Column('task_id')
    org_id = Column('org_id')
    type = Column('type')
    file_name = Column('file_name')
    target_id = Column('target_id')
    expire_time = Column('expire_time')
    url = Column('url')
    status = Column('status')
    data = Column('data')
    remark = Column('remark')
    md5_value = Column('md5_value')
    created_time = Column('created_time')
    last_updated_time = Column('last_updated_time')

    def load(self, res: dict):
        self.columns = res
        self.id: int = res.get('id')
        self.task_id: int = res.get('task_id')
        self.org_id: int = res.get('org_id')
        self.type: int = res.get('type')
        self.file_name: str = res.get('file_name')
        self.target_id: int = res.get('target_id')
        self.expire_time: datetime = res.get('expire_time')
        self.download_times: int = res.get('download_times')
        self.url: str = res.get('url')
        self.status: int = res.get('status')
        self.data: str = res.get('data')
        self.remark: str = res.get('remark')
        self.md5_value: str = res.get('md5_value')
        self.created_time: datetime = res.get('created_time')
        self.last_updated_time: datetime = res.get('last_updated_time')
