#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy@gmail.com
"""

"""
import time
from pydantic import BaseModel
from multitasker.models.task import TaskModel
from multitasker.models.enums import TaskStatusEnum


from rich.progress import (
    BarColumn,
    DownloadColumn,
    FileSizeColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

progress = Progress(
    TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    "{task.completed}/{task.total}",
    #  "•",
    #  DownloadColumn(),
    #  "•",
    #  TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(),
)


class TaskProgress(BaseModel):

    task_id: str
    progress_count: int = 0

    def run(self):
        """
        """
        with progress:
            self._run()

    def _run(self):
        task = TaskModel.find_by_id(self.task_id)

        progress_id = progress.add_task(task.task_type,
            filename = task.id, start=True, total = task.total_count)

        while task.progress < 1:
            time.sleep(1)
            _prog = task.finish_count
            advance = _prog - self.progress_count
            progress.update(progress_id, advance = advance)
            self.progress_count = _prog

            task = TaskModel.find_by_id(self.task_id)
            if task.status in (TaskStatusEnum.STOP.value,
                    TaskStatusEnum.FAILED.value):
                break
