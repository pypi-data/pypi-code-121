# 储存单位
import os
import platform
import re

# 文件大小单位

SUFFIX = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
# 系统的分割符
__os_sep__ = "\\" if platform.system() == 'Windows' else os.sep
# 标准文件名正着
_filename_ascii_strip_re = re.compile(r'[^A-Za-z0-9_.-]')
# windows的设备文件
_windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                         'LPT2', 'LPT3', 'PRN', 'NUL')



