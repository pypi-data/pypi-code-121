import os
from pathlib import Path

from coreutility.date_utility import as_file_timestamp, as_file_date_stamp


def read_from_file(file_path):
    with open(file_path, 'r') as data_file:
        return data_file.read()


def write_to_file(file_path, data, mode='w'):
    write_end_marker = '' if mode == 'w' else '\n'
    with open(file_path, mode) as data_file:
        data_file.write(data + write_end_marker)


def obtain_dir_files(path):
    files = [f for f in os.listdir(path) if os.path.join(path, f)]
    return files


def is_directory(dir_path):
    return Path(dir_path).is_dir()


def is_file(dir_path):
    return Path(dir_path).is_file()


def timestamp_file(file_name):
    (name, extension) = file_name.split('.')
    return '%s-%s.%s' % (name, as_file_timestamp(), extension)


def date_stamp_file(file_name):
    (name, extension) = file_name.split('.')
    return '%s-%s.%s' % (name, as_file_date_stamp(), extension)
