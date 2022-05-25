from autoai_ts_libs.deps.tspy.data_structures.observations.BoundMultiTimeSeries import BoundMultiTimeSeries


class BoundSegmentMultiTimeSeries(BoundMultiTimeSeries):

    def __init__(self, tsc, j_bound_mts):
        super().__init__(tsc, j_bound_mts)
        self._tsc = tsc
        self._j_bound_mts = j_bound_mts

    def add_segment_annotation(self, key, annotation_reducer):
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.addSegmentAnnotation(key, annotation_reducer))

    def transform_segments(self, unary_transform, annotation_mapper=None):
        if annotation_mapper is None:
            return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.transformSegments(unary_transform))
        else:
            j_annotation_mapper = self._tsc.java_bridge.convert_to_java_map(annotation_mapper)
            return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.transformSegments(unary_transform,
                                                                                              j_annotation_mapper))

    def filter(self, func):
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.filter(self._tsc.java_bridge.java_implementations.FilterFunction(func)))

    def map_segments(self, func):
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.mapSegments(self._tsc.java_bridge.java_implementations.BinaryMapFunction(func)))

    def flatten(self, key_func=None):
        if key_func is None:
            return BoundSegmentMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.flatten()
            )
        else:
            return BoundSegmentMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.flatten(self._tsc.java_bridge.UnaryMapFunction(key_func))
            )
