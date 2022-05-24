# -*- coding:utf-8 -*-
import os

import click
from prettytable import PrettyTable

from src.cmd import cmd_manager
from src.config import global_config, config_manager
from src.config.global_config import compile_ip, compile_host_mame, tools_dependency_info_arr
from src.local import http_server, pc_info, net_manager, pc_test
from src.script import script_manager
from src.server import server_config
from src.task import task_manager


def validate_ip_or_host_name_type(ctx, param, value):
    err_msg = '{}不符合ip/域名格式!请检查后输入'.format(value)
    try:
        if compile_ip.match(value):
            return value
        elif compile_host_mame.match(value):
            return value
        else:
            raise click.BadParameter(err_msg)
    except ValueError:
        raise click.BadParameter(err_msg)


def print_version(ctx, param, value):
    """
    输出工具版本
    :param ctx:   click上下文
    :param param: 参数
    :param value:  值
    :return:
    """
    if not value or ctx.resilient_parsing:
        return

    tools_lib_str = ','.join([i.cmd for i in tools_dependency_info_arr])
    version_info = """
    作者:ming 
    仅适用linux 其他平台兼容性不做保证
    启用自动补全:
    bash:在.bashrc末尾添加 eval "$(_M_COMPLETE=source m)"
    zsh:在.zshrc末尾添加 eval "$(_M_COMPLETE=source_zsh m)"
    依赖的工具：{}
    jiuming-tools Version {}""".format(tools_lib_str, global_config.get_version())
    click.echo(version_info)
    ctx.exit()


def check_tools_dependency(ctx, param, value):
    """
    输出工具版本
    由于本工具依赖众多 linux下工具
    不过不是必须  所以可以通过此方法 校验是否满足依赖  和影响的相关功能
    :param ctx:   click上下文
    :param param: 参数
    :param value:  值
    :return:
    """
    if not value or ctx.resilient_parsing:
        return
    # 读取 $PATH
    bin_path_str_arr = os.getenv("PATH").split(":")
    # 命令set集合
    cmd_name_set = set()
    for bin_path in bin_path_str_arr:
        if not os.path.exists(bin_path):
            click.echo(click.style("{}不存在!\n".format(bin_path), fg='yellow'))
            continue
        if os.path.isfile(bin_path):
            cmd_name_set.add(bin_path)
        else:
            for f in os.listdir(bin_path):
                cmd_name_set.add(f)
    # 获取系统依赖工具列表
    t_table = PrettyTable(['name', "desc", 'result', 'remark'])
    # 设置对齐方式
    t_table.align = "l"
    # 设置表格最长列
    t_table.max_width = 80
    for i in tools_dependency_info_arr:
        t_table.add_row([i.cmd, i.desc, cmd_name_set.__contains__(i.cmd), i.install_demo_cmd])
    click.echo(t_table)
    ctx.exit()


