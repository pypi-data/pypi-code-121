from typing import Union

from typeguard import typechecked

from tecton._internals.feature_definition import FeatureDefinition
from tecton.compat.data_sources.request_data_source import RequestDataSource
from tecton.declarative.base import BaseDataSource
from tecton.declarative.data_source import RequestSource
from tecton.feature_services.feature_service_args import FeaturesConfig
from tecton_spark.time_utils import assert_valid_time_string


class Input:
    """
    Instantiates a new Input for use in a Feature View definition.

    :param source: Data Source that this Input class wraps.
    :param window: How long to look back for data from the current time. For Batch Data Sources only.
        Use the WINDOW_UNBOUNDED_PRECEDING string constant to include all data up to the current time.
    :param schedule_offset: By default, batch run immediately at the end of the batch schedule period.
        This parameter configures how long to wait after the end of the period before starting, typically to ensure that all data has landed.
        For example, if the `batch_schedule='1d'` for my Feature View  and `schedule_offset` is not set, then the jobs will run at 00:00 UTC. If `schedule_offset='1h'`, then the jobs will run at 01:00 UTC.
    :returns: An Input to pass into a Feature View.

    Example Input declaration:

    .. code-block:: python

        from tecton.compat import batch_feature_view, BatchDataSource, HiveDSConfig
        from tecton.compat import Input
        from tecton.compat import WINDOW_UNBOUNDED_PRECEDING

        # Declare a BatchDataSource that is an input parameter to the Input class instance. The
        # BatchDataSource is wrapped inside an Input class instance
        batch_ds = BatchDataSource(name='credit_scores_batch',
                                   batch_ds_config=HiveDSConfig(database='demo_fraud',
                                                                table='credit_scores',
                                                                timestamp_column_name='timestamp'),
                                   family='fraud_detection')

        # Wrap the batch_ds as an input to the batch feature view. This is a common
        # way to wrap data sources as Input data to feature views.
        @batch_feature_view(inputs={"data": Input(source=batch_ds,
                                                  window=WINDOW_UNBOUNDED_PRECEDING,
                                                  schedule_offset='1hr')},
            ...
        )
        ...
    """

    @typechecked
    def __init__(
        self,
        source: Union[BaseDataSource, RequestDataSource, RequestSource, FeatureDefinition, FeaturesConfig],
        window: str = None,
        schedule_offset: str = None,
    ):

        # convert to FeaturesConfig
        if isinstance(source, FeatureDefinition):
            source = source[None]
        self.source = source
        if window is not None:
            assert_valid_time_string(window, allow_unbounded=True)
        self.window = window
        self.schedule_offset = schedule_offset
