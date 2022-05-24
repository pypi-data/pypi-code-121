# -*- coding: utf-8 -*-

import click
from itertools import chain
from functools import wraps
import json as json_lib
import os
import sys
import tuxsuite
import tuxsuite.download
import tuxsuite.exceptions
import tuxsuite.gitutils
from urllib.parse import urlparse
from tuxsuite.cli.build import handlers as build_handlers
from tuxsuite.cli.test import handlers as test_handlers
from tuxsuite.cli.plan import handlers as plan_handlers
from tuxsuite.cli.utils import LIMIT


from tuxsuite.utils import (
    defaults,
    ResultState,
    result_states,
    tuxcli_load,
)


info = click.echo


def error(msg):
    raise click.ClickException(msg)


def warning(msg):
    click.echo(msg, err=True)


def no_info(_):
    pass


def quiet_output(quiet):
    global info
    info = no_info if quiet else click.echo


def print_state(state, prefix=""):
    msg = click.style(
        f"{prefix}{state.icon} {state.message}: ", fg=state.cli_color, bold=True
    ) + str(state.build)

    if state.status == "fail" or state.state == "error" or state.warnings:
        warning(msg)
    else:
        info(msg)


def wait_for_object(build_object):
    result = True
    for state in build_object.watch():
        print_state(state)
        if state.status in ["error", "fail"] or state.state == "error" and state.final:
            result = False
    return result


def key_value(s):
    if "=" not in s:
        error(f"Key Value pair not valid: {s}")
    parts = s.split("=")
    return (parts[0], "=".join(parts[1:]))


def get_make_targets_vars(targets):
    target_list = []
    make_variables = {}
    if targets:
        key_values = [arg for arg in targets if "=" in arg]
        for kv in key_values:
            if kv.count("=") > 1:
                sys.stderr.write(f"Error: invalid KEY=VALUE: {kv}")
                sys.exit(1)
            make_variables = dict((arg.split("=") for arg in key_values))
        target_list = [arg for arg in targets if "=" not in arg]
    return (target_list, make_variables)


def plan_summary(plan):
    bs = f"builds ({len(plan.builds)}):"
    provisioning = len(
        plan.filter_builds(lambda _, b: b.status["state"] == "provisioning")
    )
    running = len(plan.filter_builds(lambda _, b: b.status["state"] == "running"))
    passing = len(
        plan.filter_builds(
            lambda _, b: b.status["result"] == "pass"
            and b.status["warnings_count"] == 0
        )
    )
    warning = len(
        plan.filter_builds(
            lambda _, b: b.status["result"] == "pass"
            and b.status["warnings_count"] != 0
        )
    )
    failing = len(plan.filter_builds(lambda _, b: b.status["result"] == "fail"))
    error = len(plan.filter_builds(lambda _, b: b.status["result"] == "error"))

    if provisioning:
        bs += f" ⚙️  {provisioning}"
    if running:
        bs += f" 🚀 {running}"
    if passing:
        bs += f" 🎉 {passing}"
    if warning:
        bs += f" 👾 {warning}"
    if failing:
        bs += f" 👹 {failing}"
    if error:
        bs += f" 🔧 {error}"

    ts = f"tests ({len(plan.tests)}):"
    waiting = len(plan.filter_tests(lambda _, t: t.status["state"] == "waiting"))
    provisioning = len(
        plan.filter_tests(lambda _, t: t.status["state"] == "provisioning")
    )
    running = len(plan.filter_tests(lambda _, t: t.status["state"] == "running"))
    passing = len(plan.filter_tests(lambda _, t: t.status["result"] == "pass"))
    failing = len(plan.filter_tests(lambda _, t: t.status["result"] == "fail"))
    error = len(plan.filter_tests(lambda _, t: t.status["result"] == "error"))

    if waiting:
        ts += f" ⏳ {waiting}"
    if provisioning:
        ts += f" ⚙️  {provisioning}"
    if running:
        ts += f" 🚀 {running}"
    if passing:
        ts += f" 🎉 {passing}"
    if failing:
        ts += f" 👹 {failing}"
    if error:
        ts += f" 🔧 {error}"
    return (bs, ts)


