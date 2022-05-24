#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
from multiprocessing import Process
import showlog
import time
import copy
import os
os_cpu_count = os.cpu_count()  # CPU核心数


def run(
        task_list: list,
        task_function,
        subprocess_keep: bool = False,
        subprocess_limit: int = os_cpu_count * 2,
        master_process_delay: int = 1,

        silence: bool = False,
):
    """
    多进程 进程控制
    :param task_list: 任务列表，list格式
    :param task_function: 子任务的function，需提前写好，入参为：(task_index, task_info)，例如：task_function(task_index, task_info)
    :param subprocess_keep: 是否保持子进程，True为保持进程，死掉会自动重启；False为不保持，自然退出
    :param subprocess_limit: 进程数限制，0为无限制，否则按照设定的数量限制并行的子进程数量
    :param master_process_delay: 主进程循环延时，单位为秒，默认为1秒
    :param silence: 静默模式，为True是不产生任何提示

    demo:
    def task_function(
            task_index,
            task_info
    ):
        # 进程详细的内容
        print(task_index, task_info)
    """
    active_process = dict()  # 活跃进程，存放进程，以task_index为key，进程信息为value的dict
    task_count = len(task_list)  # 总任务数量
    task_index_start = 0  # 用来计算启动的累计进程数

    showlog.info(f'正在准备多进程执行任务，总任务数为：{task_count}，进程数限制为：{subprocess_limit}...')
    # 创建并启动线程
    while True:
        this_time_start = copy.deepcopy(task_index_start)  # 确定本次循环的起点任务序号
        for task_index in range(this_time_start, task_count):  # 按照任务量遍历
            if task_index in active_process.keys():
                # 进程已存在，不重复创建，跳过
                continue
            else:
                # 进程不存在，待定
                if subprocess_limit > 0:
                    # 存在子进程数量限制规则，待定
                    if len(active_process) >= subprocess_limit:
                        # 当前活跃进程数量达到子进程数限制，本次循环不再新增进程，跳出
                        if silence is False:
                            showlog.warning('达到进程数限制')
                        break
                # 不存在子进程限制规则/当前活跃进程数量未达到进程数限制，将开启一个新进程
                if silence is False:
                    showlog.info(f'发现需要开启的进程：{task_index}')
                task_info = task_list[task_index]  # 提取将开启的进程的任务内容
                # ---------- 开启进程 ----------
                p = Process(
                    target=task_function,
                    args=(task_index, task_info)
                )
                p.start()
                # ---------- 开启进程 ----------
                active_process[task_index] = {
                    'task_index': task_index,  # 任务序号
                    'task_info': task_info,  # 任务详情
                    'process': p,  # 进程对象
                }  # 记录开启的进程
                if silence is False:
                    showlog.info(f'进程：{task_index} 已开启')
                task_index_start += 1  # 记录累计开启进程数

        # 检测非活跃进程，并从active_process中剔除非活跃进程，以便开启新的进程
        inactive_process = list()  # 非活跃进程
        for process_index, process_info in active_process.items():
            if process_info['process'].is_alive() is False:
                if silence is False:
                    showlog.warning(f'进程 {process_index} 不活跃，将被剔除...')
                inactive_process.append(process_index)
        for each_dead_process in inactive_process:
            active_process.pop(each_dead_process)

        if task_index_start >= len(task_list) and len(active_process) == 0:
            if silence is False:
                showlog.info('全部任务执行完成')
            if subprocess_keep is True:
                task_index_start = 0  # 将累计启动进程数重置为0
            else:
                return
        time.sleep(master_process_delay)
