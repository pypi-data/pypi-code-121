import re

EMPTY_CELL = 'te6ccgEBAQEAAgAAAA=='  # b5ee9c72 | 01 01 01 01 | 00 02 | 00 | 00 00

GRAPHQL_LIMIT = 50

ADDRESS_REGEX = re.compile(r'(0|-1):[0-9a-f]{64}')
