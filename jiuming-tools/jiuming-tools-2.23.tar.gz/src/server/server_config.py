# 默认配置路径
import os
import shutil
import socket
import time

import click
import pexpect
import psutil

from src.config.global_config import private_key_default_file, compile_ip, compile_host_mame, \
    compile_tun_value
from src.server import server_store
from src.server.server_store import ServerConfig


def server_add(name, host, port, username, password, path):
    """
    添加服务配置
    :param name: 服务器名称
    :param host: 服务器地址
    :param port: 服务器ssh端口
    :param username: 服务器用户名
    :param password: 服务器用户密码
    :param path: 文件地址
    :return:
    """
    name = name.strip()
    secret_key_path = None
    if path is not None:
        abs_path = path
        # 处理用户目录
        if str(path).startswith('~'):
            abs_path = str(path).replace('~', os.path.expanduser('~'))
        click.echo(abs_path)
        if os.path.exists(abs_path) and os.path.isfile(abs_path):
            # 计算密钥地址
            secret_key_path = private_key_default_file + '/{}_{}.id_rsa'.format(name, username)
            click.echo(abs_path + '00' + secret_key_path)
            # 复制密钥到配置目录命名规则 服务器名_用户名_host地址
            shutil.copyfile(abs_path, secret_key_path)
        else:
            raise click.FileError('保存密钥异常！未找到密钥或者无权限')

    sc = ServerConfig(name=name, host=host, port=port, username=username, password=password,
                      secret_key_path=secret_key_path)
    server_store.create(sc)
    echo_str = '\n录入的服务器信息:\n名称:{}\n地址:{}\nssh端口:{}'.format(name, host, port)
    if secret_key_path is not None:
        echo_str += '\n密钥地址:{}'.format(secret_key_path)
    click.echo(echo_str)


def server_edit():
    server_store.edit()


def server_remove(name):
    """
    删除服务器配置信息
    获取所有配置  删除其中name符合的数据
    :param name: 服务器名称
    :return:
    """
    server_store.remove_by_name(name)


def server_list():
    sc_list = server_store.find_all()
    if sc_list is None:
        return
    config_str = "服务器信息列表:\n"
    for index, sc in enumerate(sc_list):
        config_str += '第{}台服务器名称:{},登录用户名:{},地址:{},端口:{}'.format(index + 1, sc.name, sc.username, sc.host, str(sc.port))
        if sc.secret_key_path is not None:
            config_str = config_str + ',密钥地址:{}'.format(sc.secret_key_path)
        config_str = config_str + '\n'
    config_str += "\n共{}台服务器".format(len(sc_list))
    click.echo(config_str)


def server_connect(name):
    click.echo("连接{}服务器...".format(name))
    sc = server_store.find_by_name(name)
    if sc is None:
        click.echo("未找到{}服务器配置!".format(name))
        return
    # 如果存在密钥 优先使用密钥登录服务器
    if sc.secret_key_path is not None:
        open_ssh_secret_key_tty(sc.host, sc.port, sc.username, sc.secret_key_path)
    else:
        open_ssh_password_tty(sc.host, sc.port, sc.username, sc.password)


def open_ssh_secret_key_tty(host, port, username, secret_key_path):
    cmd = 'ssh -o StrictHostKeyChecking=no -i {}  -p {} {}@{}'.format(secret_key_path, port, username, host)
    # 授权600
    os.chmod(secret_key_path, 0o600)
    p_ssh = pexpect.spawn(command=cmd)
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_ssh.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示终端
    p_ssh.interact()


def open_ssh_password_tty(host, port, username, password):
    cmd = 'ssh -o StrictHostKeyChecking=no  -p {} {}@{}'.format(port, username, host)
    p_ssh = pexpect.spawn(command=cmd)
    # 输入密码
    try:
        p_ssh.expect("password:", timeout=3)
        p_ssh.sendline(password)
    except pexpect.exceptions.TIMEOUT:
        click.echo(click.style("等待输入密码消息超时!", fg='yellow'))
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_ssh.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示终端
    p_ssh.interact()


def server_sftp(name, cwd_path):
    click.echo("连接{}服务器sftp服务...".format(name))
    sc = server_store.find_by_name(name)
    if sc is None:
        click.echo("未找到{}服务器配置!".format(name))
        return
    if sc.secret_key_path is not None:
        open_sftp_secret_key_tty(sc.host, sc.port, sc.username, sc.secret_key_path,
                                 cwd_path)
    else:
        open_sftp_password_tty(sc.host, sc.port, sc.username, sc.password, cwd_path)


def open_sftp_password_tty(host, port, username, password, cwd_path):
    # 执行sftp命令
    cmd = 'sftp -o StrictHostKeyChecking=no -P {} {}@{}'.format(port, username, host)
    p_sftp = pexpect.spawn(command=cmd, cwd=cwd_path)
    # 输入密码
    try:
        p_sftp.expect("password:", timeout=3)
        p_sftp.sendline(password)
    except pexpect.exceptions.TIMEOUT:
        click.echo(click.style("等待输入密码消息超时!", fg='yellow'))
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_sftp.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示sftp终端
    p_sftp.interact()


