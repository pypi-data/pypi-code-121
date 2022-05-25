# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2012>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import datetime
import time
import os
import re
import threading
import traceback
import shutil

from lettuce.exceptions import StepLoadingError
import six
world = threading.local()
world._set = False


def _function_matches(one, other):

    if hasattr(one, 'func_code'):
        one_func_code = one.func_code
    else:
        one_func_code = six.get_function_code(one)

    if hasattr(other, 'func_code'):
        other_func_code = other.func_code
    else:
        other_func_code = six.get_function_code(other)

    return (os.path.abspath(one_func_code.co_filename) == os.path.abspath(other_func_code.co_filename) and
            one_func_code.co_firstlineno == other_func_code.co_firstlineno)


def build_case_old(scenario):

    with open(f'{world.cache_path}/res.txt', 'a+', encoding='utf8') as f:
        with open(f'{world.cache_path}/error_case.feature', 'a+', encoding='utf8') as c:
            with open(f'{world.cache_path}/temp_case.feature', 'a+', encoding='utf8') as t:
                _case = world.case[:]
                temp_list = list()
                for i in _case:
                    a = i.replace("\033[1;37m", '')
                    a = a.replace("\033[1;32m", '')
                    a = a.replace("\033[1;30m", '')
                    a = a.replace("\033[0m", '')
                    a = a.replace("\033[A", '')
                    a = a.replace("\033[0;36m", '')
                    if not a.startswith("Feature"):
                        if a in temp_list:
                            pass
                        else:
                            temp_list.append(a)
                            if world.fail_flag is True or world.skip_flag is True:

                                # 收集错误案例详情，支持-lf指令执行上次失败的案例
                                if "\033[0;31m" not in a and "\033[1;31m" not in a:
                                    if "#" in a:
                                        c.write(a.split('#')[0].rstrip() + '\n')
                                    elif "|" in a:
                                        c.write(a)

                                # 收集错误信息，保存在结果文件
                                a = a.replace("\033[0;31m", 'error!')
                                a = a.replace("\033[1;31m", 'error!')
                                a = a.replace("\033[1;41;33m", '')
                                f.write(f'{a}\n')
                            else:
                                # 创建临时文件，此处存放执行通过的案例，如果存在执行失败的案例此处临时文件会与错误案例文件合并，
                                # 生成新案例文件,支持-ff指令优先执行上次执行失败的案例
                                if "#" in a:
                                    t.write(a.split('#')[0].rstrip() + '\n')
                                elif "|" in a:
                                    t.write(a)
                if world.fail_flag is True or world.skip_flag is True:
                    world.case_log_name = int(time.time())
                    f.write(f'日志详情见：{world.case_log_name}')
                
    world.fail_flag = False
    world.skip_flag = False
    world.case = []


def case_data():
    temp_list = list()
    _case = world.case[:]
    for i in _case:
        a = i.replace("\033[1;37m", '')
        a = a.replace("\033[1;32m", '')
        a = a.replace("\033[1;30m", '')
        a = a.replace("\033[0m", '')
        a = a.replace("\033[A", '')
        a = a.replace("\033[0;36m", '')
        if not a.startswith("Feature"):
            if a in temp_list:
                ...
            else:
                temp_list.append(a)
                yield a


def build_case(scenario):
    
    if world.fail_flag is True or world.skip_flag is True:
        with open(f'{world.cache_path}/res.txt', 'a+', encoding='utf8') as f:
            with open(f'{world.cache_path}/error_case.feature', 'a+', encoding='utf8') as c:
                for a in case_data():
                    # 收集错误案例详情，支持-lf指令执行上次失败的案例
                    if "\033[0;31m" not in a and "\033[1;31m" not in a:
                        if "#" in a:
                            c.write(a.split('#')[0].rstrip() + '\n')
                        elif "|" in a:
                            c.write(a)
                    # 收集错误信息，保存在结果文件
                    a = a.replace("\033[0;31m", 'error!')
                    a = a.replace("\033[1;31m", 'error!')
                    a = a.replace("\033[1;41;33m", '')
                    f.write(f'{a}\n')                        
    else:
        with open(f'{world.cache_path}/temp_case.feature', 'a+', encoding='utf8') as t:
            for a in case_data():
                if "#" in a:
                    t.write(a.split('#')[0].rstrip() + '\n')
                elif "|" in a:
                    t.write(a)
    if world.fail_flag is True or world.skip_flag is True:
        world.case_log_name = int(time.time())
        with open(f'{world.cache_path}/res.txt', 'a+', encoding='utf8') as f:
            f.write(f'日志详情见：{world.case_log_name}')

    world.fail_flag = False
    world.skip_flag = False
    world.case = []



