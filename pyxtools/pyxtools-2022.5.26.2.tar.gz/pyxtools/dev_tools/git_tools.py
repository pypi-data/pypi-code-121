# -*- coding:utf-8 -*-
from __future__ import absolute_import

import fnmatch
import json
import logging
import os
import subprocess
import sys
from optparse import OptionParser
from subprocess import check_output

import requests

from .crlf_tools import change_crlf_mode_of_file, CRLF_VALUE
from ..basic_tools.log import global_init_logger

logger = logging.getLogger(__name__)

"""
git config:
```
[core]
    fileMode = false
    autocrlf = true
    safecrlf = true
```

create .gitattributes file with content:
```
# Set the default behavior, in case people don't have core.autocrlf set.
* text eol=lf

core.autocrlf=true
core.fileMode=false
```

fore change crlf if found error before `git commit`
```
 python -c "from pyxtools import git_crlf_helper as g;g()" -d . -t lf -i *.py -e *.pyc
```

"""


def git_list_status_file(path) -> list:
    """ list all file showed in `cd path && git status -s` """
    raw_path = os.getcwd()
    try:
        os.chdir(path)
        raw_lines = check_output(["git", "status", "-s"]).decode("utf-8").split("\n")
        logger.info("result of `git status -s` is {}".format("\n".join(raw_lines)))

        def _get_file_name(_line: str) -> str:
            blank_index = _line.find(" ")
            if blank_index > -1:
                return _line[blank_index:]
            return ""

        lines = [_get_file_name(clear_line) for clear_line in [line.strip("\r").strip() for line in raw_lines]]
        file_list = [os.path.join(path, file_name) for
                     file_name in [line.strip() for line in lines] if len(file_name) > 0]
        logger.info("result of `git_list_status_file` is ['{}']".format("'\n'".join(file_list)))
        return file_list
    finally:
        os.chdir(raw_path)


def git_crlf_fatal_file(path) -> list:
    """ list all file showed in `cd path && git status -s` """
    raw_path = os.getcwd()
    try:
        os.chdir(path)
        try:
            output = check_output(["git", "add", "."], shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output

        raw_lines = output.decode("utf-8").split("\n")
        logger.info("result of `git add .` is {}".format("\n".join(raw_lines)))
        fatal_line = raw_lines[0].strip()

        file_list = []
        if fatal_line.find("fatal") > -1:
            file_name = os.path.join(path, fatal_line.split(" ")[-1].rstrip("."))
            if os.path.exists(file_name) and os.path.isfile(file_name):
                file_list = [file_name]
            else:
                logger.warning("{} not exists!".format(file_name))
        if file_list:
            logger.info("result of `git_crlf_fatal_file` is ['{}']".format("'\n'".join(file_list)))
        else:
            logger.info("result of `git_crlf_fatal_file` is []")
        return file_list
    finally:
        os.chdir(raw_path)


def is_git_repo_log_dir(log_dir: str) -> bool:
    return os.path.isdir(log_dir) and \
           os.path.exists(os.path.join(log_dir, "index")) and \
           os.path.exists(os.path.join(log_dir, "HEAD"))


def find_git_log_dir(path: str) -> (str, str):
    while True:
        if not os.path.exists(path) or not os.path.isdir(path):
            raise ValueError("fail to find git log dir")

        git_log = os.path.join(path, ".git")
        if os.path.exists(git_log):
            if is_git_repo_log_dir(git_log):
                return path, git_log
        else:
            with open(git_log, "r", encoding="utf-8") as f:
                for line in f:
                    if line.find("gitdir:") > -1:
                        relative_path = line[line.find("gitdir:"):].strip("\n").strip("\r").strip()
                        real_git_log = os.path.join(path, relative_path)
                        if is_git_repo_log_dir(real_git_log):
                            return path, real_git_log

        path = os.path.join(path, "..")


def git_crlf_helper():
    global_init_logger()
    hstr = '%prog custom help string'
    parser = OptionParser(hstr, description='custom description', version='%prog 1.0')
    parser.add_option('-d', '--dir', action='store', dest='dir', default=".", help='working dir')
    parser.add_option('-i', '--include', action='store', dest='include', default="",
                      help='include pattern, join by `,`')
    parser.add_option('-e', '--exclude', action='store', dest='exclude', default="",
                      help='exclude pattern, join by `,`')
    parser.add_option('-t', '--target', action='store', dest='target', default="lf",
                      help='target: crlf, lf, cr')
    if sys.argv[0] == "-c":
        argv = list(sys.argv)
        argv[0] = __file__
        options, args = parser.parse_args(argv)
    else:
        options, args = parser.parse_args(sys.argv)

    if options.target in CRLF_VALUE:
        options.target = CRLF_VALUE[options.target]

    include = None
    if len(options.include) > 0:
        include = [pattern for pattern in options.include.split(",") if len(pattern) > 0]

    file_list = git_list_status_file(options.dir)
    all_file_list = []
    for file_name in file_list:
        if not os.path.exists(file_name):
            logger.warning("{} not exists, ignore it".format(file_name))
        else:
            all_file_list.append(file_name)
    file_list = list(all_file_list)

    if include is not None and len(include) > 0:
        all_file_list = []
        for pattern in include:
            all_file_list.extend(fnmatch.filter(file_list, pattern))
        file_list = list(set(all_file_list))

    exclude = None
    if len(options.exclude) > 0:
        exclude = [pattern for pattern in options.exclude.split(",") if len(pattern) > 0]
    if exclude is not None and len(exclude) > 0:
        exclude_file_list = []
        for pattern in exclude:
            exclude_file_list.extend(fnmatch.filter(file_list, pattern))
        file_list = list(set(file_list) - set(exclude_file_list))

    if len(file_list) == 0:
        logger.info("not file in unstage status!")
        return

    [change_crlf_mode_of_file(file_name, options.target) for file_name in file_list]

    count = 100
    file_list = git_crlf_fatal_file(options.dir)
    while count > 0 and len(file_list) > 0:
        change_crlf_mode_of_file(file_list[0], options.target)
        file_list = git_crlf_fatal_file(options.dir)
        count -= 1


def md2html_by_github(content: str) -> str:
    """ use github api """
    logger.info("requesting github...")
    url = "https://api.github.com/markdown"
    return requests.post(url, data=json.dumps({"text": content, "mode": "markdown"})).text


def git_export(export_zip_file_name: str, git_project_path: str = "./"):
    """
        导出git项目的纯净代码

        git archive --format zip --output "./output.zip" master -0
        # 将代码导出并 zip 打包后放在当前目录下，`output.zip`就是需要的文件，`-0`的意思是不压缩
    """
    current = os.getcwd()
    try:
        os.chdir(git_project_path)
        process = subprocess.Popen(
            ["git", "archive", "master", "--format", "zip", "--output", export_zip_file_name, ]
        )
        process.wait()
    finally:
        os.chdir(current)


def git_fetch_all(git_path: str):
    """ run `cd git_path && git fetch --all` """
    raw_path = os.getcwd()
    try:
        os.chdir(git_path)
        subprocess.Popen(["git", "fetch", "--all"]).wait()
    finally:
        os.chdir(raw_path)


__all__ = ("git_list_status_file", "is_git_repo_log_dir", "git_crlf_fatal_file",
           "find_git_log_dir", "md2html_by_github", "git_crlf_helper", "git_export",
           "git_fetch_all")
