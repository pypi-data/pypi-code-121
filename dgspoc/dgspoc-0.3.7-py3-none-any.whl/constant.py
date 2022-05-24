"""Module containing the logic for constant definition"""

import re
from enum import IntFlag


class ICSValue:
    """Treating value as ignore case and ignore space during evaluating
    string equality"""
    def __init__(self, value, equality='', stripped=False):
        self.value = str(value)
        self.equality = equality
        self.stripped = stripped

    def __eq__(self, other):
        value1 = self.value.lower()

        if isinstance(other, self.__class__):
            value2 = other.value.lower()
        else:
            value2 = str(other).lower()

        value1 = re.sub(' +', ' ', value1)
        value2 = re.sub(' +', ' ', value2)

        if self.stripped:
            value1 = value1.strip()
            value2 = value2.strip()

        if self.equality:
            if isinstance(self.equality, (list, tuple)):
                is_equal = True
                for item in self.equality:
                    item = str(item)
                    try:
                        is_equal = bool(re.match(item, value2, re.I))
                    except Exception as ex:     # noqa
                        item = re.sub(' +', ' ', item.lower())
                        is_equal &= item == value2
                return is_equal
            else:
                pattern = str(self.equality)
                try:
                    is_equal = bool(re.match(pattern, value2, re.I))
                except Exception as ex:     # noqa
                    equality = re.sub(' +', ' ', str(self.equality).lower())
                    is_equal = equality == value2
                return is_equal
        else:
            chk = value1.strip() == value2.strip()
        return chk

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return self.value


class ICSStripValue(ICSValue):
    """Treating value as ignore case, ignore space, and strip during evaluating
    string equality"""
    def __init__(self, value, equality=''):
        super().__init__(value, equality=equality, stripped=True)


class ECODE(IntFlag):
    SUCCESS = 0
    BAD = 1
    PASSED = SUCCESS
    FAILED = BAD


class FWTYPE:
    UNITTEST = ICSStripValue('unittest')
    PYTEST = ICSStripValue('pytest')
    ROBOTFRAMEWORK = ICSStripValue('robotframework', equality=r'(rf|robotframework)$')


class CONVTYPE:
    CSV = ICSStripValue('csv')
    JSON = ICSStripValue('json')
    TEMPLATE = ICSStripValue('template')


class COMMAND:
    BUILD = ICSStripValue('build')
    INFO = ICSStripValue('info')
    REPORT = ICSStripValue('report')
    SEARCH = ICSStripValue('search')
    TEST = ICSStripValue('test')
    VERSION = ICSStripValue('version')
    USAGE = ICSStripValue('usage')


class FEATURE:
    TEMPLATE = ICSStripValue('template')
    SCRIPT = ICSStripValue(
        'script', equality=r'(unittest|pytest|robotframework|rf)([_ -]?script)?$'
    )
    BATCH = ICSStripValue('batch')
    UNITTEST = ICSStripValue('unittest', equality=r'unittest([_ -]?script)?$')
    PYTEST = ICSStripValue('pytest', equality=r'pytest([_ -]?script)?$')
    ROBOTFRAMEWORK = ICSStripValue(
        'robotframework', equality=r'(robotframework|rf)([_ -]?script)?$'
    )
