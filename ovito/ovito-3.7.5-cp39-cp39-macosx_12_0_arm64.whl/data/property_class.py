import numpy
import contextlib
from . import Property
from .ovito_ndarray_adapter import add_ndarray_interface

# Give the Property class a Numpy-like interface.
add_ndarray_interface(Property)

# Returns a NumPy array wrapper for a property.
# For backward compatibility with OVITO 2.9.0:
def _Property_array(self):
    # This attribute returns a NumPy array, which provides read access to the per-element data stored in this property object.
    return self.__array__()
Property.array = property(_Property_array)

# Returns a NumPy array wrapper for a property with write access.
# For backward compatibility with OVITO 2.9.0:
def _Property_marray(self):
    with self: 
        return self.__array__()

# This is needed to enable the augmented assignment operators (+=, -=, etc.) for the 'marray' property.
# For backward compatibility with OVITO 2.9.0:
def _Property_marray_assign(self, other):
    if not hasattr(other, "__array_interface__"):
        raise ValueError("Only objects supporting the array interface can be assigned to the 'marray' property.")
    o = other.__array_interface__
    s = self.__array_interface__
    if o["shape"] != s["shape"] or o["typestr"] != s["typestr"] or o["data"] != s["data"]:
        raise ValueError("Assignment to the 'marray' property is restricted. Left and right-hand side must be identical.")
    # Assume that the data has been changed in the meantime.
    self.notify_object_changed()

# For backward compatibility with OVITO 2.9.0:
Property.marray = property(_Property_marray, _Property_marray_assign)
Property.get_type_by_id = lambda self, id: self.type_by_id(id)
Property.get_type_by_name = lambda self, name: self.type_by_name(name)
Property.type_list = property(lambda self: self.types)
