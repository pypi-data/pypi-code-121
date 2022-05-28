# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
import os
import shutil

CRLF_VALUE = {"lf": "\n", "crlf": "\r\n", "cr": "\r"}


def change_crlf_mode_of_file(file_name, dst_lf):
    tmp_file = file_name + ".bak"
    shutil.copy(file_name, tmp_file, follow_symlinks=False)

    with open(tmp_file, 'r', newline=None, encoding="utf-8") as infile, \
            open(file_name, 'w', newline=dst_lf, encoding="utf-8") as outfile:
        outfile.writelines(infile.readlines())

    os.remove(tmp_file)


def change_to_lf(file_list: list):
    for file_name in file_list:
        try:
            change_crlf_mode_of_file(file_name, "\n")
        except Exception as e:
            logging.error(e, exc_info=True)


def change_to_crlf(file_list: list):
    for file_name in file_list:
        try:
            change_crlf_mode_of_file(file_name, "\r\n")
        except Exception as e:
            logging.error(e, exc_info=True)


__all__ = ("change_to_crlf", "change_to_lf", "change_crlf_mode_of_file", "CRLF_VALUE")