def format_plan_result(build, tests):
    fail = False
    if build.status["result"] == "pass":
        if build.status["warnings_count"] == 0:
            icon = "🎉"
            message = "Pass"
            cli_color = "green"
        else:
            icon = "👾"
            cli_color = "yellow"
            if build.status["warnings_count"] == 1:
                message = "Pass (1 warning)"
            else:
                message = "Pass ({} warnings)".format(build.status["warnings_count"])
    elif build.status["result"] == "fail":
        fail = False
        icon = "👹"
        cli_color = "bright_red"
        if build.status["errors_count"] == 1:
            message = "Fail (1 error)"
        else:
            message = "Fail ({} errors)".format(build.status["errors_count"])
    elif build.status["result"] == "error":
        fail = False
        icon = "🔧"
        cli_color = "bright_red"
        message = build.status["status_message"]
    else:
        raise NotImplementedError()

    if hasattr(build, "target_arch") and hasattr(build, "toolchain"):
        builds = (
            build.uid
            + " "
            + click.style(f"{icon} {message}", fg=cli_color, bold=True)
            + " "
            + build.target_arch
            + "@"
            + build.toolchain
        )
    elif hasattr(build, "build_definition"):
        builds = (
            build.uid
            + " "
            + click.style(f"{icon} {message}", fg=cli_color, bold=True)
            + " "
        )
    else:
        builds = (
            build.uid + " " + click.style(f"{icon} {message}", fg=cli_color, bold=True)
        )

    tests_str = ""
    tests_pass = sorted(
        set(
            chain.from_iterable(
                [t.tests for t in tests if t.status["result"] == "pass"]
            )
        )
    )
    tests_fail = sorted(
        set(
            chain.from_iterable(
                [t.tests for t in tests if t.status["result"] == "fail"]
            )
        )
    )
    tests_error = sorted(
        set(
            chain.from_iterable(
                [t.tests for t in tests if t.status["result"] == "error"]
            )
        )
    )

    if tests_pass:
        tests_str += " 🎉 " + click.style(
            f"Pass: {','.join(tests_pass)}", fg="green", bold=True
        )
    if tests_fail:
        tests_str += " 👹 " + click.style(
            f"Fail: {','.join(tests_fail)}", fg="bright_red", bold=True
        )
    if tests_error:
        tests_str += " 🔧 " + click.style(
            f"Error: {','.join(tests_error)}", fg="bright_red", bold=True
        )

    if fail or tests_fail or tests_error:
        warning(builds + tests_str)
    else:
        info(builds + tests_str)


def format_result(result_json, tuxapi_tests_url=None, prefix=""):
    state = result_states.get(result_json["state"], None)
    result = result_json["result"]
    result_msg = ""
    if "build_name" in result_json:
        if (
            result_json.get("target_arch")
            and result_json.get("kconfig")
            and result_json.get("toolchain")
        ):
            result_msg = (
                f"{result_json['target_arch']} "
                f"({','.join(result_json['kconfig'])}) "
                f"with {result_json['toolchain']} @ {result_json['download_url']}"
            )
        elif result_json.get("build_definition"):
            result_msg = f"with {result_json['build_definition']} @ {result_json['download_url']}"

    elif "tests" in result_json:
        result_msg = (
            f"[{','.join(result_json['tests'])}] "
            f"{result_json['device']} @ {tuxapi_tests_url}"
        )
    if state is None:
        errors = 0
        warnings = 0

        if result == "pass":
            warnings = result_json.get("warnings_count", 0)
            if warnings == 0:
                icon = "🎉"
                message = "Pass"
                cli_color = "green"
            else:
                icon = "👾"
                cli_color = "yellow"
                if warnings == 1:
                    message = "Pass (1 warning)"
                else:
                    message = "Pass ({} warnings)".format(warnings)
        elif result == "fail":
            icon = "👹"
            cli_color = "bright_red"
            errors = result_json.get("errors_count", 0)
            if errors == 1:
                message = "Fail (1 error)"
            else:
                message = "Fail ({} errors)".format(errors)
            if "tests" in result_json:
                errors = [
                    name
                    for name in result_json["results"]
                    if result_json["results"][name] == "fail"
                ]
                message = "Fail ({})".format(", ".join(errors))
                errors = len(errors)
        else:
            icon = "🔧"
            cli_color = "bright_red"
            message = result_json["status_message"]
        state = ResultState(
            state=state,
            status=result_json["state"],
            final=True,
            message=message,
            icon=icon,
            cli_color=cli_color,
            warnings=warnings,
            errors=errors,
        )
    msg = (
        prefix
        + click.style(f"{state.icon} {state.message}: ", fg=state.cli_color, bold=True)
        + result_msg
    )
    if result == "fail" or result == "error":
        warning(msg)
    else:
        info(msg)


