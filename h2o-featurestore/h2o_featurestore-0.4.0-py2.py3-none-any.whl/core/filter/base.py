from google.protobuf.json_format import Parse

from .. import FeatureSetSearch_pb2 as pb


class Field(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, value):
        return self._build("eq", value)

    def __ne__(self, value):
        return self._build("ne", value)


class StringField(Field):
    def like(self, value):
        return self._build("regex", value)

    def in_(self, *args):
        return self._build("in", args)

    def _build(self, operator, value):
        _filter = pb.Filter()
        text_filter = pb.TextualFilter()
        text_filter.field = self.name
        if isinstance(value, (list, tuple, set)):
            text_filter.value.extend([str(i) for i in value])
        else:
            text_filter.value.append(str(value))
        text_filter.operator = operator
        _filter.text.CopyFrom(text_filter)
        return _filter


class BooleanField(Field):
    def _build(self, operator, value):
        _filter = pb.Filter()
        boolean_filter = pb.BooleanFilter()
        boolean_filter.field = self.name
        boolean_filter.value = bool(value)
        boolean_filter.operator = operator
        _filter.boolean.CopyFrom(boolean_filter)
        return _filter


class NumericField(Field):
    def __init__(self, name):
        super(NumericField, self).__init__(name)
        self._aggregate = None

    def __gt__(self, value):
        return self._build("gt", value)

    def __lt__(self, value):
        return self._build("lt", value)

    def __ge__(self, value):
        return self._build("gte", value)

    def __le__(self, value):
        return self._build("lte", value)

    def sum(self):
        self._aggregate = "sum"
        return self

    def avg(self):
        self._aggregate = "avg"
        return self

    def min(self):
        self._aggregate = "min"
        return self

    def max(self):
        self._aggregate = "max"
        return self

    def _build(self, operator, value):
        _filter = pb.Filter()
        numeric_filter = pb.NumericalFilter()
        numeric_filter.field = self.name
        numeric_filter.value = value
        numeric_filter.operator = operator
        if self._aggregate:
            numeric_filter.aggregate = self._aggregate
        _filter.numeric.CopyFrom(numeric_filter)
        self._aggregate = ""  # reset
        return _filter


class ArrayField(StringField):
    def __init__(self, name):
        super(ArrayField, self).__init__(name)
        self._aggregate = None

    def in_(self, *args):
        return super(ArrayField, self)._build("in", args)

    def length(self):
        self._aggregate = "length"
        return self

    def __gt__(self, value):
        return self._build("gt", value)

    def __lt__(self, value):
        return self._build("lt", value)

    def __ge__(self, value):
        return self._build("gte", value)

    def __le__(self, value):
        return self._build("lte", value)

    def _build(self, operator, value):
        _filter = pb.Filter()
        if isinstance(value, str):
            text_filter = pb.TextualFilter()
            text_filter.field = self.name
            text_filter.value.extend([value])
            text_filter.operator = operator
            _filter.text.CopyFrom(text_filter)
        else:
            numeric_filter = pb.NumericalFilter()
            numeric_filter.field = self.name
            numeric_filter.value = value
            numeric_filter.operator = operator
            if self._aggregate:
                numeric_filter.aggregate = self._aggregate
            _filter.numeric.CopyFrom(numeric_filter)
        self._aggregate = ""
        return _filter


class Case(Field):
    def __init__(self, case):
        self._case = case

    def count(self):
        count_case_filter = pb.CountCaseFilter()
        if self._case.text.ByteSize():
            count_case_filter.text.CopyFrom(self._case.text)
        elif self._case.numeric.ByteSize():
            count_case_filter.numeric.CopyFrom(self._case.numeric)
        elif self._case.boolean.ByteSize():
            count_case_filter.boolean.CopyFrom(self._case.boolean)
        self._count_case = count_case_filter
        return self

    def _build(self, operator, value):
        _filter = pb.Filter()
        self._count_case.operator = operator
        self._count_case.value = value
        _filter.count_case.CopyFrom(self._count_case)
        return _filter

    def __gt__(self, value):
        return self._build("gt", value)

    def __lt__(self, value):
        return self._build("lt", value)

    def __ge__(self, value):
        return self._build("gte", value)

    def __le__(self, value):
        return self._build("lte", value)


class FilterBuilder(object):
    def __init__(self):
        self._filters = []

    def add(self, filter):
        self._filters.append(filter)
        return self

    def build(self):
        query = pb.Query()
        query.filters.extend(self._filters)
        return query


def convert_json_query_to_proto(json_query):
    query = pb.Query()
    return Parse(text=json_query, message=query)
