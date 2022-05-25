import numpy as np
import ctypes
import sys


class CtypeField():
  def __init__(self, field_name, dtype, shape=None, ndim=None):
    self.field_name = field_name
    self.dtype = dtype
    self.shape = shape
    self.ndim = ndim
    if shape != None:
      self.ndim = len(shape)

  def to_input_tuple(self):    
    if self.ndim == None:
      data = (self.field_name, self.dtype)
    else:
      if self.ndim == 1:
        pointer = ctypes.POINTER(self.dtype)
      elif self.ndim == 2:
        pointer = ctypes.POINTER(self.dtype * self.shape[0])
      elif self.ndim == 3:
        pointer = ctypes.POINTER(self.dtype * self.shape[0] * self.shape[1])    
      else:
        raise Exception()
      data = (self.field_name, pointer)
    return data

  def to_output_tuple(self):    
    if self.ndim == None:
      data = (self.field_name, self.dtype)
    else:
      np_dtype = to_numpy_dtype(self.dtype)
      pointer = np.ctypeslib.ndpointer(dtype=np_dtype, ndim=self.ndim)
      data = (self.field_name, pointer)
    return data

class StructFactory():

  def _create_struct(self, ctype_fields, struct_fields):
    class Struct( ctypes.Structure ):
      _fields_ = struct_fields

      def __init__(self):
        self.fields = {}     
        for ctype_field in ctype_fields:
          self.fields[ctype_field.field_name] = ctype_field   
    return Struct() 
  
  def create_input_struct(self, ctype_fields):
    input_struct = self._create_struct(ctype_fields, [ctype_field.to_input_tuple() for ctype_field in ctype_fields])
    for ctype_field in ctype_fields:
      input_struct.fields[ctype_field.field_name] = ctype_field
      if ctype_field.shape != None:
        if ctype_field.ndim == 1:
          setattr(input_struct, ctype_field.field_name, (ctype_field.dtype * ctype_field.shape[0])())
        elif ctype_field.ndim == 2:
          setattr(input_struct, ctype_field.field_name, ( (ctype_field.dtype * ctype_field.shape[0]) * ctype_field.shape[1] )())
        elif ctype_field.ndim == 3:
          setattr(input_struct, ctype_field.field_name, ( ( ( (ctype_field.dtype * ctype_field.shape[0]) * ctype_field.shape[1] ) * ctype_field.shape[2] ) )())
 
    return input_struct


  def create_output_struct(self, ctype_fields):
    return self._create_struct(ctype_fields, [ctype_field.to_output_tuple() for ctype_field in ctype_fields])


def to_numpy_dtype(dtype):
  if dtype == ctypes.c_int:
    return np.int32
  elif dtype == ctypes.c_double:
    return np.double              

def update_struct(src_dict, struct):
  for field_name, field_type in struct._fields_:
    if field_name in src_dict:
      np_dtype = to_numpy_dtype(struct.fields[field_name].dtype)  
      if field_type in [ctypes.c_double, ctypes.c_int]:
        value = np_dtype(src_dict[field_name])
        setattr(struct, field_name, value)
      else:             
        np_dtype = to_numpy_dtype(struct.fields[field_name].dtype)
        ndarray = np.array(src_dict[field_name], dtype=np_dtype)                    
        src_dict[field_name] = ndarray #prevent pointer of ndarray reassigned
        setattr(struct, field_name, ndarray.ctypes.data_as(field_type))    

def struct_to_dict(struct):
  data = {}
  struct.fields
  for field_name in struct.fields.keys():
    np_dtype = to_numpy_dtype(struct.fields[field_name].dtype)  
    if struct.fields[field_name].shape == None:
      value = np_dtype(getattr(struct, field_name))
    else:
      ptr = getattr(struct, field_name)      
      shape = struct.fields[field_name].shape      
      value = make_nd_array(ptr, shape, dtype=np_dtype)    
    data[field_name] = value              
  return data

def make_nd_array(c_pointer, shape, dtype=np.float64, order='C', own_data=True):
  arr_size = np.prod(shape[:]) * np.dtype(dtype).itemsize 
  if sys.version_info.major >= 3:
    buf_from_mem = ctypes.pythonapi.PyMemoryView_FromMemory
    buf_from_mem.restype = ctypes.py_object
    buf_from_mem.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
    buffer = buf_from_mem(c_pointer, arr_size, 0x100)
  else:
    buf_from_mem = ctypes.pythonapi.PyBuffer_FromMemory
    buf_from_mem.restype = ctypes.py_object
    buffer = buf_from_mem(c_pointer, arr_size)
  arr = np.ndarray(tuple(shape[:]), dtype, buffer, order=order)
  if own_data and not arr.flags.owndata:
    return arr.copy().tolist()
  else:
      return arr.tolist()