def file_or_url(path):
    """Validate if path is a file/directory or an URL and check its existence"""
    if urlparse(path).scheme in ["http", "https"]:
        return path
    elif os.path.exists(path):
        return path
    raise click.BadParameter(f"{path} does not exist or invalid")


@click.group(name="tuxsuite")
@click.version_option()  # Implement --version
def cli():
    pass


BUILD_SUBCOMMANDS = ["config", "get", "list", "logs", "wait"]


def common_options(required):
    def option(*args, **kwargs):
        kw = kwargs.copy()
        kw["required"] = False
        if any(cmd in BUILD_SUBCOMMANDS for cmd in args):
            for a in args:
                if a in required:
                    kw["required"] = True
        return click.option(*args, **kw)

    toolchains = [
        "gcc-8",
        "gcc-9",
        "gcc-10",
        "gcc-11",
        "clang-10",
        "clang-11",
        "clang-12",
        "clang-13",
        "clang-14",
        "clang-nightly",
        "clang-android",
        "rust",
        "rustgcc",
        "rustclang",
        "rustllvm",
    ]

    options = [
        option(
            "--no-cache",
            default=False,
            is_flag=True,
            help="Build without using any compilation cache",
        ),
        option(
            "--image-sha",
            default=None,
            help=("Pin the container image sha (64 hexadecimal digits)"),
        ),
        option(
            "--limit", default=LIMIT, help="Limit to LIMIT output. Used with [list]"
        ),
        option(
            "--json",
            default=False,
            is_flag=True,
            help="Show json output. Used with [get | list]",
        ),
        option("--git-repo", help="Git repository"),
        option("--git-ref", help="Git reference"),
        option("--git-sha", help="Git commit"),
        option(
            "--git-head",
            default=False,
            is_flag=True,
            help="Build the current git HEAD. Overrrides --git-repo and --git-ref",
        ),
        option(
            "--target-arch",
            help="Target architecture [arc|arm|arm64|hexagon|i386|mips|parisc|powerpc|riscv|s390|sh|sparc|x86_64]",
        ),
        option(
            "--kernel-image",
            help="Specify custom kernel image that you wish to build",
        ),
        option(
            "--kconfig",
            multiple=True,
            help="Kernel kconfig arguments (may be specified multiple times)",
        ),
        option(
            "--toolchain",
            help=f"Toolchain [{'|'.join(toolchains)}]",
        ),
        option(
            "--build-name",
            help=("User defined string to identify the build"),
        ),
        option(
            "--json-out",
            help="Write json build status out to a named file path",
            type=click.File("w", encoding="utf-8"),
        ),
        option(
            "-d",
            "--download",
            default=False,
            is_flag=True,
            help="Download artifacts after builds finish",
        ),
        option(
            "-o",
            "--output-dir",
            default=".",
            help="Directory where to download artifacts",
        ),
        option(
            "-n",
            "--no-wait",
            default=False,
            is_flag=True,
            help="Don't wait for the builds to finish",
        ),
        option(
            "-q",
            "--quiet",
            default=False,
            is_flag=True,
            help="Supress all informational output; prints only the download URL for the build",
        ),
        option(
            "-s",
            "--show-logs",
            default=False,
            is_flag=True,
            help="Prints build logs to stderr in case of warnings or errors",
        ),
        option(
            "-e",
            "--environment",
            type=key_value,
            multiple=True,
            help="Set environment variables for the build. Format: KEY=VALUE",
        ),
        option(
            "-p",
            "--patch-series",
            type=file_or_url,
            default=None,
            help=(
                "Patches to apply before building the kernel. Accepts patch "
                "series that applies directly with 'git am' or "
                "'git quiltimport' i.e., a mbox file or directory or gzipped "
                "tarball (.tar.gz)"
            ),
        ),
    ]

    def wrapper(f):
        f = wraps(f)(process_git_head(f))
        for opt in options:
            f = opt(f)
        return f

    return wrapper


