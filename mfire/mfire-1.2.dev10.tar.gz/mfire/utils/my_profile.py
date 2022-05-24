"""
This module comes from slackoverflow :
https://stackoverflow.com/questions/552744/how-do-i-profile-memory-usage-in-python
After importing it in your module, you can use the profile decorator in your function.

Example :

@profile
def my_func(x):
    y = x >0
    return y

Warning :
When used with multiprocess, produce a bug
"""
import time
import os
import psutil
import cProfile
from io import StringIO
import functools
import inspect
import pstats
import multiprocessing as mp


def monitor(target, args=None, kwargs=None, fname="test.png"):
    import psutil
    import matplotlib.pyplot as plt

    ts = 0.1
    if kwargs is not None and args is not None:
        worker_process = mp.Process(target=target, args=args, kwargs=kwargs)
    else:
        print("Monitors")
        worker_process = mp.Process(target=target)
    worker_process.start()
    p = psutil.Process(worker_process.pid)

    # log cpu usage of `worker_process` every 10 ms
    cpu_percents = []
    user_cpu_times = []
    system_cpu_times = []
    io_cpu_times = []
    mem_shared = []
    mem_rss = []
    mem_vms = []
    read_count = []
    read_chars = []
    read_bytes = []
    # io_counter = []
    # open_files = []
    while worker_process.is_alive():
        try:
            cpu_percents.append(p.cpu_percent())
            cpu_times = p.cpu_times()
            user_cpu_times.append(cpu_times[0])
            system_cpu_times.append(cpu_times[1])
            io_cpu_times.append(cpu_times[4])
            mi = p.memory_info()
            io_info = p.io_counters()
            print(cpu_times)
            print(mi)
            print(io_info)

            mem_shared.append(mi.shared / 1073741824)
            mem_rss.append(mi.rss / 1073741824)
            mem_vms.append(mi.vms / 1073741824)
            read_count.append(io_info.read_count)
            read_bytes.append(io_info.read_bytes / 1048576)
            read_chars.append(io_info.read_chars / 1048576)
        except Exception as e:
            print("Exception in monitor", repr(e))
            pass

        # io_counter.append(p.io_counters())
        # open_files.append(p.open_files())
        time.sleep(ts)
    worker_process.join()

    def xaxis(d):
        return [n * ts for n in range(len(d))]

    fig, [(ax1, ax2), (ax3, ax4), (ax5, ax6)] = plt.subplots(3, 2, figsize=(30, 20))
    ax6.remove()
    ax1.plot(xaxis(cpu_percents), cpu_percents)
    ax1.set_xlabel("time (in s)")
    ax1.set_ylabel("cpu percentage (%)")
    ax1.set_title("Cpu usage")
    ax2.plot(xaxis(user_cpu_times), user_cpu_times, label="user")
    ax2.plot(xaxis(system_cpu_times), system_cpu_times, label="system")
    ax2.plot(xaxis(io_cpu_times), io_cpu_times, label="io_wait")
    ax2.set_xlabel("time (in s)")
    ax2.set_ylabel("cpu times")
    ax2.legend()
    ax3.plot(xaxis(mem_rss), mem_rss, label="RSS")
    ax3.plot(xaxis(mem_vms), mem_vms, label="VMS")
    ax3.plot(xaxis(mem_shared), mem_shared, label="Shared")
    ax3.set_xlabel("time (in s)")
    ax3.set_ylabel("Memory size (GigaBytes)")
    ax3.legend()
    ax4.plot(xaxis(read_count), read_count, label="Read_count")

    ax4.set_xlabel("time (in s)")
    ax4.set_ylabel(" Number of read")
    ax4.legend()
    ax5.plot(xaxis(read_bytes), read_bytes, label="Read bytes")
    ax5.plot(xaxis(read_chars), read_chars, label="Read chars")
    ax5.set_xlabel("time (in s)")
    ax5.set_ylabel(" Bytes (in MBytes)")
    ax5.legend()
    fig.savefig(fname)

    return cpu_percents


def elapsed_since(start):
    # return time.strftime("%H:%M:%S", time.gmtime(time.time() - start))
    elapsed = time.time() - start
    if elapsed < 1:
        return str(round(elapsed * 1000, 2)) + "ms"
    if elapsed < 60:
        return str(round(elapsed, 2)) + "s"
    if elapsed < 3600:
        return str(round(elapsed / 60, 2)) + "min"
    else:
        return str(round(elapsed / 3600, 2)) + "hrs"


def get_process_memory():
    process = psutil.Process(os.getpid())
    mi = process.memory_info()
    return mi.rss, mi.vms, mi.shared


def format_bytes(bytes):
    if abs(bytes) < 1000:
        return str(bytes) + "B"
    elif abs(bytes) < 1e6:
        return str(round(bytes / 1e3, 2)) + "kB"
    elif abs(bytes) < 1e9:
        return str(round(bytes / 1e6, 2)) + "MB"
    else:
        return str(round(bytes / 1e9, 2)) + "GB"


def cprofile(_func=None, **kwargs_dec):
    """
    Define a decorator with options
    _func : Nothing should be done.
        If some optional argument are present _func is the function wrapped.
        Else _func is None
    Optional :
        sortby (str) : Should be in ["time", "cumulative"]
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()
            result = func(*args, **kwargs)
            pr.disable()
            s = StringIO()
            sortby = kwargs_dec.get("sortby", "time")
            if sortby in ["time", "cumulative"]:
                ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            else:
                raise (
                    ValueError(
                        "sortby option of cprofile decorator "
                        "should be in ['time','cumulative']"
                    )
                )
            ps.print_stats(100)
            print(s.getvalue())
            return result

        if inspect.isfunction(func):
            return wrapper
        elif inspect.ismethod(func):
            return wrapper(**kwargs_dec)

    if _func is None:
        return decorator
    else:
        print(_func)
        return decorator(_func)


def profile_mem(func, *args, **kwargs):
    # RSS: aka “Resident Set Size”, this is the non-swapped physical
    #       memory a process has used. Equivalent to top RES column.
    # VMS: aka “Virtual Memory Size”, this is the total amount of virtual
    #       memory used by the process.  It matches “top“‘s VIRT column.
    # SHR: memory that could be potentially shared with other processes.
    def wrapper(*args, **kwargs):
        rss_before, vms_before, shared_before = get_process_memory()
        start = time.time()
        result = func(*args, **kwargs)
        elapsed_time = elapsed_since(start)
        rss_after, vms_after, shared_after = get_process_memory()
        print(
            "Profiling: {:>20}  RSS: {:>8} | VMS: {:>8} | SHR {"
            ":>8} | time: {:>8}".format(
                "<" + func.__name__ + ">",
                format_bytes(rss_after - rss_before),
                format_bytes(vms_after - vms_before),
                format_bytes(shared_after - shared_before),
                elapsed_time,
            )
        )
        return result

    if inspect.isfunction(func):
        return wrapper
    elif inspect.ismethod(func):
        return wrapper(*args, **kwargs)


def logwrap(logger):
    def _logwrap(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            logger.info("Entering", process=mp.current_process().name, func=fn.__name__)
            t0 = time.time()
            out = fn(*args, **kwargs)
            t1 = time.time()
            logger.info(
                "Exiting",
                process=mp.current_process().name,
                func=fn.__name__,
                elapsed_time=t1 - t0,
            )
            return out

        return wrapper

    return _logwrap
