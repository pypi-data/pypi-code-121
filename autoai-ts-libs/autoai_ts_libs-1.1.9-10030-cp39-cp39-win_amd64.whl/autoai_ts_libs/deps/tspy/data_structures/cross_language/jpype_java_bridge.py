from jpype import JImplements, JOverride, JObject, JString, JArray, JDouble, JInt, JBoolean

from autoai_ts_libs.deps.tspy.data_structures.cross_language.JPypeTSBuilder import JPypeTSBuilder
from autoai_ts_libs.deps.tspy.data_structures.observations.TSBuilder import TSBuilder
from autoai_ts_libs.deps.tspy.data_structures.cross_language.Packages import Packages
from autoai_ts_libs.deps.tspy.data_structures.cross_language.java_bridge import JavaBridge
from autoai_ts_libs.deps.tspy.data_structures.observations.Segment import Segment
from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries
from autoai_ts_libs.deps.tspy.data_structures.observations.Observation import Observation
from autoai_ts_libs.deps.tspy.data_structures.forecasting.Prediction import Prediction
from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries
from autoai_ts_libs.deps.tspy.data_structures.cross_language.JavaImplementations import JavaImplementations

class JPypeJavaBridge(JavaBridge):
    """a JavaBridge using JPype"""

    def __init__(self, tsc):
        super().__init__(tsc)
        import jpype
        import jpype.imports
        self._jpype = jpype
        self._jpype_packages = None

    def startJVM(self, **kwargs):
        if not self._tsc.is_jvm_active:
            self._jpype.startJVM(**kwargs)
            self._jpype_packages = JPypePackages()
            self._java_apis = JPypeJavaImplementations(self)

    def stopJVM(self):
        if self._tsc is not None and self._tsc.is_jvm_active:
            self._jpype.shutdownJVM()
            self._tsc = None

    @property
    def package_root(self):
        return self._jpype_packages

    def is_instance_of_java_class(self, obj, fully_qualified_class):
        return type(obj).__name__ == fully_qualified_class

    def is_java_obj(self, obj):
        return isinstance(obj, JObject)

    def convert_to_primitive_java_array(self, values, type_in):
        map_types = {
          str: JArray(JString),
          int: JArray(JInt),
          float: JArray(JDouble),
          bool: JArray(JBoolean),
        }
        j_cls = map_types.get(type_in, JArray(JObject))
        return j_cls(values)

    def convert_to_java_map(self, python_dict):
        java_map = self._tsc.packages.java.util.HashMap()
        for k, v in python_dict.items():
            java_map.put(k, self.cast_to_j_if_necessary(v))
        return java_map

    def convert_to_java_list(self, python_list):
        java_list = self._tsc.packages.java.util.ArrayList(len(python_list))
        for v in python_list:
            java_list.add(self.cast_to_j_if_necessary(v))
        return java_list

    def convert_to_java_set(self, python_list):
        java_set = self._tsc.packages.java.util.HashSet(len(python_list))
        for v in python_list:
            java_set.add(self.cast_to_j_if_necessary(v))
        return java_set

    def cast_to_py_if_necessary(self, obj, obj_type=None):
        if obj_type is None:
            if isinstance(obj, JObject):

                if isinstance(obj, self._tsc.packages.time_series.core.utils.Segment):
                    return Segment(self._tsc, obj, obj.start(), obj.end()), 2
                elif isinstance(obj, self._tsc.packages.time_series.core.utils.ObservationCollection):
                    return BoundTimeSeries(self._tsc, obj), 3
                elif isinstance(obj, self._tsc.packages.time_series.core.observation.Observation):
                    return Observation(self._tsc, obj.getTimeTick(), obj.getValue()), 4
                elif isinstance(obj, self._tsc.packages.time_series.core.utils.Pair):
                    return (obj.left(), obj.right()), 5
                elif isinstance(obj, self._tsc.packages.time_series.core.utils.Prediction):
                    return Prediction(self._tsc, obj), 6
                elif isinstance(obj, self._tsc.packages.java.lang.String):
                    return str(obj), 7
                else:
                    return obj, 0
            else:
                return obj, 0
        else:
            if obj_type == 0:
                return obj, 0
            elif obj_type == 2:
                return Segment(self._tsc, obj, obj.start(), obj.end()), 2
            elif obj_type == 3:
                return BoundTimeSeries(self._tsc, obj), 3
            elif obj_type == 4:
                return Observation(self._tsc, obj.getTimeTick(), obj.getValue()), 4
            elif obj_type == 5:
                return (obj.left(), obj.right()), 5
            elif obj_type == 6:
                return Prediction(self._tsc, obj), 6
            elif obj_type == 7:
                return str(obj), 7

    def cast_to_j_if_necessary(self, obj):
        if isinstance(obj, Segment):
            return obj._j_segment
        elif isinstance(obj, BoundTimeSeries):
            return obj._j_observations
        elif isinstance(obj, Observation):
            return obj._j_observation
        elif isinstance(obj, list):
            return self.convert_to_java_list(obj)
        elif isinstance(obj, tuple):
            return self._tsc.packages.time_series.core.utils.Pair(obj[0], obj[1])
        elif isinstance(obj, dict):
            return self.convert_to_java_map(obj)
        elif isinstance(obj, Prediction):
            return obj._j_prediction
        elif isinstance(obj, str):
            return JString(obj)
        else:
            return obj

    def builder(self) -> TSBuilder:
        """return a timeseries builder"""
        return JPypeTSBuilder(self._tsc)



