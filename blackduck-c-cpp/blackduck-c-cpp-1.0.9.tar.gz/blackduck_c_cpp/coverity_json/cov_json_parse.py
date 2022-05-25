"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import os
import json
import logging
import re
from blackduck_c_cpp.util import global_settings


class CovJsonParser:
    """
    To get header, linker and executables from json generated from cov-emit-link tool
    """

    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.source_files_set = set()
        self.linker_files_set = set()
        self.executable_files_set = set()
        self.header_files_set = set()
        self.files_dict = {}
        self.file_id_kind_dict = {}

        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, 'r') as f:
                    self.raw_bdio_json = json.load(f)
            except PermissionError:
                logging.error(
                    "you don't have permission to read file {}, please make sure you correct permissions".format(
                        self.json_file_path))
        else:
            self.raw_bdio_json = {}
            logging.error(
                "coverity json file not created. please verify if build completed successfully and json is written")

    def create_file_id_dict(self):
        """
        Function to create a dictionary with file_id as key and value as path
        {1: /g/b/c/a.so,2: /CMakeFiles/b/c/temp.a...}
        """
        try:
            files_list_dict = self.raw_bdio_json['files']
            for each_file in files_list_dict:
                file = each_file['case-preserved']
                file_id = each_file['id']
                if file_id in self.files_dict:
                    continue
                else:
                    self.files_dict[file_id] = file.strip()
        except KeyError:
            self.files_dict = {}

    def add_file_to_set(self, input_dict, file_id_type):
        """
        Function to disambiguate files to source, header and executables list
        param: file_id_type: can be 'file_id' or 'primary_file_id' from json
                input_dict: dictionary with file_id,kind as keys
                eg: {file:id: 1, kind: 'shared library'}
        """
        try:
            if len(self.file_id_kind_dict[input_dict[file_id_type]]) > 1:
                file = self.files_dict[input_dict[file_id_type]]
                if re.match(global_settings.so_pattern, file.strip()) or re.match(global_settings.dll_pattern,
                                                                                  file.strip()):
                    input_dict['kind'] = 'shared library'
                elif re.match(global_settings.a_pattern, file.strip()) or re.match(global_settings.lib_pattern,
                                                                                   file.strip()):
                    input_dict['kind'] = 'static library'
                elif re.match(global_settings.o_pattern, file.strip()) or re.match(global_settings.obj_pattern,
                                                                                   file.strip()):
                    input_dict['kind'] = 'object file'
                elif re.match(global_settings.c_pattern, file.strip()) or re.match(global_settings.cpp_pattern,
                                                                                   file.strip()) or re.match(
                    global_settings.cxx_pattern, file.strip()) or re.match(global_settings.cp_pattern,
                                                                           file.strip()) or re.match(
                    global_settings.cc_pattern, file.strip()) or re.match(
                    global_settings.cplus_pattern, file.strip()) or re.match(
                    global_settings.cppm_pattern, file.strip()) or re.match(
                    global_settings.ixx_pattern, file.strip()) or re.match(global_settings.h_pattern,
                                                                          file.strip()) or re.match(
                    global_settings.hpp_pattern,
                    file.strip()) or re.match(
                    global_settings.hxx_pattern, file.strip()):
                    input_dict['kind'] = 'source file'

            if input_dict['kind'] == "source file":
                self.source_files_set.add(self.files_dict[input_dict[file_id_type]])
            elif input_dict['kind'] == "shared library" or input_dict['kind'] == "static library" or input_dict[
                'kind'] == "object file":
                self.linker_files_set.add(self.files_dict[input_dict[file_id_type]])
            elif input_dict['kind'] == "executable":
                self.executable_files_set.add(self.files_dict[input_dict[file_id_type]])
        except KeyError:
            pass

    def parse_for_files(self, unit_type):
        """
        Function to look at each dictionary in translation units and link units and
        call function to disambiguate files to source, header and executables list
        param: unit_type: 'translation units' or 'link-units'
        """
        try:
            tu_list_dict = self.raw_bdio_json[unit_type]
            for each_tu_dict in tu_list_dict:
                # logging.debug("each_tu_dict is {}".format(each_tu_dict))
                self.add_file_to_set(each_tu_dict, 'primary-file-id')
                for each_input_dict in each_tu_dict['input-files']:
                    # logging.debug("each_input_dict is {}".format(each_input_dict))
                    self.add_file_to_set(each_input_dict, 'file-id')
        except KeyError:
            logging.error("Unit not found in json: {}".format(unit_type))

    def add_file_to_dict(self, input_dict, file_id_type):
        """
        function to create dictionary with key as file-id amd value as list of all kinds
        params: file_id_type: can be 'file_id' or 'primary_file_id' from json
                input_dict: dictionary with file_id,kind as keys
        """
        if input_dict[file_id_type] in self.file_id_kind_dict:
            self.file_id_kind_dict[input_dict[file_id_type]].add(input_dict['kind'])
        else:
            self.file_id_kind_dict[input_dict[file_id_type]] = set([input_dict['kind']])

    def create_ambiguous_files_dict(self):
        """
        function to iterate through json and call another function to
        create dictionary with key as file-id amd value as list of all kinds
        for it from both translation and link units
        """
        units = ['translation-units', 'link-units']
        for each_unit in units:
            try:
                tu_list_dict = self.raw_bdio_json[each_unit]
                for each_tu_dict in tu_list_dict:
                    self.add_file_to_dict(each_tu_dict, 'primary-file-id')
                    for each_input_dict in each_tu_dict['input-files']:
                        self.add_file_to_dict(each_input_dict, 'file-id')
            except KeyError:
                logging.error("Unit not found in json: {}".format(each_unit))
                self.file_id_kind_dict = {}

    def get_header_files(self):
        """
        function to select header files from source files
        """
        return {file for file in self.source_files_set if file != ':' and (
                re.match(global_settings.hxx_pattern, file) or re.match(global_settings.hpp_pattern, file) or
                re.match(global_settings.h_pattern, file)) and os.path.exists(file)}

    def run(self):
        if self.raw_bdio_json:
            self.create_file_id_dict()
            self.create_ambiguous_files_dict()
            self.parse_for_files('translation-units')
            self.parse_for_files('link-units')
            self.header_files_set = self.get_header_files()
            logging.debug(
                "number of distinct executable files from coverity json are {}".format(len(self.executable_files_set)))
            logging.debug(
                "number of distinct linker files from coverity json are {}".format(len(self.linker_files_set)))
            logging.debug(
                "number of distinct header files from coverity json are {}".format(len(self.header_files_set)))
            return self.header_files_set, self.linker_files_set, self.executable_files_set
