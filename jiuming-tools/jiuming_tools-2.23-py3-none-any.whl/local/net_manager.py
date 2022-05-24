import datetime
import socket

import click
from scapy.all import traceroute
from scapy.as_resolvers import AS_resolver_radb

from src.config.global_config import compile_ip, compile_host_mame


def net_test(host, port):
    try:
        remote_ip = host
        if compile_host_mame.match(host):
            remote_ip = socket.gethostbyname(host)
        elif compile_ip.match(host):
            remote_ip = socket.gethostbyaddr(host)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((remote_ip, port))
        click.echo("{}的{}端口连接成功!".format(host, port))
        sock.close()
    except socket.error as e:
        click.echo("{}的{}端口连接失败,原因:{}".format(host, port, e))


def trace_route(dir, port, host):
    domains = host
    target = domains.split(' ')
    dport = [int(port)]
    if len(target) >= 1 and target[0] != '':
        # 启动路由跟踪
        svg_path = "{}/traceroute_{}.svg".format(dir, datetime.datetime.now().__format__('%Y%m%d%H%M%S'))
        res, unans = traceroute(domains, dport=dport, retry=-2)
        # traceroute生成的信息绘制成svg
        res.graph(target="> {}".format(svg_path),
                  ASres=AS_resolver_radb(),
                  type="svg")  # ASres=AS_resolver_radb()改变为可用的whois提供商,而非原来的ASres=None后默认的被qiang了的提供商
        click.echo("svg生成地址:{}".format(svg_path))
    else:
        raise click.BadParameter("IP/domain number of errors, exit")
