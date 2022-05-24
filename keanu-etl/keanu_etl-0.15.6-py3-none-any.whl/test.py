import unittest
from unittest import TestSuite


import click
from . import config, helpers
from .sql_loader import SqlLoader

current_config = None

def _batch_test(func, mode):
    "Annotate a function with mode (initial or incremental)"
    func._keanu_batchMode = mode
    return func

def initial_test(func):
    "Annotate function with initial mode"
    return _batch_test(func, "INITIAL")

def incremental_test(func):
    "Annotate function with incremental mode"
    return _batch_test(func, "INCREMENTAL")

def _fixture(func, source, load_after_step):
    """Annotate function with fixture metadata.

    :param int load_after_step: fixture will be loaded after given step - lets you inject some change in the middle of keanu batch
    :param source: the source db .. ?
    """
    func._keanu_fixture = True
    func._keanu_source = source
    func._keanu_step = load_after_step
    return func

def initial_fixture(source, load_after_step=0):
    "Decorate funcation with mode=initial and fixture metadata"
    def decorator(func):
        return initial_test(_fixture(func, source, load_after_step))
    return decorator

def incremental_fixture(source, load_after_step=0):
    "Decorate funcation with mode=incremental and fixture metadata"
    def decorator(func):
        return incremental_test(_fixture(func, source, load_after_step))
    return decorator

class BatchTestCase(unittest.TestCase):
    "A single test case (one file)"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_order = 0
        self.connection = None

    @property
    def config(self):
        return current_config

    @property
    def _source(self):
        testMethod = getattr(self, self._testMethodName)
        return testMethod._keanu_source

    def setUp(self):
        self.batch = config.build_batch({'display': True}, self.config)
        if self._is_fixture():
            sourcedb = self.batch.find_source_by_name(self._source)
            sourcedb.use()
            self.connection = sourcedb.connection()
        else:
            self.batch.destination.use()
            self.connection = self.batch.destination.connection()

    def incremental_load(self, order=None):
        if order is None:
            order = self.default_order
        batch = config.build_batch({'display': True, "incremental": True, "order": order}, self.config)

        for _ in batch.execute():
            pass

    def _is_incremental(self):
        testMethod = getattr(self, self._testMethodName)
        return getattr(testMethod, "_keanu_batchMode", "INITIAL") == "INCREMENTAL"

    def _is_fixture(self):
        testMethod = getattr(self, self._testMethodName)
        return getattr(testMethod, "_keanu_fixture", False)


class TestRunner:
    """Orchestrate the discovery and running of tests using unittest classes"""

    def __init__(self, configuration):
        super().__init__()
        self.config = configuration

    def run(self, directory, pattern='test*.py'):
        global current_config
        current_config = self.config
        text_runner = unittest.TextTestRunner(verbosity=2)

        (initial_tests, incremental_tests) = self.discover_tests(directory, pattern)
        (initial_fixtures, incremental_fixtures) = self.discover_fixtures(directory, pattern)

        self.run_global_fixtures()
        self.initial_load(initial_fixtures, text_runner.stream)

        initial_result = text_runner.run(initial_tests)

        self.incremental_load(incremental_fixtures, text_runner.stream)

        incremental_result = text_runner.run(incremental_tests)

        return initial_result.wasSuccessful() and incremental_result.wasSuccessful()

    def discover_tests(self, directory, pattern, methodPrefix="test"):
        test_loader = unittest.TestLoader()
        test_loader.testMethodPrefix = methodPrefix
        suite = test_loader.discover(directory, pattern)
        if test_loader.errors:
            raise Exception("💥 Error while discovering {methodPrefix} functions:\n"
                + "\n".join(test_loader.errors))
        return self.split_suite(suite)

    def discover_fixtures(self, directory, pattern):
      return map(lambda suite: self.map_steps(suite), self.discover_tests(directory, pattern, "load"))

    def run_global_fixtures(self):
        mode = {}
        batch = config.build_batch(mode, self.config)

        for step in self.config:
            if "destination" in step and "fixtures" in step["destination"]:
                self.load_fixtures(batch.destination, step["destination"]["fixtures"])
            elif "source" in step and "fixtures" in step["source"]:
                src = batch.find_source(lambda s: s.name == step["source"]["name"])
                self.load_fixtures(src, step["source"]["fixtures"])

        return batch

    def load_fixtures(self, db, fixtures):
        db.use()
        for fixture in fixtures:
            click.echo("🚚 Loading fixture {}...".format(fixture))
            if not fixture.endswith(".sql"):
                fixture = helpers.schema_path(fixture)
            loader = SqlLoader(fixture, {}, None, db)
            loader.replace_sql_object("keanu", db.schema)
            for _ in loader.execute():
                pass

    def split_suite(self, suite):
        """Split the given test suite into a initial suite and incremental suite"""
        initial = TestSuite()
        incremental = TestSuite()
        for test in suite:
            if isinstance(test, TestSuite):
                (sub_initial, sub_incremental) = self.split_suite(test)
                initial.addTest(sub_initial)
                incremental.addTest(sub_incremental)
            elif isinstance(test, BatchTestCase) and test._is_incremental():
                incremental.addTest(test)
            else:
                initial.addTest(test)

        return (initial, incremental)

    def map_steps(self, fixtures, result=None):
        if result is None:
            result = {}
        for fixture in fixtures:
            if isinstance(fixture, TestSuite):
                self.map_steps(fixture, result)
            else:
                method = getattr(fixture, fixture._testMethodName)
                step = method._keanu_step
                if step not in result:
                    result[step] = TestSuite()
                result[step].addTest(fixture)
        return result

    def run_load(self, incremental, fixtures, stream):
        mode = "incremental" if incremental else "initial"
        if 0 in fixtures:
            self.run_test_fixtures(fixtures[0], stream, mode)
        click.echo(f"🚚 Performing {mode} load...")
        batch = config.build_batch({"incremental": incremental}, self.config)
        steps_run = set()
        for event, data in batch.execute():
            scr = data["script"]
            if event.endswith("script.end") and scr.order in fixtures and scr.order not in steps_run:
                self.run_test_fixtures(fixtures[scr.order], stream, "post-step " + str(scr.order))
                steps_run.add(scr.order)

    def initial_load(self, fixtures, stream):
        self.run_load(False, fixtures, stream)

    def incremental_load(self, fixtures, stream):
        self.run_load(True, fixtures, stream)

    def run_test_fixtures(self, fixtures, stream, mode):
        click.echo("🚚 Loading {} fixtures...".format(mode))
        result = unittest.TextTestResult(stream, True, verbosity=1)
        fixtures.run(result)
        if result.errors:
            raise Exception("💥 Error(s) while loading fixtures:\n"
                + "\n".join(map(lambda e: e[1], result.errors)))
        else:
            click.echo("")
