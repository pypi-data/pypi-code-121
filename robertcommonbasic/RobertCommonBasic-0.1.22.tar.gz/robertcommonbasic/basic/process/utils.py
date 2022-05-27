import os
import sys
import argparse
import platform
import uuid
import time
from ctypes import windll, c_int, byref

import psutil
import subprocess
from ..cls.utils import daemon_thread

#检测PID是否在进程列表
def is_pid_exist(pid: int):
    return psutil.pid_exists(pid)

def kill_pid(pid: int):
    if is_pid_exist(pid) is True:
        #os.popen(f"taskkill.exe /F /t /pid:{pid}")
        os.kill(pid, 9)

#显示全部进程
def get_all_pids():
    return psutil.pids()

# 获取当前进程ID
def get_current_pid():
    return os.getpid()

#获取进程
def get_process(pid: int):
    return psutil.Process(pid)

#获取进程信息
def get_process_info(pid: int) -> dict:
    info = {}
    p = get_process(pid)
    if p:
        with p.oneshot():
            info['memory'] = p.memory_info().rss/1024/1024
            info['threads'] = p.num_threads()
            info['connections'] = p.connections()
            info['cpu'] = p.cpu_percent()
            info['create'] = p.create_time()
    return info

def get_process_name(pid: int):
    return psutil.Process(pid).name()

def get_process_by_path(path: str):
    process_dir = os.path.dirname(path).replace('\\','/')
    process_name = os.path.basename(path)
    process_ext = os.path.splitext(path)[-1][1:]  # 进程后缀名
    for process in psutil.process_iter():
        if process_ext == 'exe':
            if process.name() == process_name:
                if process.cwd().replace('\\', '/') == process_dir:
                    return process.pid
        elif process_ext == 'py':
            if process.name() == 'python.exe':
                if process.cwd().replace('\\', '/') == process_dir:
                    return process.pid
    return -1

def close_dump(child_id: int):
    # 检测崩溃弹框，关闭掉
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', action='store_false', help='User name')
    parser.add_argument('-p', type=int, help='Process ID')
    parser.add_argument('-s', help='??')

    pids = get_all_pids()
    for pid in pids:
        if is_pid_exist(pid) is True:
            process = get_process(pid)
            if process is not None and 'WerFault.exe' in process.name():
                args, unknown_args = parser.parse_known_args(process.cmdline())
                if args.p == child_id:  # 如果进程子ID =
                    kill_pid(process.pid)

#关闭进程
def close_process(pid: int, dump_close: bool=True):
    if dump_close is True:
        close_dump(pid)

    os.kill(pid, 9)  # 进行升级，退出此程序

#启动进程
def open_process(process_path: str):
    if os.path.exists(process_path) is True:
        process_folder = os.path.dirname(process_path)
        process_ext = os.path.splitext(process_path)[-1][1:]  # 进程后缀名
        if process_ext == 'bat':
            return subprocess.Popen(f'cmd.exe /c {process_path}', creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=process_folder).pid  # 结束进程
        elif process_ext == 'exe':
            return subprocess.Popen(process_path, creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=process_folder).pid  # 结束进程
        elif process_ext == 'py':
            return subprocess.Popen(f'python.exe {process_path}', creationflags=subprocess.CREATE_NEW_CONSOLE, cwd=process_folder).pid  # 结束进程
    return -1

#重启进程
def restart_process(process_path: str):
    pid = get_process_by_path(process_path)
    if pid > 0:
        close_process(pid)
    return open_process(process_path)

#开机自启动
def auto_start(app_path: str):
    if platform.system().lower() == 'windows':
        import win32api
        import win32con
        app_name = os.path.basename(app_path)
        app_ext = os.path.splitext(app_path)[1]
        reg_path = app_path
        reg_name = os.path.splitext(app_name)[0]
        if app_ext == '.py':
            reg_path = f"{os.path.dirname(app_path)}/{reg_name}.bat"
            base_dir = os.path.splitdrive(app_path)[0]  # 驱动器
            app_dir = os.path.dirname(app_path)  # 文件路径

            with open(reg_path, 'w') as f:
                f.write(f"@echo off\n")
                f.write(f"{base_dir}\n")
                f.write(f"cd {app_dir}\n")
                f.write(f"start {app_name}\n")
                f.write(f"exit")

        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Run', 0, win32con.KEY_ALL_ACCESS)
        try:
            reg_tuple = win32api.RegQueryValueEx(key, reg_name)
            if len(reg_tuple) > 0 and reg_tuple[0] != reg_path:
                win32api.RegSetValueEx(key, reg_name, 0, win32con.REG_SZ, reg_path)
                win32api.RegCloseKey(key)
            return True
        except:
            win32api.RegSetValueEx(key, reg_name, 0, win32con.REG_SZ, reg_path)
            win32api.RegCloseKey(key)
    return False

#重启自身
def restart():
    path = sys.executable
    if platform.system().lower() == 'windows':
        os.execv(path, [path, '"' + sys.argv[0] + '"'] + sys.argv[1:])
    else:
        os.execl(path, path, *sys.argv)

#延迟重启
@daemon_thread
def restart_delay(delay: int):
    while delay > 0:
        time.sleep(1)
        delay = delay - 1
    return restart()

#退出
def exit():
    return os._exit(0)

@daemon_thread
def exit_delay(delay: int):
    while delay > 0:
        time.sleep(1)
        delay = delay - 1
    return exit()

#更新
def update(update_path: str):
    if os.path.exists(update_path) is True:
        bat_path = 'update.bat'
        current_path = os.path.realpath(sys.argv[0])
        with open(bat_path, 'w+') as f:
            f.write(f"@echo off\n")         # 关闭bat脚本的输出
            f.write(f"if not exist {update_path} exit \n")      # 新文件不存在,退出脚本执行
            f.write(f"choice /t 3 /d y /n >nul\n")      # 3秒后删除旧程序（3秒后程序已运行结束，不延时的话，会提示被占用，无法删除）
            f.write(f"if exist {current_path} del {current_path}\n")            # 删除当前文件
            f.write(f"copy /y {update_path} {current_path}\n")      # 拷贝新文件并重命名成旧名称
            f.write(f"start {current_path}")
        subprocess.Popen(bat_path)
        if current_path.endswith('exe') is True:
            close_process(get_current_pid())  # 进行升级，退出此程序
        else:
            sys.exit()      # 进行升级，退出此程序
    else:
        raise Exception(f"update path not exist")

#重置控制台属性
def reset_console_property():
    if platform.system().lower() == 'windows':
        STD_INPUT_HANDLE = -10
        ENABLE_QUICK_EDIT_MODE = 0x0040
        ENABLE_MOUSE_INPUT = 0x0010
        ENABLE_INSERT_MODE = 0x0020
        handle = windll.kernel32.GetStdHandle(STD_INPUT_HANDLE)
        if handle:
            inMode = c_int(0)
            windll.kernel32.GetConsoleMode(c_int(handle), byref(inMode))

            inMode = c_int(inMode.value & ~ENABLE_QUICK_EDIT_MODE)  # 移除快速编辑模式
            inMode = c_int(inMode.value & ~ENABLE_INSERT_MODE)  # 移除插入模式
            inMode = c_int(inMode.value & ~ENABLE_MOUSE_INPUT)  #
            windll.kernel32.SetConsoleMode(c_int(handle), inMode)
            
#获取MAC地址
def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)]).upper()