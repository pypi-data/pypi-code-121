# Author: Snow Yang
# Date  : 2022/03/21

import os
import sys
import stat
import errno
import pathlib
import shutil
import requests
import tarfile
import zipfile
from rich.progress import Progress, BarColumn, TimeElapsedColumn, DownloadColumn, TransferSpeedColumn

from mdev import log

'''
URL example:
http://firmware.mxchip.com/mdev/cmake-mac.tar.bz2
http://firmware.mxchip.com/mdev/ninja-mac.tar.bz2
'''

url_common_header = 'http://firmware.mxchip.com/mdev/'

toolchains_afterfix = {
    'darwin': '-mac.zip',
    'linux': '-linux.zip',
    'win32': '-win.zip',
}

user_home = str(pathlib.Path.home())
env_root = os.path.abspath(os.path.join(user_home, '.mdev'))
build_root = os.path.join(env_root, 'build')
if sys.platform == 'darwin':
    cmake_exe = os.path.join(build_root, 'CMake.app', 'Contents', 'bin', 'cmake')
    ninja_exe = os.path.join(build_root, 'ninja')
elif sys.platform == 'linux':
    cmake_exe = os.path.join(build_root, 'cmake', 'bin', 'cmake')
    ninja_exe = os.path.join(build_root, 'ninja')
elif sys.platform == 'win32':
    cmake_exe = os.path.join(build_root, 'cmake', 'bin', 'cmake.exe')
    ninja_exe = os.path.join(build_root, 'ninja.exe')
else:
    log.err(f'{sys.platform} is not support')
    exit(1)



def mkdir_p(path):  # type: (str) -> None
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST or not os.path.isdir(path):
            raise

def add_execute_permission(exe):
    st = os.stat(exe)
    os.chmod(exe, st.st_mode | stat.S_IEXEC)

def check_and_download(exe, zip, name):
    exe_zip = os.path.join(build_root, zip)
    if not os.path.exists(exe):
        log.inf(f'{name} was not found.')
        if not os.path.exists(exe_zip):
            download(f'{url_common_header}{zip}', exe_zip)
        extract(exe_zip)
        os.remove(exe_zip)
        add_execute_permission(exe)

def get_env():  # type: () -> None
    # Create env directory
    if not os.path.exists(env_root):
        log.inf(f'Directory {env_root} was not found.')
        log.inf(f'Creating {env_root} ...')
        mkdir_p(env_root)
        
    # Create build tools directory
    if not os.path.exists(build_root):
        log.inf(f'Directory {build_root} was not found.')
        log.inf(f'Creating {build_root} ...')
        os.makedirs(build_root)
    
    check_and_download(cmake_exe, f'cmake{toolchains_afterfix[sys.platform]}', 'CMake')
    check_and_download(ninja_exe, f'ninja{toolchains_afterfix[sys.platform]}', 'Ninja')

    return env_root.replace("\\", "/")

def get_cmake():
    return cmake_exe.replace("\\", "/")

def get_ninja():
    return ninja_exe.replace("\\", "/")

def download(url, destination): # type: (str, str) -> None
    log.inf(f'Downloading {url} to {os.path.dirname(destination)} ...')
    try:
        with requests.get(url, stream=True) as response:
            block_size = 1024 #1 Kibibyte
            with open(destination, 'wb') as file:
                with Progress(BarColumn(bar_width=None), 
                TimeElapsedColumn(), 
                DownloadColumn(), 
                TransferSpeedColumn()) as progress:
                    task = progress.add_task("", total=int(response.headers.get('content-length', 0)))
                    for data in response.iter_content(block_size):
                        progress.update(task, advance=block_size)
                        file.write(data)
    except:
        if os.path.exists(destination):
            os.remove(destination)
            log.err('Error in downloading, exit.')
            exit(1)

def extract(filename, destination=None):  # type: (str, str) -> None
    if destination == None:
        destination = os.path.dirname(filename)
    log.inf(f'Extracting {filename} to {destination} ...')
    if filename.endswith(('.tar.gz', '.tgz')):
        archive_obj = tarfile.open(filename, 'r:gz')
    elif filename.endswith(('.tar.xz')):
        archive_obj = tarfile.open(filename, 'r:xz')
    elif filename.endswith(('.tar.bz2')):
        archive_obj = tarfile.open(filename, 'r:bz2')    
    elif filename.endswith('zip'):
        archive_obj = zipfile.ZipFile(filename)
    else:
        raise NotImplementedError('Unsupported archive type')
    if sys.version_info.major == 2:
        # This is a workaround for the issue that unicode destination is not handled:
        # https://bugs.python.org/issue17153
        destination = str(destination)
    try:
        archive_obj.extractall(destination)
    except:
        shutil.rmtree(destination, ignore_errors=True)
        log.err('Error in extracting, exit.')
        exit(1)
