#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: m3u8 tasker

from multitasker.base import MultiTasker
from multitasker.models.task import SubTaskModel

import os
import shutil
from typing import List
from pydantic import BaseModel

from wpy import BaseEnum

class FSActionEnum(BaseEnum):
    COPY = 'copy'
    MOVE = 'move'


class FileSystemTasker(MultiTasker):

    action: str
    from_file: str
    to_file: str

    class Config:
        task_type = 'filesystem'

    def __init__(self, action: str, from_file: str, to_file: str):
        self.action = action
        self.from_file = from_file
        self.to_file = to_file

    def build_task(self) -> dict:
        return {}

    def build_sub_tasks(self) -> List[SubTaskModel]:
        func_name = f"build_{self.action}_sub_tasks"
        func = getattr(self, func_name)
        return func()

    def build_copy_sub_tasks(self) -> List[SubTaskModel]:
        if not os.path.exists(self.from_file):
            raise RuntimeError(f'File {self.from_file} is not exists')

        if os.path.exists(self.to_file) and os.path.isfile(self.to_file):
            raise RuntimeError(f"File {self.to_file} is exists")

        if os.path.isdir(self.from_file):
            to_dir = self.to_file
            if os.path.exists(self.to_file):
                to_dir = os.path.join(self.to_file, os.path.basename(self.from_file))
            if not os.path.exists(to_dir):
                os.mkdir(to_dir)

            sub_tasks = []
            for name in os.listdir(self.from_file):
                from_path = os.path.join(self.from_file, name)
                if os.path.isdir(from_path):
                    # TODO 需要可以复制文件夹
                    continue
                to_path = os.path.join(to_dir, name)

                sub_task = SubTaskModel(task_type = 'copy',
                    detail = {"from_path": from_path, "to_path": to_path})
                sub_tasks.append(sub_task)
            return sub_tasks


        return []

class FSModel(BaseModel):
    from_path: str
    to_path: str

@FileSystemTasker.trigger_sub_task('copy')
def sub_task_copy(sub_task) -> bool:
    import time
    time.sleep(1)
    fs = FSModel(**sub_task.detail)
    if os.path.exists(fs.to_path):
        return True
    try:
        shutil.copy(fs.from_path, fs.to_path)
    except PermissionError as e:
        print(e)
    except OSError as e:
        print(e)
    return True

@FileSystemTasker.trigger_sub_task('move')
def sub_task_move(sub_task) -> bool:
    fs = FSModel(**sub_task.detail)
    shutil.move(fs.from_path, fs.to_path)
    return True

if __name__ == "__main__":
    import time
    import sys
    args = sys.argv[1:]
    tasker = FileSystemTasker(action = 'copy',
        from_file = '/tmp',
        to_file = '/tmp/test'
    )
    tasker.build()
    b = time.time()
    tasker.run()
    print(time.time() - b)

    tasker = FileSystemTasker(action = 'copy',
        from_file = '/tmp',
        to_file = '/tmp/test'
    )
    tasker.build()
    b = time.time()
    tasker.run()
    print(time.time() - b)

