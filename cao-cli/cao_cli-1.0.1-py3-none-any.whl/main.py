import typer
import socket
import json
import pyperclip
import time
from time import time
import os
from tabulate import tabulate
import wcwidth
import urllib3
from uuid import getnode as get_mac
import sys
from pathlib import Path

downloads_path = str(Path.home() / "Downloads")

HOST = "localhost"
PC_PORT = 19091
FIRST_TASK_TAG = 'Zmlyc3QgdGFzaw=='

MAC_ADDRESS = '-'.join(['{:02X}'.format((get_mac() >> ele) & 0xff) for ele in range(0, 8 * 6, 8)][::-1])
URL = "https://cloudapi.bytedance.net/faas/services/ttpduz/invoke/caoEvent"

app = typer.Typer()


def start():
    print("Hello")


FILE_PATH = 'cache.json'


def put(task):
    if len(task['method']['params']) == 0:
        return
    with open(FILE_PATH, 'w+') as file:
        data = {}
        try:
            data = json.load(file)
        except ValueError as e:
            sys.stderr.write("e")
        if str(task['key']) in data:
            old_list = data[task['key']]
        else:
            old_list = []
        for idx, item in enumerate(old_list):
            if item == task:
                old_list.insert(0, old_list.pop(idx))
                return
        old_list.insert(0, task)
        data[task['key']] = old_list
        json.dump(data, file)


def get(key):
    with open(FILE_PATH, 'r+') as file:
        data = json.load(file)
        return data[key]


def has_key(key):
    with open(FILE_PATH, 'r+') as file:
        data = json.load(file)
        return str(key) in data


def clear():
    with open(FILE_PATH, 'w+') as file:
        json.dump({}, file)


def create_file_if_not_exists():
    cache_file = Path(FILE_PATH)
    cache_file.touch(exist_ok=True)
    file = open(FILE_PATH, "w+")
    data = file.read()
    if not data:
        file.write("{}")


@app.command(name="list")
def list(search: str = typer.Argument("")):
    create_file_if_not_exists()
    start_time = current_milli_time()
    os.system('source ~/.bash_profile')
    # 这里暂存到临时文件中，避免控制台输出
    os.system('adb forward tcp:19091 tcp:19191 > temp.log')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PC_PORT))
    sock.send("\n".encode())
    response = get_all_data(sock)
    sock.close()
    tasks = json.loads(response.decode('utf-8'))
    mobLoadTasks(current_milli_time() - start_time)

    print_list = []
    for index, task in enumerate(tasks, 1):
        print_item = [index, task['title'], task['ownerName'], task['emailPrefix']]
        print_list.append(print_item)
    typer.secho(tabulate(print_list, headers=["ID", "TITLE", "AUTHOR", "Email"], tablefmt='pretty'),
                fg=typer.colors.BLUE, bold=True)
    typer.secho("\n")

    task_id = typer.prompt("需要执行哪个任务? (输入ID)")
    execute_start = current_milli_time()
    task = tasks[int(task_id) - 1]

    if has_key(task['key']):
        cache_list = []
        input_item = [1, "重新输出参数"]
        cache_list.append(input_item)
        for cache_idx, cache in enumerate(get(task['key']), 2):
            cache_item = [cache_idx, ','.join(cache['method']['params'])]
            cache_list.append(cache_item)
        typer.secho(tabulate(cache_list, headers=["ID", "Parameters"], tablefmt='pretty'), fg=typer.colors.BLUE,
                    bold=True)
        typer.secho("\n")

        cache_id = typer.prompt("选择缓存项")

        if cache_id == '1':
            input_params(task)
        else:
            task = get(task['key'])[int(cache_id) - 2]
    else:
        input_params(task)

    rsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rsock.connect((HOST, PC_PORT))
    rsock.send(FIRST_TASK_TAG.encode())
    rsock.send("\n".encode())
    rsock.send(json.dumps(task).encode())
    rsock.send("\n".encode())
    response = get_all_data(rsock)
    rsock.close()

    put(task)

    mobExecuteMethodEvent(task['key'], current_milli_time() - execute_start)

    if task['outputType'] == 0:
        pyperclip.copy(response.decode("utf-8"))
        typer.secho(str(response.decode('utf-8')), fg=typer.colors.BLUE, bold=True)
    elif task['outputType'] == 2:
        time_str = time.strftime("%Y-%m-%d-%H_%M_%S")
        file_name = downloads_path + time_str + ".json"

        f = open(file_name, 'w')
        f.write(json.dumps(json.loads(response)))
        f.close()

        os.system("open " + file_name)
    else:
        # 列表结果
        list_tasks = json.loads(response.decode('utf-8'))

        print_list = []
        for index, task in enumerate(list_tasks, 1):
            print_item = [index, task['title'], task['subTitle']]
            print_list.append(print_item)
        typer.secho(tabulate(print_list, headers=["ID", "TITLE", "SUBTITLE"], tablefmt='simple'),
                    fg=typer.colors.BLUE, bold=True)
        typer.secho("\n")

        selected_index = typer.prompt("选择其中一个选项(输入ID)")
        selected_task = list_tasks[int(selected_index) - 1]

        print_list = []
        for index, task in enumerate(selected_task['options'], 1):
            print_item = [index, task['title'], task['subTitle']]
            print_list.append(print_item)
        typer.secho(tabulate(print_list, headers=["ID", "TITLE", "SUBTITLE"], tablefmt='simple'),
                    fg=typer.colors.BLUE, bold=True)
        typer.secho("\n")

        option_index = int(typer.prompt("选择操作项(输入ID)")) - 1
        selected_start_time = current_milli_time()
        executed_method(json.dumps(selected_task['options'][option_index]))
        mobExecuteMethodEvent(selected_task['key'], current_milli_time() - selected_start_time)


def input_params(task):
    params_hint = task['method']['paramsHint']
    # Input Params
    for index, paramHint in enumerate(params_hint, 0):
        task['method']['params'].append(typer.prompt(task['method']['paramsHint'][index]))


def executed_method(task_str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PC_PORT))
    sock.send(FIRST_TASK_TAG.encode())
    sock.send("\n".encode())
    sock.send(task_str.encode())
    sock.send("\n".encode())
    response = get_all_data(sock)
    sock.close()
    typer.secho(response, fg=typer.colors.GREEN, bold=True)


def get_all_data(sock):
    BUFF_SIZE = 4096  # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data


def current_milli_time():
    return int(time() * 1000)


def mobExecuteMethodEvent(key, duration):
    http = urllib3.PoolManager()
    PARAMS = {"event": "execute_method",
              "key": key,
              "id": MAC_ADDRESS,
              "client": "CLI",
              "duration": duration,
              "time_stamp": current_milli_time()
              }
    http.request('GET', URL, fields=PARAMS)


def mobLoadTasks(duration):
    http = urllib3.PoolManager()
    PARAMS = {"event": "load_tasks", "client": "CLI", "id": MAC_ADDRESS, "duration": duration,
              "time_stamp": current_milli_time()}
    http.request('GET', URL, fields=PARAMS)
