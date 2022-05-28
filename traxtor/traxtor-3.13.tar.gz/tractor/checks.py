#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi<dani.behzi@ubuntu.com>, 2020-2021

"""
actions for tractor internals
"""

import os
import sys
from getpass import getuser
from gi.repository import Gio
from psutil import process_iter
from requests import get


def dconf():
    '''
    returns dconf object
    '''
    schema = 'org.tractor'
    schemas = Gio.SettingsSchemaSource.get_default()
    if not Gio.SettingsSchemaSource.lookup(schemas, schema, False):
        print('''
        Please compile the "tractor.gschema.xml" file.
        In GNU/Linux you can copy it to "/usr/share/glib-2.0/schemas/"
        and run "sudo glib-compile-schemas /usr/share/glib-2.0/schemas/".
        The file is located at {}.
        '''.format(os.path.dirname(os.path.abspath(__file__))))
        sys.exit(404)
    mydconf = Gio.Settings.new(schema)
    return mydconf


def procs():
    '''
    return tor processes of the user
    '''
    return [p.info for p in process_iter(attrs=['pid', 'name', 'username'])
            if p.info['name'] == 'tor' and p.info['username'] == getuser()]


def running():
    '''
    checks if Tractor is running or not
    '''
    conf = dconf()
    pid = conf.get_int("pid")
    if pid == 0:
        return False
    tor_procs = procs()
    if pid in [proc['pid'] for proc in tor_procs]:
        return True
    return False


def connected():
    '''
    checks if Tractor is connected or not
    '''
    if running():
        conf = dconf()
        port = conf.get_int("socks-port")
        host = "https://check.torproject.org/"
        proxy = "socks5h://127.0.0.1:{}".format(port)
        expectation = "Congratulations."
        try:
            request = get(
                host,
                proxies={"http": proxy, "https": proxy},
                timeout=10)
            if request.status_code == 200 and expectation in request.text:
                return True
            return False
        except Exception:
            return False
    return False
