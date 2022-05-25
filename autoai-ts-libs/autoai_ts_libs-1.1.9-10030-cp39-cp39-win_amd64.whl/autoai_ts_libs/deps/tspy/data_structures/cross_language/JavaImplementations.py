import abc

class JavaImplementations(object, metaclass=abc.ABCMeta):

    def __init__(self, java_bridge):
        self._java_bridge = java_bridge

    @abc.abstractmethod
    def JavaTimeSeriesReader(self, py_reader_in):
        pass

    @abc.abstractmethod
    def JavaToPythonUnaryTransformFunction(self, py_func_in):
        pass

    @abc.abstractmethod
    def JavaToPythonBinaryTransformFunction(self, py_func_in):
        pass

    @abc.abstractmethod
    def Interpolator(self, interpolator_f_in):
        pass

    @abc.abstractmethod
    def FilterFunction(self, f_in):
        pass

    @abc.abstractmethod
    def UnaryMapFunction(self, f_in):
        pass

    @abc.abstractmethod
    def BinaryMapFunction(self, f_in):
        pass

    @abc.abstractmethod
    def NaryMapFunction(self, f_in):
        pass

    @abc.abstractmethod
    def IObjectDistanceCalculator(self, func_in):
        pass

    @abc.abstractmethod
    def IMatcher(self, func_in):
        pass

    @abc.abstractmethod
    def JavaDataSink(self, python_data_sink_in):
        pass

    @abc.abstractmethod
    def JavaMultiDataSink(self, python_multi_data_sink_in):
        pass

    @abc.abstractmethod
    def JavaTimeSeriesWriteFormat(self, python_time_series_writer_in):
        pass

    @abc.abstractmethod
    def JavaMultiTimeSeriesWriteFormat(self, python_multi_time_series_writer_in):
        pass

    @abc.abstractmethod
    def UnaryMapFunctionTupleResultingInOptional(self, func_in):
        pass

    @abc.abstractmethod
    def UnaryMapFunctionResultingInOptional(self, func_in):
        pass

    @abc.abstractmethod
    def IteratorMessageSupplier(self, py_supplier_in):
        pass

    @abc.abstractmethod
    def JavaPullStreamMultiTimeSeriesReader(self, py_reader_in):
        pass

    @abc.abstractmethod
    def JavaPushStreamMultiTimeSeriesReader(self, py_reader_in):
        pass

    @abc.abstractmethod
    def JavaPullStreamTimeSeriesReader(self, py_reader_in):
        pass

    @abc.abstractmethod
    def JavaPushStreamTimeSeriesReader(self, py_reader_in):
        pass
