from doctest import testmod
from subprocess import check_output, CalledProcessError, STDOUT
from types import ModuleType
from typing import Any
from unittest import TestCase

from logsmal import logger
from logsmal import loglevel

logger.testfull_pack_info = logger.info
logger.testfull_pack_info.title_logger = 'TEST_FULL_PACK INFO'
logger.testfull_pack_error = logger.error
logger.testfull_pack_error.title_logger = 'TEST_FULL_PACK ERROR'


def os_exe(
        command: list[str],
) -> tuple[bool, Any, int]:
    """
    Выполнить CLI команду и получить ответ
    :param command:
    :return: ПроизошлаЛиОшибка, Ответ, КодОтвета
    """
    try:
        _response: bytes = check_output(command, shell=True, stderr=STDOUT)
        return True, _response.decode('utf-8'), 0
    except CalledProcessError as e:
        return False, e.output.decode('utf-8'), e.returncode


class TestDoc(TestCase):
    """
    Протестировать документацию у модулей

    .. code-block::python

        import logic_helpful
        from configer.test.helpful_test import TestDoc

        # Док тесты
        TestDoc.list_mod = (
            logic_helpful,
        )
    """
    #: Список модулей
    list_mod: tuple[ModuleType] = (
        # Модули у которых нужно проводить док тесты
    )

    def setUp(self):
        # Отключаем логирование ``logsmal``
        loglevel.__call__ = lambda *args, **kwargs: None

    def test_docs_from_module(self):
        for _m in TestDoc.list_mod:
            # Выполняем док тесты
            self.assertEqual(testmod(_m).failed, 0)


class colors:
    green = '\x1b[32m'
    reset = '\x1b[0m'
    red = '\x1b[31m'
    black = '\x1b[30m'
    yellow = '\x1b[33m'
    blue = '\x1b[34m'
    magenta = '\x1b[35m'
    cyan = '\x1b[36m'
    white = '\x1b[37m'
    bg_red = '\x1b[41m'
    bg_green = '\x1b[42m'


def diff_string(str1: str, str2: str) -> tuple[str, str]:
    """

    :param str1:
    :param str2:

    :Пример:

    .. code-block:: python

        st1 = "/media/user/dd19b13d-bd85-46bb-8db9-5b8f6cf7a825/MyProject/PycharmProject/testfull_pack/venvs/bin/python/scratch_34.py"
        st2 = "/media/user/dd19b13d-bd85-46bb-8et9-5b8f6cf7a825/MyProject/PycharmProjects/testfull_pack/venvs/bin/python/scratch_34.py"
        # Пример 1
        rst1, rst2 = diff_string(st1, st2)
        print(f'str1:::\n{rst1}')
        print(f'str2:::\n{rst2}')

    """
    _max = max([len(str1), len(str2)])

    _len_str1 = len(str1)
    _len_str2 = len(str2)
    _res1 = ''
    _res2 = ''

    for _symbol in range(_max):

        if _symbol < _len_str1 and _symbol < _len_str2:
            if str1[_symbol] == str2[_symbol]:
                _res1 += '{1}{0}{2}'.format(str1[_symbol], colors.green, colors.reset)
                _res2 += '{1}{0}{2}'.format(str2[_symbol], colors.green, colors.reset)
            else:
                _res1 += '{1}{0}{2}'.format(str1[_symbol], colors.red, colors.reset)
                _res2 += '{1}{0}{2}'.format(str2[_symbol], colors.red, colors.reset)
                continue

        elif _symbol < _len_str1:
            _res1 += '{1}{0}{2}'.format(str1[_symbol], colors.bg_green, colors.reset)
            _res2 += '{1}{0}{2}'.format(' ', colors.bg_red, colors.reset)
        elif _symbol < _len_str2:
            _res1 += '{1}{0}{2}'.format(' ', colors.bg_red, colors.reset)
            _res2 += '{1}{0}{2}'.format(str2[_symbol], colors.bg_green, colors.reset)

        else:
            raise ValueError

    return _res1, _res2
