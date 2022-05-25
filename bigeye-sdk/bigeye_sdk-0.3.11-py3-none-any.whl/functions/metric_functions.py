from __future__ import annotations

import datetime
import logging
from typing import List, Union

from bigeye_sdk.log import get_logger
from bigeye_sdk.generated.com.torodata.models.generated import Threshold, NotificationChannel, MetricRunFailureReason, \
    ForecastModelType, MetricInfo, MetricConfiguration, MetricParameter, MetricType, Table, LookbackType, \
    ConstantThreshold, SimpleBound, SimpleBoundType
from bigeye_sdk.class_ext.enum_ext import EnumExtension
from bigeye_sdk.model.enums import SimpleMetricType

log = get_logger(__file__)


def filter_metrics_by_table_ids(metrics: List[dict], table_ids: List[int]) -> List[dict]:
    """
    Deprecated.  Previously used to filter raw HTTP responses.
    :param metrics: Metrics to filter
    :param table_ids: Table ids to filter it by
    :return: List of raw metric dictionaries.
    """
    log.info('Filtering Metric IDs')
    return [d for d in metrics if d['datasetId'] in table_ids]


def get_metric_ids(metrics: List[dict]) -> List[int]:
    """
    Deprecated.  Previously used to pull the metric ids from a raw list of metric dictionaries.
    :param metrics: list of metric dictionaries.
    :return: list of integers.
    """
    metric_ids = [d['metricConfiguration']['id'] for d in metrics]
    return metric_ids


def is_freshness_metric(metric_name: str) -> bool:
    """
    Indicates whether a particular metric, by name, is a freshness metric.
    :param metric_name:  The metric name.
    :return: Boolean.
    """
    return "HOURS_SINCE_MAX" in metric_name


def is_same_metric(metric: MetricConfiguration, metric_name: str, user_defined_name: str,
                   group_by: List[str], filters: List[str]) -> bool:
    """
    Used to determin whether a particular MetricConfiguration is the same based on metric name, user defined name,
    group by columns, and filters.
    :param metric: Metric Configuration to compare from
    :param metric_name: Metric name to compare to
    :param user_defined_name: User defined name to compare to
    :param group_by: Group by column list to compare to
    :param filters: Filter list to compare to
    :return: Boolean
    """
    both_freshness_metrics = is_freshness_metric(SimpleMetricType.get_metric_name(metric.metric_type)) \
                             and is_freshness_metric(metric_name)
    has_same_user_def_name = metric.name == user_defined_name
    is_same_type = SimpleMetricType.get_metric_name(metric.metric_type) == metric_name
    same_group_by = [i.lower() for i in metric.group_bys] == [i.lower() for i in group_by]
    same_filters = [i.lower() for i in metric.filters] == [i.lower() for i in filters]
    return (is_same_type or both_freshness_metrics) and has_same_user_def_name and same_filters and same_group_by

    # Deprecated code:
    # keys = ["metricType", "predefinedMetric", "metricName"]
    # result = reduce(lambda val, key: val.get(key) if val else None, keys, metric)
    # if result is None:
    #     return False

    # return result is not None and (result == metric_name or both_metrics_freshness) \
    #        and same_group_by and same_filters


def get_column_name(metric: MetricConfiguration) -> str:
    """
    Pulls the column name from a MetricConfiguration object.
    :param metric: MetricConfiguraiton object
    :return: Column name.
    """
    i: MetricParameter
    for i in metric.parameters:
        if i.key == 'arg1':
            return i.column_name


def is_same_column_metric(metric: MetricConfiguration, column_name):
    """
    Determines whether a particular MetricConfiguration is on a particular column by column name.
    :param metric: MetricConfiguraiton object
    :param column_name: Column Name
    :return: Boolean indicating whether a metric is on a particular column.
    """
    return get_column_name(metric).lower() == column_name.lower()


def get_proto_interval_type(interval_type: str) -> str:
    """
    Determines the correct Protobuf IntervalType for a particular short name.
    :param interval_type:
    :return:
    """
    if "minute" in interval_type:
        return "MINUTES_TIME_INTERVAL_TYPE"
    elif "hour" in interval_type:
        return "HOURS_TIME_INTERVAL_TYPE"
    elif "weekday" in interval_type:
        return "WEEKDAYS_TIME_INTERVAL_TYPE"
    elif "day" in interval_type:
        return "DAYS_TIME_INTERVAL_TYPE"


def get_max_hours_from_cron(cron):
    cron_values = cron.split(" ")
    hours = cron_values[1]
    if hours == "*":
        return 0
    return int(hours.split(",")[-1])


