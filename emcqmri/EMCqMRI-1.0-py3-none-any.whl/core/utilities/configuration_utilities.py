from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import argparse
import json
import logging

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


class ParseConfiguration(object):
    def __init__(self):
        pass
    
    def parse_configuration(self, configuration_file):
        self.configuration_file = configuration_file
        if os.path.isfile(self.configuration_file):
            configuration = parse_json_configuration(self.configuration_file)
            return configuration
        else:
            logging.error('Invalid path for configuration file: {}'.format(self.configuration_file))
            exit()


class DictToAttribute(object):

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __update__(self, **entries):
        self.__dict__.update(entries)

    def __list_attr__(self):
        for k, v in self.__dict__.items():
            print("*** {}--> '{}'".format(k,v))


class OptsToAttributes(object):
    def __init__(self, **entries):
        self.__dict__.update(**entries)

    def __update__(self, **entries):
        self.__dict__.update(entries)

    def __list_attr__(self):
        for key_, val_ in self.__dict__.items():
            print("Configuration: {}".format(key_))
            val_.__list_attr__()
            print("")
            

def parse_json_configuration(filename):
    with open(filename) as json_file:  
        config_params = json.load(json_file)
        config_parameters = {}
        for l1_keys in config_params.keys():
            for l2_keys in config_params[l1_keys].keys():
                for l3_keys in config_params[l1_keys][l2_keys].keys():
                    config_parameters[l3_keys] = config_params[l1_keys][l2_keys][l3_keys]
    return config_parameters


def convert_argparse_to_attr(config_args):
    task_console_configuration = {}
    for k in config_args.__dict__:
        if config_args.__dict__[k] is not None:
            task_console_configuration[k] = config_args.__dict__[k]
    return task_console_configuration