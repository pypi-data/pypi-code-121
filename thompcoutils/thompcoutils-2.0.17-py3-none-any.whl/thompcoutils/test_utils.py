from thompcoutils.string_utils import list_to_string


class TestException(Exception):
    pass


def assert_test(value, message=None, error=None, passed=None):
    if message is not None:
        print(message, end="...")
    if value:
        if passed is None:
            print("passed")
        else:
            print(passed)
    else:
        if error is None:
            print("FAILED!!")
        else:
            print(error)
        assert False


def exception_test(message,  exception, method_to_test, **kwargs):
    print(message, end="...")
    try:
        method_to_test(**kwargs)
        print()
        raise TestException("{} test should have failed".format(message))
    except exception as e:
        if isinstance(e, TestException):
            raise e
        pass
    print("passed")


def _test(throws, ex):
    if throws:
        raise ex("Throws")


class FailedTestException(Exception):
    pass


def test(method, params, expected_value=None, expected_exception=None):
    method_name = str(method).split(" ")[1]
    print("starting {}({})...".format(method_name, list_to_string(params)), end="")
    if expected_exception is None:
        if expected_value is None:
            method(*params)
        elif method(*params) == expected_value:
            print("passed")
        else:
            str1 = "FAILED EXPECTED VALUE {}({})".format(method_name, list_to_string(params))
            raise FailedTestException(str1)
    else:
        try:
            if method(*params) == expected_value:
                str1 = "FAILED EXCEPTION {}({})".format(method_name, list_to_string(params))
                raise FailedTestException(str1)
        except expected_exception:
            print("passed")


def main():
    exception_test("testing - should throw 0", Exception, _test, throws=True, ex=Exception)
    try:
        exception_test("testing - should throw because the function didn't throw", TestException,
                       _test, throws=False, ex=TestException)
        raise Exception("this should not pass!")
    except TestException:
        pass
    try:
        exception_test("testing - should throw because exceptions don't match", Exception,
                       _test, throws=False, ex=TestException)
        raise Exception("this should not pass!")
    except TestException:
        pass
    assert_test(True, "just some testing 0")
    assert_test(True, "just some testing 1", "error occurred 1")
    assert_test(True, "just some testing 2", "error occurred 2", "this passed 2")
    # assert_test(False, "error occurred 3")
    # assert_test(False, "just some testing 4", "error occurred 4")
    # assert_test(False, "just some testing 5", "error occurred 5", "this passed 5")


if __name__ == '__main__':
    main()
