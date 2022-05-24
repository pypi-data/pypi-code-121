# -*- coding: utf-8 -*-

import tuxsuite.cli.colors as colors
import tuxsuite.cli.icons as icons
from tuxsuite.cli.models import Build
from tuxsuite.cli.requests import apiurl, get
from tuxsuite.cli.utils import LIMIT, datediff, fetch_next

import json
import requests
import sys
import time


def handle_config(options, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/builds/{options.uid}",
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    # TODO: add a wrapper around requests.get
    ret = requests.get(f"{ret.json()['download_url']}config")
    if ret.status_code != 200:
        raise NotImplementedError()
    print(ret.text)
    return 0


def handle_get(options, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/builds/{options.uid}",
    )
    if ret.status_code != 200:
        raise NotImplementedError()

    build = Build.new(**ret.json())
    if options.json:
        print(build.as_json())
    else:
        print(f"url      : {apiurl(config, build.url())}")
        print(f"project  : {build.project}")
        print(f"uid      : {build.uid}")
        print(f"plan     : {build.plan}")
        if build.waited_by:
            print(f"tests    : {', '.join(build.waited_by)}")
        print(f"user     : {build.user}")

        print(f"kconfig  : {', '.join(build.kconfig)}")
        print(f"target   : {build.target_arch}@{build.toolchain}")
        print(f"git repo : {build.git_repo}")
        print(f"git ref  : {build.git_ref}")
        print(f"git sha  : {build.git_sha}")
        print(f"git desc : {build.git_describe}")

        if build.provisioning_time:
            print(f"{icons.PROVISIONING} time  : {build.provisioning_time}")
        if build.running_time:
            print(f"{icons.RUNNING} time  : {build.running_time}")

        if build.state == "finished":
            if build.result == "pass" and build.warnings_count == 0:
                icon = icons.PASS
            elif build.result == "pass" and build.warnings_count != 0:
                icon = icons.WARNING
            elif build.result == "error":
                icon = icons.ERROR
            elif build.result == "fail":
                icon = icons.FAIL
            print(f"{icon} time  : {build.finished_time}")
        if build.duration:
            print(f"duration : {build.duration}")

        print(f"state    : {build.state}")
        color = ""
        if build.result == "pass":
            color = colors.green
        elif build.result in ["error", "fail"]:
            color = colors.red
        print(f"result   : {color}{build.result}{colors.reset}")

        if build.errors_count:
            print(f"warnings : {colors.red}{build.errors_count}{colors.reset}")
        if build.warnings_count:
            print(f"warnings : {colors.yellow}{build.warnings_count}{colors.reset}")

    return 0


def handle_list(options, config):
    url = f"/v1/groups/{config.group}/projects/{config.project}/builds"
    ret = get(config, url)
    if ret.status_code != 200:
        raise NotImplementedError()

    builds = [Build.new(**b) for b in ret.json()["results"][: options.limit]]
    n_token = ret.json()["next"]
    if options.json:
        print(json.dumps([b.as_dict() for b in builds]))
    else:
        while True:
            previous_pt = None
            for build in builds:
                state = build.result if build.state == "finished" else build.state
                state_msg = (
                    f"{colors.state(build.state, build.result)}{state}{colors.reset}"
                )
                warnings = (
                    f" {colors.yellow}warnings={build.warnings_count}{colors.reset}"
                    if build.warnings_count
                    else ""
                )
                errors = (
                    f" {colors.red}errors={build.errors_count}{colors.reset}"
                    if build.errors_count
                    else ""
                )
                pt = build.provisioning_time
                if pt is None:
                    pt = "....-..-..T..:..:........."
                pt = pt[:-7]
                print(
                    f"{datediff(previous_pt, pt)} {build.uid} [{state_msg}] "
                    f"{build.target_arch}@{build.toolchain}{errors}{warnings}"
                )

                previous_pt = pt
            if sys.stdout.isatty():
                # fetch next list of builds
                builds, n_token = fetch_next(Build, config, url, n_token, options.limit)
    return 0


def handle_logs(options, config):
    ret = get(
        config,
        f"/v1/groups/{config.group}/projects/{config.project}/builds/{options.uid}",
    )
    if ret.status_code == 404:
        print(f"warning: {colors.red}Log unavailable{colors.reset}")
        return 0
    elif ret.status_code != 200:
        raise NotImplementedError()

    # TODO: add a wrapper around requests.get
    ret = requests.get(f"{ret.json()['download_url']}build.log")
    if ret.status_code != 200:
        raise NotImplementedError()
    print(ret.text)
    return 0


def handle_wait(options, config):
    previous_state = None
    while True:
        ret = get(
            config,
            f"/v1/groups/{config.group}/projects/{config.project}/builds/{options.uid}",
        )
        if ret.status_code != 200:
            raise NotImplementedError()

        build = Build.new(**ret.json())
        if previous_state is None:
            previous_state = build.state
            print(f"url      : {apiurl(config, build.url())}")
            print(f"project  : {build.project}")
            print(f"uid      : {build.uid}")
            print(f"plan     : {build.plan}")
            if build.waited_by:
                print(f"tests    : {', '.join(build.waited_by)}")
            print(f"user     : {build.user}")

            print(f"kconfig  : {', '.join(build.kconfig)}")
            print(f"target   : {build.target_arch}@{build.toolchain}")
            print(f"git repo : {build.git_repo}")
            print(f"git ref  : {build.git_ref}")
            print(f"git sha  : {build.git_sha}")
            print(f"git desc : {build.git_describe}")

            if build.provisioning_time:
                print(f"{icons.PROVISIONING} time  : {build.provisioning_time}")
            if build.running_time:
                print(f"{icons.RUNNING} time  : {build.running_time}")

        if build.state != previous_state:
            if build.state == "provisioning":
                print(f"{icons.PROVISIONING} time  : {build.provisioning_time}")
            elif build.state == "running":
                print(f"{icons.RUNNING} time  : {build.running_time}")
            previous_state = build.state
        if build.state == "finished":
            break
        time.sleep(5)

    if build.result == "pass" and build.warnings_count == 0:
        icon = icons.PASS
    elif build.result == "pass" and build.warnings_count != 0:
        icon = icons.WARNING
    elif build.result == "error":
        icon = icons.ERROR
    elif build.result == "fail":
        icon = icons.FAIL
    print(f"{icon} time  : {build.finished_time}")
    if build.duration:
        print(f"duration : {build.duration}")

    print(f"state    : {build.state}")
    if build.result == "pass":
        color = colors.green
    elif build.result in ["error", "fail"]:
        color = colors.red
    print(f"result   : {color}{build.result}{colors.reset}")

    if build.errors_count:
        print(f"warnings : {colors.red}{build.errors_count}{colors.reset}")
    if build.warnings_count:
        print(f"warnings : {colors.yellow}{build.warnings_count}{colors.reset}")

    return 0


handlers = {
    "config": handle_config,
    "get": handle_get,
    "list": handle_list,
    "logs": handle_logs,
    "wait": handle_wait,
}


def setup_parser(parser):
    # "build config <uid>"
    t = parser.add_parser("config")
    t.add_argument("uid")

    # "build get <uid>"
    p = parser.add_parser("get")
    p.add_argument("uid")
    p.add_argument("--json", action="store_true")

    # "build list"
    p = parser.add_parser("list")
    p.add_argument("--json", action="store_true")
    p.add_argument("--limit", type=int, default=LIMIT)

    # "build logs <uid>"
    t = parser.add_parser("logs")
    t.add_argument("uid")

    # "build wait <uid>"
    p = parser.add_parser("wait")
    p.add_argument("uid")
