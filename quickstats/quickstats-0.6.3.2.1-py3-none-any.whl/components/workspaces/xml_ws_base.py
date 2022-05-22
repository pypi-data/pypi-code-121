import os
import re
import time
import difflib
from functools import partial
from typing import Optional, Union, List, Dict

import numpy as np

import quickstats
from quickstats import semistaticmethod
from quickstats.components import AbstractObject
from quickstats.utils.io import Verbosity
from quickstats.utils.xml_tools import TXMLTree
from quickstats.utils.enums import GeneralEnum
from quickstats.maths.numerics import to_bool
from quickstats.utils.root_utils import load_macro,get_macro_TClass

import ROOT

class WSObjectType(GeneralEnum):
    DEFINED    = 0
    FUNCTION   = 1
    VARIABLE   = 2
    CONSTRAINT = 3

class XMLAttribType(GeneralEnum):
    STR        = 0
    BOOL       = 1
    INT        = 2
    FLOAT      = 3
    STR_LIST   = 4
    INT_LIST   = 5
    FLOAT_LIST = 6
    
ConversionOperators = {
    XMLAttribType.STR: str,
    XMLAttribType.BOOL: to_bool,
    XMLAttribType.INT: int,
    XMLAttribType.FLOAT: float,
    XMLAttribType.STR_LIST  : lambda s: [i.strip() for i in s.split(",") if i],
    XMLAttribType.INT_LIST  : lambda s: [int(i) for i in s.split(",") if i],
    XMLAttribType.FLOAT_LIST: lambda s: [float(i) for i in s.split(",") if i]
}

class XMLWSBase(AbstractObject):
    
    def __init__(self, source:Optional[Union[str, Dict]]=None, basedir:Optional[str]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.source = source
        if basedir is not None:
            self.basedir = basedir
        # source is a filepath
        elif isinstance(source, str):
            self.basedir = os.path.dirname(source)
        else:
            self.basedir = os.getcwd()
        self.suppress_roofit_message()
        self.custom_classes = {}
        
    @semistaticmethod
    def load_extension(self):
        extensions = quickstats.get_workspace_extensions()
        for extension in extensions:
            result = load_macro(extension)
            if (result is not None) and hasattr(ROOT, extension):
                self.stdout.info(f'INFO: Loaded extension module "{extension}"')
            cls = get_macro_TClass(extension)
            self.custom_classes[extension] = cls
    
    @staticmethod
    def suppress_roofit_message():
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.NumIntegration)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.Fitting)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.Minimization)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.InputArguments)
        ROOT.RooMsgService.instance().getStream(1).removeTopic(ROOT.RooFit.Eval)
        ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)
        
    def get_relpath(self, filename:str):
        if filename.startswith("/") or filename.startswith("~"):
            return filename
        return os.path.join(self.basedir, filename)
    
    def check_file_exist(self, filename:str):
        return os.path.exists(self.get_relpath(filename))        
    
    @semistaticmethod
    def _xml_to_dict(self, filename:str):
        try:
            xml_dict = TXMLTree(file=filename).to_dict()
        except:
            raise RuntimeError(f"failed to load xml document `{filename}`")
        return xml_dict
    
    @staticmethod
    def _get_node_attrib(node:Dict, attrib_name:str, required:bool=True,
                         default:Optional[str]=None,
                         dtype:Union[XMLAttribType,str]='str'):
        attrib_node = node['attrib']
        if attrib_name in attrib_node:
            attrib_val = attrib_node[attrib_name]
        else:
            if required:
                raise RuntimeError(f"attribute `{attrib_name}` not found in the "
                                   f"node `{node['tag']}`")
            else:
                attrib_val = default
        if not isinstance(attrib_val, str):
            return attrib_val
        attrib_val = re.sub('\s+', '', attrib_val)
        dtype = XMLAttribType.parse(dtype)
        attrib_val = ConversionOperators[dtype](attrib_val)
        return attrib_val
    
    def import_object(self, ws:ROOT.RooWorkspace, obj, *args, silent:bool=True):
        if silent:
            getattr(ws, "import")(obj, *args, ROOT.RooFit.Silence())        
        else:
            getattr(ws, "import")(obj, *args)    
    
    def import_expression(self, ws:ROOT.RooWorkspace, object_expr:str, check_defined:bool=False):
        object_name, object_type = self._get_object_name_and_type_from_expr(object_expr)
        # throw error when attemping to access undefined object
        if object_type == "defined":
            if (not ws.arg(object_name)):
                raise RuntimeError(f"object `{object_name}` does not exist")
            else:
                return object_name
        # throw error? when attemping to define already existing object
        if check_defined:
            if ws.arg(object_name):
                self.stdout.debug(f"REGTEST: object {object_name} already exists")
                return object_name
        self.stdout.debug(f"REGTEST: Generating {object_type} {object_expr}")
        status = ws.factory(object_expr)
        if not status:
            raise RuntimeError(f"object creation from expression `{object_expr}` had failed")
        return object_name
    
    @semistaticmethod
    def get_name_mapping_str(self, old_name:str, new_name:str, width:int=40):
        sequence = difflib.SequenceMatcher(None, old_name, new_name)
        match = sequence.find_longest_match(0, len(old_name), 0, len(new_name))
        ahead = old_name[ : match.a]
        atail = old_name[match.a + match.size : ]
        bhead = new_name[ : match.b]
        btail = new_name[match.b + match.size : ]
        common1 = old_name[match.a : match.a+match.size]
        common2 = new_name[match.b : match.b+match.size]
        result = f'{ahead}\033[91m{common1}\033[0m{atail}'.rjust(width, ' ') + ' -> ' + f'{bhead}\033[92m{common1}\033[0m{btail}'
        return result
    
    @semistaticmethod
    def get_name_mapping_str_arrays(self, rename_map:Dict):
        results = []
        if not rename_map:
            return results        
        width = max([len(i) for i in list(rename_map)]) + 20
        for old_name, new_name in rename_map.items():
            results.append(self.get_name_mapping_str(old_name, new_name, width))
        return results
    
    def get_workspace_arg(self, ws:ROOT.RooWorkspace, arg_name:str, strict:bool=True):
        obs = ws.arg(arg_name)
        if not arg_name:
            if strict:
                raise RuntimeError(f"variable {arg_name} does not exist in workspace")
            return None
        return obs    
    
    def import_expressions(self, ws:ROOT.RooWorkspace, object_expr_list:List[str],
                       check_defined:bool=False):
        object_names = []
        for object_expr in object_expr_list:
            object_name = self.import_expression(ws, object_expr, check_defined=check_defined)
            object_names.append(object_name)
        return ",".join(object_names)    