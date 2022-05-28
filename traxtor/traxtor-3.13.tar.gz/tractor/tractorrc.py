#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi<dani.behzi@ubuntu.com>, 2020-2021

"""
this module creates tractorrc file
"""

import os
import tempfile
from . import bridges
from . import checks


def create():
    '''
    main function of the module
    #TODO: refactor to more little functions
    '''
    dconf = checks.dconf()
    accept_connection = dconf.get_boolean("accept-connection")
    if accept_connection:
        myip = "0.0.0.0"
    else:
        myip = "127.0.0.1"
    socks_port = str(dconf.get_int("socks-port"))
    dns_port = str(dconf.get_int("dns-port"))
    http_port = str(dconf.get_int("http-port"))
    exit_node = dconf.get_string("exit-node")
    bridges_file = bridges.get_file()
    with open(bridges_file) as file:
        mybridges = file.read()
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, "tractorrc")
    with open(path, 'w') as file:
        socks_port_line = "SocksPort {}:{}\n".format(myip, socks_port)
        file.write(socks_port_line)
        if accept_connection:
            file.write("SocksPolicy accept *\n")
        dns_port_lines = (
            "DNSPort {}:{}\n"
            "AutomapHostsOnResolve 1\n"
            "AutomapHostsSuffixes .exit,.onion\n").format(myip, dns_port)
        file.write(dns_port_lines)
        http_port_line = "HTTPTunnelPort {}:{}\n".format(myip, http_port)
        file.write(http_port_line)
        if exit_node != "ww":
            exit_node_policy = (
                "ExitNodes {}{}{}\n"
                "StrictNodes 1\n").format('{', exit_node, '}')
            file.write(exit_node_policy)
        if dconf.get_boolean("use-bridges"):
            file.write("UseBridges 1\n")
            obfs4_path = dconf.get_string("obfs4-path")
            file.write(
                "ClientTransportPlugin obfs4 exec {}\n".format(obfs4_path))
            file.write(mybridges)
    return tmpdir, path
