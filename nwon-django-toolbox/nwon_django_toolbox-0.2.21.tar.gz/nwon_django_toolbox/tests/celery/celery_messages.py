import json
from typing import List, Optional, Tuple, Union

from nwon_baseline.directory_helper import (
    file_paths_in_directory,
    get_latest_file_in_directory,
)
from nwon_baseline.file_helper import read_file_content

from nwon_django_toolbox.tests.celery.celery_folders import get_path_to_celery_folder
from nwon_django_toolbox.typings.celery.celery_folders import CeleryFolder


def count_messages(celery_folder: CeleryFolder) -> int:
    path = get_path_to_celery_folder(celery_folder)

    return len(file_paths_in_directory(path)) if path is not None else 0


def path_to_latest_celery_message(celery_folder: CeleryFolder) -> Union[str, None]:
    path = get_path_to_celery_folder(celery_folder)
    return get_latest_file_in_directory(path) if path is not None else None


def celery_messages_information(celery_folder: CeleryFolder) -> List[str]:
    return [
        "task " + task + " in queue " + queue
        for (task, queue) in enqueued_tasks_and_messages(celery_folder)
    ]


def enqueued_tasks_and_messages(celery_folder: CeleryFolder) -> List[Tuple[str, str]]:
    """
    Returns a Tuple (task_name, queue_name)
    """

    path = get_path_to_celery_folder(celery_folder)
    files = file_paths_in_directory(path) if path else []

    return [(task_name_for_message(file), queue_for_message(file)) for file in files]


def enqueued_tasks(celery_folder: CeleryFolder) -> List[str]:
    path = get_path_to_celery_folder(celery_folder)
    files = file_paths_in_directory(path) if path else []

    return [task_name_for_message(file) for file in files]


def task_name_for_message(message_path: str) -> str:
    message = __read_celery_message(message_path)
    return message["headers"]["task"] if message else "unknown"


def queue_for_message(message_path: str) -> str:
    message = __read_celery_message(message_path)
    return (
        message["properties"]["delivery_info"]["routing_key"] if message else "unknown"
    )


def __read_celery_message(file_path: str) -> Optional[dict]:
    content = read_file_content(file_path)
    return json.loads(content) if content is not None else None
