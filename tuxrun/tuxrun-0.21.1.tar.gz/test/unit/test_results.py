from tuxrun.results import Results
from tuxrun.tests import Test


def test_returns_0_by_default():
    results = Results([])
    results.__data__ = {"lava": {}}
    assert results.ret() == 0


def gen_test(name, result, suite_name="mytestsuite"):
    return f'{{ "lvl": "results", "msg": {{"definition": "{suite_name}", "case": "{name}", "result": "{result}"}}}}'


def test_returns_0_with_no_failures():
    t1 = Test(timeout=None)
    t1.name = "mytestsuite"
    results = Results([t1])
    results.parse(gen_test("test1", "pass"))
    results.parse(gen_test("test2", "pass"))
    results.parse(gen_test("job", "pass", suite_name="lava"))
    assert results.ret() == 0


def test_returns_1_on_failure():
    results = Results([])
    results.parse(gen_test("test1", "pass", suite_name="lava"))
    results.parse(gen_test("test2", "fail", suite_name="lava"))
    assert results.ret() == 1


def test_returns_2_on_missing_test():
    t1 = Test(timeout=None)
    t1.name = "mytestsuite"
    results = Results([t1])
    results.parse(gen_test("test1", "pass", suite_name="lava"))
    assert results.ret() == 2


def test_returns_invalid_logs():
    results = Results([])
    results.parse("{")
    results.parse('{ "lvl": "results", "msg": {"case": "tux", "result": "pass"}}')


def test_data():
    results = Results([])
    results.parse(gen_test("test1", "pass"))
    assert results.data["mytestsuite"]["test1"]["result"] == "pass"
