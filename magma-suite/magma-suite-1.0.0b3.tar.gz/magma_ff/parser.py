#!/usr/bin/env python3

################################################
#
#   Parser to handle compatibility between
#       magma and portal json formats
#
#   Michele Berselli
#   berselli.michele@gmail.com
#
################################################

################################################
#   Libraries
################################################
import sys, os
import json

################################################
#   ParserFF
################################################
class ParserFF(object):
    """
    """

    def __init__(self, input_json):
        """Initialize the object and set all attributes.

        :param input_json: MetaWorkflow[portal] or MetaWorkflowRun[portal]
        :type input_json: dict
        """
        self.in_json = input_json
    #end def

    def arguments_to_json(self):
        """Parse MetaWorkflow[portal] or MetaWorkflowRun[portal] stored as self.in_json.
        If input, convert and replace arguments in input from string to json.
        If workflows, for each step convert and replace arguments in input from string to json.
        """
        if self.in_json.get('input'):
            self._input_to_json(self.in_json['input'])
        #end if
        if self.in_json.get('workflows'):
            self._workflows_to_json(self.in_json['workflows'])
        #end if
        return self.in_json
    #end def

    def _workflows_to_json(self, workflows):
        """
        """
        for workflow in workflows:
            self._input_to_json(workflow['input'])
        #end for
    #end def

    def _input_to_json(self, input):
        """Loop through arguments in input and
        calls appropriate conversion function for argument_type.
        """
        for arg in input:
            if arg['argument_type'] == 'file':
                self._file_to_json(arg)
            else: # is parameter
                self._parameter_to_json(arg)
            #end if
        #end for
    #end def

    def _file_to_json(self, arg):
        """Convert file argument from string to json
        and replace the argument value (files).
        """
        if arg.get('files'):
            arg['files'] = self._files_to_json(arg['files'])
        #end if
    #end def

    def _files_to_json(self, files, sep=','):
        """Convert file argument from string to json.

        :param files: List of dictionaries representing files
            and information on their dimensional structure
            e.g. "files": [
                            {
                                "file": "A",
                                "dimension": "0"
                                # 0D missing, 1D X, 2D X:X, 3D X:X:X, ...
                            },
                            {
                               "file": "B",
                               "dimension": "1"
                            }
                        ]
        :type files: list(dict)
        :return: Converted argument value (files)
        :rtype: list(str)
        """
        list_ = []
        # Get max dimensions needed
        for file in files:
            dimension = file.get('dimension')
            if not dimension:
                return file.get('file')
            #end if
            dimension_ = list(map(int, dimension.split(sep)))
            # Expand input list based on dimensions
            self._init_list(list_, dimension_)
            # Add element
            tmp_list = list_
            for i in dimension_[:-1]:
                tmp_list = tmp_list[i]
            #end for
            tmp_list[dimension_[-1]] = file.get('file')
        #end for
        return list_
    #end def

    def _init_list(self, list_, dimension_):
        """ """
        tmp_list = list_
        for i in dimension_[:-1]:
            try: # index esist
                tmp_list[i]
            except IndexError: # create index
                for _ in range(i-len(tmp_list)+1):
                  tmp_list.append([])
            #end try
            tmp_list = tmp_list[i]
        #end for
        for _ in range(dimension_[-1]-len(tmp_list)+1):
            tmp_list.append(None)
        #end for
    #end def

    def _parameter_to_json(self, arg):
        """Convert parameter argument from string to json
        and replaces the argument value (value).

        possible values for value_type:
            json | string | integer | boolean | float
        """
        if not arg.get('value'):
            return
        #end if
        value = arg['value']
        value_type = arg['value_type']
        if value_type == 'json':
            value = json.loads(value)
        elif value_type == 'integer':
            value = int(value)
        elif value_type == 'float':
            value = float(value)
        elif value_type == 'boolean':
            if value.lower() == 'true':
                value = True
            else: value = False
            #end if
        #end if
        arg['value'] = value
        del arg['value_type']
    #end def

#end class
