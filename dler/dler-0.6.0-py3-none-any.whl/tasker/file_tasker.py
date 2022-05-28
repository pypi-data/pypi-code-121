#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: m3u8 tasker

from multitasker import SubTaskModel
import requests

import os
import time
from typing import List
from pydantic import BaseModel

from dler.constants import SEGMENT_SIZE
from dler.models import HeaderModel
from .base import BaseConfig, BaseTasker
from .models import DownloadTaskModel, MergeTaskModel
from . import tasktools


class FileDetailModel(BaseModel):
    headers: HeaderModel


class FileTasker(BaseTasker):
    detail: FileDetailModel

    class Config(BaseConfig):
        task_type: str = 'file'

    def build_task(self) -> dict:

        res = requests.head(self.url)
        headers = dict(res.headers)
        header = HeaderModel(**headers)
        self.detail = FileDetailModel(headers = header)

        return self.detail.dict()

    def build_sub_tasks(self) -> List[SubTaskModel]:

        sub_tasks = []
        headers = self.detail.headers
        if headers.accept_ranges == 'bytes' and headers.content_length > SEGMENT_SIZE:
            length = headers.content_length
            merge_files = []
            total_page = int(length / SEGMENT_SIZE) + 1
            # 分拆下载子任务
            for i in range(total_page):
                begin = i * SEGMENT_SIZE
                if begin >= length:
                    break
                end = (i + 1) * SEGMENT_SIZE - 1
                if end >= length:
                    end = length - 1

                header_range = f'bytes={begin}-{end}'
                path = os.path.join(self.cache_dir, f'{begin}-{end}')

                sub_detail = DownloadTaskModel(url = self.url, path = path,
                    headers = { "Range": header_range })
                sub_task = SubTaskModel(
                    task_type = 'download', detail = sub_detail.dict())
                sub_tasks.append(sub_task)
                merge_files.append(path)

            # 增加 merge 子任务
            merge_task = MergeTaskModel(
                filepath = self.filepath, merge_files = merge_files,
            )
            sub_tasks.append(SubTaskModel(
                task_type = 'merge', detail = merge_task.dict()
            ))
            return sub_tasks

        # 直接下载
        sub_detail = DownloadTaskModel(url = self.url, path = self.filepath)
        sub_task = SubTaskModel(
            task_type = 'download', detail = sub_detail.dict())
        sub_tasks.append(sub_task)

        return sub_tasks

    def run(self):
        if os.path.exists(self.filepath):
            print(f"{self.filename} 已经下载完成")
            return
        super().run()


FileTasker.trigger_sub_task('download')(tasktools.download)

@FileTasker.trigger_sub_task('merge')
def sub_task_merge(sub_task) -> bool:
    task = MergeTaskModel(**sub_task.detail)
    merge_map = {}

    while len(merge_map) != len(task.merge_files):
        for merge_file in task.merge_files:
            if os.path.exists(merge_file):
                merge_map[merge_file] = True

        time.sleep(1)

    with open(task.filepath, 'wb') as wf:
        for merge_file in task.merge_files:
            with open(merge_file, 'rb') as rf:
                wf.write(rf.read())

    return True
