from dataclasses import dataclass
from typing import Union

import pendulum
from typeguard import typechecked

from tecton_spark.errors import TectonValidationError


@dataclass
class BaseMaterializationContext:
    _feature_start_time_DONT_ACCESS_DIRECTLY: pendulum.DateTime
    _feature_end_time_DONT_ACCESS_DIRECTLY: pendulum.DateTime
    _batch_schedule_DONT_ACCESS_DIRECTLY: pendulum.Duration

    @property
    def start_time(self) -> pendulum.DateTime:
        return self._feature_start_time_DONT_ACCESS_DIRECTLY

    @property
    def end_time(self) -> pendulum.DateTime:
        return self._feature_end_time_DONT_ACCESS_DIRECTLY

    @property
    def batch_schedule(self) -> pendulum.Duration:
        return self._batch_schedule_DONT_ACCESS_DIRECTLY

    @property
    def start_time_string(self) -> str:
        return self.feature_start_time.to_datetime_string()

    @property
    def end_time_string(self) -> str:
        return self.feature_end_time.to_datetime_string()

    @typechecked
    def time_filter_sql(self, timestamp_expr: str) -> str:
        return f"('{self.start_time_string}' <= ({timestamp_expr}) AND ({timestamp_expr}) < '{self.end_time_string}')"

    def time_filter_pyspark(self, timestamp_expr: Union[str, "pyspark.sql.Column"]) -> "pyspark.sql.Column":
        from pyspark.sql.functions import expr
        from pyspark.sql.functions import lit

        if isinstance(timestamp_expr, str):
            timestamp_expr = expr(timestamp_expr)
        return (lit(self.start_time_string) <= timestamp_expr) & (timestamp_expr < lit(self.end_time_string))

    def feature_time_filter_pyspark(self, timestamp_expr: Union[str, "pyspark.sql.Column"]) -> "pyspark.sql.Column":
        return self.time_filter_pyspark(timestamp_expr)

    # EVERTHING BELOW IS DEPRECATED
    @property
    def feature_start_time(self) -> pendulum.DateTime:
        return self._feature_start_time_DONT_ACCESS_DIRECTLY

    @property
    def feature_end_time(self) -> pendulum.DateTime:
        return self._feature_end_time_DONT_ACCESS_DIRECTLY

    @property
    def feature_start_time_string(self) -> str:
        return self.feature_start_time.to_datetime_string()

    @property
    def feature_end_time_string(self) -> str:
        return self.feature_end_time.to_datetime_string()

    @typechecked
    def feature_time_filter_sql(self, timestamp_expr: str) -> str:
        return self.time_filter_sql(timestamp_expr)


@dataclass
class UnboundMaterializationContext(BaseMaterializationContext):
    """
    This is only meant for instantiation in transformation default args. Using it directly will fail.
    """

    @property
    def batch_schedule(self):
        raise TectonValidationError(
            "tecton.materialization_context() must be passed in via a kwarg default only. Instantiation in function body is not allowed."
        )

    @property
    def start_time(self):
        raise TectonValidationError(
            "tecton.materialization_context() must be passed in via a kwarg default only. Instantiation in function body is not allowed."
        )

    @property
    def end_time(self):
        raise TectonValidationError(
            "tecton.materialization_context() must be passed in via a kwarg default only. Instantiation in function body is not allowed."
        )

    @property
    def feature_start_time(self):
        raise TectonValidationError(
            "tecton.materialization_context() must be passed in via a kwarg default only. Instantiation in function body is not allowed."
        )

    @property
    def feature_end_time(self):
        raise TectonValidationError(
            "tecton.materialization_context() must be passed in via a kwarg default only. Instantiation in function body is not allowed."
        )


@dataclass
class BoundMaterializationContext(BaseMaterializationContext):
    @classmethod
    def create(cls, feature_start_time, feature_end_time):
        # user facing version
        return BoundMaterializationContext(
            _feature_start_time_DONT_ACCESS_DIRECTLY=feature_start_time,
            _feature_end_time_DONT_ACCESS_DIRECTLY=feature_end_time,
            # batch_schedule is passed by pipeline helper
            _batch_schedule_DONT_ACCESS_DIRECTLY=pendulum.duration(seconds=0),
        )

    @classmethod
    def _create_internal(cls, feature_start_time, feature_end_time, batch_schedule):
        # should only be used in pipeline_helper
        return BoundMaterializationContext(
            _feature_start_time_DONT_ACCESS_DIRECTLY=feature_start_time,
            _feature_end_time_DONT_ACCESS_DIRECTLY=feature_end_time,
            _batch_schedule_DONT_ACCESS_DIRECTLY=batch_schedule,
        )


def materialization_context():
    """
    Used as a default value for the context argument for Transformations that take in a context argument.
    """
    dummy_time = pendulum.datetime(1970, 1, 1)
    dummy_period = pendulum.duration()
    return UnboundMaterializationContext(
        _feature_start_time_DONT_ACCESS_DIRECTLY=dummy_time,
        _feature_end_time_DONT_ACCESS_DIRECTLY=dummy_time,
        _batch_schedule_DONT_ACCESS_DIRECTLY=dummy_period,
    )