def process_git_head(f):
    def wrapper(**kw):
        git_head = kw["git_head"]
        if git_head:
            try:
                repo, sha = tuxsuite.gitutils.get_git_head()
                kw["git_repo"] = repo
                kw["git_sha"] = sha
            except Exception as e:
                error(e)
        return f(**kw)

    return wrapper


def show_log(build, download, output_dir):
    if not build.warnings_count and not build.errors_count:
        return
    print("📄 Logs for {}:".format(build), file=sys.stderr)
    sys.stderr.flush()
    if download:
        for line in open(os.path.join(output_dir, build.uid, "build.log")):
            print(line.strip(), file=sys.stderr)
    else:
        tuxsuite.download.download_file(
            os.path.join(build.build_data, "build.log"), sys.stderr.buffer
        )


description = (
    "Subcommands:\n\n"
    "config \t\t\t    [uid]\n\n"
    "get   \t\t\t    [uid] [--json]\n\n"
    "list   \t\t\t    [--json] [--limit LIMIT]\n\n"
    "logs   \t\t\t    [uid]\n\n"
    "wait   \t\t\t    [uid]\n\n"
    "Positional arguments:\n\n"
    "[KEY=VALUE | target] ...    Make variables to use and targets to build."
    "\n\n"
    "\t\t\t    If no TARGETs are specified, tuxsuite will build "
    f"{' + '.join(defaults.targets)}."
)


@click.group(
    help="Do an OE/Yocto build with bitbake like 'tuxsuite bake submit <build-definition.json>'",
    short_help="Do an OE/Yocto build with bitbake like 'tuxsuite bake submit <build-definition.json>'",
)
def bake():
    pass


@bake.command(
    help="Run a single OE build with 'tuxsuite bake submit <build-definition.json>'",
    short_help="Run a single OE build with 'tuxsuite bake submit <build-definition.json>'",
)
@click.argument("build_definition", nargs=1)
@click.option(
    "--json-out",
    help="Write json build status out to a named file path",
    type=click.File("w", encoding="utf-8"),
)
@click.option(
    "-l",
    "--local-manifest",
    type=file_or_url,
    default=None,
    help=(
        "Path to a local manifest file which will be used during repo sync."
        "This input is ignored if sources used is git_trees in the build"
        "definition. Should be a valid XML"
    ),
)
def submit(build_definition, json_out=None, local_manifest=None):
    try:
        with open(os.path.abspath(build_definition)) as reader:
            data = json_lib.load(reader)
    except Exception:
        sys.stderr.write(
            f"Problem parsing {build_definition}, Is it a valid json file ?\n"
        )
        sys.exit(1)
    if local_manifest:
        data["manifest"] = click.format_filename(local_manifest)
    try:
        build = tuxsuite.Bitbake(data=data)
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)
    info(
        "*** WARNING: BITBAKE SUPPORT IS EXPERIMENTAL ***\n"
        "Building target: {} with bitbake from {} source with distro: {} machine: {} arguments".format(
            build.build_definition.target,
            build.build_definition.sources,
            build.build_definition.distro,
            build.build_definition.machine,
        )
    )
    try:
        build.build()
        info("uid: {}".format(build.uid))
    except tuxsuite.exceptions.BadRequest as e:
        raise (click.ClickException(str(e)))

    build_result = wait_for_object(build)
    if json_out:
        json_out.write(json_lib.dumps(build.status, sort_keys=True, indent=4))
    if not build_result:
        sys.exit(1)


cli.add_command(bake)