def get_days_since_n_weekdays(start_date, n):
    days_since_last_business_day = 0
    weekday_ordinal = datetime.date.weekday(start_date - datetime.timedelta(days=n))
    # 5 is Saturday, 6 is Sunday
    if weekday_ordinal >= 5:
        days_since_last_business_day = 2
    return days_since_last_business_day


def get_notification_channels(notifications: List[str]) -> List[NotificationChannel]:
    channels: List[NotificationChannel] = []

    for n in notifications:
        nc = NotificationChannel()

        if n.startswith('#') or n.startswith('@'):
            nc.slack_channel = n
        elif '@' in n and '.' in n:
            nc.email = n
        else:
            raise Exception(f'Invalid notification format: {n}')

        channels.append(nc)

    return channels


def get_freshness_metric_name_for_field(table: Table, column_name: str) -> MetricType:
    for c in table.columns:
        if c.name.lower() == column_name.lower():
            if c.type == "TIMESTAMP_LIKE":
                return SimpleMetricType.PREDEFINED.factory("HOURS_SINCE_MAX_TIMESTAMP")
            elif c.type == "DATE_LIKE":
                return SimpleMetricType.PREDEFINED.factory("HOURS_SINCE_MAX_DATE")
            else:
                raise Exception(f'Type not compatible with freshness: {c.type}')


def get_file_name_for_metric(m: MetricInfo):
    """
    Formats a name for persisting metrics to files.
    :param m: MetricInfo object from which we build the name.
    :return:  Formated name: scnama_name-dataset_name-field_name-metric_name.json
    """
    mc = m.metric_configuration
    md = m.metric_metadata
    fn = f"{'_'.join(md.schema_name.split('.'))}-{md.dataset_name}-{md.field_name}-{mc.name}.json"
    return fn.replace(' ', '_')


def is_auto_threshold(t: Threshold) -> bool:
    return "autoThreshold" in t.to_dict()


def has_auto_threshold(ts: List[Threshold]) -> bool:
    for t in ts:
        if "autoThreshold" in t.to_dict():
            return True
    return False


def set_default_model_type_for_threshold(thresholds: List[Threshold]) -> List[Threshold]:
    for t in thresholds:
        if is_auto_threshold(t):
            if not t.auto_threshold.model_type:
                t.auto_threshold.model_type = ForecastModelType.BOOTSTRAP_THRESHOLD_MODEL_TYPE

    return thresholds


def get_thresholds_for_metric(metric_name: str, timezone: str = None, delay_at_update: str = None,
                              update_schedule: str = None, thresholds: List[Threshold] = None) -> List[Threshold]:
    # if threshold has been defined user then use it!
    if thresholds:
        return thresholds
    # If its a freshness
    elif is_freshness_metric(metric_name):
        tj = {
            "freshnessScheduleThreshold": {
                "bound": {
                    "boundType": "UPPER_BOUND_SIMPLE_BOUND_TYPE",
                    "value": -1
                },
                "cron": update_schedule,
                "timezone": timezone,
                "delayAtUpdate": get_time_interval_for_delay_string(delay_at_update,
                                                                    metric_name,
                                                                    update_schedule)
            }
        }
        return [Threshold().from_dict(tj)]
    # Default to autothresholds
    else:
        return [
            Threshold().from_dict({"autoThreshold": {"bound":
                                                         {"boundType": "LOWER_BOUND_SIMPLE_BOUND_TYPE", "value": -1.0},
                                                     "modelType": "BOOTSTRAP_THRESHOLD_MODEL_TYPE"}}),
            Threshold().from_dict({"autoThreshold": {"bound":
                                                         {"boundType": "UPPER_BOUND_SIMPLE_BOUND_TYPE", "value": -1.0},
                                                     "modelType": "BOOTSTRAP_THRESHOLD_MODEL_TYPE"}})
        ]


def get_time_interval_for_delay_string(delay_at_update: str, metric_type: str, update_schedule: str) -> dict:
    """
    Identifies correct time interval for freshness metrics.
    :param delay_at_update: number of minutes or hours to delay at update.
    :param metric_type: string name of metric type.
    :param update_schedule: cron update schedule for table.
    :return:
    """
    # TODO must unit test.  Also refactor to return a TimeInterval instead of a dict!.
    split_input = delay_at_update.split(" ")
    interval_value = int(split_input[0])
    if interval_value == 0:
        """Returns None if interval value is 0 -- default.  This works to remove the TimeInterval from the final created
        object so that default is used at the service."""
        return None
    interval_type = get_proto_interval_type(split_input[1])
    if metric_type == "HOURS_SINCE_MAX_DATE":
        hours_from_cron = get_max_hours_from_cron(update_schedule)
        if interval_type == "HOURS_TIME_INTERVAL_TYPE" or interval_type == "MINUTES_TIME_INTERVAL_TYPE":
            logging.warning("Delay granularity for date column must be in days, ignoring value")
            interval_type = "HOURS_TIME_INTERVAL_TYPE"
            interval_value = hours_from_cron
        elif interval_type == "WEEKDAYS_TIME_INTERVAL_TYPE":
            lookback_weekdays = interval_value + 1 if datetime.datetime.utcnow().hour <= hours_from_cron \
                else interval_value
            logging.info("Weekdays to look back {}".format(lookback_weekdays))
            days_since_last_business_day = get_days_since_n_weekdays(datetime.date.today(), lookback_weekdays)
            logging.info("total days to use for delay {}".format(days_since_last_business_day))
            interval_type = "HOURS_TIME_INTERVAL_TYPE"
            interval_value = (days_since_last_business_day + lookback_weekdays) * 24 + hours_from_cron
        else:
            interval_type = "HOURS_TIME_INTERVAL_TYPE"
            interval_value = interval_value * 24 + hours_from_cron
    return {
        "intervalValue": interval_value,
        "intervalType": interval_type
    }


