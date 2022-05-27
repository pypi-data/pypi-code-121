import numpy
import contextlib

# A Numpy array sub-class, which represents a view into an OVITO data object.
# This class manages write access to the underlying data values manages by the OVITO object.
class DataArrayView(numpy.ndarray):

    # No-op context manager, which is used if a DataArrayView object is not backed by an OVITO data object. 
    # For example, if the DataArrayView was created by a call to numpy.zeros_like(<DataObject>), then it inherits 
    # the ndarray sub-type from the given input array but has its own memory.
    _write_access_manager = contextlib.nullcontext()

    def __new__(cls, input_array, write_access_manager):
        # Input array is an already formed ndarray instance. We first cast to be our class type.
        obj = input_array.view(cls)
        # Keep a reference to the underlying OVITO object managing the memory.
        obj._write_access_manager = write_access_manager
        # Finally, return the newly created object.
        return obj

    # __array_finalize__() is the mechanism that Numpy provides to allow subclasses to 
    # handle the various ways that new instances get created.
    def __array_finalize__(self, obj):
        if obj is None: return
        # Do not keep a reference to the underlying OVITO object if this NumPy array manages its own memory (independent of OVITO).
        # To find out, we need to walk up the chain of base objects.
        b = self
        while isinstance(b, numpy.ndarray):
            if b.flags.owndata: return
            b = b.base
        try:
            self._write_access_manager = obj._write_access_manager
        except AttributeError:
            pass

    # Indexed assignment.
    def __setitem__(self, idx, value):
        # Request write access to the underlying OVITO data:
        with self._write_access_manager: super().__setitem__(idx, value)

    # Augmented arithmetic assignment operators, which all require write access to the underlying array data:
    def __iadd__(self, y):
        with self._write_access_manager: return super().__iadd__(y)
    def __isub__(self, y):
        with self._write_access_manager: return super().__isub__(y)
    def __imul__(self, y):
        with self._write_access_manager: return super().__imul__(y)
    def __idiv__(self, y):
        with self._write_access_manager: return super().__idiv__(y)
    def __itruediv__(self, y):
        with self._write_access_manager: return super().__itruediv__(y)
    def __ifloordiv__(self, y):
        with self._write_access_manager: return super().__ifloordiv__(y)
    def __imod__(self, y):
        with self._write_access_manager: return super().__imod__(y)
    def __ipow__(self, y):
        with self._write_access_manager: return super().__ipow__(y)
    def __iand__(self, y):
        with self._write_access_manager: return super().__iand__(y)
    def __ior__(self, y):
        with self._write_access_manager: return super().__ior__(y)
    def __ixor__(self, y):
        with self._write_access_manager: return super().__ixor__(y)