@cli.command(help=description, short_help="Run a single build.")
@click.argument("action", metavar="[ACTION ...]", required=False)
@common_options(required=["--target-arch", "--kconfig", "--toolchain"])
@click.argument("targets", metavar="[VAR=VALUE...] [target ...]", nargs=-1)
def build(
    json_out=None,
    quiet=False,
    show_logs=None,
    git_head=False,
    download=False,
    output_dir=None,
    no_wait=False,
    no_cache=False,
    patch_series=None,
    limit=LIMIT,
    json=False,
    action=None,
    **build_params,
):
    quiet_output(quiet)

    if action in BUILD_SUBCOMMANDS:
        cfg, options = tuxcli_load()
        if limit != LIMIT:
            options.limit = limit
        if json:
            options.json = json
        build_handlers[action](options, cfg)
        return

    if action is not None:
        if build_params["targets"]:
            targets = list(build_params["targets"])
            targets.append(action)
            build_params["targets"] = tuple(targets)
        else:
            build_params["targets"] = (action,)

    # This is to show a valid help message when no arguments are supplied.
    if build_params["toolchain"] is None:
        error_message = (
            "Missing option --toolchain.\n\n Try 'tuxsuite build --help' for help."
        )
        raise click.exceptions.UsageError(error_message)

    if "targets" in build_params:
        target_list, make_vars = get_make_targets_vars(build_params["targets"])
        build_params["targets"] = target_list
        build_params["make_variables"] = make_vars

    if patch_series:
        build_params["patch_series"] = click.format_filename(patch_series)

    build_params["no_cache"] = no_cache
    try:
        build = tuxsuite.Build(**build_params)
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)
    info(
        "Building Linux Kernel {} at {}".format(
            build.git_repo, build.git_ref or build.git_sha
        )
    )
    try:
        build.build()
        info("uid: {}".format(build.uid))
    except tuxsuite.exceptions.BadRequest as e:
        raise (click.ClickException(str(e)))

    build_result = True

    if no_wait:
        format_result(build.status)
    else:
        build_result = wait_for_object(build)

    if json_out:
        json_out.write(json_lib.dumps(build.status, sort_keys=True, indent=4))
    if download:
        tuxsuite.download.download(build, output_dir)
    if show_logs:
        show_log(build, download, output_dir)
    if quiet:
        print(build.build_data)

    if not build_result:
        sys.exit(1)


@cli.command(help=description, short_help="Run a set of builds.")
@click.option("--set-name", required=True, help="Set name")
@click.option("--tux-config", help="Path or a web URL to tuxsuite config file")
@click.argument("targets", metavar="[VAR=VALUE...] [target ...]", nargs=-1)
@common_options(required=[])
def build_set(
    tux_config,
    set_name,
    json_out=None,
    quiet=None,
    show_logs=None,
    git_head=False,
    download=False,
    output_dir=None,
    no_wait=False,
    patch_series=None,
    no_cache=False,
    **build_params,
):
    quiet_output(quiet)

    if "targets" in build_params:
        target_list, make_vars = get_make_targets_vars(build_params["targets"])
        build_params["targets"] = target_list
        build_params["make_variables"] = make_vars

    if patch_series:
        build_params["patch_series"] = click.format_filename(patch_series)

    try:
        plan_config = tuxsuite.config.BuildSetConfig(set_name, tux_config)
        if not plan_config.plan:
            warning("Empty plan, skipping")
            return
        plan = tuxsuite.Plan(plan_config, **build_params)
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)

    try:
        plan.submit()
    except tuxsuite.exceptions.BadRequest as e:
        raise (click.ClickException(str(e)))

    info("Building Linux Kernel build set {}".format(plan_config.name))

    result = True

    if no_wait:
        for build in plan.builds:
            format_result(build.status)
    else:
        result = wait_for_object(plan)

    if json_out:
        json_out.write(json_lib.dumps(plan.build_status_list, sort_keys=True, indent=4))

    if download:
        for build in plan.builds:
            tuxsuite.download.download(build, output_dir)
    if show_logs:
        for build in plan.builds:
            show_log(build, download, output_dir)

    if quiet:
        for build in plan.builds:
            print(build.build_data)

    if not result:
        sys.exit(1)