def is_failed(datum: dict) -> bool:
    if 'latestMetricRuns' in datum and datum['latestMetricRuns']:
        if 'failureReason' in datum['latestMetricRuns'][-1]:
            failure_reason = datum['latestMetricRuns'][-1]['failureReason']
            log.info(failure_reason)
            return failure_reason in MetricRunFailureReason

    return False


def get_failed_code(datum: dict) -> Union[None, str]:
    if 'latestMetricRuns' in datum and datum['latestMetricRuns']:
        if 'failureReason' in datum['latestMetricRuns'][-1]:
            failure_reason = datum['latestMetricRuns'][-1]['failureReason']
            log.info(failure_reason)
            return failure_reason

    return None


def get_seconds_from_window_size(window_size):
    if window_size == "1 day":
        return 86400
    elif window_size == "1 hour":
        return 3600
    else:
        raise Exception("Can only set window size of '1 hour' or '1 day'")


class MetricTimeNotEnabledStats(EnumExtension):
    HOURS_SINCE_MAX_TIMESTAMP = 'HOURS_SINCE_MAX_TIMESTAMP'
    HOURS_SINCE_MAX_DATE = 'HOURS_SINCE_MAX_DATE'
    PERCENT_DATE_NOT_IN_FUTURE = 'PERCENT_DATE_NOT_IN_FUTURE'
    PERCENT_NOT_IN_FUTURE = 'PERCENT_NOT_IN_FUTURE'
    COUNT_DATE_NOT_IN_FUTURE = 'COUNT_DATE_NOT_IN_FUTURE'


def is_metric_time_enabled(predefined_metric_name: str):
    return predefined_metric_name.upper() in MetricTimeNotEnabledStats.list()


def enforce_lookback_type_defaults(predefined_metric_name: str, lookback_type: str,
                                   metric_time_exists: bool) -> LookbackType:
    if is_metric_time_enabled(predefined_metric_name=predefined_metric_name):
        lbts = 'DATA_TIME_LOOKBACK_TYPE'
    elif lookback_type is None:
        lbts = "METRIC_TIME_LOOKBACK_TYPE"
    else:
        lbts = lookback_type

    if metric_time_exists:
        return LookbackType.from_string(lbts)
    else:
        return LookbackType.UNDEFINED_LOOKBACK_TYPE


def get_grain_seconds(lookback_type: LookbackType, window_size_seconds: int):
    if lookback_type == LookbackType.METRIC_TIME_LOOKBACK_TYPE:
        return window_size_seconds


def merge_existing_metric_conf(new_metric: MetricConfiguration, is_freshness_metric: bool, metric_time_exists: bool,
                               existing_metric: MetricConfiguration = None) -> MetricConfiguration:
    """
    Updates/Merges an existing metric configuration with a new metric configuration.  Enforces updatable configurations.
    If existing metric configuration is none the new metric configuration is returned with no chagnes..
    :param new_metric: new MetricConfiguration
    :param is_freshness_metric: whether its a freshness metric
    :param metric_time_exists: whether metric time exists on the table.
    :param existing_metric: existing metric configuration.
    :return: Merged MetricConfiguration
    """
    # TODO move to SimpleUpsertMetricRequest as private instance method.  This isnt really intended for reuse.
    if not existing_metric:
        return new_metric
    else:
        existing_metric.name = new_metric.name
        existing_metric.thresholds = new_metric.thresholds
        existing_metric.notification_channels = new_metric.notification_channels if new_metric.notification_channels \
            else []
        existing_metric.schedule_frequency = new_metric.schedule_frequency
        if not is_freshness_metric and metric_time_exists:
            existing_metric.lookback_type = new_metric.lookback_type
            existing_metric.lookback = new_metric.lookback
            existing_metric.grain_seconds = new_metric.grain_seconds
        return existing_metric
