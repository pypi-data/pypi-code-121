from __future__ import absolute_import
from datetime import datetime, timedelta

import enum
import six
import pytz

from rapyuta_io.utils.error import InvalidParameterException
from rapyuta_io.utils.object_converter import ObjBase, enum_field, list_field
from rapyuta_io.utils.utils import valid_list_elements


def _use_clickhouse(start_datetime):
    use_clickhouse_window = timedelta(days=7)
    if start_datetime.tzinfo:
        interval = datetime.now(tz=pytz.UTC) - start_datetime.astimezone(tz=pytz.UTC)
    else:
        interval = datetime.now() - start_datetime
    return interval > use_clickhouse_window


class _StepIntervalInflux(str, enum.Enum):

    def __str__(self):
        return str(self.value)

    ONE_SECOND = '1s'
    TEN_SECONDS = '10s'
    THIRTY_SECONDS = '30s'
    ONE_MINUTE = '1m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'


class _StepIntervalClickhouse(str, enum.Enum):

    def __str__(self):
        return str(self.value)

    ONE_MINUTE = '1m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'


class StepInterval(str, enum.Enum):
    """
    StepInterval may be one of: \n
    StepInterval.ONE_SECOND (1s) \n
    StepInterval.TEN_SECONDS (10s)  \n
    StepInterval.THIRTY_SECONDS (30s) \n
    StepInterval.ONE_MINUTE (1m) \n
    StepInterval.FIVE_MINUTES (5m) \n
    StepInterval.FIFTEEN_MINUTES (15m) \n
    """

    def __str__(self):
        return str(self.value)

    ONE_SECOND = '1s'
    TEN_SECONDS = '10s'
    THIRTY_SECONDS = '30s'
    ONE_MINUTE = '1m'
    FIVE_MINUTES = '5m'
    FIFTEEN_MINUTES = '15m'


class MetricFunction(str, enum.Enum):
    """
    MetricFunction may be one of: \n
    MetricFunction.COUNT (count)\n
    MetricFunction.DISTINCT (distinct) \n
    MetricFunction.MEAN (mean) \n
    MetricFunction.MEDIAN (median) \n
    MetricFunction.MODE (mode) \n
    MetricFunction.AVG (avg) \n

    MetricFunction.STDDEV (stddev) \n
    MetricFunction.DERIVATIVE (derivative) \n

    MetricFunction.MAX (max) \n
    MetricFunction.MIN (min) \n
    MetricFunction.FIRST (first) \n
    MetricFunction.LAST (last) \n
    MetricFunction.PERCENTILE_95 (percentile_95) \n
    MetricFunction.PERCENTILE_99 (percentile_99) \n

    """

    def __str__(self):
        return str(self.value)

    COUNT = 'count'
    DISTINCT = 'distinct'
    MEAN = 'mean'
    MEDIAN = 'median'
    MODE = 'mode'
    AVG = 'avg'

    # Transformations
    STDDEV = 'stddev'
    DERIVATIVE = 'derivative'

    # Selectors
    MAX = 'max'
    MIN = 'min'
    FIRST = 'first'
    LAST = 'last'
    PERCENTILE_95 = 'percentile_95'
    PERCENTILE_99 = 'percentile_99'


class SortOrder(str, enum.Enum):
    """
    SortOrder may be one of: \n
    SortOrder.ASC (asc) \n
    SortOrder.DESC (desc) \n
    """

    def __str__(self):
        return str(self.value)

    ASC = 'asc'
    DESC = 'desc'


class Entity(str, enum.Enum):
    """
    Entity may be one of: \n
    Entity.DEVICE (device) \n
    Entity.DEPLOYMENT (deployment) \n
    Entity.PROJECT (project) \n
    Entity.ORGANIZATION (organization) \n
    """

    def __str__(self):
        return str(self.value)

    DEVICE = 'device'
    DEPLOYMENT = 'deployment'
    PROJECT = 'project'
    ORGANIZATION = 'organization'


