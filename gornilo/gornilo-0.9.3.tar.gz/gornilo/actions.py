import asyncio
import inspect
import sys
import json
import socket

from contextlib import redirect_stdout, suppress
from traceback import format_exc
from typing import Dict, Callable
from copy import copy

from gornilo.models.api_constants import *
from gornilo.models.action_names import INFO, CHECK, PUT, GET, TEST
from gornilo.models.checksystem_request import CheckRequest, PutRequest, GetRequest
from gornilo.models.verdict import Verdict
from gornilo.setup_logging import setup_logging


with suppress(ImportError):
    import requests


class Checker:
    def __init__(self):
        self.__info_distribution = {}
        self.__multiple_actions = frozenset((PUT, GET))
        self.__actions_handlers: Dict[str, Dict[int, Callable[[CheckRequest], Verdict]]] = {
            CHECK: None,
            PUT: {},
            GET: {},
        }

    @staticmethod
    def __check_function(func: callable, func_type: type):
        func_name = func.__code__.co_name
        func_args_spec = inspect.getfullargspec(func)

        if func_args_spec.annotations.get("return") != Verdict:
            raise TypeError(f"Checker function ({func_name}) should return {Verdict} object!")

        if len(func_args_spec.args) < 1:
            raise TypeError(f"{func_name} should have 1 or more args!")

        func_arg_name = func_args_spec.args[0]
        func_arg_type = func_args_spec.annotations.get(func_arg_name)

        if not issubclass(func_arg_type, func_type):
            raise TypeError(f"{func_name} first arg should be typed as {func_type}")

    def __register_action(self, action_name: str, action: callable, action_period: int = None):
        if action_name in self.__multiple_actions:
            if action_period is None:
                raise ValueError("Period should not be None for multiple actions!")
            self.__actions_handlers[action_name][action_period] = action
        else:
            if action_name in self.__actions_handlers:
                if self.__actions_handlers[action_name] is not None:
                    raise ValueError("Action has been already registered!")
                self.__actions_handlers[action_name] = action
            else:
                raise ValueError("Incorrect action name!")

    def __run_tests(self, team_ip) -> int:
        from gornilo.utils import measure, generate_flag
        from uuid import uuid4
        import subprocess

        return_codes = []

        with measure(CHECK):
            check_result = subprocess.run([sys.executable, sys.argv[0], CHECK, team_ip], text=True, capture_output=True)
        print(f"Check completed with {check_result.returncode} exitcode, "
              f"stdout: {check_result.stdout}, "
              f"stderr: {check_result.stderr}")

        return_codes.append(check_result.returncode)

        info_response = subprocess.run([sys.executable, sys.argv[0], INFO], text=True, capture_output=True).stdout
        vulns_amount = len(info_response.split("\n")[0].split(":")) - 1

        for i in range(vulns_amount):

            flag = generate_flag()
            flag_id = str(uuid4())

            with measure(f"{PUT} vuln {i + 1}"):
                put_result = subprocess.run([sys.executable, sys.argv[0], PUT, team_ip, flag_id, flag, str(i + 1)],
                                            text=True, capture_output=True)
            print(f"{PUT} exited with {put_result.returncode}, "
                  f"stdout: {put_result.stdout}, "
                  f"stderr: {put_result.stderr}")

            return_codes.append(put_result.returncode)

            if put_result.stdout:
                flag_id = put_result.stdout
            with measure(f"{GET} vuln {i + 1}"):
                get_result = subprocess.run([sys.executable, sys.argv[0], GET, team_ip, flag_id, flag, str(i + 1)],
                                            text=True, capture_output=True)
            print(f"{GET} exited with {get_result.returncode}, "
                  f"stdout: {get_result.stdout}, "
                  f"stderr: {get_result.stderr}")

            return_codes.append(get_result.returncode)

        print(f"All return codes: {return_codes}, using max as a return value. 101 transforms to 0")
        return max(return_codes)

    def define_check(self, func: callable) -> callable:
        self.__check_function(func, CheckRequest)
        self.__register_action(CHECK, func)
        return func

    def define_put(self, vuln_num: int, vuln_rate: int) -> callable:
        if not isinstance(vuln_num, int) or vuln_num < 1:
            raise TypeError(f'You should provide vulnerability natural number as a decorator argument!')

        def wrapper(func: callable):
            self.__check_function(func, PutRequest)
            self.__register_action(PUT, func, vuln_num)
            self.__info_distribution[vuln_num] = vuln_rate
            return func
        return wrapper

    def __extract_info_call(self):
        return VULNS + VULNS_SEP.join(str(self.__info_distribution[key]) for key in sorted(self.__info_distribution))

    def define_get(self, vuln_num: int) -> callable:
        if not isinstance(vuln_num, int) or vuln_num < 1:
            raise TypeError(f'You should provide vulnerability natural number as a decorator argument!')

        def wrapper(func: callable):
            self.__check_function(func, GetRequest)
            self.__register_action(GET, func, vuln_num)
            return func
        return wrapper

    def __async_wrapper(self, func_result):
        if asyncio.iscoroutine(func_result):
            return asyncio.run(func_result)
        return func_result

    def __try_extract_public_flag_id(self, request_content: dict) -> dict or None:
        try:
            request_content = copy(request_content)

            flag_id = request_content["flag_id"]
            json_flag_id = json.loads(flag_id)

            public_flag_id = json_flag_id.pop(PUBLIC_FLAG_ID)
            private_flag_id = json_flag_id.pop(PRIVATE_CONTENT)

            request_content[PUBLIC_FLAG_ID] = public_flag_id

            if not isinstance(private_flag_id, str):
                private_flag_id = json.dumps(private_flag_id)

            request_content["flag_id"] = private_flag_id

            return request_content
        except Exception:
            # any exception here means something gone wrong with json;
            # should fallback to legacy models
            return None

    # noinspection PyProtectedMember
    def run(self, *args):
        setup_logging()
        result = Verdict.CHECKER_ERROR("Something gone wrong")
        try:
            if not args:
                args = sys.argv[1:]
            with redirect_stdout(sys.stderr):
                result = self.__run(*args)

            if type(result) != Verdict:
                print(f"Checker function returned not Verdict value, we need to fix it!", file=sys.stderr)
                result = Verdict.CHECKER_ERROR("")
        except Exception as e:
            print(f"Checker caught an error: {e},\n {format_exc()}", file=sys.stderr)
            result = Verdict.CHECKER_ERROR("")

            if isinstance(e, socket.timeout):
                result = Verdict.DOWN("Socket timeout")

            if "requests" in globals() and any(isinstance(e, exc) for exc in (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.TooManyRedirects)):
                result = Verdict.DOWN("Could not process routine due to timeout or connection error!")
        finally:
            if result._public_message:
                print(result._public_message, file=sys.stdout)
            sys.exit(result._code)

    def __run(self, command=None, hostname=None, flag_id=None, flag=None, vuln_id=None) -> Verdict:
        commands = [CHECK, PUT, GET, INFO, TEST]

        if command is None:
            raise ValueError("Expected 1 or more args!")

        command = command.upper()

        if command not in commands:
            raise ValueError(f"Unknown ({command}) command! (Expected one of ({','.join(commands)})")

        if command == INFO:
            return Verdict.OK(self.__extract_info_call())

        if hostname is None:
            raise ValueError("Can't find 'hostname' arg! (Expected 2 or more args)")

        check_func = self.__actions_handlers[CHECK]
        request_content = {
            "hostname": hostname
        }

        if command == CHECK:
            # noinspection PyCallingNonCallable
            return self.__async_wrapper(check_func(CheckRequest(**request_content)))

        if command == TEST:
            return_code = self.__run_tests(hostname)
            return Verdict(0 if return_code == 101 else return_code, "Tests has been finished")

        if flag_id is None:
            raise ValueError("Can't find 'flag_id' arg! (Expected 3 or more args)")

        if flag is None:
            raise ValueError("Can't find 'flag' arg (Expected 4 or more args)")

        if vuln_id is None:
            raise ValueError("Can't find 'vuln_id' arg (Expected 5 or more args)")
        try:
            vuln_id = int(vuln_id)
            assert vuln_id > 0
            assert vuln_id in self.__actions_handlers[PUT]
            assert vuln_id in self.__actions_handlers[GET]
        except (TypeError, AssertionError):
            raise ValueError("'vuln_id' should be representative as a natural number, "
                             f"{GET}/{PUT} methods should be registered in checker!")

        put_func = self.__actions_handlers[PUT][vuln_id]
        get_func = self.__actions_handlers[GET][vuln_id]

        request_content.update({
            "flag_id": flag_id,
            "flag": flag,
            "vuln_id": vuln_id
        })

        if command == PUT:
            return self.__async_wrapper(put_func(PutRequest(**request_content)))

        if command == GET:
            result = self.__try_extract_public_flag_id(request_content)
            return self.__async_wrapper(get_func(GetRequest(**(result or request_content))))

        raise RuntimeError("Something went wrong with checker scenario :(")
