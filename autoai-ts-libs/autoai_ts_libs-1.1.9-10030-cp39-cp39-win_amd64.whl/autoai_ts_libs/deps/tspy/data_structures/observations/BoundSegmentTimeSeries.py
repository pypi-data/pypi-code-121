
from autoai_ts_libs.deps.tspy.data_structures.observations.BoundMultiTimeSeries import BoundMultiTimeSeries
from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries


class BoundSegmentTimeSeries(BoundTimeSeries):

    # j_observations will always be a java bound segment time-series
    def __init__(self, tsc, j_observations):
        super().__init__(tsc, j_observations)
        self._tsc = tsc
        self._j_observations = j_observations

    def add_segment_annotation(self, key, annotation_reducer):
        return BoundSegmentTimeSeries(self._tsc, self._j_observations.addSegmentAnnotation(key, annotation_reducer))

    def transform_segments(self, unary_transform, annotation_mapper=None):
        if annotation_mapper is None:
            return BoundSegmentTimeSeries(self._tsc, self._j_observations.transformSegments(unary_transform))
        else:
            j_annotation_mapper = self._tsc.java_bridge.convert_to_java_map(annotation_mapper)
            return BoundSegmentTimeSeries(self._tsc, self._j_observations.transformSegments(unary_transform,
                                                                                            j_annotation_mapper))

    def filter(self, func):
        return BoundSegmentTimeSeries(self._tsc, self._j_observations.filter(self._tsc.java_bridge.java_implementations.FilterFunction(func)))

    def map_segments(self, func):
        return BoundSegmentTimeSeries(self._tsc, self._j_observations.mapSegments(self._tsc.java_bridge.java_implementations.BinaryMapFunction(func)))

    def flatten(self, key_func=None):
        if key_func is None:
            return BoundMultiTimeSeries(
                self._tsc,
                self._j_observations.flatten()
            )
        else:
            return BoundMultiTimeSeries(
                self._tsc,
                self._j_observations.flatten(self._tsc.java_bridge.java_implementations.UnaryMapFunction(key_func))
            )
