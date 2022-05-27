from enum import Enum


class Context(Enum):
    EXCHANGE = 'exchange'
    TRADE = 'trade'

    @staticmethod
    def parse(value):
        result = [member for name, member in Context.__members__.items() if member.value.lower() == value.lower()]
        return result[0]
