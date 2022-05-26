from collections import namedtuple

Transaction = namedtuple('Transaction', ['signal', 'value'])


def create_info_type(features):
    return namedtuple('Info', [*features])
