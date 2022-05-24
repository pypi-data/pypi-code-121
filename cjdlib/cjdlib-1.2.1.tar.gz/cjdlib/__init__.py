import time
import psutil
import platform
import os
import socket
import sys
from psutil._common import bytes2human
from rich.traceback import install
from rich.progress import track

# A variable.
name = "cjdlib"
# A variable.
v = "1.1.6"
_ = install()


def print_the_time() -> None:
    """
Print the time every second
    """
    while True:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        time.sleep(1)


def decomposed_prime_factor(num: int) -> None:
    """
The function is to decompose the prime factor of a number

:param num: The number you want to decompose
:type num: int
    """
    m = []
    while num != 1:
        for i in range(2, int(num + 1)):
            if num % i == 0:
                m.append(str(i))
                num /= i
        if num == 1:
            break
    print('×'.join(m))


# This class is used to print colored text to the terminal.
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_disk_space(path: str) -> tuple:
    """
Given a path, return the total, used, and free disk space in bytes

:param path: The path to the folder you want to check the disk space of
:type path: str
    """
    usage = psutil.disk_usage(path)
    space_total = bytes2human(usage.total)
    space_used = bytes2human(usage.used)
    space_free = bytes2human(usage.free)
    print(f"总容量：{space_total}\n已用：{space_used}\n剩余：{space_free}")
    return space_total, space_used, space_free


def get_os_info() -> None:
    """
It returns the OS name and version.
    """

    def showinfo(tip, info):
        print(f"{tip}:{info}")

    showinfo("操作系统及版本信息", platform.platform())
    showinfo('获取系统版本号', platform.version())
    showinfo('获取系统名称', platform.system())
    showinfo('系统位数', platform.architecture())
    showinfo('计算机类型', platform.machine())
    showinfo('计算机名称', platform.node())
    showinfo('处理器类型', platform.processor())
    showinfo('计算机相关信息', platform.uname())
    showinfo('python相关信息', platform.python_build())
    showinfo('python版本信息:', platform.python_version())


def get_time_of_the_year(year: str, month: str, day: str) -> None:
    """
It returns the time of the year.

:param year: a string representing the year
:type year: str
:param month: A string of the month
:type month: str
:param day: str - the day of the month
:type day: str
    """
    read_time = f'{year}-{month}-{day}'
    stru_time = time.strptime(read_time, r'%Y-%m-%d')
    print('这一天是这一年的第', stru_time.tm_yday, '天')


def print_all(string: str, times: float = 0.1, line_feed: bool = False) -> None:
    # sourcery skip: remove-unnecessary-cast
    """
Prints the given strings,
separated by spaces, and then prints a newline character

:param string: str: The String to output
:type string: str
:param times: float = 0.1
:type times: float
:param line_feed: If True, a line feed is printed after the string, defaults to False
:type line_feed: bool (optional)
    """
    if line_feed:
        print("\n")
    for strs in str(string):
        sys.stdout.write(strs)
        sys.stdout.flush()
        time.sleep(times)
    sys.stdout.write("\n")
    sys.stdout.flush()


def countdown_day(day: str) -> str:
    """
It takes a string and returns a string.

:param day: str
:type day: str
    """
    t = abs(time.mktime(time.strptime(day, "%Y-%m-%d %H:%M:%S")) - time.time())
    d = int(t // 86400)
    h = int(t % 86400 // 3600)
    m = int(t % 3600 // 60)
    return f"距离目标还有{d}天{h}小时{m}分钟{int(t % 60)}秒"


def prime_number(num: int) -> bool:
    """
Returns True if the given number is a prime number, False otherwise

:param num: int
:type num: int
    """
    x = True
    for n in range(2, num):
        if num % n == 0:
            x = False
            return False
    if x is True:
        return True


def perfect_number(num: int) -> bool:
    """
It checks if a number is perfect or not.

:param num: int
:type num: int
    """
    x = 0
    for n in range(1, num):
        if num % n == 0:
            x += n
        if x > num:
            return False
    return num == x


def find_file_by_suffix(suffix: str, path: str = os.getcwd()) -> list:
    """
Given a suffix and a path, return a list of files with that suffix.

:param suffix: The suffix of the file you want to find
:type suffix: str
:param path: The path to the directory where the search should start
:type path: str
    """
    file_list = os.listdir(path)
    for file in file_list:
        if file[-3:] != suffix:
            file_list.remove(file)
    return [os.path.join(path, file) for file in file_list]


def get_host_ip() -> str:
    """
Get the host's IP address
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8", 80))
        ip = s.getsockname()[0]
    return ip


def timestamp_to_time(t: float) -> str:
    """
Converts a timestamp to a time string.

:param t: The timestamp to convert to a time string
:type t: float
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def progress_bar(t=0.2) -> None:
    """
Prints a progress bar to the console

:param t: the amount of time to sleep before moving the progress bar
    """
    for _ in track(range(100)):
        time.sleep(t)


def log(func) -> any:
    "装饰器函数，用于记录函数信息"
    def inner(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        end_time = time.time()
        sys.stdout.write("--------------------\n")
        sys.stdout.flush()
        sys.stdout.write(f"{func.__name__}()函数运行完成，用时{round(end_time-start_time)}秒 {args} -> {res}\n按任意键继续...")
        sys.stdout.flush()
        sys.stdin.readline()[:-1]
        return res
    return inner