@click.group()
@click.option('--version', '-v', help='工具版本', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.option('--check', '-c', help='检测当前环境下工具依赖是否完整', is_flag=True, callback=check_tools_dependency,
              expose_value=False,
              is_eager=True)
def cli():
    pass


# ---------------------- server tools ----------------------------------------------------------------------------------
@cli.group(help='远程服务器管理')
def server():
    pass


@server.command("list", help='显示所有服务器配置')
def server_list():
    server_config.server_list()


@server.command("add", help='添加服务器配置')
@click.option('--name', '-n', prompt='请输入服务器名称')
@click.option('--host', '-h', prompt='请输入服务器地址', callback=validate_ip_or_host_name_type)
@click.option('--port', '-p', prompt='请输入服务器ssh端口,默认为22', default=22)
@click.option('--username', '-u', prompt='请输入服务器用户名')
@click.option('--mode', '-m', prompt='指定模式', type=click.Choice(['PASSWORD', 'SECRET'], case_sensitive=False))
def server_add(name, host, port, username, mode):
    password = None
    path = None

    if str(mode).upper() == 'PASSWORD':
        password = click.prompt('请输入密码', type=str)
    elif str(mode).upper() == 'SECRET':
        path = click.prompt('密钥位置', type=click.Path(exists=True))
    else:
        click.echo('无法识别此模式!' + mode)
        return
    server_config.server_add(str(name).strip(), host, port, username, password, path)


@server.command("remove", help='根据名称删除服务器配置')
@click.option('--name', '-n', type=str, prompt='请输入服务器名称', help='服务器名称')
def server_remove(name):
    server_config.server_remove(name)


@server.command('edit', help='使用vi编辑服务器配置')
def server_edit():
    server_config.server_edit()


@server.command('connect', help='连接服务器')
@click.option('--name', '-n', type=str, help='服务器名称')
def server_connect(name):
    if name is None or name == '':
        # 当名称为空的时候  读取list 排序出来  增加编号选择处理
        server_config.server_select_connect()
    else:
        server_config.server_connect(name)


@server.command('sftp', help='打开sftp客户端')
@click.option('--name', '-n', type=str, help='服务器名称')
@click.option('--cwd', '-cwd', type=click.Path(exists=True), default='.', help='本地工作目录,默认为.')
def server_sftp(name, cwd):
    if name is None or name == '':
        server_config.server_select_sftp(cwd)
    else:
        server_config.server_sftp(name, cwd)


@server.command('ping', help='检测服务器是否可链接(建立socket方式，不使用ping指令)')
@click.option('--name', '-n', multiple=True)
def server_ping(name):
    server_config.ping_ssh_server(name)


@server.command('tun', help='ssh tun 打洞，默认将左边地址映射到右边地址')
@click.option('--left', '-l', type=str, prompt='请输入左边端口映射(host:port)', help='左边')
@click.option('--right', '-r', type=str, prompt='请输入右边边端口映射(host:port)', help='右边')
@click.option('--name', '-n', type=str, prompt='请输入服务器名称', help='服务器名称')
@click.option('--reverse', is_flag=True, help='反转，将右边地址映射到左边')
def server_tun(left, right, name, reverse):
    server_config.server_tun(left, right, reverse, name)


# ----------------------------------- local tools ----------------------------------------------------------------------

@cli.group(help='本机使用的工具')
def local():
    pass


@local.command('pc', help='电脑配置')
def local_pc_info():
    pc_info.echo_pc_info()


@local.command('http', help='根据指定文件夹开启临时http服务器')
@click.option('--dir', '-d', type=click.Path(exists=True), default='.', nargs=1, help='指定静态文件目录,默认为.')
@click.option('--port', '-p', default=20000, type=int, nargs=1, help='指定服务端口,默认为20000')
@click.option('--host', '-h', default='0.0.0.0', callback=validate_ip_or_host_name_type, type=str, nargs=1,
              help='指定服务监听地址,默认为0.0.0.0')
def local_tmp_http(dir, port, host):
    http_server.http_server(dir, port, host)


@local.command('traceroute', help='路由跟踪,需要root权限')
@click.option('--dir', '-d', type=click.Path(exists=True), default='.', nargs=1, help='生成svg文件目录,默认为.')
@click.option('--port', '-p', default=80, type=int, nargs=1, help='端口,默认为80')
@click.option('--host', '-h', default='0.0.0.0', callback=validate_ip_or_host_name_type, type=str, nargs=1,
              help='跟踪地址,默认为0.0.0.0')
def local_traceroute(dir, port, host):
    net_manager.trace_route(dir, port, host)


@local.command('socket-test', help='测试服务器是否可以打开socket')
@click.option('--host', '-h', type=str, prompt='请输入服务器地址', callback=validate_ip_or_host_name_type, help='服务器地址')
@click.option('--port', '-p', type=int, default=80, help='探测端口号(默认为80)')
def socket_test(host, port):
    net_manager.net_test(host, port)


@local.command('test-disk', help='测试服务器磁盘性能')
@click.option('--size', '-s', type=int, default=2, help='测试磁盘数据大小，单位GB，默认2GB')
def test_disk(size):
    pc_test.testDisk(size)


@local.command('test-net', help='测试服务器网络速度')
@click.option('--threads', '-t', type=int, default=None, help='线程数,默认为speettest的默认参数')
def test_network(threads):
    pc_test.testNetwork(threads)


@local.command('pid-info', help='获取指定pid进程的信息,需要访问对应进程的权限')
@click.option('--pid', '-pid', type=int, prompt='线程PID', help='线程PID')
@click.option('--details', '-d', type=click.BOOL, default=False, help='显示详情')
def pid_info(pid, details):
    pc_info.pid_info(pid, details)


@local.command('mem-info', help='获取指定pid进程的信息,需要root权限')
@click.option('--top', '-top', type=int, default=10, help="显示topN的信息,默认显示top10")
@click.option('--pid', '-pid', type=int, help='线程PID')
@click.option('--details', '-d', type=click.BOOL, default=False, help='显示详情')
def mem_info(top, pid, details):
    pc_info.mem_info(top, pid, details)


@local.command('net-info', help='获取网络信息,需要root权限')
@click.option('--details', '-d', type=click.BOOL, default=False, help='显示详情')
def net_info(details):
    pass


# @local.command('detect', help='侦测当前设备各项资源')
# def detect():
#     pc_info.detect()


# ----------------------------------- tools config manager  -----------------------------------------------------------

config_remark = """
配置管理 \n
使用私有git仓库作为配置保存\n  
如github 私有仓库等 \n
"""


@cli.group(help=config_remark)
def config():
    pass


@config.command('details', help='查看当前配置仓库配置')
def config_details():
    config_manager.details()


@config.command('save', help='创建当前配置仓库配置')
@click.option('--url', '-url', type=str, prompt='同步仓库url地址')
@click.option('--username', '-u', type=str, prompt='同步仓库用户名')
@click.option('--password', '-p', type=str, prompt='同步仓库密码')
def config_save(url, username, password):
    config_manager.save(url=url, username=username, password=password)


@config.command('remove', help='删除当前配置仓库配置')
def config_remove():
    config_manager.remove()


@config.command('pull', help='同步配置远程到本地')
def config_pull():
    config_manager.pull()


@config.command('push', help='同步配置本地到远程仓库')
@click.option('--remark', '-r', type=str, help='推送备注')
def config_push(remark):
    config_manager.push(remark)


@config.command('clone', help='clone配置到本地')
def config_clone():
    config_manager.clone()


# ----------------------------------- tools config manager  -----------------------------------------------------------
# linux 各种脚本管理   shell 、py 等脚本


@cli.group(help='管理常用linux的脚本')
def script():
    pass


@script.command('remove', help='删除脚本')
@click.option('--name', '-n', prompt='脚本名称')
def script_remove(name):
    script_manager.script_remove(name)


@script.command('create', help='创建脚本')
@click.option('--type', '-t', prompt='脚本类型(执行引擎名称)')
@click.option('--name', '-n', prompt='脚本名称')
@click.option('--remark', '-r', prompt='备注描述')
def script_create(type, name, remark):
    script_manager.script_create(type, name, remark)


@script.command('details', help='查看脚本详情')
@click.option('--name', '-n', prompt='脚本名称')
def script_details(name):
    script_manager.script_details(name)


@script.command('list', help='列出当前脚本')
def script_list():
    script_manager.script_list()


@script.command('exec', help='执行脚本')
@click.option('--name', '-n', prompt='脚本名称')
def script_exec(name):
    script_manager.script_exec(name)


@cli.group(name="cmd", help="命令工具")
def cmd():
    pass


@cmd.command('search', help='搜索命令使用方式,信息来源:http://linux.51yip.com/')
@click.option('--name', '-n', prompt='命令名称')
def cmd_search(name):
    cmd_manager.search(name)


@cli.group(name="task", help="个人任务安排")
def task():
    pass


@task.command("list", help='列表')
@click.option("--model", '-m', type=click.Choice(['ALL', 'TRUE', 'FALSE'], case_sensitive=False), default='FALSE',
              help='模式')
@click.option('--date', '-d', type=click.DateTime(formats=['%Y%m%d', '%Y-%m-%d']),
              # default=datetime.datetime.today().strftime('%Y%m%d'),
              help='时间,yyyyMMdd或者yyyy-MM-dd格式')
@click.option('--search', '-s', type=str, help='全文检索相关的任务')
def task_list(model, date, search):
    task_manager.list(model, date, search)


@task.command("create", help='创建任务')
@click.option('--name', '-n', prompt='任务名称')
@click.option('--content', '-c', prompt='任务内容')
@click.option('--level', '-l', type=int, prompt='任务等级')
def task_create(name, content, level):
    task_manager.create(name, content, level)


@task.command("over", help='完成任务')
@click.option('--id', '-id', help="任务id")
def task_over(id):
    if id is None:
        task_manager.select_over()
    else:
        task_manager.over(id)


@task.command("remove", help='删除任务')
@click.option('--id', '-id', help="任务id")
def task_remove(id):
    if id is None:
        task_manager.select_remove()
    else:
        task_manager.remove(id)


# main 函数
if __name__ == '__main__':
    cli()
