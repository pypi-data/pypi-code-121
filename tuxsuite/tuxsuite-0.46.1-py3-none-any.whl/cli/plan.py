# -*- coding: utf-8 -*-

from itertools import chain

import tuxsuite.cli.colors as colors
import tuxsuite.cli.icons as icons
from tuxsuite.cli.models import Plan
from tuxsuite.cli.requests import get
from tuxsuite.cli.utils import LIMIT, datediff, fetch_next

import json
import sys


def format_plan(build, tests):
    if build.result == "pass":
        if build.warnings_count == 0:
            icon = icons.PASS
            message = "Pass"
            color = colors.green
        else:
            icon = icons.WARNING
            color = colors.yellow
            if build.warnings_count == 1:
                message = "Pass (1 warning)"
            else:
                message = "Pass ({} warnings)".format(build.warnings_count)
    elif build.result == "fail":
        icon = icons.FAIL
        color = colors.red
        if build.errors_count == 1:
            message = "Fail (1 error)"
        else:
            message = "Fail ({} errors)".format(build.errors_count)
    elif build.result == "error":
        icon = icons.ERROR
        color = colors.red
        message = build.status_message
    else:
        raise NotImplementedError()

    builds = (
        build.uid
        + " "
        + f"{icon} {color}{message}{colors.reset}"
        + " "
        + build.target_arch
        + "@"
        + build.toolchain
    )

    tests_str = ""
    tests_pass = sorted(
        set(chain.from_iterable([t.tests for t in tests if t.result == "pass"]))
    )
    tests_fail = sorted(
        set(chain.from_iterable([t.tests for t in tests if t.result == "fail"]))
    )
    tests_error = sorted(
        set(chain.from_iterable([t.tests for t in tests if t.result == "error"]))
    )

    if tests_pass:
        tests_str += (
            f" {icons.PASS} {colors.green}Pass: {','.join(tests_pass)}{colors.reset}"
        )
    if tests_fail:
        tests_str += (
            f" {icons.FAIL} {colors.red}Fail: {','.join(tests_fail)}{colors.reset}"
        )
    if tests_error:
        tests_str += (
            f" {icons.ERROR} {colors.red}Error: {','.join(tests_error)}{colors.reset}"
        )

    return builds + tests_str


def format_test(test):
    if test.result == "pass":
        icon = icons.PASS
        color = colors.green
        message = "Pass"
    elif test.result == "fail":
        icon = icons.FAIL
        color = colors.red
        message = "Fail"
    elif test.result == "error":
        icon = icons.ERROR
        color = colors.red
        message = "Error"
    else:
        raise NotImplementedError()

    return (
        test.uid
        + " "
        + f"test {icon} {color}{message}: {','.join(test.tests)}{colors.reset}"
    )


def handle_get(options, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/plans/{options.uid}",
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    data = ret.json()

    start_builds = data["builds"]["next"]
    start_tests = data["tests"]["next"]
    while start_builds or start_tests:
        ret = get(
            config,
            f"/v1/groups/{config.group}/projects/{config.project}/plans/{options.uid}",
            params={"start_builds": start_builds, "start_tests": start_tests},
        )
        if ret.status_code != 200:
            raise NotImplementedError()

        datan = ret.json()
        if start_builds:
            data["builds"]["results"].extend(datan["builds"]["results"])
            start_builds = datan["builds"]["next"]
        if start_tests:
            data["tests"]["results"].extend(datan["tests"]["results"])
            start_tests = datan["tests"]["next"]

    plan = Plan.new(**data)
    if options.json:
        print(plan.as_json())
    else:
        print(
            f"{plan.provisioning_time[:-7]} {plan.uid} {plan.name} ({plan.description})"
        )

        for build in chain(
            plan.passing(), plan.warning(), plan.failing(), plan.errors()
        ):
            print(format_plan(build, plan._tests_wait_for(build.uid)))
        # Print stand alone tests
        for test in [t for t in plan.tests if t.waiting_for is None]:
            print(format_test(test))

        bs = f"builds ({len(plan.builds)}):"
        provisioning = len(plan.filter_builds(lambda _, b: b.state == "provisioning"))
        running = len(plan.filter_builds(lambda _, b: b.state == "running"))
        passing = len(
            plan.filter_builds(
                lambda _, b: b.result == "pass" and b.warnings_count == 0
            )
        )
        warning = len(
            plan.filter_builds(
                lambda _, b: b.result == "pass" and b.warnings_count != 0
            )
        )
        failing = len(plan.filter_builds(lambda _, b: b.result == "fail"))
        error = len(plan.filter_builds(lambda _, b: b.result == "error"))

        if provisioning:
            bs += f" {icons.PROVISIONING} {provisioning}"
        if running:
            bs += f" {icons.RUNNING} {running}"
        if passing:
            bs += f" {icons.PASS} {passing}"
        if warning:
            bs += f" {icons.WARNING} {warning}"
        if failing:
            bs += f" {icons.FAIL} {failing}"
        if error:
            bs += f" {icons.ERROR} {error}"
        print(bs)

        ts = f"tests ({len(plan.tests)}):"
        waiting = len(plan.filter_tests(lambda _, t: t.state == "waiting"))
        provisioning = len(plan.filter_tests(lambda _, t: t.state == "provisioning"))
        running = len(plan.filter_tests(lambda _, t: t.state == "running"))
        passing = len(plan.filter_tests(lambda _, t: t.result == "pass"))
        failing = len(plan.filter_tests(lambda _, t: t.result == "fail"))
        error = len(plan.filter_tests(lambda _, t: t.result == "error"))

        if waiting:
            ts += f" {icons.WAITING} {waiting}"
        if provisioning:
            ts += f" {icons.PROVISIONING} {provisioning}"
        if running:
            ts += f" {icons.RUNNING} {running}"
        if passing:
            ts += f" {icons.PASS} {passing}"
        if failing:
            ts += f" {icons.FAIL} {failing}"
        if error:
            ts += f" {icons.ERROR} {error}"
        print(ts)
    return 0


def handle_list(options, config):
    url = f"/v1/groups/{config.group}/projects/{config.project}/plans"
    ret = get(config, url)
    if ret.status_code != 200:
        raise NotImplementedError()

    plans = [Plan.new(**p) for p in ret.json()["results"][: options.limit]]
    n_token = ret.json()["next"]
    if options.json:
        print(json.dumps([p.as_dict() for p in plans]))
    else:
        while True:
            previous_pt = None
            for plan in plans:
                pt = plan.provisioning_time
                if pt is None:
                    pt = "....-..-..T..:..:........."
                pt = pt[:-7]

                print(
                    f"{datediff(previous_pt, pt)} {plan.uid} {plan.name} ({plan.description})"
                )
                previous_pt = pt
            if sys.stdout.isatty():
                # fetch next list of plans
                plans, n_token = fetch_next(Plan, config, url, n_token, options.limit)
    return 0


handlers = {
    "get": handle_get,
    "list": handle_list,
}


def setup_parser(parser):
    # "plan get <uid>"
    p = parser.add_parser("get")
    p.add_argument("uid")
    p.add_argument("--json", action="store_true")

    # "plan list"
    p = parser.add_parser("list")
    p.add_argument("--json", action="store_true")
    p.add_argument("--limit", type=int, default=LIMIT)