def test_options(required):
    def option(*args, **kwargs):
        kw = kwargs.copy()
        kw["required"] = False
        for a in args:
            if a in required:
                kw["required"] = True
        return click.option(*args, **kw)

    options = [
        option(
            "--device",
            help="Device type",
            type=str,
        ),
        option(
            "--kernel",
            help="URL of the kernel to test",
            default=None,
            type=str,
        ),
        option(
            "--mcp-fw", help="URL of the MCP firmware to test", default=None, type=str
        ),
        option(
            "--mcp-romfw",
            help="URL of the MCP ROM firmware to test",
            default=None,
            type=str,
        ),
        option(
            "--modules",
            help="URL of the kernel modules",
            default=None,
            type=str,
        ),
        option("--rootfs", help="URL of the rootfs to test", default=None, type=str),
        option(
            "--scp-fw", help="URL of the SCP firmware to test", default=None, type=str
        ),
        option(
            "--ap-romfw",
            help="URL of the AP ROM firmware to test",
            default=None,
            type=str,
        ),
        option(
            "--scp-romfw",
            help="URL of the SCP ROM firmware to test",
            default=None,
            type=str,
        ),
        option("--fip", help="URL of the fip.bin to test", default=None, type=str),
        option(
            "--parameters",
            help="test parameters as KEY=VALUE",
            default=[],
            type=str,
            multiple=True,
        ),
        option(
            "--tests",
            help="Comma separated list of tests",
            default="boot",
        ),
        option(
            "--timeouts",
            help="timeouts as KEY=VALUE",
            default=[],
            type=str,
            multiple=True,
        ),
        option(
            "--boot-args",
            help="Extra boot arguments",
            default=None,
            type=str,
        ),
        option(
            "--wait-for",
            help="Wait for a test uid",
            default=None,
            type=str,
        ),
        option(
            "-n",
            "--no-wait",
            default=False,
            is_flag=True,
            help="Don't wait for tests to finish",
        ),
        option(
            "--json-out",
            help="Write json test status out to a named file path",
            type=click.File("w", encoding="utf-8"),
        ),
        option(
            "--limit",
            default=LIMIT,
            help="Limit to LIMIT output. Used with [list]",
        ),
        option(
            "--json",
            default=False,
            is_flag=True,
            help="Show json output. Used with [get | list]",
        ),
        option(
            "--raw",
            default=False,
            is_flag=True,
            help="Show raw output. Used with [logs | results]",
        ),
    ]

    def wrapper(f):
        for opt in options:
            f = opt(f)
        return f

    return wrapper


test_description = (
    "Test a kernel\n\n"
    "Subcommands:\n\n"
    "get   \t\t\t    [uid] [--json]\n\n"
    "list   \t\t\t    [--json] [--limit LIMIT]\n\n"
    "logs   \t\t\t    [uid] [--raw]\n\n"
    "results   \t\t    [uid] [--raw]\n\n"
    "wait   \t\t\t    [uid]\n\n"
)


@cli.command(help=test_description, short_help="Test a kernel")
@click.argument("action", metavar="[ACTION]", required=False)
@click.argument("uid", metavar="[UID]", required=False)
@test_options(required=["--devices"])
def test(
    device,
    kernel,
    ap_romfw,
    mcp_fw,
    mcp_romfw,
    modules,
    parameters,
    rootfs,
    scp_fw,
    scp_romfw,
    fip,
    tests,
    timeouts,
    boot_args,
    wait_for,
    no_wait,
    json_out,
    json,
    raw,
    limit=LIMIT,
    action=None,
    **test_params,
):
    if action:
        cfg, options = tuxcli_load()
        if limit != LIMIT:
            options.limit = limit
        if json:
            options.json = json
        test_handlers[action](options, cfg)
        return

    # This is to show a valid help message when no arguments are supplied.
    if not device:
        error_message = (
            "Missing option '--device'.\n\n Try 'tuxsuite test --help' for help."
        )
        raise click.exceptions.UsageError(error_message)

    tests = [test for test in tests.split(",") if test]
    tests = [test for test in tests if test != "boot"]
    if wait_for:
        info(
            "Testing build {} on {} with {}".format(
                wait_for, device, ", ".join(["boot"] + tests)
            )
        )
        if kernel:
            raise click.ClickException("--kernel and --wait-for are mutually exclusive")
        if modules:
            raise click.ClickException(
                "--modules and --wait-for are mutually exclusive"
            )
    else:
        info(
            "Testing {} on {} with {}".format(
                kernel, device, ", ".join(["boot"] + tests)
            )
        )

    params = {}
    for p in parameters:
        k, v = p.split("=")
        params[k] = v

    timeouts_d = {}
    for t in timeouts:
        k, v = t.split("=")
        timeouts_d[k] = int(v)

    try:
        test = tuxsuite.Test(
            device=device,
            kernel=kernel,
            ap_romfw=ap_romfw,
            mcp_fw=mcp_fw,
            mcp_romfw=mcp_romfw,
            modules=modules,
            rootfs=rootfs,
            scp_fw=scp_fw,
            scp_romfw=scp_romfw,
            fip=fip,
            parameters=params,
            tests=tests,
            timeouts=timeouts_d,
            boot_args=boot_args,
            wait_for=wait_for,
        )
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)

    try:
        test.test()
        info("uid: {}".format(test.uid))
    except tuxsuite.exceptions.BadRequest as e:
        raise (click.ClickException(str(e)))

    test_result = True

    if no_wait:
        format_result(test.status, test.url)
    else:
        test_result = wait_for_object(test)

    if json_out:
        json_out.write(json_lib.dumps(test.status, sort_keys=True, indent=4))

    # If the test did not pass, exit with exit code of 1
    if not test_result:
        sys.exit(1)