class CallbackDict(dict):
    def append_to(self, where, when, function):
        if not any(_function_matches(o, function) for o in self[where][when]):
            self[where][when].append(function)
            if where == 'scenario' and when == 'after_each':
                self[where][when].append(build_case)


    def clear(self):
        for name, action_dict in self.items():
            for callback_list in action_dict.values():
                callback_list[:] = []

class StepDict(dict):
    def __init__(self, *args, **kwargs):
        super(StepDict, self).__init__(*args, **kwargs)
        self._compiled = {}
        self._compiled_ignore_case = {}

    def get_regex(self, step, ignore_case=False):
        if ignore_case:
            regex = self._compiled_ignore_case.get(step, None)
            if not regex:
                regex = re.compile(step, re.I)
                self._compiled_ignore_case[step] = regex
        else:
            regex = self._compiled.get(step, None)
            if not regex:
                regex = re.compile(step)
                self._compiled[step] = regex
        return regex

    def load(self, step, func):
        self._assert_is_step(step, func)
        self[step] = func
        return func

    def load_func(self, func):
        regex = self._extract_sentence(func)
        return self.load(regex, func)

    def load_steps(self, obj):
        exclude = getattr(obj, "exclude", [])
        for attr in dir(obj):
            if self._attr_is_step(attr, obj) and attr not in exclude:
                step_method = getattr(obj, attr)
                self.load_func(step_method)
        return obj

    def _extract_sentence(self, func):
        func = getattr(func, '__func__', func)
        sentence = getattr(func, '__doc__', None)
        if sentence is None:
            if six.PY2:
                sentence = func.func_name.replace('_', ' ')
            if six.PY3:
                sentence = func.__name__.replace('_', ' ')
            sentence = sentence[0].upper() + sentence[1:]
        return sentence

    def _assert_is_step(self, step, func):
        try:
            re.compile(step)
        except re.error as e:
            raise StepLoadingError("Error when trying to compile:\n"
                                   "  regex: %r\n"
                                   "  for function: %s\n"
                                   "  error: %s" % (step, func, e))

    def _attr_is_step(self, attr, obj):
        return attr[0] != '_' and self._is_func_or_method(getattr(obj, attr))

    def _is_func_or_method(self, func):
        func_dir = dir(func)
        return callable(func) and ("func_name" in func_dir or "__func__" in func_dir)


STEP_REGISTRY = StepDict()
CALLBACK_REGISTRY = CallbackDict(
    {
        'all': {
            'before': [],
            'after': [],
        },
        'step': {
            'before_each': [],
            'after_each': [],
            'before_output': [],
            'after_output': [],
        },
        'scenario': {
            'before_each': [],
            'after_each': [],
            'outline': [],
        },
        'outline': {
            'before_each': [],
            'after_each': [],
        },
        'background': {
            'before_each': [],
            'after_each': [],
        },
        'feature': {
            'before_each': [],
            'after_each': [],
        },
        'app': {
            'before_each': [],
            'after_each': [],
        },
        'harvest': {
            'before': [],
            'after': [],
        },
        'handle_request': {
            'before': [],
            'after': [],
        },
        'runserver': {
            'before': [],
            'after': [],
        },
    },
)


def call_hook(situation, kind, *args, **kw):
    for callback in CALLBACK_REGISTRY[kind][situation]:
        try:
            callback(*args, **kw)
        except Exception as e:
            # py3: mod
            print("=" * 1000)
            if six.PY2:
                traceback.print_exc(e)
            if six.PY3:
                traceback.print_exc()
            print
            raise


def clear():
    STEP_REGISTRY.clear()
    CALLBACK_REGISTRY.clear()
