import os
import shutil
from string import Template

from tests.helper import ArgumentTestCase, CommandTestCase

# TESTS = 36
TESTS = 0
DECORATORS = ['Argument', 'Command']
# DECORATORS = ['Argument']
# DECORATORS = ['Command']

TEMPLATE = """import pytest
import re
from tests.helper import _TestCase
from polidoro_argument.polidoro_argument_parser import PolidoroArgumentParser
from polidoro_argument.argument import Argument
from polidoro_argument.command import Command

parser = None


@pytest.fixture(scope="module", autouse=True)
def setup():
    global parser
    parser = PolidoroArgumentParser(prog='test$decorator')
    Argument._arguments = []
    Command._commands = {}
${methods}
${tests}
"""

if not os.getcwd().endswith('/tests'):
    os.chdir('tests')

if os.path.exists('test_files'):
    shutil.rmtree('test_files')
os.mkdir('test_files')
os.chdir('test_files')


def generate_test_cases(decorator):
    count = 0
    test_cases = []
    for var_keyword in [False, True]:
        for n_keyword in range(3):
            for var_positional in [False, True]:
                for n_positional in range(3):
                    if decorator == 'Argument':
                        test_cases.append(ArgumentTestCase(n_positional, var_positional, n_keyword, var_keyword))
                    elif decorator == 'Command':
                        test_cases.append(CommandTestCase(n_positional, var_positional, n_keyword, var_keyword))

                    count += 1
                    if TESTS == count:
                        return test_cases

    return test_cases


def generate_test_files():
    for decorator in DECORATORS:
        with open(decorator.lower() + '_test.py', 'w') as arq:
            methods = []
            tests = []
            for test_case in generate_test_cases(decorator):
                print("Generating test for: %s..." % test_case.method_name)
                methods.append(test_case.method_template)
                tests.append(test_case.usage_test)
                tests.append(test_case.help_test)
                tests.append(test_case.call_test)
                tests.append(test_case.one_less_arg_test)
                tests.append(test_case.one_more_arg_test)
                tests.append(test_case.one_more_kwarg_test)
                tests.append(test_case.one_less_kwarg_test)

            tests = [t for t in tests if t]

            arq.write(Template(TEMPLATE).substitute(
                decorator=decorator,
                decorator_import='from polidoro_argument.%s import %s' % (decorator.lower(), decorator),
                methods=''.join(methods),
                tests='\n'.join(tests)
            ))


generate_test_files()