# This helper method adds methods and properties to a DataObject-derived
# class to make it behave like a Numpy array. The DataObject-derived class
# must implement the __array__impl__() special method, which returns 
# a Numpy array view of the unterlying memory. Furthermore, the DataObject-derived
# class must implement the context manager interface, which is used to request
# explicit write access to the underlying data. 
def add_ndarray_interface(cls):

    # Indexing:
    cls.__getitem__ = lambda self, idx: self.__array__()[idx]

    # Indexed assignment.
    def __setitem__(self, idx, value):
        # Write access to a property array requires a 'with' Python statement.
        with self: self.__array__impl__()[idx] = value
    cls.__setitem__ = __setitem__

    # Implementation of the Numpy array protocol:
    def __array__(self, dtype=None):
        return DataArrayView(self.__array__impl__(dtype), self)
    cls.__array__ = __array__

    # Array element iteration.
    cls.__iter__ = lambda self: iter(self.__array__())

    # Printing / string representation.
    cls.__repr__ = lambda self: self.__class__.__name__ + "('" + self.name + "')"

    # Implement 'shape' attribute.
    cls.shape = property(lambda self: self.__array__impl__().shape)

    # Implement 'ndim' attribute.
    cls.ndim = property(lambda self: self.__array__impl__().ndim)

    # Implement 'dtype' attribute.
    cls.dtype = property(lambda self: self.__array__impl__().dtype)

    # Implement 'T' attribute (array transposition).
    cls.T = property(lambda self: self.__array__().T)

    # Standard array operators.
    cls.__eq__ = lambda self, y: self.__array__impl__().__eq__(y)
    cls.__ne__ = lambda self, y: self.__array__impl__().__ne__(y)
    cls.__lt__ = lambda self, y: self.__array__impl__().__lt__(y)
    cls.__le__ = lambda self, y: self.__array__impl__().__le__(y)
    cls.__gt__ = lambda self, y: self.__array__impl__().__gt__(y)
    cls.__ge__ = lambda self, y: self.__array__impl__().__ge__(y)
    cls.__nonzero__ = lambda self: self.__array__impl__().__nonzero__()
    cls.__neg__ = lambda self: self.__array__impl__().__neg__()
    cls.__pos__ = lambda self: self.__array__impl__().__pos__()
    cls.__abs__ = lambda self: self.__array__impl__().__abs__()
    cls.__invert__ = lambda self: self.__array__impl__().__invert__()
    cls.__add__ = lambda self, y: self.__array__impl__().__add__(y)
    cls.__sub__ = lambda self, y: self.__array__impl__().__sub__(y)
    cls.__mul__ = lambda self, y: self.__array__impl__().__mul__(y)
    cls.__matmul__ = lambda self, y: self.__array__impl__().__matmul__(y)
    cls.__div__ = lambda self, y: self.__array__impl__().__div__(y)
    cls.__divmod__ = lambda self, y: self.__array__impl__().__divmod__(y)
    cls.__truediv__ = lambda self, y: self.__array__impl__().__truediv__(y)
    cls.__floordiv__ = lambda self, y: self.__array__impl__().__floordiv__(y)
    cls.__lshift__ = lambda self, y: self.__array__impl__().__lshift__(y)
    cls.__rshift__ = lambda self, y: self.__array__impl__().__rshift__(y)
    cls.__mod__ = lambda self, y: self.__array__impl__().__mod__(y)
    cls.__pow__ = lambda self, y: self.__array__impl__().__pow__(y)
    cls.__and__ = lambda self, y: self.__array__impl__().__and__(y)
    cls.__or__ = lambda self, y: self.__array__impl__().__or__(y)
    cls.__xor__ = lambda self, y: self.__array__impl__().__xor__(y)

    # Binary arithmetic operations with reflected (swapped) operands:
    cls.__radd__ = lambda self, y: self.__array__impl__().__radd__(y)
    cls.__rsub__ = lambda self, y: self.__array__impl__().__rsub__(y)
    cls.__rmul__ = lambda self, y: self.__array__impl__().__rmul__(y)
    cls.__rmatmul__ = lambda self, y: self.__array__impl__().__rmatmul__(y)
    cls.__rtruediv__ = lambda self, y: self.__array__impl__().__rtruediv__(y)
    cls.__rfloordiv__ = lambda self, y: self.__array__impl__().__rfloordiv__(y)
    cls.__rmod__ = lambda self, y: self.__array__impl__().__rmod__(y)
    cls.__rdivmod__ = lambda self, y: self.__array__impl__().__rdivmod__(y)
    cls.__rpow__ = lambda self, y: self.__array__impl__().__rpow__(y)
    cls.__rlshift__ = lambda self, y: self.__array__impl__().__rlshift__(y)
    cls.__rrshift__ = lambda self, y: self.__array__impl__().__rrshift__(y)
    cls.__rand__ = lambda self, y: self.__array__impl__().__rand__(y)
    cls.__rxor__ = lambda self, y: self.__array__impl__().__rxor__(y)
    cls.__ror__ = lambda self, y: self.__array__impl__().__ror__(y)

    # Augmented arithmetic assignment operators, which require write access to the array:
    def __iadd__(self, y):
        with self: self.__array__impl__().__iadd__(y)
        return self
    cls.__iadd__ = __iadd__

    def __isub__(self, y):
        with self: self.__array__impl__().__isub__(y)
        return self
    cls.__isub__ = __isub__

    def __imul__(self, y):
        with self: self.__array__impl__().__imul__(y)
        return self
    cls.__imul__ = __imul__

    def __idiv__(self, y):
        with self: self.__array__impl__().__idiv__(y)
        return self
    cls.__idiv__ = __idiv__

    def __itruediv__(self, y):
        with self: self.__array__impl__().__itruediv__(y)
        return self
    cls.__itruediv__ = __itruediv__

    def __ifloordiv__(self, y):
        with self: self.__array__impl__().__ifloordiv__(y)
        return self
    cls.__ifloordiv__ = __ifloordiv__

    def __imod__(self, y):
        with self: self.__array__impl__().__imod__(y)
        return self
    cls.__imod__ = __imod__

    def __ipow__(self, y):
        with self: self.__array__impl__().__ipow__(y)
        return self
    cls.__ipow__ = __ipow__

    def __iand__(self, y):
        with self: self.__array__impl__().__iand__(y)
        return self
    cls.__iand__ = __iand__

    def __ior__(self, y):
        with self: self.__array__impl__().__ior__(y)
        return self
    cls.__ior__ = __ior__

    def __ixor__(self, y):
        with self: self.__array__impl__().__ixor__(y)
        return self
    cls.__ixor__ = __ixor__