class JPypeJavaImplementations(JavaImplementations):

    def __init__(self, java_bridge):
        super().__init__(java_bridge)

    def JavaTimeSeriesReader(self, py_reader_in):
        @JImplements('com.ibm.research.time_series.core.io.TimeSeriesReader')
        class JavaTimeSeriesReader:
            def __init__(self, java_bridge, py_reader):
                self._java_bridge = java_bridge
                self._py_reader = py_reader

            @JOverride
            def read(self, start, end, inclusive_bounds):
                py_list = self._py_reader.read(start, end, inclusive_bounds)
                py_list_j_obs = list(map(lambda obs: obs._j_observation, py_list))
                return self._java_bridge.convert_to_java_list(py_list_j_obs)

            @JOverride
            def close(self):
                self._py_reader.close()

            @JOverride
            def start(self):
                return self._py_reader.start()

            @JOverride
            def end(self):
                return self._py_reader.end()

        return JavaTimeSeriesReader(self._java_bridge, py_reader_in)

    def JavaToPythonUnaryTransformFunction(self, py_func_in):
        @JImplements('com.ibm.research.time_series.core.transform.python.PythonUnaryTransformFunction')
        class JavaToPythonUnaryTransformFunction:
            def __init__(self, java_bridge, py_func):
                self._java_bridge = java_bridge
                self._py_func = py_func

            @JOverride
            def call(self, j_time_series, start, end, inclusive_bounds):
                return self._py_func.evaluate(
                    TimeSeries(self._java_bridge._tsc, j_time_series),
                    start,
                    end,
                    inclusive_bounds
                )._j_observations

        return JavaToPythonUnaryTransformFunction(self._java_bridge, py_func_in)

    def JavaToPythonBinaryTransformFunction(self, py_func_in):
        @JImplements('com.ibm.research.time_series.core.transform.python.PythonBinaryTransformFunction')
        class JavaToPythonBinaryTransformFunction:
            def __init__(self, java_bridge, py_func):
                self._java_bridge = java_bridge
                self._py_func = py_func

            @JOverride
            def call(self, j_time_series_l, j_time_series_r, start, end, inclusive_bounds):
                return self._py_func.evaluate(
                    TimeSeries(self._java_bridge._tsc, j_time_series_l),
                    TimeSeries(self._java_bridge._tsc, j_time_series_r),
                    start,
                    end,
                    inclusive_bounds
                )._j_observations

        return JavaToPythonBinaryTransformFunction(self._java_bridge, py_func_in)

    def Interpolator(self, interpolator_f_in):
        @JImplements('com.ibm.research.time_series.core.functions.Interpolator')
        class Interpolator(object):

            def __init__(self, java_bridge, interpolator_f):
                self._java_bridge = java_bridge
                self._interpolator_f = interpolator_f

            @JOverride
            def interpolate(self, history, future, timestamp):
                py_history = BoundTimeSeries(self._java_bridge._tsc, history)
                py_future = BoundTimeSeries(self._java_bridge._tsc, future)
                return self._interpolator_f(py_history, py_future, timestamp)

            @JOverride
            def getHistorySize(self):
                return 1

            @JOverride
            def getFutureSize(self):
                return 1

        return Interpolator(self._java_bridge, interpolator_f_in)

    def FilterFunction(self, f_in):
        @JImplements('com.ibm.research.time_series.core.functions.FilterFunction')
        class FilterFunction(object):

            def __init__(self, java_bridge, f):
                self._java_bridge = java_bridge
                self._f = f
                self._obj_type = None

            @JOverride
            def evaluate(self, obj):
                py_obj, obj_type = self._java_bridge.cast_to_py_if_necessary(obj, self._obj_type)
                self._obj_type = obj_type
                return self._f(py_obj)

        return FilterFunction(self._java_bridge, f_in)

    def UnaryMapFunction(self, f_in):
        @JImplements('com.ibm.research.time_series.core.functions.UnaryMapFunction')
        class UnaryMapFunction(object):

            def __init__(self, java_bridge, f):
                self._java_bridge = java_bridge
                self._f = f
                self._obj_type = None

            @JOverride
            def evaluate(self, obj_in):
                py_obj, obj_type = self._java_bridge.cast_to_py_if_necessary(obj_in, self._obj_type)
                self._obj_type = obj_type
                return self._java_bridge.cast_to_j_if_necessary(self._f(py_obj))

        return UnaryMapFunction(self._java_bridge, f_in)

    def BinaryMapFunction(self, f_in):
        @JImplements('com.ibm.research.time_series.core.functions.BinaryMapFunction')
        class BinaryMapFunction(object):

            def __init__(self, java_bridge, f):
                self._java_bridge = java_bridge
                self._f = f
                self._obj_type1 = None
                self._obj_type2 = None
                self._out_type = None

            @JOverride
            def evaluate(self, obj_1, obj_2):
                py_obj_1, obj_type1 = self._java_bridge.cast_to_py_if_necessary(obj_1, self._obj_type1)
                py_obj_2, obj_type2 = self._java_bridge.cast_to_py_if_necessary(obj_2, self._obj_type2)
                self._obj_type1 = obj_type1
                self._obj_type2 = obj_type2
                return self._java_bridge.cast_to_j_if_necessary(self._f(py_obj_1, py_obj_2))

        return BinaryMapFunction(self._java_bridge, f_in)

    def NaryMapFunction(self, f_in):
        @JImplements('com.ibm.research.time_series.core.functions.NaryMapFunction')
        class NaryMapFunction(object):

            def __init__(self, java_bridge, f):
                self._java_bridge = java_bridge
                self._f = f
                self._obj_type = None

            @JOverride
            def evaluate(self, obj):
                py_obj, obj_type = self._java_bridge.cast_to_py_if_necessary(obj, self._obj_type)
                self._obj_type = obj_type
                py_res = self._func(py_obj)
                return self._java_bridge.cast_to_j_if_necessary(py_res)

        return NaryMapFunction(self._java_bridge, f_in)

    def IObjectDistanceCalculator(self, func_in):
        @JImplements(
            'com.ibm.research.time_series.transforms.reducers.distance.dtw.algorithm.IObjectDistanceCalculator')
        class IObjectDistanceCalculator(object):

            def __init__(self, func):
                self._func = func

            @JOverride
            def distance(self, o_1, o_2):
                return self._func(o_1, o_2)

        return IObjectDistanceCalculator(func_in)

    def IMatcher(self, func_in):
        @JImplements('com.ibm.research.time_series.transforms.reducers.distance.dl.algorithm.IMatcher')
        class IMatcher(object):

            def __init__(self, func):
                self._func = func

            @JOverride
            def match(self, obj_1, obj_2):
                return self._func(obj_1, obj_2)

            @JOverride
            def getInsertCost(self, l):
                return 1.0

            @JOverride
            def getDeleteCost(self, l):
                return 1.0

            @JOverride
            def getSubstituteCost(self, l):
                return 1.0

            @JOverride
            def getTransposeCost(self, l):
                return 1.0

        return IMatcher(func_in)

    def JavaDataSink(self, python_data_sink_in):
        @JImplements('com.ibm.research.time_series.streaming.functions.DataSink')
        class JavaDataSink:
            def __init__(self, java_bridge, python_data_sink):
                self._java_bridge = java_bridge
                self._python_data_sink = python_data_sink

            @JOverride
            def dump(self, observations):
                self._python_data_sink.dump(BoundTimeSeries(self._java_bridge._tsc, observations))

        return JavaDataSink(self._java_bridge, python_data_sink_in)

    def JavaMultiDataSink(self, python_multi_data_sink_in):
        @JImplements('com.ibm.research.time_series.streaming.functions.MultiDataSink')
        class JavaMultiDataSink:
            def __init__(self, java_bridge, python_multi_data_sink):
                self._java_bridge = java_bridge
                self._python_multi_data_sink = python_multi_data_sink

            @JOverride
            def dump(self, observations_map):
                self._python_multi_data_sink.dump(
                    {k: BoundTimeSeries(self._java_bridge._tsc, v) for k, v in observations_map.items()})

        return JavaMultiDataSink(self._java_bridge, python_multi_data_sink_in)

    def JavaTimeSeriesWriteFormat(self, python_time_series_writer_in):
        @JImplements('com.ibm.research.time_series.core.io.TimeSeriesWriteFormat')
        class JavaTimeSeriesWriteFormat:
            def __init__(self, java_bridge, python_time_series_writer):
                self._java_bridge = java_bridge
                self._python_time_series_writer = python_time_series_writer

            @JOverride
            def write(self, observations, encode_value, options):
                self._python_time_series_writer.write(
                    BoundTimeSeries(self._java_bridge._tsc, observations),
                    lambda x: self._java_bridge.cast_to_py_if_necessary(encode_value.evaluate(x))[0],
                    {key: option for key, option in options.items()}
                )

        return JavaTimeSeriesWriteFormat(self, python_time_series_writer_in)

    def JavaMultiTimeSeriesWriteFormat(self, python_multi_time_series_writer_in):
        @JImplements('com.ibm.research.time_series.core.io.MultiTimeSeriesWriteFormat')
        class JavaMultiTimeSeriesWriteFormat:
            def __init__(self, java_bridge, python_time_series_writer):
                self._java_bridge = java_bridge
                self._python_time_series_writer = python_time_series_writer

            @JOverride
            def write(self, observations_dict, encode_key, encode_value, options):
                self._python_time_series_writer.write(
                    {k: BoundTimeSeries(self._java_bridge._tsc, observations) for k, observations in
                     observations_dict.items()},
                    lambda x: self._java_bridge.cast_to_py_if_necessary(encode_key.evaluate(x))[0],
                    lambda x: self._java_bridge.cast_to_py_if_necessary(encode_value.evaluate(x))[0],
                    {key: option for key, option in options.items()}
                )

        return JavaMultiTimeSeriesWriteFormat(self._java_bridge, python_multi_time_series_writer_in)

    def TimeSeriesReader(self, py_reader_in):

        @JImplements('com.ibm.research.time_series.core.io.TimeSeriesReader')
        class TimeSeriesReader:
            def __init__(self, java_bridge, py_reader):
                self._java_bridge = java_bridge
                self._py_reader = py_reader

            @JOverride
            def read(self, start, end, inclusive_bounds):
                py_list = self._py_reader.read(start, end, inclusive_bounds)
                py_list_j_obs = list(map(lambda obs: obs, py_list))
                return self._java_bridge.convert_to_java_list(py_list_j_obs).iterator()

            @JOverride
            def close(self):
                self._py_reader.close()

            @JOverride
            def start(self):
                return self._py_reader.start()

            @JOverride
            def end(self):
                return self._py_reader.end()
        return TimeSeriesReader(self._java_bridge, py_reader_in)

    def UnaryMapFunctionTupleResultingInOptional(self, func_in):
        @JImplements('com.ibm.research.time_series.core.functions.UnaryMapFunction')
        class UnaryMapFunctionTupleResultingInOptional(object):

            def __init__(self, java_bridge, func):
                self._java_bridge = java_bridge
                self._func = func
                self._obj_type = None

            @JOverride
            def evaluate(self, obj):
                py_obj, obj_type = self._java_bridge.cast_to_py_if_necessary(obj, self._obj_type)
                self._obj_type = obj_type
                res = self._func(py_obj)

                if res is None:
                    return self._java_bridge.package_root.java.util.Optional.empty()
                else:
                    return self._java_bridge.package_root.java.util.Optional.of(
                        self._java_bridge.package_root.time_series.core.utils.Pair(
                            self._java_bridge.cast_to_j_if_necessary(res[0]),
                            self._java_bridge.cast_to_j_if_necessary(res[1])
                        )
                    )
        return UnaryMapFunctionTupleResultingInOptional(self._java_bridge, func_in)

    def UnaryMapFunctionResultingInOptional(self, func_in):
        @JImplements('com.ibm.research.time_series.core.functions.UnaryMapFunction')
        class UnaryMapFunctionResultingInOptional(object):

            def __init__(self, java_bridge, func):
                self._java_bridge = java_bridge
                self._func = func
                self._obj_type = None

            @JOverride
            def evaluate(self, obj):
                py_obj, obj_type = self._java_bridge.cast_to_py_if_necessary(obj, self._obj_type)
                self._obj_type = obj_type
                res = self._func(py_obj)

                if res is None:
                    return self._java_bridge.package_root.java.util.Optional.empty()
                else:
                    return self._java_bridge.package_root.java.util.Optional.of(self._java_bridge.cast_to_j_if_necessary(res))
        return UnaryMapFunctionResultingInOptional(self._java_bridge, func_in)

    def IteratorMessageSupplier(self, py_supplier_in):
        @JImplements('java.util.function.Supplier')
        class IteratorMessageSupplier:

            def __init__(self, java_bridge, py_supplier):
                self._java_bridge = java_bridge
                self._py_supplier = py_supplier

            @JOverride
            def get(self):
                return self._java_bridge.convert_to_java_list(self._py_supplier())

    def JavaPullStreamMultiTimeSeriesReader(self, py_reader_in):
        @JImplements('com.ibm.research.time_series.streaming.io.StreamMultiTimeSeriesReader')
        class JavaPullStreamMultiTimeSeriesReader:

            def __init__(self, py_reader):
                self._py_reader = py_reader

            @JOverride
            def parse(self, message):
                return self._py_reader._parse(message)

            @JOverride
            def read(self):
                return self._py_reader._read()

            @JOverride
            def isFinite(self):
                return False

            @JOverride
            def isFinished(self):
                return False
        return JavaPullStreamMultiTimeSeriesReader(py_reader_in)

    def JavaPushStreamMultiTimeSeriesReader(self, py_reader_in):
        @JImplements('com.ibm.research.time_series.streaming.io.StreamMultiTimeSeriesReader')
        class JavaPushStreamMultiTimeSeriesReader:

            def __init__(self, py_reader):
                self._py_reader = py_reader

            @JOverride
            def parse(self, message):
                return self._py_reader._parse(message)

            @JOverride
            def read(self):
                return self._py_reader._read()

            @JOverride
            def isFinite(self):
                return False

            @JOverride
            def isFinished(self):
                return False
        return JavaPushStreamMultiTimeSeriesReader(py_reader_in)

    def JavaPullStreamTimeSeriesReader(self, py_reader_in):
        @JImplements('com.ibm.research.time_series.streaming.io.StreamTimeSeriesReader')
        class JavaPullStreamTimeSeriesReader:

            def __init__(self, py_reader):
                self._py_reader = py_reader

            @JOverride
            def parse(self, message):
                return self._py_reader._parse(message)

            @JOverride
            def read(self):
                return self._py_reader._read()

            @JOverride
            def isFinite(self):
                return False

            @JOverride
            def isFinished(self):
                return False
        return JavaPullStreamTimeSeriesReader(py_reader_in)

    def JavaPushStreamTimeSeriesReader(self, py_reader_in):
        @JImplements('com.ibm.research.time_series.streaming.io.StreamTimeSeriesReader')
        class JavaPushStreamTimeSeriesReader:

            def __init__(self, py_reader):
                self._py_reader = py_reader

            @JOverride
            def parse(self, message):
                return self._py_reader._parse(message)

            @JOverride
            def read(self):
                return self._py_reader._read()

            @JOverride
            def isFinite(self):
                return False

            @JOverride
            def isFinished(self):
                return False

class JPypePackages(Packages):

    def __init__(self):
        import java
        from com.ibm.research import time_series
        self._java = java
        self._time_series = time_series

    @property
    def java(self):
        return self._java

    @property
    def time_series(self):
        return self._time_series