def open_sftp_secret_key_tty(host, port, username, secret_key_path, cwd_path):
    # 执行sftp命令
    cmd = 'sftp -o StrictHostKeyChecking=no -i {} -P {} {}@{}'.format(secret_key_path, port, username, host)
    p_sftp = pexpect.spawn(command=cmd, cwd=cwd_path)
    # 设置终端大小
    terminal_size = os.get_terminal_size()
    p_sftp.setwinsize(terminal_size.lines, terminal_size.columns)
    # 显示sftp终端
    p_sftp.interact()


def ping_ssh_server(name):
    """
     检查 列表中的 server是否存活
    """
    sc = server_store.find_by_name(name)
    if sc is None:
        click.echo("未找到{}服务器配置!".format(name))
        return
    # 执行探测操作
    start_time = time.perf_counter_ns()
    r = open_socket_ssh_server(sc.host, sc.port)
    end_time = time.perf_counter_ns()
    result = "{},探测结果:{},耗时:{}ms".format(sc.host + ":" + str(sc.port), r,
                                         str(round((int(round((end_time - start_time) / 1000000))), 2)))
    click.echo(result)


def open_socket_ssh_server(host, port):
    try:
        remote_ip = host
        if compile_host_mame.match(host):
            remote_ip = socket.gethostbyname(host)
        elif compile_ip.match(host):
            remote_ip = socket.gethostbyaddr(host)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((remote_ip, port))
        sock.close()
        return True
    except socket.error as e:
        click.echo("{}的{}端口连接失败,原因:{}".format(host, port, e))
        return False


def server_tun(left, right, reverse, name):
    sc = server_store.find_by_name(name)
    if sc is None:
        click.echo("未找到{}服务器配置!".format(name))
        return
    if reverse:
        cmd_str = 'ssh -CqTnN -R {} -p {} {}'.format('{}:{}'.format(get_server_config_tun_info(sc, right), left),
                                                     str(sc.port),
                                                     '{}@{}'.format(sc.username, sc.host))
        click.echo(cmd_str)
        auto_open_tun(cmd_str, sc.password)
    else:
        cmd_str = 'ssh -CqTnN -L {} -p {} {}'.format('{}:{}'.format(left, get_server_config_tun_info(sc, right)),
                                                     str(sc.port),
                                                     '{}@{}'.format(sc.username, sc.host))
        click.echo(cmd_str)
        auto_open_tun(cmd_str, sc.password)


def auto_open_tun(cmd_str, password):
    """
    自动打开 tun通道   当断开之后重连
    """
    p_tun = pexpect.spawn(command=cmd_str, cwd=".")
    # 输入密码
    try:
        p_tun.expect("password:", timeout=3)
        p_tun.sendline(password)
    except pexpect.exceptions.TIMEOUT:
        click.echo(click.style("等待输入密码消息超时!", fg='yellow'))
    pid = p_tun.pid
    click.echo(pid)
    while True:
        if not psutil.pid_exists(pid):
            p_tun = pexpect.spawn(command=cmd_str, cwd=".")
            # 输入密码
            try:
                p_tun.expect("password:", timeout=3)
                p_tun.sendline(password)
            except pexpect.exceptions.TIMEOUT:
                click.echo(click.style("等待输入密码消息超时!", fg='yellow'))
            pid = p_tun.pid
            click.echo("重连tun通道,PID:{}", pid)
        # 休眠200ms
        time.sleep(0.2)


def get_server_config_tun_info(sc: ServerConfig, tun_str):
    if compile_tun_value.match(tun_str):
        return tun_str
    else:
        return '{}:{}'.format(sc.host, sc.port)


def server_select_connect():
    # 获取服务器列表 增加编号
    sc_list = server_store.find_all()
    if sc_list is None:
        return
    config_str = '服务器信息:\n'
    index_name_map = {}
    for index, sc in enumerate(sc_list):
        index_name_map[str(index + 1)] = sc.name
        config_str += '{})台服务器名称:{},地址:{},端口:{}\n'.format(index + 1, sc.name, sc.host, str(sc.port))
    click.echo(config_str)
    # 等待用户输入服务器编号
    r = click.prompt(
        "选择服务器编号:",
        type=click.Choice(index_name_map.keys()),
        show_default=False,
    )
    server_connect(index_name_map[r])


def server_select_sftp(cwd):
    sc_list = server_store.find_all()
    if sc_list is None:
        return
    config_str = '服务器信息:\n'
    index_name_map = {}
    for index, sc in enumerate(sc_list):
        index_name_map[str(index + 1)] = sc.name
        config_str += '{})台服务器名称:{},地址:{},端口:{}\n'.format(index + 1, sc.name, sc.host, str(sc.port))
    click.echo(config_str)
    # 等待用户输入服务器编号
    r = click.prompt(
        "选择服务器编号:",
        type=click.Choice(index_name_map.keys()),
        show_default=False,
    )
    server_sftp(index_name_map[r], cwd)
