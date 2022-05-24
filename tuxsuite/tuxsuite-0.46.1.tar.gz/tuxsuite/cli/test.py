# -*- coding: utf-8 -*-

import tuxsuite.cli.colors as colors
import tuxsuite.cli.icons as icons
from tuxsuite.cli.models import Test
from tuxsuite.cli.requests import apiurl, get, post
from tuxsuite.cli.utils import LIMIT, datediff, fetch_next
from tuxsuite.cli.yaml import yaml_load

import json
import sys
import time


COLORS = {
    "exception": "\033[1;31m",
    "error": "\033[1;31m",
    "warning": "\033[1;33m",
    "info": "\033[1;37m",
    "debug": "\033[0;37m",
    "target": "\033[32m",
    "input": "\033[0;35m",
    "feedback": "\033[0;33m",
    "results": "\033[1;34m",
    "dt": "\033[0;90m",
    "end": "\033[0m",
}


def handle_get(options, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/tests/{options.uid}",
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    test = Test.new(**ret.json())
    if options.json:
        print(test.as_json())
    else:
        print(f"url     : {apiurl(config, test.url())}")
        print(f"project : {test.project}")
        print(f"uid     : {test.uid}")
        print(f"plan    : {test.plan}")
        print(f"build   : {test.waiting_for}")
        print(f"user    : {test.user}")

        print(f"device  : {test.device}")
        print(f"kernel  : {test.kernel}")
        print(f"modules : {test.modules}")
        print(f"bootargs: {test.boot_args}")

        if test.provisioning_time:
            print(f"{icons.PROVISIONING} time : {test.provisioning_time}")
        if test.running_time:
            print(f"{icons.RUNNING} time : {test.running_time}")

        if test.state == "finished":
            if test.result == "pass":
                icon = icons.PASS
            elif test.result == "error":
                icon = icons.ERROR
            elif test.result == "fail":
                icon = icons.FAIL
            print(f"{icon} time : {test.finished_time}")
        if test.duration:
            print(f"duration: {test.duration}")

        print(f"state   : {test.state}")
        color = ""
        if test.result == "pass":
            color = colors.green
        elif test.result in ["error", "fail"]:
            color = colors.red
        print(f"result  : {color}{test.result}{colors.reset}")
    return 0


def handle_list(options, config):
    url = f"/v1/groups/{config.group}/projects/{config.project}/tests"
    ret = get(config, url)
    if ret.status_code != 200:
        raise NotImplementedError()

    tests = [Test.new(**t) for t in ret.json()["results"][: options.limit]]
    n_token = ret.json()["next"]
    if options.json:
        print(json.dumps([t.as_dict() for t in tests]))
    else:
        while True:
            previous_pt = None
            for test in tests:
                state = test.result if test.state == "finished" else test.state
                state_msg = (
                    f"{colors.state(test.state, test.result)}{state}{colors.reset}"
                )
                all_tests = ",".join(test.tests)
                pt = test.provisioning_time
                if pt is None:
                    pt = "....-..-..T..:..:........."
                pt = pt[:-7]
                print(
                    f"{datediff(previous_pt, pt)} {test.uid} [{state_msg}] {all_tests}@{test.device} {test.kernel}"
                )

                previous_pt = pt
            if sys.stdout.isatty():
                # fetch next list of tests
                tests, n_token = fetch_next(Test, config, url, n_token, options.limit)
    return 0


def handle_logs(options, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/tests/{options.uid}/logs/lava",
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    if options.raw:
        print(ret.text)
        return 0

    data = yaml_load(ret.text)
    for line in data:
        level = line["lvl"]
        msg = line["msg"]
        timestamp = line["dt"].split(".")[0]

        print(
            f"{COLORS['dt']}{timestamp}{COLORS['end']} {COLORS[level]}{msg}{COLORS['end']}"
        )
    return 0


def handle_results(options, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/tests/{options.uid}/results",
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    if options.raw:
        print(ret.text)
        return 0

    data = json.loads(ret.text)
    for k1, v2 in data.items():
        for k2, v2 in v2.items():
            if v2["result"] == "pass":
                print(f"{k1}.{k2}: {colors.green}{v2['result']}{colors.reset}")
            elif v2["result"] == "fail":
                print(f"{k1}.{k2}: {colors.red}{v2['result']}{colors.reset}")
            else:
                print(f"{k1}.{k2}: {v2['result']}")
    return 0


def handle_submit(options, config):
    data = {"device": options.device}
    if options.kernel is not None:
        data["kernel"] = options.kernel
    if options.modules is not None:
        data["modules"] = options.modules
    if options.tests:
        data["tests"] = options.tests
    if options.plan:
        data["plan"] = options.plan
    if options.build:
        data["wait_for"] = options.build

    ret = post(
        config, f"/v1/groups/{config.group}/projects/{config.project}/tests", data=data
    )
    if ret.status_code != 201:
        raise NotImplementedError
    data = ret.json()
    test = Test.new(**data)
    if options.wait:
        options.uid = test.uid
        return handle_wait(options, config)

    if options.json:
        print(test.as_json())
    else:
        print(test)
    return 0


def handle_wait(options, config):
    previous_state = None
    while True:
        ret = get(
            config,
            f"/v1/groups/{config.group}/projects/{config.project}/tests/{options.uid}",
        )
        if ret.status_code != 200:
            raise NotImplementedError()

        test = Test.new(**ret.json())
        if previous_state is None:
            previous_state = test.state
            print(f"url     : {apiurl(config, test.url())}")
            print(f"project : {test.project}")
            print(f"uid     : {test.uid}")
            print(f"plan    : {test.plan}")
            print(f"build   : {test.waiting_for}")
            print(f"user    : {test.user}")

            print(f"device  : {test.device}")
            print(f"kernel  : {test.kernel}")
            print(f"modules : {test.modules}")
            print(f"bootargs: {test.boot_args}")
            if test.provisioning_time:
                print(f"{icons.PROVISIONING} time : {test.provisioning_time}")
            if test.running_time:
                print(f"{icons.RUNNING} time : {test.running_time}")

        if test.state != previous_state:
            if test.state == "provisioning":
                print(f"{icons.PROVISIONING} time : {test.provisioning_time}")
            elif test.state == "running":
                print(f"{icons.RUNNING} time : {test.running_time}")
            previous_state = test.state
        if test.state == "finished":
            break
        time.sleep(5)

    if test.result == "pass":
        icon = icons.PASS
    elif test.result == "error":
        icon = icons.ERROR
    elif test.result == "fail":
        icon = icons.FAIL
    print(f"{icon} time : {test.finished_time}")

    if test.duration:
        print(f"duration: {test.duration}")

    print(f"state   : {test.state}")
    if test.result == "pass":
        color = colors.green
    elif test.result in ["error", "fail"]:
        color = colors.red
    print(f"result  : {color}{test.result}{colors.reset}")
    return 0


handlers = {
    "get": handle_get,
    "list": handle_list,
    "logs": handle_logs,
    "results": handle_results,
    "submit": handle_submit,
    "wait": handle_wait,
}


def setup_parser(parser):
    # "test get <uid>"
    t = parser.add_parser("get")
    t.add_argument("uid")
    t.add_argument("--json", action="store_true")

    # "test list"
    t = parser.add_parser("list")
    t.add_argument("--json", action="store_true")
    t.add_argument("--limit", type=int, default=LIMIT)

    # "test logs <uid>"
    t = parser.add_parser("logs")
    t.add_argument("uid")
    t.add_argument("--raw", action="store_true")

    # "test results <uid>"
    t = parser.add_parser("results")
    t.add_argument("uid")
    t.add_argument("--raw", action="store_true")

    # "test submit"
    t = parser.add_parser("submit")
    t.add_argument("--device", required=True)
    t.add_argument("--kernel", default=None)
    t.add_argument("--modules", default=None)
    t.add_argument("--tests", default=[], nargs="+")
    t.add_argument("--plan", default=None)
    t.add_argument("--build", default=None)
    t.add_argument("--json", action="store_true")
    t.add_argument("--wait", action="store_true")

    # "test wait <uid>
    t = parser.add_parser("wait")
    t.add_argument("uid")
