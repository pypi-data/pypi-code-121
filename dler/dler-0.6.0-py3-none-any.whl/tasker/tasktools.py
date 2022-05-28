
from multitasker import SubTaskModel

from dler.downloaders import download_url
from .models import DownloadTaskModel


def download(sub_task: SubTaskModel) -> bool:
    """下载任务"""
    task = DownloadTaskModel(**sub_task.detail)
    return download_url(task.url, task.path, headers = task.headers)
