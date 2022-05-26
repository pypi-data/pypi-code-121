from typing import List, Optional

from django.conf import settings
from nwon_baseline.directory_helper import clean_directory, create_pathes

from nwon_django_toolbox.typings.celery.celery_folders import CeleryFolder


def clean_all_celery_messages():
    for folder in __get_all_celery_message_folder():
        clean_directory(folder)


def create_celery_folder():
    if "broker_transport_options" in settings.CELERY_SETTINGS:
        create_pathes(__get_all_celery_message_folder())


def get_path_to_celery_folder(celery_folder: CeleryFolder) -> Optional[str]:
    if "broker_transport_options" in settings.CELERY_SETTINGS:
        return settings.CELERY_SETTINGS["broker_transport_options"][celery_folder.value]

    return None


def __get_all_celery_message_folder() -> List[str]:
    celery_message_folders = [
        get_path_to_celery_folder(folder)
        for folder in [
            CeleryFolder.DataFolderIn,
            CeleryFolder.DataFolderOut,
            CeleryFolder.DataFolderProcessed,
        ]
    ]

    return [x for x in celery_message_folders if x is not None]


__all__ = [
    "clean_all_celery_messages",
    "create_celery_folder",
    "get_path_to_celery_folder",
]
