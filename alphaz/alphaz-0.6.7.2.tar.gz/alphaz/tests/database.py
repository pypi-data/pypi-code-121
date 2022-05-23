import datetime
from alphaz.models.tests import AlphaTest, test
from core import core

from alphaz.libs import date_lib
import alphaz.models.database.main_definitions as defs
from alphaz.models.database.main_definitions import Test
from alphaz.models.database.operators import Operators

log = core.get_logger("tests")


class Database(AlphaTest):
    connected = False

    columns = [Test.name_.key, Test.text_.key, Test.number_.key]

    date_datetime = date_lib.str_to_datetime("2020/01/07 10:02:03")
    parameters = {
        Test.name_.key: "insert",
        Test.text_.key: "insert_text",
        Test.number_.key: 12,
        Test.date_.key: date_datetime,
    }

    select_parameters = {
        Test.name_.key: "select",
        Test.text_.key: "select",
        Test.number_.key: 12,
    }

    def __init__(self):
        super().__init__()

        self.db = core.db
        self.connected = self.db.test()

        if not self.connected:
            log.error("not connected")
            return
        self.db.truncate(Test)

    def count(self):
        rows = self.db.select(Test)
        return len(rows)

    @test(save=False)
    def connexion(self):
        return self.connected

    @test(save=False)
    def insert(self):
        self.db.truncate(Test)
        self.db.add(Test, self.parameters)
        rows = self.db.select(Test)
        if len(rows) == 0:
            return False
        values = {x: getattr(rows[0], x) for x in self.parameters}
        return len(rows) == 1 and values == self.parameters

    @test(save=False)
    def insert2(self):
        self.db.truncate(Test)
        self.db.add(
            Test,
            {
                Test.name_: self.parameters[Test.name_.key],
                Test.number_: self.parameters[Test.number_.key],
                Test.text_: self.parameters[Test.text_.key],
                Test.date_: self.parameters[Test.date_.key],
            },
        )
        rows = self.db.select(Test)
        if len(rows) == 0:
            return False
        values = {x: getattr(rows[0], x) for x in self.parameters}
        return len(rows) == 1 and values == self.parameters

    @test(save=False)
    def insert3(self):
        self.db.truncate(Test)
        self.db.add(Test(**self.parameters))
        rows = self.db.select(Test)
        if len(rows) == 0:
            return False
        values = {x: getattr(rows[0], x) for x in self.parameters}
        return len(rows) == 1 and values == self.parameters

    @test(save=False)
    def select_dict(self):
        self.db.truncate(Test)
        self.db.add(Test, self.parameters)
        rows = self.db.select(Test, columns=self.columns, json=True)
        log.info(f"Selected {len(rows)} elements, expecting 1")
        if len(rows) == 0:
            return False
        values = {x: rows[0][x] for x in self.columns}
        parameters_values = {x: self.parameters[x] for x in self.columns}
        json_values = rows[0].to_json() if hasattr(rows[0], "to_json") else rows[0]
        return (
            len(rows) == 1
            and values == parameters_values
            and len(json_values) == len(self.columns)
        )

    @test(save=False)
    def delete(self):
        self.db.truncate(Test)
        self.db.add(Test, self.parameters)
        self.db.delete(Test, filters=[Test.name_ == self.parameters[Test.name_.key]])
        rows = self.db.select(Test)
        return len(rows) == 0

    @test(save=False)
    def delete2(self):
        self.db.truncate(Test)
        test = Test(**self.parameters)
        self.db.add(test)
        self.db.delete(test)
        rows = self.db.select(Test)
        return len(rows) == 0

    @test(save=False)
    def select_unique(self):
        self.db.truncate(Test)
        self.db.add(Test, self.parameters)
        rows = self.db.select(Test, unique=Test.name_.key)
        valid = len(rows) == 1
        if not valid:
            return False
        return rows[0] == self.parameters[Test.name_.key]

    @test(save=False)
    def select_unique2(self):
        self.db.truncate(Test)
        self.db.add(Test, self.parameters)
        rows = self.db.select(Test, unique=Test.name_)
        valid = len(rows) == 1
        if not valid:
            return False
        return rows[0] == self.parameters[Test.name_.key]

    @test(save=False)
    def add_update(self):
        self.db.truncate(Test)
        self.db.add(Test, self.parameters)
        parameters = {x: y for x, y in self.parameters.items()}
        parameters[Test.number_.key] += 1
        self.db.add(Test, parameters=parameters, update=True)
        rows = self.db.select(Test)
        return len(rows) == 1 and parameters == {
            x: getattr(rows[0], x) for x in self.parameters
        }

    @test(save=False)
    def add_or_update(self):
        self.db.truncate(Test)
        self.db.add(Test, self.parameters)
        parameters = {x: y for x, y in self.parameters.items()}
        parameters[Test.number_.key] += 1
        test2 = Test(**parameters)
        self.db.add_or_update(test2)
        rows = self.db.select(Test)
        return len(rows) == 1 and parameters == {
            x: getattr(rows[0], x) for x in self.parameters
        }

    @test(save=False)
    def add_or_update_multiple(self):
        self.db.truncate(Test)
        tests = [Test(**self.parameters)]
        for i in range(5):
            parameters = {x: y for x, y in self.parameters.items()}
            parameters[Test.number_.key] += i
            tests.append(Test(**parameters))
        tests.append(Test(**self.parameters))
        self.db.add_or_update(tests)
        rows = self.db.select(Test)
        return len(rows) == 1 and self.parameters == {
            x: getattr(rows[0], x) for x in self.parameters
        }

    @test(save=False)
    def add_or_update_multiple2(self):
        # take the first insert
        self.db.truncate(Test)
        tests = [Test(**self.parameters)]
        for i in range(5):
            parameters = {x: y for x, y in self.parameters.items()}
            parameters[Test.number_.key] += i
            tests.append(Test(**parameters))
        self.db.add_or_update(tests)
        rows = self.db.select(Test)
        return len(rows) == 1 and self.parameters == {
            x: getattr(rows[0], x) for x in self.parameters
        }

    @test(save=False)
    def add_or_update_multiple3(self):
        self.db.truncate(Test)
        tests = [Test(**self.parameters)]
        for i in range(5):
            parameters = {x: y for x, y in self.parameters.items()}
            parameters[Test.number_.key] += i
            tests.append(Test(**parameters))
        parameters2 = {x: y for x, y in self.parameters.items()}
        parameters2[Test.name_.key] = "new"
        tests.append(Test(**parameters2))
        self.db.add_or_update(tests)
        rows = self.db.select(Test)
        return len(rows) == 2 and self.parameters == {
            x: getattr(rows[0], x) for x in self.parameters
        }

    @test()
    def bulk_update(self):
        self.db.truncate(Test)

        rows = self.db.select(Test)
        self.assert_is_empty(rows)

        tests = [Test(**self.parameters)]
        for i in range(5):
            parameters = {x: y for x, y in self.parameters.items()}
            parameters[Test.number_.key] += i
            tests.append(Test(**parameters))
        self.db.add_or_update(tests)
        numbers = self.db.select(Test, unique=Test.number_)
        self.assert_length(numbers, 5)
        self.assert_equal(set(numbers), set([12, 13, 14, 15, 16]))

        rows = self.db.select(Test)
        update_data = []
        for i, row in enumerate(rows):
            p = row.to_json()
            p[Test.number_.key] = 0
            p[Test.update_date.key] = datetime.datetime.now()
            p[Test.date_.key] = datetime.datetime.strptime(
                p[Test.date_.key], "%Y-%m-%dT%H:%M:%S"
            )
            update_data.append(p)

        self.db.session.bulk_update_mappings(Test, update_data)
        self.db.session.commit()

        numbers = self.db.select(Test, unique=Test.number_)
        self.assert_length(numbers, 1)
        self.assert_equal(set(numbers), set([0]))
        
    @test()
    def bulk_update_2(self):
        self.db.truncate(Test)

        rows = self.db.select(Test)
        self.assert_is_empty(rows)

        tests = [Test(**self.parameters)]
        for i in range(5):
            parameters = {x: y for x, y in self.parameters.items()}
            parameters[Test.number_.key] += i
            tests.append(Test(**parameters))
        self.db.add_or_update(tests)
        numbers = self.db.select(Test, unique=Test.number_)
        self.assert_length(numbers, 5)
        self.assert_equal(set(numbers), set([12, 13, 14, 15, 16]))

        rows = self.db.select(Test)
        for i, row in enumerate(rows):
            row.number_ = 0

        self.db.session.commit()

        numbers = self.db.select(Test, unique=Test.number_)
        self.assert_length(numbers, 1)
        self.assert_equal(set(numbers), set([0]))

    """@test(save=False)
    def upsert(self):
        self.db.truncate(Test)
        test = Test(**self.parameters)
        self.db.add(test)
        parameters = {x:y for x,y in self.parameters.items()}
        parameters[Test.number_.key] += 1
        test2 = Test(**self.parameters)
        self.db.upsert(Test,test2)
        rows    = self.db.select(Test)
        return len(rows) == 1 and parameters == {x:getattr(rows[0],x) for x in self.parameters}"""

    @test()
    def filters(self):
        self.db.truncate(Test)
        tests = [Test(**self.parameters)]
        for i in range(5):
            parameters = {x: y for x, y in self.parameters.items()}
            parameters[Test.number_.key] = i
            parameters[Test.date_.key] = date_lib.str_to_datetime("2020/01/%s 10:02:03"%(i+1))
            tests.append(Test(**parameters))
        self.db.add_or_update(tests)
        
        tests = self.db.select(Test,
            filters=[
                {
                    Test.number_: {
                        Operators.IN: 1
                    }
                },
            ]
        )
        self.assert_length(tests, 1)
        
        tests = self.db.select(Test,
            filters=[
                {
                    Test.number_: {
                        Operators.IN: [1,100]
                    }
                },
            ]
        )
        self.assert_length(tests, 1)
        
        tests = self.db.select(Test,
            filters=[
                {
                    Test.date_: {
                        Operators.SUPERIOR_OR_EQUAL: date_lib.str_to_datetime("01/01/2020 10:02:03"), 
                        Operators.INFERIOR_OR_EQUAL:  date_lib.str_to_datetime("03/01/2020 10:02:03")
                    },
                },
            ]
        )
        self.assert_length(tests, 1)
        
        tests = self.db.select(Test,
            filters=[
                {
                    Test.date_: {
                        Operators.BETWEEN_OR_EQUAL: (date_lib.str_to_datetime("01/01/2020 10:02:03"), date_lib.str_to_datetime("03/01/2020 10:02:03"))
                    },
                },
            ]
        )
        self.assert_length(tests, 1)