"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import subprocess
import logging
import os
import sys
import glob

'''
Utility class to keep commonly used methods/functionality here
'''


def conf_cmd(spec, cov_bin, cov_conf):
    try:
        cov_configure_path = glob.glob(os.path.join(cov_bin, 'cov-configure*'))[0]
    except IndexError:
        error_and_exit.error("cov-configure not found in bin directory at location: {}".format(cov_bin))
    return '"{}" -c "{}" {}'.format(cov_configure_path, os.path.join(cov_conf, "bld.xml"), spec)


def run_cmd(cmd, curdir=None, suppress_output=False, env=None):
    logging.debug("command to run in run_cmd {}".format(cmd))
    if env and curdir:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True,
                                   cwd=curdir)
    elif env:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    elif curdir:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, cwd=curdir)
    else:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    while True:
        try:
            realtime_output = process.stdout.readline().decode("utf-8")
            if realtime_output == '' and process.poll() is not None:
                break
            if realtime_output:
                try:
                    if not suppress_output:
                        logging.info(realtime_output.strip())
                    if suppress_output:
                        logging.debug(realtime_output.strip())
                except UnicodeEncodeError:
                    logging.warning("UnicodeEncodeError Exception occurred: skipping a line")
                except UnicodeDecodeError:
                    logging.warning("UnicodeDecodeError Exception occurred: skipping a line")
        except UnicodeEncodeError:
            logging.warning("UnicodeEncodeError Exception occurred: skipping a line")
        except UnicodeDecodeError:
            logging.warning("UnicodeDecodeError Exception occurred: skipping a line")
    return process.returncode


def run_cmd_emit(cmd):
    logging.debug("command to run in run_cmd_emit {}".format(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, encoding='utf-8')
    return p.stdout.replace(os.linesep, '\n').split('\n')


def value_getstatusoutput(output):
    status = False
    if output[0] == 0:  ## success
        status = True
        return status, output[1]
    else:  ## failed
        return status, "no path found matching pattern"


def resolve_path(path):
    """
    Function to resolve a path that contains "../" segments
    For example /lib/a/b/../c -> /lib/a/c.
    param: (string) path
    return: (string) resolved path
    """
    new_path = []
    for component in path.split('/'):
        if len(component) > 0:
            if component == '..':
                new_path = new_path[0:len(new_path) - 1]
            else:
                new_path = new_path + [component]
    return '/' + '/'.join(new_path)


def error_and_exit(message):
    logging.error(message)
    sys.exit(1)
