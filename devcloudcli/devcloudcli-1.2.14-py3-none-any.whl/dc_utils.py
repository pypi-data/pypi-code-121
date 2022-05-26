# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Author: Karthik Kumaar <karthikx.kumaar@intel.com>

from email.policy import default
import pexpect
import os
import sys
import json
import re


defaultInput={"password for*": "intel123",
            "Password*":"intel123",
            "Do you want to continue?": "Y"}


def execute_process(process_string, serviceName, version=None):
    '''
    Execute the process from CLI, 
    cmd will look for scripts inside /opt/eval/ folder 
    '''
    ret_status = True
    try:
        if process_string != "":
            cmd = "/bin/bash -c 'ls'"
            cmd = "/bin/bash -c '{0}.sh {1}'".format(process_string,serviceName)
            #cmd = "/bin/bash -c '{0} {1}'".format(process_string,serviceName)
        else:
            return("Command not found")
        result = expect_wrapper(cmd)
        return(result)

    except BaseException as error:
        print('{0}:An exception occurred: {1}'.format(__file__, error))
        ret_status = False

    return ret_status

def processArgs(process_string,serviceName):
    '''
    Get arguments based on user entry in CLI
    '''
    try:
        execute_process(process_string,serviceName)
    
    except BaseException as error:
        print('An exception occurred: {0}'.format(error))
        raise


def expect_wrapper(cmd, input_dict=defaultInput):
    '''
    Execute command for spawning child applications using pexpect
    '''
    try:
        child = pexpect.spawn(cmd, timeout=None, encoding='utf8')
        child.logfile = sys.stdout
        temp = list(input_dict.keys())
        temp.append(pexpect.EOF)
        #print_msg("Temp {0}".format(temp))
        while child.isalive():
            i = child.expect(temp)
            #print_msg("Input expect {0} ".format(i))
            if i != len(temp)-1:
                child.setecho(True)
                child.sendline((list(input_dict.values())[i]))
            else:
                break
        child.close()
        try:
            '''
            Decoding CLI output for reports
            '''
            data=child.before
            # ansi_escape_8bit = re.compile(br'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])')
            # data=ansi_escape_8bit.sub(b'', data)
            # data=data.replace(b'\r',b'')
            #data=data.decode("latin-1")
            print("Command line output for: {0} {1}".format(cmd,data))
        except BaseException as error:
            print('An exception occurred while decoding CLI output: {}'.format(error))
        finally:
            return (child.before, child.status, child.exitstatus)
    except BaseException as error:
        print('An exception occurred in wrapper: {}'.format(error))
        raise
