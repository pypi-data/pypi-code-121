import datetime, re
import typing

from core import core
from ..database.main_definitions import Tests

from ...libs import number_lib

from ._levels import Levels

log = core.get_logger("tests")


class TestMethod:
    def __init__(
        self,
        classTest,
        name: str,
        method,
        category: str,
        group: str,
        func,
        save: bool = False,
        description: str = "",
        stop: bool = False,
        disable: bool = False,
        level: Levels = Levels.MEDIUM,
    ):
        self.name: str = name
        self.method = method
        self.classTest = classTest
        self.category: str = category
        self.group: str = group
        self.func = func

        self.save = save
        self.description = description
        self.stop = stop
        self.disable = disable
        self.level = level

        self.status: bool = None
        self.start_time: datetime.datetime = None
        self.end_time: datetime.datetime = None
        self.elapsed: int = 0
        self.last_run_elapsed = None
        self.coverages: typing.Dict[str, object] = {}

        self.ex: Exception = None

    def test(self, classTest=None, coverage: bool = False):
        if classTest is None:
            classTest = self.classTest()

        self.start_time = datetime.datetime.now()

        log.info(
            f"Testing function <{self.name}> of <{type(self).__name__}> in category <{self.category}>"
        )

        self.status = False
        try:
            result = classTest.test(self.name, coverage=coverage)
            self.coverages[self.name] = (
                classTest.coverages[self.name]
                if self.name in classTest.coverages
                else None
            )
            self.status = result if type(result) == bool else False
        except Exception as ex:
            self.ex = ex
            raise ex
        classTest.end()

        log.info(
            f"Function <{self.name}> of <{type(self).__name__}> in category <{self.category}>: {'X' if not self.status else 'O'}"
        )

        self.end_time = datetime.datetime.now()
        self.elapsed = (self.end_time - self.start_time).total_seconds()

        self.update_database()
        self._proceed()

        return self.status

    def update_database(self):
        test = Tests(
            category=self.category,
            tests_group=self.group,
            name=self.name,
            status=self.status,
            start_time=self.start_time,
            end_time=self.end_time,
            elapsed=self.elapsed,
        )
        core.db.add(test)

    def update_from(self, source):
        for key in self.__dict__.keys():
            if hasattr(source, key):
                source_element = getattr(source, key)
                if key == "elapsed":
                    source_element = number_lib.myround(source_element, 2)
                self.__dict__[key] = source_element

        self._proceed()

    def get_from_database(self):
        test = core.db.select(
            Tests,
            filters=[
                Tests.category == self.category,
                Tests.tests_group == self.group,
                Tests.name == self.name,
            ],
            order_by=Tests.start_time.desc(),
            first=True,
        )
        self.update_from(test)

    def save(self):
        classTest = self.classTest()
        classTest.save(self.name)

    def is_valid(self):
        return self.status != None and self.status

    def print(self):
        return "OK" if self.status else "X"

    def _proceed(self):
        self.last_run_elapsed = (
            None
            if self.start_time is None
            else str(datetime.datetime.now() - self.start_time).split(".")[0]
        )

    def to_json(self):
        return {
            "status": self.status,
            "elapsed": number_lib.myround(self.elapsed, 2),
            "end_time": self.start_time,
            "last_run_elapsed": self.last_run_elapsed,
            "description": self.description,
            "level": self.level,
        }