class MetricOperation(ObjBase):
    """
    MetricsOperation class that defines a function over a metric

    :ivar function: function to applied on metric
    :vartype function: :py:class:`~rapyuta_io.clients.metrics.MetricFunction`
    :ivar metric_name: name of the metric
    :vartype metric_name: str

    :param function: function to applied on metric
    :type function: :py:class:`~rapyuta_io.clients.metrics.MetricFunction`
    :param metric_name: name of the metric
    :type metric_name: str
    """
    def __init__(self, function, metric_name):
        self.validate(function, metric_name)
        self.function = function
        self.metric_name = metric_name

    @staticmethod
    def validate(function, metric_name):
        if function not in list(MetricFunction.__members__.values()):
            raise InvalidParameterException('function should be member of MetricFunction')
        if not isinstance(metric_name, six.string_types):
            raise InvalidParameterException('metric name should be a string')

    def get_deserialize_map(self):
        return {}

    def get_serialize_map(self):
        return {
            'function': 'function',
            'metric_name': 'metric_name'
        }


class QueryMetricsRequest(ObjBase):
    """
    QueryMetricsRequest class

    :ivar from_datetime: start time of querying metrics
    :vartype from_datetime: :py:class:`~datetime.datetime`
    :ivar to_datetime: end time of querying metrics
    :vartype to_datetime: :py:class:`~datetime.datetime`
    :ivar step_interval: time interval to group data
    :vartype step_interval: :py:class:`~rapyuta_io.clients.metrics.StepInterval`
    :ivar ~.metrics: list of metrics
    :vartype ~.metrics: list(:py:class:`~rapyuta_io.clients.metrics.MetricOperation`)
    :ivar tags: key pair of tags (must include project_id and organization_id)
    :vartype tags: dict
    :ivar sort: ordering to sort the metrics
    :vartype sort: :py:class:`~rapyuta_io.clients.metrics.SortOrder`
    :ivar groupby: list of tags to group data
    :vartype groupby: list(str)

    :param from_datetime: start time of querying metrics
    :type from_datetime: :py:class:`~datetime.datetime`
    :param to_datetime: end time of querying metrics
    :type to_datetime: :py:class:`~datetime.datetime`
    :param step_interval: time interval to group data
    :type step_interval: :py:class:`~rapyuta_io.clients.metrics.StepInterval`
    :param metrics: list of metrics
    :type metrics: list(:py:class:`~rapyuta_io.clients.metrics.MetricOperation`)
    :param tags: key pair of tags (must include project_id and organization_id)
    :type tags: dict
    :param sort: ordering to sort the metrics
    :type sort: :py:class:`~rapyuta_io.clients.metrics.SortOrder`
    :param groupby: list of tags to group data
    :type groupby: list(str)
    """

    PROJECT_ID_TAG = 'project_id'
    ORGANIZATION_ID_TAG = 'organization_id'

    def __init__(self, from_datetime, to_datetime, step_interval, metrics, tags=None, sort=None, groupby=None):
        self.validate(from_datetime, to_datetime, step_interval, metrics, tags, sort, groupby)
        self.from_datetime = from_datetime
        self.to_datetime = to_datetime
        self.step_interval = step_interval
        self.metrics = metrics
        self.sort = sort or SortOrder.ASC
        self.groupby = groupby
        self.tags = tags or {}

    def validate(self, from_datetime, to_datetime, step_interval, metrics, tags, sort, groupby):

        if not isinstance(from_datetime, datetime):
            raise InvalidParameterException('from_datetime should be a datetime object')
        if not isinstance(to_datetime, datetime):
            raise InvalidParameterException('to_datetime should be a datetime object')
        if not valid_list_elements(metrics, MetricOperation) or len(metrics) < 1:
            raise InvalidParameterException('metrics should be non-empty list of MetricOperation objects')
        if sort is not None and sort not in list(SortOrder.__members__.values()):
            raise InvalidParameterException('sort should be a member of SortOrder enum')
        if groupby is not None and not valid_list_elements(groupby, six.string_types):
            raise InvalidParameterException('grouby should be list of strings')
        if tags is not None and not isinstance(tags, dict):
            raise InvalidParameterException('tags should be key value of tags and values')
        if step_interval not in list(StepInterval.__members__.values()):
            raise InvalidParameterException('step_interval should be a member of StepInterval enum')

        step_interval_enums = _StepIntervalInflux
        if _use_clickhouse(from_datetime):
            step_interval_enums = _StepIntervalClickhouse

        choices = [v.value for v in step_interval_enums]
        if step_interval.value not in choices:
            raise InvalidParameterException('step_interval must be one of 1m, 5m, 15m '
                                            'for from_datetime before 7 days from today')

        if from_datetime > to_datetime:
            raise InvalidParameterException('from_datetime must be less than to_datetime')

    def get_deserialize_map(self):
        return {}

    def serialize(self):
        serialized = super(QueryMetricsRequest, self).serialize()
        serialized.update({'from': self.from_datetime.isoformat(),
                           'to': self.to_datetime.isoformat()})
        return serialized

    def get_serialize_map(self):
        return {
            'step': 'step_interval',
            'metrics': 'metrics',
            'sort': 'sort',
            'groupby': 'groupby',
            'tags': 'tags',
        }


