import datetime
import json
import random
import string

from sqlalchemy import Column, Integer, INT, String, Text, JSON, ARRAY, Date, DateTime, TIMESTAMP, Boolean


class TestColumn:

    @classmethod
    def init_field(cls, column: Column):
        if isinstance(column.type, (Integer, INT)):
            return IntField(column)
        elif isinstance(column.type, (String, Text)):
            return StringField(column)
        elif isinstance(column.type, JSON):
            return JsonField(column)
        elif isinstance(column.type, ARRAY):
            return ArrayField(column)
        elif isinstance(column.type, Date):
            return DateField(column)
        elif isinstance(column.type, DateTime):
            return DateTimeField(column)
        elif isinstance(column.type, TIMESTAMP):
            return TimestampField(column)
        elif isinstance(column.type, Boolean):
            return BooleanField(column)


class Field:

    def __init__(self, column: Column):
        self._column = column

    def random_value(self):
        raise NotImplementedError

    def _random_int(self, max_num=100):
        return random.randint(0, max_num)

    def _random_string(self, max_length):
        length = random.randint(0, max_length)
        return ''.join(random.choices(string.digits + string.ascii_letters, k=length))

    def _random_json(self):
        length = random.randint(0, 10)
        result = {
            ''.join(random.choices(string.digits + string.ascii_letters, k=8)): i
            for i in range(length)
        }

        return result

    def _random_text(self):
        return random.sample(string.digits + string.ascii_letters, 100)

    def _random_list(self):
        length = random.randint(0, 10)
        return [random.sample(string.digits + string.ascii_letters, i) for i in range(length)]

    def _random_date(self):
        return datetime.date.today()

    def _random_datetime(self):
        return datetime.datetime.utcnow()

    def _random_array(self, child_type: "Field"):
        length = random.randint(0, 10)
        return [child_type.random_value() for i in range(length)]

    def _random_timestamp(self):
        return datetime.datetime.now().timestamp()

    def _random_boolean(self):
        return bool(random.randint(0, 2))


class IntField(Field):
    def __init__(self, column):
        super(IntField, self).__init__(column)

    def random_value(self):
        return self._random_int()


class BooleanField(Field):
    def __init__(self, column):
        super(BooleanField, self).__init__(column)

    def random_value(self):
        return self._random_boolean()


class StringField(Field):
    def __init__(self, column):
        super(StringField, self).__init__(column)
        self.max_length = 100 if type(column.type) == Text else column.type.length
        self.default = column.default or column.server_default

    def random_value(self):
        if self.default == "{}":
            return json.dumps(self._random_json())
        elif self.default == "[]":
            return json.dumps(self._random_list())
        return self._random_string(self.max_length)


class JsonField(Field):
    def __init__(self, column):
        super(JsonField, self).__init__(column)

    def random_value(self):
        return self._random_json()


class ArrayField(Field):
    def __init__(self, column):
        super(ArrayField, self).__init__(column)

        self._item_type = column.type.item_type
        self._item_type_ins = TestColumn.init_field(Column(self._item_type))

    def random_value(self):
        return self._random_array(self._item_type_ins)


class DateField(Field):
    def __init__(self, column):
        super(DateField, self).__init__(column)

    def random_value(self):
        return self._random_date()


class DateTimeField(Field):
    def __init__(self, column):
        super(DateTimeField, self).__init__(column)

    def random_value(self):
        return self._random_datetime()


class TimestampField(Field):
    def __init__(self, column):
        super(TimestampField, self).__init__(column)

    def random_value(self):
        return self._random_timestamp()