plan_description = (
    "Run the specified plan file.\n\n"
    "Subcommands:\n\n"
    "get   \t\t\t    [uid] [--json]\n\n"
    "list   \t\t\t    [--json] [--limit LIMIT]\n\n"
)


@cli.command(help=plan_description, short_help="Run a plan file.")
@click.option("--name", default=None, help="Set name")
@click.option("--description", default=None, help="Set description")
@click.option("--job-name", default=None, help="Job name")
@click.option("--git-repo", default=None, help="Git repository")
@click.option("--git-ref", default=None, help="Git reference")
@click.option("--git-sha", default=None, help="Git commit")
@click.option(
    "--git-head",
    default=False,
    is_flag=True,
    help="Build the current git HEAD. Overrrides --git-repo and --git-ref",
)
@click.option(
    "-d",
    "--download",
    default=False,
    is_flag=True,
    help="Download artifacts after builds finish",
)
@click.option(
    "-o",
    "--output-dir",
    default=".",
    help="Directory where to download artifacts",
)
@click.option(
    "-s",
    "--show-logs",
    default=False,
    is_flag=True,
    help="Prints build logs to stderr in case of warnings or errors",
)
@click.option(
    "--no-cache",
    default=False,
    is_flag=True,
    help="Build without using any compilation cache",
)
@click.option(
    "-n",
    "--no-wait",
    default=False,
    is_flag=True,
    help="Don't wait for plan to finish",
)
@click.option(
    "--json-out",
    help="Write json results out to a named file path",
    type=click.File("w", encoding="utf-8"),
)
@click.option(
    "-p",
    "--patch-series",
    type=file_or_url,
    default=None,
    help=(
        "Patches to apply before building the kernel. Accepts patch "
        "series that applies directly with 'git am' or "
        "'git quiltimport' i.e., a mbox file or directory or gzipped "
        "tarball (.tar.gz)"
    ),
)
@click.option(
    "--limit",
    default=LIMIT,
    help="Limit to LIMIT output. Used with [list]",
)
@click.option(
    "--json",
    default=False,
    is_flag=True,
    help="Show json output. Used with [get | list]",
)
@click.argument("action", metavar="[ACTION]", required=False)
@click.argument("uid", metavar="[UID]", required=False)
@click.argument("config", required=False)
def plan(
    name,
    description,
    job_name,
    config,
    show_logs=None,
    download=False,
    output_dir=None,
    no_wait=False,
    json_out=None,
    json=False,
    limit=LIMIT,
    action=None,
    **build_params,
):
    if action in ["list", "get"]:
        cfg, options = tuxcli_load()
        if limit != LIMIT:
            options.limit = limit
        if json:
            options.json = json
        plan_handlers[action](options, cfg)
        return
    else:
        config = action

    # This is to show a valid help message when no arguments are supplied.
    if not config:
        error_message = (
            "Missing argument 'CONFIG'.\n\n Try 'tuxsuite plan --help' for help."
        )
        raise click.exceptions.UsageError(error_message)

    if build_params["git_head"]:
        try:
            repo, sha = tuxsuite.gitutils.get_git_head()
            build_params["git_repo"] = repo
            build_params["git_sha"] = sha
        except Exception as e:
            error(e)
    del build_params["git_head"]

    try:
        plan_config = tuxsuite.config.PlanConfig(name, description, config, job_name)

        # setting respective plan type class obj (Kernel or Bake)
        plan_type = plan_config.plan_type

        if plan_config.schema_warning:
            warning(f"Invalid plan file: {plan_config.schema_warning}")

        if not plan_config.plan:
            warning("Empty plan, skipping")
            return
        plan = tuxsuite.Plan(plan_config, **build_params)
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)

    plan_type.plan_info(plan_config.name, plan_config.description)

    try:
        plan.submit()
        info("Plan {}/plans/{}\n".format(plan.url, plan.plan))
        info("uid: {}".format(plan.plan))
    except tuxsuite.exceptions.BadRequest as e:
        raise (click.ClickException(str(e)))

    result = True

    if no_wait:
        for build in plan.builds:
            format_result(build.status)
        for test in plan.tests:
            format_result(test.status, plan.url + "/tests/{}".format(test.uid))
    else:
        result = wait_for_object(plan)
        info(f"\nSummary: {plan.url}/plans/{plan.plan}")
        for b in chain(plan.passing(), plan.warning(), plan.failing(), plan.errors()):
            format_plan_result(b, plan._tests_wait_for(b.uid))

    if json_out:
        json_out.write(json_lib.dumps(plan.status, sort_keys=True, indent=4))

    if download:
        for build in plan.builds:
            tuxsuite.download.download(build, output_dir)
    if show_logs:
        for build in plan.builds:
            show_log(build, download, output_dir)

    if not result:
        sys.exit(1)


