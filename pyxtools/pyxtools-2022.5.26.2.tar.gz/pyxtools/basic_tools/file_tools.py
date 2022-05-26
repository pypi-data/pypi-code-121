# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import time
import zipfile

import fnmatch
import functools
import os
import shutil
import tarfile


def list_files(folder):
    """

    :type folder: str
    :rtype: list of str
    """
    file_list = []
    for file_name in os.listdir(folder):
        full_file_name = os.path.join(folder, file_name)
        if os.path.isdir(full_file_name):
            file_list.extend(list_files(full_file_name))
        else:
            file_list.append(full_file_name)

    file_list.sort()
    return file_list


def remove_empty_sub_dir(folder, remove_input_folder=False):
    """

    :type remove_input_folder: bool
    :type folder: str
    :rtype: list of str
    """
    file_list = os.listdir(folder)

    for file_name in file_list:
        full_file_name = os.path.join(folder, file_name)
        if os.path.isdir(full_file_name):
            remove_empty_sub_dir(full_file_name, remove_input_folder=True)

    if not os.listdir(folder) and remove_input_folder:
        shutil.rmtree(folder)


def include_patterns(*patterns):
    """
    ref: https://stackoverflow.com/questions/42487578/python-shutil-copytree-use-ignore-function-to-keep-specific-files-types

    Factory function that can be used with copytree() ignore parameter.

    Arguments define a sequence of glob-style patterns
    that are used to specify what files to NOT ignore.
    Creates and returns a function that determines this for each directory
    in the file hierarchy rooted at the source directory when used with
    shutil.copytree().
    """

    def _ignore_patterns(path, names):
        keep = set(name for pattern in patterns
                   for name in fnmatch.filter(names, pattern))
        ignore = set(name for name in names
                     if name not in keep and not os.path.isdir(os.path.join(path, name)))
        return ignore

    return _ignore_patterns


def compress_by_tar(source, target_file_name, absolute_dir=True):
    """

    :type source: str
    :type target_file_name: str
    :type absolute_dir: bool
    """
    tar_filetype_list = {"tar", "gz"}
    file_type = os.path.basename(target_file_name).split(".")[-1]
    if file_type not in tar_filetype_list:
        raise ValueError("{} type not support!")

    def tar_add_folder(_folder, _tar, _relative_path=None):
        if _relative_path is None:
            _relative_path = _folder

        for _file_name in os.listdir(_folder):
            _full_file_name = os.path.join(_folder, _file_name)
            _current_rpath = os.path.join(_relative_path, _file_name)
            if os.path.isdir(_full_file_name):
                tar_add_folder(_full_file_name, _tar, _relative_path=_current_rpath)
            else:
                tar.add(_full_file_name, arcname=_current_rpath)

    with tarfile.open(target_file_name, "w:{}".format(file_type)) as tar:
        if os.path.isdir(source):
            if absolute_dir:
                tar_add_folder(source, tar, _relative_path=source)
            else:
                tar_add_folder(source, tar, _relative_path=os.path.basename(source))
        else:
            if absolute_dir:
                tar.add(source, arcname=source)
            else:
                tar.add(source, arcname=os.path.basename(source))


def check_file_exists(func):
    @functools.wraps(func)
    def check(*args, **kwargs):
        start_time = time.time()
        file_list = func(*args, **kwargs)
        result = [file_name for file_name in file_list if os.path.exists(file_name)]
        logging.info("check_file_exists cost time: {}s".format(time.time() - start_time))
        return result

    return check


def zip_compress_file(src_file_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, mode="w") as zf:
        zf.write(src_file_path, os.path.basename(src_file_path), compress_type=zipfile.ZIP_DEFLATED)


def get_base_name_of_file(path_or_file_name: str) -> str:
    if path_or_file_name.find("\\") > -1:
        path_or_file_name = path_or_file_name.replace("\\", "/")

    name_list = path_or_file_name.split("/")
    for name in name_list[::-1]:
        if name:
            return name

    return path_or_file_name


__all__ = ("get_base_name_of_file", "zip_compress_file", "check_file_exists", "list_files", "remove_empty_sub_dir",
           "compress_by_tar", "include_patterns")
