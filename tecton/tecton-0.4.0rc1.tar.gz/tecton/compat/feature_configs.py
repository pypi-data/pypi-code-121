from typing import List
from typing import Optional
from typing import Union

import attr
import pendulum
import pytimeparse
from google.protobuf.duration_pb2 import Duration

from tecton._internals import errors
from tecton.aggregation_functions import AggregationFunction
from tecton_proto.args import feature_view_pb2


BACKFILL_CONFIG_MODE_PROTO_PREFIX = "BACKFILL_CONFIG_MODE_"
BACKFILL_CONFIG_MODE_MULTIPLE = "multiple_batch_schedule_intervals_per_job"
BACKFILL_CONFIG_MODE_SINGLE = "single_batch_schedule_interval_per_job"


@attr.s(auto_attribs=True)
class FeatureAggregation(object):
    """
    This class describes a single aggregation that is applied in a batch or stream window aggregate feature view.

    :param column: Column name of the feature we are aggregating.
    :type column: str
    :param function: One of the built-in aggregation functions.
    :type function: Union[str, AggregationFunction]
    :param time_windows: Duration to aggregate over in pytimeparse_ format. Examples: ``"30days"``, ``["8hours", "30days", "365days"]``.
    :type time_windows: Union[str, List[str]]

    `function` can be one of predefined numeric aggregation functions, namely ``"count"``, ``"sum"``, ``"mean"``, ``"min"``, ``"max"``. For
    these numeric aggregations, you can pass the name of it as a string. Nulls are handled like Spark SQL `Function(column)`, e.g. SUM/MEAN/MIN/MAX of all nulls is null and COUNT of all nulls is 0.

    In addition to numeric aggregations, :class:`FeatureAggregation` supports "last-n" aggregations that
    will compute the last N distinct values for the column by timestamp. Right now only string column types are supported as inputs
    to this aggregation, i.e., the resulting feature value will be a list of strings. Nulls are not included in the aggregated list.

    You can use it via the ``last_distinct()`` helper function like this:

    .. code-block:: python

        from tecton.aggregation_functions import last_distinct
        my_fv = BatchWindowAggregateFeatureView(
        ...
        aggregations=[FeatureAggregation(
            column='my_column',
            function=last_distinct(15),
            time_windows=['7days'])],
        ...
        )

    .. _pytimeparse: https://pypi.org/project/pytimeparse/
    """

    column: str
    """Column name of the feature we are aggregating."""
    function: Union[str, AggregationFunction]
    """One of the built-in aggregation functions (`'count'`, `'sum'`, `'mean'`, `'min'`, `'max'`)."""
    time_windows: Union[str, List[str]]
    """
       Examples: `"30days"`, `["8hours", "30days", "365days"]`.

       .. _pytimeparse: https://pypi.org/project/pytimeparse/
       """

    def _to_proto(self):
        proto = feature_view_pb2.FeatureAggregation()
        proto.column = self.column

        if isinstance(self.function, str):
            proto.function = self.function
        elif isinstance(self.function, AggregationFunction):
            proto.function = self.function.name
            for k, v in self.function.params.items():
                assert isinstance(v, int)
                proto.function_params[k].CopyFrom(feature_view_pb2.ParamValue(int64_value=v))
        else:
            raise TypeError(f"Invalid function type: {type(self.function)}")

        windows = self.time_windows if isinstance(self.time_windows, list) else [self.time_windows]
        for w in windows:
            duration = Duration()
            duration.FromTimedelta(pendulum.duration(seconds=pytimeparse.parse(w)))
            proto.time_windows.append(duration)
            proto.time_window_strs.append(w)
        return proto


@attr.s(auto_attribs=True)
class BackfillConfig:
    """Configuration used to specify backfill options.

    This class configures the backfill behavior of a Batch Feature View. Requires
    materialization to be enabled.

    :param mode: Determines whether Tecton batches backfill jobs:
        [``single_batch_schedule_interval_per_job``, ``multiple_batch_schedule_intervals_per_job``]
    """

    mode: str

    def _to_proto(self) -> feature_view_pb2.BackfillConfig:
        proto = feature_view_pb2.BackfillConfig()
        try:
            proto.mode = feature_view_pb2.BackfillConfigMode.Value(
                BACKFILL_CONFIG_MODE_PROTO_PREFIX + self.mode.upper()
            )
        except ValueError:
            # TODO: add BACKFILL_CONFIG_MODE_SINGLE when supported
            raise errors.InvalidBackfillConfigMode(self.mode, [BACKFILL_CONFIG_MODE_MULTIPLE])
        return proto


@attr.s(auto_attribs=True)
class MonitoringConfig:
    """Configuration used to specify monitoring options.

    This class describes the FeatureView materialization freshness and alerting configurations. Requires
    materialization to be enabled. Freshness monitoring requires online materialization to be enabled.
    See `Monitoring Materialization`_ for more details.

    :param monitor_freshness: Defines the enabled/disabled state of monitoring when feature data is materialized to the online feature store.
    :type monitor_freshness: bool
    :param expected_feature_freshness: Threshold used to determine if recently materialized feature data is stale.
        Data is stale if ``now - anchor_time(most_recent_feature_value) > expected_feature_freshness``.
        Value must be at least 2 times the feature tile length.
        If not specified, a value determined by the Tecton backend is used
    :type expected_feature_freshness: str, optional
    :param alert_email: Email that alerts for this FeatureView will be sent to.
    :type alert_email: str, optional

    An example declaration of a MonitorConfig

        .. code-block:: python

            from tecton import batch_feature_view, Input, MonitoringConfig
            # For all named arguments to the batch feature view, see docs for details and types.
            @batch_feature_view(
                inputs={'credit_scores': Input(credit_scores_batch)},
                # Can be an argument instance to a batch feature view decorator
                monitoring = MonitoringConfig(
                    monitor_freshness=True,
                    expected_feature_freshness="1w",
                    alert_email="brian@tecton.ai"
                ),
                # Other named arguments
                ...
            )

            # Your batch feature view function
            def credit_batch_feature_view(credit_scores):
              ...

    .. _Monitoring Materialization: https://docs.tecton.ai/v2/overviews/monitoring_materialization.html
    """

    monitor_freshness: bool
    expected_feature_freshness: Optional[str] = None
    alert_email: Optional[str] = None

    def _to_proto(self) -> feature_view_pb2.MonitoringConfig:
        proto = feature_view_pb2.MonitoringConfig()

        if self.expected_feature_freshness:
            proto.expected_feature_freshness.FromTimedelta(
                pendulum.duration(seconds=pytimeparse.parse(self.expected_feature_freshness))
            )

        proto.alert_email = self.alert_email or ""
        proto.monitor_freshness = self.monitor_freshness
        return proto
