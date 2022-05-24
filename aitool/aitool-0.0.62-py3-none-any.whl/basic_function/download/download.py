# -*- coding: UTF-8 -*-
# Copyright©2020 xiangyuejia@qq.com All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""

"""
from typing import Dict, Tuple, Union, List, Iterator, Any, NoReturn, Callable
import sys
from urllib import request, error
# TODO 最基础的网络下载能力，后续download/utils里的修改为复用本文件里的方法
# TODO 有另外一个类似的函数需要合并 from aitool.basic_function.file import download_file


def _report_process(block_num, block_size, total_size):
    sys.stdout.write('\r>> Downloading %.1f%%' % (float(block_num * block_size) / float(total_size) * 100.0))
    sys.stdout.flush()


def download_file(
        url: str,
        filename: str = None,
        reporthook: Callable = _report_process,
        data: Any = None,
        show: bool = True,
) -> None:
    try:
        if show:
            print("Start downloading {} to {}...".format(url, filename))
        request.urlretrieve(url, filename, reporthook, data)
        if show:
            print("Download {} successfully!".format(url))
    except (error.HTTPError, error.URLError) as e:
        print(e)


if __name__ == '__main__':
    pass
