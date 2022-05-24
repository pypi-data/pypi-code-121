import argparse
import pypers.utils.utils as ut
from pypers.core.pipelines import Pipeline
from pypers.core.step import Step
import sys
import subprocess
import logging
import glob
import os
import shutil
import tarfile
from distutils.dir_util import copy_tree
from urllib import parse as urlparse
import requests
import paramiko
import getpass
import multiprocessing
import numpy as np
import cv2
import math


LOG_DIR = '/data/%(type)s/updates/log'


def build_command_parser(options, doc):
    parser = argparse.ArgumentParser(description=doc,
                                     formatter_class=argparse.RawTextHelpFormatter)
    for config in options:
        name = config.pop('name')
        parser.add_argument(*name, **config)
    return parser.parse_args()


def apply_custom(config, custom):
    """
    Replace/add custom values to that in config.
    Config is a dictionary and is expected to have a 'config' section.
    Custom is a list of custom parameters of the form 'a.b.c=value'
    """
    ut.pretty_print("Setting custom params: %s" % custom)
    for c in custom:
        path, v = c.split('=')
        keys = path.split('.')
        if 'config' not in config:
            config['config'] = {}
        param = config['config']
        for key in keys[:-1]:
            if key not in param:
                ut.pretty_print(
                    '*** WARNING: creating new parameter %s (a typo?)' % key)
                param[key] = {}
            param = param[key]
        name = keys[-1]
        if name in param:
            # if already set, preserve type
            ptype = type(param[name])
        else:
            ptype = type(v)
        param.update({name: ptype(v)})


pi = None

def exec_cmd(cmd):
    subprocess.call(cmd.split(' '),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)


def init_logger():
    logFormatter = logging.Formatter(
        '%(asctime)s [%(levelname)-5.5s]  %(message)s', '%Y-%m-%d %H:%M:%S')
    rootLogger = logging.getLogger()

    # log to console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.DEBUG)
    return rootLogger


def notify_err(conf, coll, files=[], email_all='_all_',
               sender='webadmin@bsidx1n.wipo.int'):
    email_this = conf.get(coll, {}).get('notify', {}).get('error', [])
    if email_this == []:
        email_all = conf[email_all].get('notify', {}).get('error', [])

    subject = '%s: Error executing fetch' % coll.upper()
    body = 'check attachement for details'

    ut.send_mail(sender,
                 email_this + email_all,
                 subject, text=body, files=files)


def notify_success(conf, run_id, releasetar_dir):
    email_all = conf['_all_'].get('notify', {}).get('success', [])

    colls_tm = glob.glob(os.path.join(releasetar_dir % {'type': 'brands'},
                                      '%s_*.tar' % run_id))
    colls_id = glob.glob(os.path.join(releasetar_dir % {'type': 'designs'},
                                      '%s_*.tar' % run_id))

    colls_tm = [os.path.basename(r).replace(
        '%s_' % run_id, '').replace('.tar', '').upper() for r in colls_tm]
    colls_id = [os.path.basename(r).replace(
        '%s_' % run_id, '').replace('.tar', '').upper() for r in colls_id]

    subject = '%s updates released' % run_id

    body = '[%s] TradeMarks: %s\n' % (len(colls_tm), ' - '.join(colls_tm))
    body += '[%s] Designs:    %s\n' % (len(colls_id), ' - '.join(colls_id))

    ut.send_mail('webadmin@bsidx1n.wipo.int', email_all, subject, text=body)


