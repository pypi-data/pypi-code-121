import datetime
import json

from duyan_download_task import DownloadTaskBase, SubTypeInfo
from duyan_download_task.constants import ItemStatus
from duyan_download_task.model import DownloadTaskMain, DownloadItem


class DemoTask(DownloadTaskBase):
    task_info = SubTypeInfo(task_name='DemoTask', type=10, sub_type=15, queue_key='demo_task_queue',
                            is_multi_task=False)

    def __init__(self, config_path: str, logger_name: str):
        super().__init__(self.task_info, config_path, logger_name)

    def get_validated_data_params(self, task_item_id: int, data: str) -> dict or None:
        self._logger.info(f"校验数据:[ID:{task_item_id}],data:{data}")
        return json.loads(data)

    def export(self, task_item: DownloadItem, data_obj: dict) -> tuple:
        self._logger.info(f"校验导出:[item:{data_obj}],data:{data_obj}")
        return None, None, None

    def split_task(self, task: DownloadTaskMain) -> list:
        pass


class DemoMultiItemTask(DownloadTaskBase):
    task_info = SubTypeInfo(task_name='DemoMultiItemTask', type=11, sub_type=11, queue_key='demo_multi_item_task_queue',
                            is_multi_task=True)

    def __init__(self, config_path: str, logger_name: str):
        super().__init__(self.task_info, config_path, logger_name)

    def get_validated_data_params(self, task_item_id: int, data: str) -> dict or None:
        self._logger.info(f"校验数据:[ID:{task_item_id}],data:{data}")
        return json.loads(data)

    def export(self, task_item: DownloadItem, data_obj: dict) -> tuple:
        self._logger.info(f"校验导出:[item:{data_obj}],data:{data_obj}")
        url = 'http://duyan-record-download.oss-cn-hangzhou.aliyuncs.com/100757218773722020-04-27.zip?OSSAccessKeyId=LTAI4GFAeToJVw9E8eoLK8Wu&Expires=1968908476&Signature=KugYlSKBX6d6ExiDWcJKk4KoA1Y%3D'
        md5 = 'f9d991b4a0522dfa77da67d68c675261'
        file_name = '100757218773722020-04-27.zip'
        return url, md5, file_name

    def split_task(self, task: DownloadTaskMain) -> list:
        items = []
        now = datetime.datetime.now()
        for i in range(2):
            item = DownloadItem()
            item.org_id = task.org_id
            item.task_id = task.id
            item.type = self.task_info.sub_type
            item.data = task.data
            item.status = ItemStatus.READY.value
            item.created_time = now
            item.last_updated_time = now
            items.append(item)
        return items


def task_test():
    task = DemoTask('config.ini', 'demo_task')
    task.start()


def multi_item_task_test():
    task = DemoMultiItemTask('config.ini', 'demo_task')
    task.start()


if __name__ == '__main__':
    multi_item_task_test()
