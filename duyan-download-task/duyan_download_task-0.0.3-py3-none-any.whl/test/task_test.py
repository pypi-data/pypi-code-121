import json

from duyan_download_task import DownloadTaskBase, SubTypeInfo
from duyan_download_task.model import DownloadTaskMain, DownloadItem


class DemoTask(DownloadTaskBase):

    def __init__(self, task_info: SubTypeInfo, config_path: str, logger_name: str):
        super().__init__(task_info, config_path, logger_name)

    def get_validated_data_params(self, task_item_id: int, data: str) -> dict or None:
        self._logger.info(f"校验数据:[ID:{task_item_id}],data:{data}")
        return json.loads(data)

    def export(self, task_item: DownloadItem, data_obj: dict) -> tuple:
        self._logger.info(f"校验导出:[item:{data_obj}],data:{data_obj}")
        return None, None, None

    def split_task(self, task: DownloadTaskMain) -> list:
        pass


def task_test():
    info = SubTypeInfo(task_name='DemoTask', type=10, sub_type=15, queue_key='demo_task_queue', is_multi_task=False)
    task = DemoTask(info, 'config.ini', 'demo_task')
    task.start()


if __name__ == '__main__':
    task_test()
