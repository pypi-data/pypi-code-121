import os
import sys

def get_sys_path():
    return os.path.abspath('.')

def get_agrv_path():
    return sys.argv[0]

def get_real_path():
    return os.path.realpath('.')

def get_current_folder():
    return os.getcwd()

def create_dir_if_not_exist(folder: str):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return True

def rm_dir(folder: str):
    return os.rmdir(folder)