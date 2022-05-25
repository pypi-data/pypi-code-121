import abc

from autoai_ts_libs.deps.tspy.data_structures.cross_language.JavaImplementations import JavaImplementations
from autoai_ts_libs.deps.tspy.data_structures.cross_language.Packages import Packages
from autoai_ts_libs.deps.tspy.data_structures.observations.TSBuilder import TSBuilder


class JavaBridge(object, metaclass=abc.ABCMeta):
    """a JavaBridge abstract class for Python code"""

    def __init__(self, tsc):
        self._tsc = tsc
        self._java_apis = None  # to be instantiated in `startJVM` API

    @abc.abstractmethod
    def startJVM(self, **kwargs):
        pass

    @abc.abstractmethod
    def stopJVM(self):
        pass

    @abc.abstractmethod
    def is_instance_of_java_class(self, obj, fully_qualified_class):
        pass

    @abc.abstractmethod
    def is_java_obj(self, obj):
        """check if the given object is a JObject object"""
        pass

    @abc.abstractmethod
    def convert_to_primitive_java_array(self, values, type_in):
        pass

    @abc.abstractmethod
    def convert_to_java_map(self, python_dict):
        pass

    @abc.abstractmethod
    def convert_to_java_list(self, python_list):
        pass

    @abc.abstractmethod
    def convert_to_java_set(self, python_list):
        pass

    @abc.abstractmethod
    def cast_to_py_if_necessary(self, obj, obj_type=None):
        pass

    @abc.abstractmethod
    def cast_to_j_if_necessary(self, obj):
        pass

    @abc.abstractmethod
    def builder(self) -> TSBuilder:
        pass

    @property
    def java_implementations(self) -> JavaImplementations:
        return self._java_apis

    @property
    @abc.abstractmethod
    def package_root(self) -> Packages:
        pass
