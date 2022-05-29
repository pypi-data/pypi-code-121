import logging
from enum import Enum
from typing import Optional

from nwon_django_toolbox.settings import NWON_DJANGO_SETTINGS
from nwon_django_toolbox.tests.celery.celery_messages import (
    celery_messages_information,
    count_messages,
    enqueued_tasks,
    enqueued_tasks_and_messages,
    path_to_latest_celery_message,
    queue_for_message,
    task_name_for_message,
)
from nwon_django_toolbox.typings.celery.celery_folders import CeleryFolder

LOGGER = logging.getLogger(NWON_DJANGO_SETTINGS.logger_name)


def check_number_of_created_tasks(celery_folder: CeleryFolder, expected_number: int):
    if count_messages(celery_folder) != expected_number:
        LOGGER.debug(
            "Expected "
            + expected_number.__str__()
            + " celery tasks. Found "
            + count_messages(celery_folder).__str__()
            + "\n\n Messages\n"
            + celery_messages_information(celery_folder).__str__()
        )

    assert count_messages(celery_folder) == expected_number


def check_task_has_been_enqueued(
    celery_folder: CeleryFolder,
    task_name: Enum,
    queue: Optional[Enum] = None,
    number_of_occurrences: int = 1,
):
    tasks = enqueued_tasks(celery_folder)

    if number_of_occurrences > 0:
        if task_name.value not in tasks:
            __log_information(celery_folder=celery_folder)

        assert task_name.value in tasks

    if queue:
        information = enqueued_tasks_and_messages(celery_folder)

        if information.count((task_name.value, queue.value)) != number_of_occurrences:
            __log_information(celery_folder=celery_folder)

        assert (
            information.count((task_name.value, queue.value)) == number_of_occurrences
        )
    else:
        assert tasks.count(task_name.value) == number_of_occurrences


def check_latest_task(
    celery_folder: CeleryFolder,
    task_name: Optional[Enum] = None,
    queue: Optional[Enum] = None,
):
    if task_name or queue:
        message_path = path_to_latest_celery_message(celery_folder)

        if task_name and message_path:
            assert task_name.value in task_name_for_message(message_path)

        if queue and message_path:
            assert queue.value == queue_for_message(message_path)


def __log_information(celery_folder: CeleryFolder):
    information = enqueued_tasks_and_messages(celery_folder)
    LOGGER.debug("Currently scheduled tasks: %s", information.__str__())


__all__ = [
    "check_latest_task",
    "check_task_has_been_enqueued",
    "check_number_of_created_tasks",
]