class QueryMetricsResponse(ObjBase):
    """
    QueryMetricsResponse class

    :ivar columns: list of columns object
    :vartype columns: :py:class:`~rapyuta_io.clients.metrics.Column`
    :ivar rows: list of metrics values
    :vartype rows: :py:class:`list(list(float))`
    """
    def __init__(self):
        self.rows = []
        self.columns = []

    def get_serialize_map(self):
        return {}

    def get_deserialize_map(self):
        return {
            'rows': 'rows',
            'columns': list_field('columns', Column),
        }

    def to_row_column_format(self):
        """
        Returns rows and columns in a format that can be passed to `pandas.DataFrame()`.

        :rtype: tuple(generator, list)
        """
        return zip(*self.rows), list(map(str, self.columns))


class Column(ObjBase):
    """
    Column class

    :ivar name: name of metric
    :vartype name: str
    :ivar function: applied metric function
    :vartype function: :py:class:`~rapyuta_io.clients.metrics.MetricFunction`
    :ivar metric_group: metric group
    :vartype metric_group: str
    :ivar tag_names: list of tag names
    :vartype tag_names: str
    :ivar tag_values: list of tag values
    :vartype tag_values: str
    """
    def __init__(self):
        self.name = None
        self.function = None
        self.metric_group = None
        self.tag_names = None
        self.tag_values = None

    def get_serialize_map(self):
        return {}

    def get_deserialize_map(self):
        return {
            'name': 'name',
            'function': enum_field('function', MetricFunction),
            'metric_group': 'metric_group',
            'tag_names': 'tag_names',
            'tag_values': 'tag_values',
        }

    def __str__(self):
        if self.name == 'timestamp':
            return self.name

        if self.tag_values:
            tag_pair = ['{}={}'.format(k, v) for k, v in zip(self.tag_names, self.tag_values)]
            tags = '{' + ','.join(tag_pair) + '}'
            return '{}({}.{}){}'.format(self.function, self.metric_group, self.name, tags)

        return '{}({}.{})'.format(self.function, self.metric_group, self.name)


