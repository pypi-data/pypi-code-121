#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description: m3u8 tasker

from multitasker import SubTaskModel

import os
import m3u8
from m3u8.model import Segment, Key, M3U8
from urllib.parse import urlparse
from typing import List
from wpy.functools import run_shell

from .base import BaseConfig, BaseTasker
from .models import DownloadTaskModel
from . import tasktools
from .exceptions import FileExistsException


class M3u8Tasker(BaseTasker):
    m3u8_download_dir: str = ""
    m3u8path: str = ""
    m3: M3U8
    m3_url: str

    class Config(BaseConfig):
        task_type: str = 'm3u8'

    def _init(self):
        super()._init()
        self.m3u8_download_dir = self.build_download_dir()

        filename = f'{self.filename.split(".")[0]}.m3u8' or os.path.basename(
            self.urlparse.path)
        _path = os.path.join(self.m3u8_download_dir, filename)
        self.m3u8path = _path

    def before_build(self):
        super().before_build()

        self.m3_url = self.url
        self.m3 = m3u8.load(self.m3_url)

        if self.m3.playlists:
            play_url = self.format_url(self.m3.playlists[0].uri)
            self.m3_url = play_url
            self.m3 = m3u8.load(self.m3_url)


    def build_task(self) -> dict:
        detail = {}
        if self.url:
            detail['url'] = self.url

        return {}

    def build_sub_tasks(self) -> List[SubTaskModel]:

        sub_tasks = []
        if self.url:
            sub_tasks.append(self.build_dl_m3u8_sub_task())
            for ts_url in self.generate_urls():
                _path = os.path.join(self.m3u8_download_dir,
                    os.path.basename(urlparse(ts_url).path))
                detail = DownloadTaskModel(url = ts_url, path = _path).dict()
                st = SubTaskModel(detail = detail, task_type = 'download')
                sub_tasks.append(st)
            return sub_tasks

        return []

    def build_dl_m3u8_sub_task(self) -> SubTaskModel:
        detail = DownloadTaskModel(url = self.m3_url,
            path = self.m3u8path).dict()
        return SubTaskModel(detail = detail, task_type = 'download_m3u8')

    def build_download_dir(self):
        filename = self.filename.split('.')[0] or os.path.basename(
            self.url).split('.')[0]
        dl_dir = os.path.join(self.download_dir, filename)
        if not os.path.exists(dl_dir):
            os.mkdir(dl_dir)
        return dl_dir

    def generate_urls(self):
        name: str
        for i, name in enumerate(self.m3.files):
            if not name:
                continue
            ts_url = self.format_url(name)
            yield ts_url

    def after_run(self):
        if self.filetype and self.filetype != 'm3u8':
            self.transcoding(self.filetype)

    def transcoding(self, trans_type: str):
        if os.path.exists(self.filepath):
            raise FileExistsException()
        print("开始转码")
        cmd = f'ffmpeg -allowed_extensions ALL -i {self.m3u8path} -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 {self.filepath}'
        run_shell(cmd)

    def format_url(self, url: str):
        _parse = urlparse(self.m3_url)
        if url.startswith('/'):
            url = f"{_parse.scheme}://{_parse.hostname}{url}"
        if not url.startswith('http'):
            url = os.path.join(self.m3.base_uri, url)
        return url


M3u8Tasker.trigger_sub_task('download')(tasktools.download)

@M3u8Tasker.trigger_sub_task('download_m3u8')
def download_m3u8(sub_task: SubTaskModel) -> bool:
    flag = tasktools.download(sub_task)
    if flag:
        # 修改 m3u8 文件
        task = DownloadTaskModel(**sub_task.detail)
        m3 = m3u8.load(task.path)
        seg: Segment
        for seg in m3.segments:
            seg.uri = os.path.basename(urlparse(seg.uri).path)

        key: Key
        for key in m3.keys:
            if not key:
                continue
            key.uri = os.path.basename(urlparse(key.uri).path)

        m3.dump(task.path)

    return flag

