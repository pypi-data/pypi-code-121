#!/usr/bin/python3
# Released under GPLv3+ License
# Danial Behzadi<dani.behzi@ubuntu.com>, 2020-2021

"""
module to manages bridges
"""

import os
import shutil
import sys
from gi.repository import GLib


def get_sample_bridges():
    '''
    there should be some sample bridges in the package
    '''
    return os.path.dirname(os.path.abspath(__file__))+"/SampleBridges"


def copy_sample_bridges(bridges_file):
    '''
    function to copy sample bridges for tractor
    '''
    sample_bridges_file = get_sample_bridges()
    try:
        shutil.copyfile(sample_bridges_file, bridges_file)
    except IOError as exception:
        print("There is an error: %s" % exception)
        sys.exit(1)


def get_file():
    '''
    get bridges file address
    '''
    config_dir = GLib.get_user_config_dir() + "/tractor"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    bridges_file = config_dir + "/Bridges"
    if not os.path.isfile(bridges_file):
        copy_sample_bridges(bridges_file)
    return bridges_file
