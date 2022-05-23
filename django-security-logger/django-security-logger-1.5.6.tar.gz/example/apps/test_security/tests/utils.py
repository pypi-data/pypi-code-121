import datetime
import uuid
import decimal

from germanium.test_cases.default import GermaniumTestCase
from germanium.tools import assert_equal

from security.utils import serialize_data, deserialize_data


class UtilsTestCase(GermaniumTestCase):

    def test_utils_serialize_and_deserialize_data_should_return_right_values(self):
        data = {
            'a': datetime.datetime(2018, 1, 10, 5, 47, 11),
            'b': [datetime.date(2020, 5, 21), datetime.time(16, 59)],
            'c': {
                'd': uuid.UUID('06335e84-2872-4914-8c5d-3ed07d2a2f16'),
                'e': decimal.Decimal('158.687')
            },
            'f': datetime.timedelta(days=4, hours=15, minutes=6, seconds=45),
            'g': [5, 'test'],
        }
        serialized_data = {
            'a': {'@type': 'datetime', '@value': '2018-01-10T05:47:11'},
            'b': [{'@type': 'date', '@value': '2020-05-21'}, {'@type': 'time', '@value': '16:59:00'}],
            'c': {
                'd': {'@type': 'uuid', '@value': '06335e84-2872-4914-8c5d-3ed07d2a2f16'},
                'e': {'@type': 'decimal', '@value': '158.687'}
            },
            'f': {'@type': 'timedelta', '@value': 'P4DT15H06M45S'},
            'g': [5, 'test']
        }
        assert_equal(serialize_data(data), serialized_data)
        assert_equal(deserialize_data(serialized_data), data)