@cli.command(help="Fetch results", short_help="Fetch results")
@click.option("--build", help="UID of the build to fetch result", default="", type=str)
@click.option("--test", help="UID of the test to fetch result", default="", type=str)
@click.option("--plan", help="UID of the plan to fetch result", default="", type=str)
@click.option(
    "--from-json",
    help="Read status input from named json file path",
    type=click.File("r", encoding="utf-8"),
)
@click.option(
    "--json-out",
    help="Write json results out to a named file path",
    type=click.File("w", encoding="utf-8"),
)
def results(build, test, plan, from_json, json_out):
    result_json = {}
    try:
        results = tuxsuite.Results()
    except (AssertionError, tuxsuite.exceptions.TuxSuiteError) as e:
        error(e)

    try:
        if from_json:
            data = json_lib.loads(from_json.read())
            if "builds" in data and "tests" in data:
                plan = data["builds"][list(data["builds"].keys())[0]]["plan"]
            elif "build_name" in data:
                build = data["uid"]
            elif "tests" in data:
                test = data["uid"]
            elif isinstance(data, list):
                result_json = []
                for res in data:
                    results.uid = res["uid"]
                    build_result = results.get_build()
                    format_result(build_result)
                    if json_out:
                        result_json.append(build_result)
        elif not any([build, test, plan]):  # get all results with no options
            result_json, tuxapi_tests_url = results.get_all()
            for key in result_json.keys():
                info(f"{key.capitalize()}:")
                for result in result_json[key].get("results", None):
                    if key == "plans":
                        info(f"{result['uid']}: {result['name']} {result['project']}")
                    else:
                        format_result(result, f"{tuxapi_tests_url}/{result['uid']}")
                info("\n")
        if build:
            results.uid = build
            result_json = results.get_build()
            format_result(result_json)
        if test:
            results.uid = test
            result_json, tuxapi_tests_url = results.get_test()
            format_result(result_json, tuxapi_tests_url)
        if plan:
            results.uid = plan
            result_json, tuxapi_plan_url = results.get_plan()

            plan_obj = tuxsuite.Plan("")
            plan_obj.plan = plan
            plan_obj.load(result_json)
            info(f"Summary: {plan_obj.url}/plans/{plan_obj.plan}")
            for b in chain(
                plan_obj.passing(),
                plan_obj.warning(),
                plan_obj.failing(),
                plan_obj.errors(),
            ):
                format_plan_result(b, plan_obj._tests_wait_for(b.uid))
            # TODO: print stand alone tests

            (build_summary, test_summary) = plan_summary(plan_obj)
            info(build_summary)
            info(test_summary)

    except tuxsuite.exceptions.URLNotFound as e:
        raise (click.ClickException(str(e)))

    if json_out:
        json_out.write(json_lib.dumps(result_json, sort_keys=True, indent=4))


def main():
    cli.main(prog_name="tuxsuite")
