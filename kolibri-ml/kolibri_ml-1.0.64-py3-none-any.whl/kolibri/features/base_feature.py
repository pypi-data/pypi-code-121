import scipy.sparse
from abc import ABCMeta, abstractmethod
import time


# class MetafeatureFunctions(object):
#     def __init__(self):
#         self.functions = OrderedDict()
#         self.dependencies = OrderedDict()
#         self.values = OrderedDict()
#
#     def clear(self):
#         self.values = OrderedDict()
#
#     def __iter__(self):
#         return self.functions.__iter__()
#
#     def __getitem__(self, item):
#         return self.functions.__getitem__(item)
#
#     def __setitem__(self, key, value):
#         return self.functions.__setitem__(key, value)
#
#     def __delitem__(self, key):
#         return self.functions.__delitem__(key)
#
#     def __contains__(self, item):
#         return self.functions.__contains__(item)
#
#     def get_value(self, key):
#         return self.values[key].value
#
#     def set_value(self, key, item):
#         self.values[key] = item
#
#     def is_calculated(self, key):
#         """Return if a helper function has already been executed.
#
#         Necessary as get_value() can return None if the helper function hasn't
#         been executed or if it returned None."""
#         return key in self.values
#
#     def get_dependency(self, name):
#         """Return the dependency of metafeature "name".
#         """
#         return self.dependencies.get(name)
#
#     def define(self, name, dependency=None):
#         """Decorator for adding metafeature functions to a "dictionary" of
#         metafeatures. This behaves like a function decorating a function,
#         not a class decorating a function"""
#         def wrapper(metafeature_class):
#             instance = metafeature_class()
#             self.__setitem__(name, instance)
#             self.dependencies[name] = dependency
#             return instance
#         return wrapper
#

class AbstractFeature(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, name):
        self.time=None
        self.name=name
        self.message=""
        self.type_='FEATURE'
        pass

    @abstractmethod
    def _calculate(cls, X, y, logger, categorical):
        pass

    def __call__(self, X, y, logger, categorical=None):
        if categorical is None:
            categorical = [False for i in range(X.shape[1])]
        starttime = time.time()

        try:
            if scipy.sparse.issparse(X) and hasattr(self, "_sparse_calculate"):
                value = self._sparse_calculate(X, y, logger, categorical)
            else:
                value = self._calculate(X, y, logger, categorical)
            self.message = ""
        except MemoryError as e:
            value = None
            self.message = "Out of Memory Error: "+str(e)

        self.time = time.time()-starttime

        return value