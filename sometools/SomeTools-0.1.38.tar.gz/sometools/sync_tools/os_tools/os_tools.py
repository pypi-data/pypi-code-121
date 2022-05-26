import psutil
from sometools.sync_tools.base import Base


class OsMixin(Base):
    def __init__(self, *args, **kwargs):
        super(OsMixin, self).__init__(*args, **kwargs)

    @staticmethod
    def os_memory_info() -> str:
        return psutil.virtual_memory()

    @staticmethod
    def os_cpu_info() -> str:
        # CPU逻辑数量
        # psutil.cpu_count()
        # CPU物理核心
        # psutil.cpu_count(logical=False)
        # CPU的用户／系统／空闲时间
        # psutil.cpu_times()
        # CPU使用率
        # psutil.cpu_percent(interval=1, percpu=True)
        return {"logical_core": psutil.cpu_count(),
                "physical core": psutil.cpu_count(logical=False),
                "user/system/free_time": psutil.cpu_times(),
                "usage_rate": psutil.cpu_percent(interval=1, percpu=True),
                }


    @staticmethod
    def os_disk_info() -> str:
        return {"disk_partitions": psutil.disk_partitions(),  # 磁盘分区信息
                "disk_usage": psutil.disk_usage('/'),  # 磁盘使用情况
                "disk_io_counters": psutil.disk_io_counters(),  # 磁盘IO
                }

    @staticmethod
    def os_net_info() -> str:
        return {"net_io_counters": psutil.net_io_counters(),  # 获取网络读写字节／包的个数
                "net_if_addrs": psutil.net_if_addrs(),  # 获取网络接口信息
                "net_if_stats": psutil.net_if_stats(),  # 获取网络接口状态
                "net_connections": psutil.net_connections(),  # 当前网络连接信息
                }

    # >> > psutil.pids()  # 所有进程ID
    # [3865, 3864, 3863, 3856, 3855, 3853, 3776, ..., 45, 44, 1, 0]
    # >> > p = psutil.Process(3776)  # 获取指定进程ID=3776，其实就是当前Python交互环境
    # >> > p.name()  # 进程名称
    # 'python3.6'
    # >> > p.exe()  # 进程exe路径
    # '/Users/michael/anaconda3/bin/python3.6'
    # >> > p.cwd()  # 进程工作目录
    # '/Users/michael'
    # >> > p.cmdline()  # 进程启动的命令行
    # ['python3']
    # >> > p.ppid()  # 父进程ID
    # 3765
    # >> > p.parent()  # 父进程
    # < psutil.Process(pid=3765, name='bash')
    # at
    # 4503144040 >
    # >> > p.children()  # 子进程列表
    # []
    # >> > p.status()  # 进程状态
    # 'running'
    # >> > p.username()  # 进程用户名
    # 'michael'
    # >> > p.create_time()  # 进程创建时间
    # 1511052731.120333
    # >> > p.terminal()  # 进程终端
    # '/dev/ttys002'
    # >> > p.cpu_times()  # 进程使用的CPU时间
    # pcputimes(user=0.081150144, system=0.053269812, children_user=0.0, children_system=0.0)
    # >> > p.memory_info()  # 进程使用的内存
    # pmem(rss=8310784, vms=2481725440, pfaults=3207, pageins=18)
    # >> > p.open_files()  # 进程打开的文件
    # []
    # >> > p.connections()  # 进程相关网络连接
    # []
    # >> > p.num_threads()  # 进程的线程数量
    # 1
    # >> > p.threads()  # 所有线程信息
    # [pthread(id=1, user_time=0.090318, system_time=0.062736)]
    # >> > p.environ()  # 进程环境变量
    # {'SHELL': '/bin/bash', 'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:...', 'PWD': '/Users/michael',
    #  'LANG': 'zh_CN.UTF-8', ...}
    # >> > p.terminate()  # 结束进程
    # Terminated: 15 < -- 自己把自己结束了

    # psutil.test() 可以模拟出ps命令的效果

    # https://github.com/giampaolo/psutil