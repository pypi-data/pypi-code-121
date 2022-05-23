from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import functools
import sys
import pdb

import kdutils.division.decorator as decorator


ESTIMATOR_API_NAME = 'estimator'
KERAS_API_NAME = 'keras'
KD_API_NAME = 'kd'

SUBPACKAGE_NAMESPACES = [ESTIMATOR_API_NAME]

_Attributes = collections.namedtuple(
    'ExportedApiAttributes', ['names', 'constants'])

API_ATTRS = {
    KD_API_NAME: _Attributes(
        '_kd_api_names',
        '_kd_api_constants'),
    ESTIMATOR_API_NAME: _Attributes(
        '_estimator_api_names',
        '_estimator_api_constants'),
    KERAS_API_NAME: _Attributes(
        '_keras_api_names',
        '_keras_api_constants')
}

API_ATTRS_V1 = {
    KD_API_NAME: _Attributes(
        '_kd_api_names_v1',
        '_kd_api_constants_v1'),
    ESTIMATOR_API_NAME: _Attributes(
        '_estimator_api_names_v1',
        '_estimator_api_constants_v1'),
    KERAS_API_NAME: _Attributes(
        '_keras_api_names_v1',
        '_keras_api_constants_v1')
}

_NAME_TO_SYMBOL_MAPPING = dict()

_PACKET_TO_MAPPING = dict()

def f_s(f):
    nlist = f.split('.')
    if 'v1' in nlist:
        return
    # [0] 包名 [1]类名  [2] 函数  [3] 参数
    class_mapping = _PACKET_TO_MAPPING[nlist[0]] if _PACKET_TO_MAPPING.get(nlist[0], False)  else dict()
    function_list = class_mapping[nlist[1]] if class_mapping.get(nlist[1], False) else list()
    function_list.append(nlist[2])
    class_mapping[nlist[1]] = function_list
    _PACKET_TO_MAPPING[nlist[0]] = class_mapping
    
    
def get_symbol_sets():
    _PACKET_TO_MAPPING.clear()
    [f_s(func) for func in _NAME_TO_SYMBOL_MAPPING.keys()]
    return _PACKET_TO_MAPPING
    
def get_symbol_from_name(name):
    return _NAME_TO_SYMBOL_MAPPING.get(name)

class api_export(object):
    def __init__(self, *args, **kwargs):
        self._names = args
        self._names_v1 = kwargs.get('v1', args)
        self._api_name = kwargs.get('api_name', KD_API_NAME)
        self._overrides = kwargs.get('overrides', [])
        self._allow_multiple_exports = kwargs.get('allow_multiple_exports', False)
        self._validate_symbol_names()
        
    def _validate_symbol_names(self):
        all_symbol_names = set(self._names) | set(self._names_v1)
        if self._api_name == KD_API_NAME:
            for subpackage in SUBPACKAGE_NAMESPACES:
                if any(n.startswith(subpackage) for n in all_symbol_names):
                    raise InvalidSymbolNameError(
                        '@export is not allowed to export symbols under %s.*' % (subpackage))
        else:
            if not all(n.startswith(self._api_name) for n in all_symbol_names):
                raise InvalidSymbolNameError(
                    'Can only export symbols under package name of component. '
                    'e.g. tensorflow_estimator must export all symbols under '
                    'decorator.estimator')
                
    def __call__(self, func):
        api_names_attr = API_ATTRS[self._api_name].names
        api_names_attr_v1 = API_ATTRS_V1[self._api_name].names
        for f in self._overrides:
            _, undecorated_f = decorator.unwrap(f)
            delattr(undecorated_f, api_names_attr)
            delattr(undecorated_f, api_names_attr_v1)
            
        _, undecorated_func = decorator.unwrap(func)
        self.set_attr(undecorated_func, api_names_attr, self._names)
        self.set_attr(undecorated_func, api_names_attr_v1, self._names_v1)
        
        for name in self._names:
            _NAME_TO_SYMBOL_MAPPING[name] = func
        for name_v1 in self._names_v1:
            _NAME_TO_SYMBOL_MAPPING['compat.v1.%s' % name_v1] = func
        return func
    
    def set_attr(self, func, api_names_attr, names):
        if api_names_attr in func.__dict__:
            if not self._allow_multiple_exports:
                raise SymbolAlreadyExposedError(
                    'Symbol %s is already exposed as %s.' %
                    (func.__name__, getattr(func, api_names_attr)))  # pylint: disable=protected-access
        setattr(func, api_names_attr, names)
        
    def export_constant(self, module_name, name):
        module = sys.modules[module_name]
        api_constants_attr = API_ATTRS[self._api_name].constants
        api_constants_attr_v1 = API_ATTRS_V1[self._api_name].constants
        
        if not hasattr(module, api_constants_attr):
            setattr(module, api_constants_attr, [])
         
        getattr(module, api_constants_attr).append(
            (self._names, name))
        
        if not hasattr(module, api_constants_attr_v1):
            setattr(module, api_constants_attr_v1, [])
        getattr(module, api_constants_attr_v1).append(
            (self._names_v1, name))

        
        
export = functools.partial(api_export, api_name=KD_API_NAME)