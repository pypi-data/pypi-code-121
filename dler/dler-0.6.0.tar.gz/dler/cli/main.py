#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
"""

"""
import typer
import time
from typer import Argument, Option

from dler import Dler

app = typer.Typer()

@app.command()
def start(
    url: str = Argument(..., help="URL 路径"),
    name: str = Option(None, '-n', '--name', help="下载文件保存名"),
    download_dir: str = Option(None, '--download-dir', help="下载目录"),
):
    """开始下载任务"""

    begin = time.time()
    config = {}
    if download_dir:
        config['download_dir'] = download_dir
    dl = Dler(url, filename = name, config = config)
    dl.run()

    cost = time.time() - begin
    typer.echo(f'下载完成，耗时: {cost}')


@app.command()
def run():
    print('test')

if __name__ == "__main__":
    app()