class _MetricsMetaRequest(object):
    """
    Metrics Metadata Query

    :ivar entity: one of Entity enum
    :vartype entity: :py:class:`~rapyuta_io.clients.metrics.Entity`
    :ivar entity_id: value of entity
    :vartype entity_id: str
    :ivar start_date: filter from start_date
    :vartype start_date: :py:class:`~datetime.datetime`
    :ivar end_date: filter to end_date
    :vartype end_date: :py:class:`~datetime.datetime`

    :param entity: one of Entity enum
    :type entity: :py:class:`~rapyuta_io.clients.metrics.Entity`
    :param entity_id: value of entity
    :type entity_id: str
    :param start_date: filter from start_date
    :type start_date: :py:class:`~datetime.datetime`
    :param end_date: filter to end_date
    :type end_date: :py:class:`~datetime.datetime`
    """

    def __init__(self, entity, entity_id, start_date, end_date):
        self.validate(entity, entity_id, start_date, end_date)
        self.entity = entity
        self.entity_id = entity_id
        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def validate(entity, entity_id, start_date, end_date):
        if entity not in list(Entity.__members__.values()):
            raise InvalidParameterException('entity should be a member of Entity enum')
        if not isinstance(entity_id, six.string_types) or not entity_id:
            raise InvalidParameterException('entity_id non empty string')
        if not isinstance(start_date, datetime):
            raise InvalidParameterException('start_date should be a datetime object')
        if not isinstance(end_date, datetime):
            raise InvalidParameterException('end_date should be a datetime object')

        if start_date > end_date:
            raise InvalidParameterException('start_date must be less than end_date')

        if entity == Entity.ORGANIZATION and not _use_clickhouse(start_date):
            raise InvalidParameterException('Entity.ORGANIZATION cannot be queried '
                                            'for start_date before 7 days from today')

    def to_dict(self):
        return {
            'entity': self.entity,
            'entity_id': self.entity_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
        }


class Metric(ObjBase):
    """
    Metric class, has metric_group and list of metric names

    :ivar metric_group: name of the metric
    :vartype metric_group: str
    :ivar metric_names: list of metrics
    :vartype metric_names: list(str)
    """

    def get_serialize_map(self):
        return {}

    def get_deserialize_map(self):
        return {
            'metric_group': 'metric_group',
            'metric_names': 'metric_names'
        }


class Tags(ObjBase):
    """
    Tags class, has metric_group and list of tags

    :ivar metric_group: name of the metric
    :vartype metric_group: str
    :ivar tags: list of tags
    :vartype tags: list(str)
    """

    def get_serialize_map(self):
        return {}

    def get_deserialize_map(self):
        return {
            'metric_group': 'metric_group',
            'tags': 'tags'
        }


class ListMetricsRequest(_MetricsMetaRequest):

    __doc__ = _MetricsMetaRequest.__doc__.replace('Metrics Metadata Query', 'List Metrics Request')

    def __init__(self, entity, entity_id, start_date, end_date):
        super(ListMetricsRequest, self).__init__(entity, entity_id, start_date, end_date)


class ListTagKeysRequest(_MetricsMetaRequest):

    __doc__ = _MetricsMetaRequest.__doc__.replace('Metrics Metadata Query', 'List Tag Keys Request')

    def __init__(self, entity, entity_id, start_date, end_date):
        super(ListTagKeysRequest, self).__init__(entity, entity_id, start_date, end_date)


class ListTagValuesRequest(_MetricsMetaRequest):
    """
    List Tag Values Request

    :ivar entity: one of Entity enum
    :vartype entity: :py:class:`~rapyuta_io.clients.metrics.Entity`
    :ivar entity_id: value of entity
    :vartype entity_id: str
    :ivar tag: value of the tag key
    :vartype tag: str
    :ivar start_date: filter from start_date
    :vartype start_date: :py:class:`~datetime.datetime`
    :ivar end_date: filter to end_date
    :vartype end_date: :py:class:`~datetime.datetime`

    :param entity: one of Entity enum
    :type entity: :py:class:`~rapyuta_io.clients.metrics.Entity`
    :param entity_id: value of entity
    :type entity_id: str
    :param tag: value of the tag key
    :type tag: str
    :param start_date: filter from start_date
    :type start_date: :py:class:`~datetime.datetime`
    :param end_date: filter to end_date
    :type end_date: :py:class:`~datetime.datetime`
    """

    def __init__(self, entity, entity_id, tag, start_date, end_date):
        self.validate_tag(tag)
        super(ListTagValuesRequest, self).__init__(entity, entity_id, start_date, end_date)
        self.tag = tag

    @staticmethod
    def validate_tag(tag):
        if not isinstance(tag, six.string_types) or not tag:
            raise InvalidParameterException('tag non empty string')
