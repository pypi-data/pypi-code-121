# -*- coding: utf-8 -*-

from collections import OrderedDict
import configparser
import io
import os
import pickle
import sys


class FileReader:
    @staticmethod
    def read_file_list(filename, encoding='utf-8'):
        to_ret = []
        if sys.version[0] == '3':
            with open(filename, encoding=encoding) as f:
                for line in f:
                    to_ret.append(line.strip())
        else:
            with io.open(filename, encoding=encoding) as f:
                for line in f:
                    to_ret.append(line.strip())
        return to_ret

    @staticmethod
    def read_file_property(filename, section_name, key):
        config = configparser.ConfigParser()
        config.read_file(filename, encoding='utf-8')
        if section_name not in config or key not in config[section_name]:
            return None
        return config[section_name][key]

    @staticmethod
    def get_json_cfg(filename):
        dir_path = os.path.dirname(__file__)
        cfg_path = os.path.join(dir_path, '../../cfg/' + filename)
        cfg_string = FileReader.get_file_content(cfg_path)
        return cfg_string

    @staticmethod
    def get_file_content(filename):
        file_object = open(filename, 'r', encoding='utf-8') if sys.version[0] == '3' else io.open(filename, 'r', encoding='utf-8')
        try:
            content = file_object.read()
        finally:
            file_object.close()
        return content

    @staticmethod
    def load_progress(file_name, equ_init_date):
        """
        读取个股处理进度字典，
        :param file_name: @format "stock start_date" or "stock"
        :param equ_init_date:
        :return: {stock:start_date}
        """
        stock_progress_list = FileReader.read_file_list(file_name)
        stock_progress_dict = OrderedDict()
        for line in stock_progress_list:
            items = line.split(',')
            stock_progress_dict[items[0]] = equ_init_date if len(items) == 1 else items[1]
        return stock_progress_dict

    @staticmethod
    def load_object_from_file(file_name):
        obj = pickle.load(open(file_name, 'rb'))
        return obj