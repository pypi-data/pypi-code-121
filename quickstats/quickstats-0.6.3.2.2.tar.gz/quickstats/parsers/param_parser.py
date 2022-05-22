from typing import Optional, Union, Dict, List
import os
import re
import copy
import glob
import fnmatch
import itertools

import numpy as np

from quickstats import semistaticmethod
from quickstats.maths.numerics import pretty_float, str_encode_value, str_decode_value


signature_regex = {
    'F': r"\d+[.]?\d*",
    'P': r"n?\d+p?\d*",
    'S': r"\w+"
}

signature_parser = {
    'F': pretty_float,
    'P': str_decode_value,
    'S': str
}

signature_regex = {
    'F': r"\d+[.]?\d*",
    'P': r"n?\d+p?\d*",
    'S': r"\w+"
}

signature_parser = {
    'F': pretty_float,
    'P': str_decode_value,
    'S': str
}

class ParamParser:
    
    DEFAULT_FORMAT_STR = r"[\w-]+"
    
    DEFAULT_FILE_EXT = ".root"
    
    @property
    def format_str(self):
        return self._format_str
    
    @format_str.setter
    def format_str(self, val):
        if val is None:
            self._format_str = self.DEFAULT_FORMAT_STR
        else:
            self._format_str = val
        self.fname_regex   = self.get_fname_regex(self._format_str, self.file_ext)
        self.attribute_parser = self.get_attribute_parser(self._format_str)
        
    @property
    def file_ext(self):
        return self._file_ext
    
    @file_ext.setter
    def file_ext(self, val):
        if val is None:
            self._file_ext = self.DEFAULT_FILE_EXT
        else:
            if not val.startswith("."):
                self._file_ext = f".{val}"
            else:
                self._file_ext = val

    def __init__(self, format_str:Optional[str]=None,
                 param_str:Optional[str]=None,
                 file_ext:Optional[str]=None,
                 allow_none:bool=True):
        self.allow_none = allow_none
        self.setup(format_str, param_str, file_ext)
    
    def setup(self, format_str:Optional[str]=None,
              param_str:Optional[str]=None,
              file_ext:Optional[str]=None):
        self.file_ext   = file_ext
        self.format_str = format_str
        self.param_str  = param_str
        self.param_names = self._get_param_names(self.format_str, self.param_str)

    @semistaticmethod
    def _get_param_names(self, format_str:Optional[str]=None,
                        param_str:Optional[str]=None):
        ext_param_names = self._get_format_str_attributes(format_str)
        int_param_names = self._get_param_str_attributes(param_str)
        if set(int_param_names) & set(ext_param_names):
            raise RuntimeError("internal and external parameters are not mutually exclusive")
        return sorted(int_param_names + ext_param_names)
            
    @staticmethod
    def get_signature_map(format_str:str):
        attribute_groups = re.findall(r"<(\w+)\[(\w)\]>", format_str)
        signature_map = {}
        for group in attribute_groups:
            attribute, signature = group[0], group[1]
            signature_map[attribute] = signature
        return signature_map
    
    @staticmethod
    def get_fname_regex(format_str:str, ext:Optional[str]=None):
        if ext is None:
            ext = ParamParser.DEFAULT_FILE_EXT    
        expr = format_str
        signature_map = ParamParser.get_signature_map(format_str)
        for attribute, signature in signature_map.items():
            attribute_expr = signature_regex.get(signature.upper(), None)
            if expr is None:
                raise ValueError(f"unknown signature `{signature}`")
            group_expr = f"(?P<{attribute}>{attribute_expr})"
            expr = expr.replace(f"<{attribute}[{signature}]>", group_expr)
        expr += (ext.replace('.', r'\.') + "$")
        regex = re.compile(expr)
        return regex
   
    @staticmethod
    def sort_param_points(param_points:List, attributes:List):
        key = lambda d: tuple(d['parameters'][attrib] for attrib in attributes)
        return sorted(param_points, key=key)
    
    @semistaticmethod
    def get_attribute_parser(self, format_str:str):
        attribute_parser = {}
        signature_map = self.get_signature_map(format_str)
        for attribute, signature in signature_map.items():
            parser = signature_parser.get(signature, None)
            if parser is None:
                raise ValueError(f"unknown signature `{signature}`")
            attribute_parser[attribute] = parser
        return attribute_parser
    
    @staticmethod
    def _get_param_str_attributes(param_str:Optional[str]=None):
        if param_str is None:
            return []
        attributes = []
        param_expr_list = [s.strip() for s in param_str.split(',')]
        param_expr_list = [s for s in param_expr_list if s]
        for expr in param_expr_list:
            tokens = expr.split('=')
            if len(tokens) not in [1, 2]:
                raise ValueError('invalid expression for parameterisation')
            attribute = tokens[0]
            if attribute not in attributes:
                attributes.append(attribute)
        return attributes
    
    @semistaticmethod
    def _get_format_str_attributes(self, format_str:Optional[str]=None):
        if format_str is None:
            return []
        attribute_parser = self.get_attribute_parser(format_str)
        return list(attribute_parser)

    @staticmethod
    def parse_param_str(param_str:Optional[str]=None):
        if param_str is None:
            return {}
        param_values = {}
        param_expr_list = [s.strip() for s in param_str.split(',')]
        param_expr_list = [s for s in param_expr_list if s]
        for expr in param_expr_list:
            tokens = expr.split('=')
            # floating poi
            if len(tokens) == 1:
                param_name = tokens[0]
                if param_name in param_values:
                    raise RuntimeError(f"profiled parameter {param_name} appeared more than once in the parameter "
                                       f"expression: {param_str}")
                param_values[param_name] = [None]
                continue
            if len(tokens) != 2:
                raise ValueError('invalid expression for parameterisation')
            param_name = tokens[0]
            values_expr = tokens[1]
            tokens = values_expr.split('_')
            # fixed value
            if len(tokens) == 1:
                values = [float(tokens[0])]
            # scan across range
            elif len(tokens) == 3:
                poi_min = float(tokens[0])
                poi_max = float(tokens[1])
                poi_step = float(tokens[2])
                values = np.arange(poi_min, poi_max + poi_step, poi_step)
            else:
                raise ValueError('invalid expression for parameterisation')
            if param_name not in param_values:
                param_values[param_name] = np.array([])
            if None in param_values[param_name]:
                raise RuntimeError(f"the parameter {param_name} is being profiled and non-profiled at the same time "
                                   f"in the parameter expression: {param_str}")
            param_values[param_name] = np.concatenate([param_values[param_name], values])
        param_names = list(param_values.keys())
        combinations = [param_values[param_name] for param_name in param_names]
        combinations = itertools.product(*combinations)
        param_points = []
        for combination in combinations:
            param_point = {k:v for k,v in zip(param_names, combination)}
            param_points.append(param_point)
        return param_points
    
    @staticmethod
    def val_encode_parameters(parameters:Dict):
        tokens = []
        for param, value in parameters.items():
            if value is None:
                token = f"{param}"
            else:
                token = f"{param}={round(value, 8)}"
            tokens.append(token)
        return ",".join(tokens)
    
    @staticmethod
    def str_encode_parameters(parameters:Dict):
        encoded_str_list = []
        for param, value in parameters.items():
            if isinstance(value, float):
                value = str_encode_value(round(value, 8))
            encoded_str = f"{param}_{value}"
            encoded_str_list.append(encoded_str)
        return "_".join(encoded_str_list)

    def get_external_param_points(self, dirname:str="",
                                  filter_expr:Optional[str]=None,
                                  exclude_expr:Optional[str]=None):
        if os.path.isdir(dirname):
            fnames = glob.glob(os.path.join(dirname, '*'))
        else:
            fnames = glob.glob(dirname)
        param_points = []
        for fname in fnames:
            basename = os.path.basename(fname)
            match = self.fname_regex.match(basename)
            if not match:
                continue
            point = {'filename': fname, 'parameters':{}}
            point['basename'] = basename.split('.')[0]
            for key, value in match.groupdict().items():
                parser = self.attribute_parser[key]
                point['parameters'][key] = parser(value)
            param_points.append(point)
        attributes = list(self.attribute_parser)
        param_points = self.sort_param_points(param_points, attributes)
        selected_param_points = self.select_param_points(param_points, filter_expr,
                                                         exclude_expr, dict_key="parameters")
        return selected_param_points
    
    def get_internal_param_points(self, filter_expr:Optional[str]=None,
                                  exclude_expr:Optional[str]=None):
        param_points = self.parse_param_str(self.param_str)
        selected_param_points = self.select_param_points(param_points, filter_expr,
                                                         exclude_expr)
        return selected_param_points
    
    @staticmethod
    def parse_filter_expr(expr:Optional[str]=None):
        if expr is None:
            return {}
        tokens = expr.split(";")
        conditions = {}
        for token in tokens:
            subtokens = token.split("=")
            if len(subtokens) != 2:
                raise RuntimEerror(f"invalid filter/exclude expression `{expr}`")
            param_name = subtokens[0].strip()
            param_conditions = [s.strip() for s in subtokens[1].split(",")]
            conditions[param_name] = param_conditions
        return conditions
    
    @staticmethod
    def select_param_point(parameters, conditions:Dict, default:bool=True):
        selected = {}
        for param_name in conditions:
            if param_name not in parameters:
                selected[param_name] = default
                continue
            param_value = parameters[param_name]
            if isinstance(param_value, float):
                param_value = round(param_value, 8)
            param_value = str(param_value)
            param_conditions = conditions[param_name]
            selected[param_name] = any([fnmatch.fnmatch(param_value, cond) for cond in param_conditions])
        selected = all([v for v in selected.values()])
        return selected
    
    def select_param_points(self, param_points:List,
                            filter_expr:Optional[str]=None,
                            exclude_expr:Optional[str]=None,
                            dict_key:Optional=None):
        selected_param_points = []
        filter_conditions = self.parse_filter_expr(filter_expr)
        exclude_conditions = self.parse_filter_expr(exclude_expr)
        for param_point in param_points:
            if dict_key:
                parameters = param_point[dict_key]
            else:
                parameters = param_point               
            keep = True
            if filter_conditions:
                keep = self.select_param_point(parameters, filter_conditions, default=True)
            if exclude_conditions:
                keep &= not (self.select_param_point(parameters, exclude_conditions, default=False))
            if keep:
                selected_param_points.append(param_point)
        return selected_param_points
    
    def sanity_check(self, internal_param_points:Dict, external_param_points:Dict):
        if not self.allow_none:
            for int_point in internal_param_points:
                for param_name, param_value in int_point.items():
                    if param_value is None:
                        raise RuntimeError(f"profiled parameter is not allowed ({param_name})")
    
    def get_param_points(self, dirname:str="",
                         filter_expr:Optional[str]=None,
                         exclude_expr:Optional[str]=None):
        external_param_points = self.get_external_param_points(dirname, filter_expr, exclude_expr)     
        internal_param_points = self.get_internal_param_points(filter_expr, exclude_expr)
        self.sanity_check(internal_param_points, external_param_points)
        if len(internal_param_points) == 0:
            internal_param_points = [{}]
        param_points = []
        for ext_point in external_param_points:
            fname = ext_point['filename']
            basename = ext_point['basename']
            ext_params = ext_point['parameters']
            for int_params in internal_param_points:
                param_point = {}
                param_point['filename'] = fname
                param_point['basename'] = basename
                param_point['external_parameters'] = {**ext_params}
                param_point['internal_parameters'] = {**int_params}
                param_points.append(param_point)
        return param_points