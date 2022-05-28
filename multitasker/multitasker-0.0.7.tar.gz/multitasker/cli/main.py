#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy <wxnacy@gmail.com>
# Description:

from multitasker.models.base import Base, engine
from multitasker.filesystem import FileSystemTasker
from multitasker.models.task import SubTaskModel

import typer

app = typer.Typer()

@app.command()
def init():
    """
    初始化数据库等信息
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

@app.command()
def copy(from_path: str, to_path: str):
    """复制文件"""
    tasker = FileSystemTasker(action = 'copy',
        from_file = from_path,
        to_file = to_path
    )
    tasker.build()
    tasker.run()

    #  tasker = FileSystemTasker(action = 'copy',
        #  from_file = from_path,
        #  to_file = to_path + "/ss"
    #  )
    #  tasker.build()
    #  tasker.run()

@app.command()
def test():
    """
    初始化数据库等信息
    """
    SubTaskModel.delete({ "task_type": "test" })

if __name__ == "__main__":
    app()
