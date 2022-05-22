from typing import List
import cppyy
import ctypes
import numpy as np

from quickstats.interface import cppyy as interface_cppyy

ctype_maps = {
    np.dtype('bool'): ctypes.c_bool,
    np.dtype('byte'): ctypes.c_byte,
    np.dtype('ubyte'): ctypes.c_ubyte,
    np.dtype('short'): ctypes.c_short,
    np.dtype('ushort'): ctypes.c_ushort,
    np.dtype('intc'): ctypes.c_int,
    np.dtype('uintc'): ctypes.c_uint,
    np.dtype('single'): ctypes.c_float,
    np.dtype('float32'): ctypes.c_float,
    np.dtype('double'): ctypes.c_double,
    np.dtype('float64'): ctypes.c_double,
    np.dtype('int64'): ctypes.c_int64,
    np.dtype('int32'): ctypes.c_int32
}

ctype_str_maps = {
    ctypes.c_int : "int",
    ctypes.c_uint : "unsigned int",
    ctypes.c_float : "float",
    ctypes.c_double : "double",
    ctypes.c_bool : "bool",
    ctypes.c_byte : "byte",
    ctypes.c_ubyte : "unsigned char",
    ctypes.c_short : "short",
    ctypes.c_ushort : "unsigned short",
    ctypes.c_int64 : "long",
    ctypes.c_long : "long",
}

py_type_str_maps = {
    str: "string",
    int: "int",
    float: "double",
    bool: "bool"
}

np_type_str_maps = {
    np.dtype('bool'): "bool",
    np.dtype('byte'): "char",
    np.dtype('ubyte'): "unsigned char",
    np.dtype('short'): "short",
    np.dtype('ushort'): "unsigned short",
    np.dtype('intc'): "int",
    np.dtype('uintc'): "unsigned int",
    np.dtype('single'): "float",
    np.dtype('float32'): "float",
    np.dtype('double'): "double",
    np.dtype('float64'): "double",
    np.dtype('int64'): "long long",
    np.dtype('int32'): "int"
}

typecode_to_np_type_maps = {
    'b': np.dtype('byte'),
    'B': np.dtype('ubyte'),
    'h': np.dtype('short'),
    'H': np.dtype('ushort'),
    'i': np.dtype('intc'),
    'I': np.dtype('uintc'),
    'l': np.dtype('int32'),
    'L': np.dtype('uint'),
    'q': np.dtype('int64'),
    'Q': np.dtype('ulonglong'),
    'f': np.dtype('float32'),
    'd': np.dtype('float64')
}

def as_vector(data:np.ndarray):
    if data.ndim != 1:
        raise ValueError("data must be 1D array")
    c_type = ctype_maps.get(data.dtype, None)
    if c_type is None:
        raise ValueError(f"unsupported data type \"{data.dtype}\"")
    c_type_p = ctypes.POINTER(c_type)
    c_type_str = ctype_str_maps[c_type]
    c_data = data.ctypes.data_as(c_type_p)
    size = data.shape[0]
    result = cppyy.gbl.VecUtils.as_vector[c_type_str](c_data, size)
    return result

def list2vec(data:List):
    if not isinstance(data, list):
        raise ValueError("data must be a python list")
    if not data:
        raise ValueError("data must have size > 0")
    dtype = type(data[0])
    if not all(isinstance(x, dtype) for x in data):
        raise ValueError("all elements in list must have same type")
    c_type = py_type_str_maps.get(dtype, None)
    if c_type is None:
        raise ValueError(f"unsupported data type \"{data.dtype}\"")
    vec = cppyy.gbl.std.vector[c_type](data)
    return vec

def as_c_array(data:np.ndarray):
    if data.ndim != 1:
        raise ValueError("data must be 1D array")
    c_type = ctype_maps.get(data.dtype, None)
    if c_type is None:
        raise ValueError(f"unsupported data type \"{data.dtype}\"")
    c_type_p = ctypes.POINTER(c_type)
    c_type_str = ctype_str_maps[c_type]
    c_data = data.ctypes.data_as(c_type_p)
    return c_data

def as_np_array(vec:cppyy.gbl.std.vector):
    if vec.value_type == 'std::string':
        return np.array([str(v) for v in vec])
    return np.array(vec.data())

def c_array_to_np_array(arr:"cppyy.LowLevelView", size:int, shape=None, copy:bool=True):
    if not hasattr(arr, 'typecode'):
        raise RuntimeError(f"input must be an instance of cppyy.LowLevelView")
    np_type = typecode_to_np_type_maps.get(arr.typecode, None)
    if not np_type:
        raise RuntimeError(f"unsupported typecode \"{arr.typecode}\"")
    arr.reshape((size,))
    np_arr = np.frombuffer(arr, dtype=np_type, count=size)
    if shape is not None:
        return np_arr.reshape(shape)
    if copy:
        return np.array(np_arr)
    return np_arr