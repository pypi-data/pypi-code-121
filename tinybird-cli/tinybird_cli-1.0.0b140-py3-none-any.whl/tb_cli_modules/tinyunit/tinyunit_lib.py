import json
from json import JSONEncoder
from collections import namedtuple


class MyJSONEncoder(JSONEncoder):
    # def default(self, in_obj):
    #     loaded_data = [
    #             DataUnitTest(
    #                 getattr(unitDataTest, 'id'),
    #                 getattr(unitDataTest, 'description'),
    #                 getattr(unitDataTest, 'enabled'),
    #                 getattr(unitDataTest, 'endpoint'),
    #                 getattr(unitDataTest, 'result'),
    #                 getattr(unitDataTest, 'time'),
    #                 getattr(unitDataTest, 'sql'))
    #             for unitDataTest in in_obj]
    #     return loaded_data
    def default(self, obj):
        return obj.to_json()


class DataUnitTest:
    def __init__(self, id, description, enabled, endpoint, result, time, sql):
        self.id = id
        self.description = description
        self.enabled = enabled
        self.endpoint = endpoint
        self.result = result
        self.time = time
        self.sql = sql

    def __iter__(self):
        yield from {
            "id": self.id,
            "description": self.description,
            "enabled": self.enabled,
            "endpoint": self.endpoint,
            "sql": self.sql,
            "result": self.result,
            "time": self.time
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        return self.__str__()


def customDataUnitTestDecoder(dataUnitTestDict):
    return namedtuple('X', dataUnitTestDict.keys())(*dataUnitTestDict.values())
