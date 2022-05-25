# coding=utf-8
import shutil
from lettuce import world
from optparse import OptionParser
import os

world.fail_flag = False
world.skip_flag = False
world.re_flag = str()
world.case = list()
world.task_path = str()
world.task_name = str()
world.cache_path = str()
world.case_log_name = str()


def wrapped():
    parser = OptionParser()
    parser.add_option("--lf", "--last-failed", dest="last_failed", action="store_true",
                      help="仅执行上次失败的测试案例")
    parser.add_option("--ff", "--failed-first", dest="failed_first", action="store_true",
                      help="优先执行上次失败的测试案例")
    parser.add_option("--cc", "--clear-cache", dest="clear_cache", action="store_true",
                      help="清除当前的执行缓存")
    parser.add_option("--tn", "--task-name", dest="task_name",
                      help="指定需要运行的任务名称")

    (options, args) = parser.parse_args()
    if options.clear_cache:
        if options.task_name:
            for i in os.listdir('./case_cache'):
                if options.task_name in i:
                    clear_cache(f'./case_cache/{i}')
        else:
            clear_cache('./case_cache')
    if options.task_name:
        world.task_name = options.task_name
    if options.last_failed:
        world.re_flag = 'lf'
    if options.failed_first:
        world.re_flag = 'ff'


def run_task(task_name: str) -> str:
    mkdir_cache()
    name = task_name.split('/')[-1]
    if world.task_name:
        task_name = world.task_name
    else:
        task_name = name
        world.task_name = name
    if world.re_flag:
        dir_path = 'case_cache'
        if world.re_flag == 'lf':
            # 清除上一次的执行缓存
            clear_cache(f'./case_cache/{task_name}_cache/lf_res')
            # 根据类型复制案例文件
            shutil.copyfile(f'./case_cache/{task_name}_cache/run_res/error_case.feature',
                            f'./case_cache/{task_name}_cache/{task_name}/task.feature')
            world.cache_path = f'./case_cache/{task_name}_cache/lf_res'
        if world.re_flag == 'ff':
            # 清除上一次的执行缓存
            clear_cache(f'./case_cache/{task_name}_cache/ff_res')
            # 根据类型复制案例文件
            shutil.copyfile(f'./case_cache/{task_name}_cache/run_res/failed_first_case.feature',
                            f'./case_cache/{task_name}_cache/{task_name}/task.feature')
            world.cache_path = f'./case_cache/{task_name}_cache/ff_res'
    else:
        # 清除上一次的执行缓存
        path = f'./case_cache/{task_name}_cache'
        clear_cache(path)
        dir_path = 'features'
        world.cache_path = f'./case_cache/{task_name}_cache/run_res'
    if not os.path.exists(f'./case_cache/{task_name}_cache'):
        os.mkdir(f'./case_cache/{task_name}_cache')
    if not os.path.exists(world.cache_path):
        os.mkdir(world.cache_path)
    if world.re_flag:
        return f'{dir_path}/{task_name}_cache/{task_name}'
    else:
        return f'{dir_path}/{task_name}'


def mkdir_cache():
    if not os.path.exists('./case_cache'):
        os.mkdir('./case_cache')


def get_case_py_file(path):
    task_name = world.task_path.split('/')[-1]
    shutil.copytree(path, f'./case_cache//{task_name}_cache/{task_name}', symlinks=False, ignore=None)
    for root, dirs, files in os.walk(f'./case_cache/{task_name}_cache/{task_name}'):
        for i in files:
            if '.feature' in i:
                os.remove(f'./case_cache/{task_name}_cache/{task_name}/{i}')


def clear_cache(path):
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)


def build_failed_first_case():
    # 合并失败文件与通过文件
    if os.path.exists(f'{world.cache_path}/error_case.feature'):
        with open(f'{world.cache_path}/failed_first_case.feature', 'a+', encoding='utf8') as f:
            with open(f'{world.cache_path}/error_case.feature', 'r+', encoding='utf8') as c:
                with open(f'{world.cache_path}/temp_case.feature', 'r+', encoding='utf8') as t:
                    temp = c.readlines()
                    temp_b = t.readlines()
                    f.write("Feature: failed-first-case\n")
                    f.writelines(temp + temp_b)
        with open(f'{world.cache_path}/error_case.feature', 'w+', encoding='utf8') as u:
            u.write("Feature: error-case\n")
            u.writelines(temp)
    else:
        with open(f'{world.cache_path}/failed_first_case.feature', 'a+', encoding='utf8') as f:
            with open(f'{world.cache_path}/temp_case.feature', 'r+', encoding='utf8') as t:
                temp_b = t.readlines()
                f.write("Feature: failed-first-case\n")
                f.writelines(temp_b)

    if not world.re_flag:
        get_case_py_file(world.task_path)
    if os.path.exists(f'{world.cache_path}/temp_case.feature'):
        os.remove(f'{world.cache_path}/temp_case.feature')


wrapped()
mkdir_cache()
