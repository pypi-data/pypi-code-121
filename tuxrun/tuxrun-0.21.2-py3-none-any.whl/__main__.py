#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import contextlib
import json
import logging
from pathlib import Path
import shlex
import shutil
import signal
import sys
import tempfile
from urllib.parse import urlparse

from tuxrun import templates
from tuxrun.argparse import filter_options, pathurlnone, setup_parser
from tuxrun.assets import get_rootfs, get_test_definitions
from tuxrun.devices import Device
from tuxrun.exceptions import InvalidArgument
from tuxrun.requests import requests_get
from tuxrun.results import Results
from tuxrun.runtimes import Runtime
from tuxrun.tests import Test
from tuxrun.utils import ProgressIndicator
from tuxrun.writer import Writer
from tuxrun.yaml import yaml_load


###########
# GLobals #
###########
LOG = logging.getLogger("tuxrun")


###########
# Helpers #
###########
def download(src, dst):
    url = urlparse(src)
    if url.scheme in ["http", "https"]:
        ret = requests_get(src)
        dst.write_text(ret.text, encoding="utf-8")
    else:
        shutil.copyfile(src, dst)


##############
# Entrypoint #
##############
def run(options, tmpdir: Path) -> int:
    # Render the job definition and device dictionary
    extra_assets = []
    if options.device:
        overlays = []
        if options.modules:
            overlays.append(("modules", options.modules, "/"))
            extra_assets.append(options.modules)
        for (index, item) in enumerate(options.overlays):
            overlays.append((f"overlay-{index:02}", item, "/"))
            extra_assets.append(item)

        # Add test definitions only when needed
        test_definitions = None
        if any(t.need_test_definition for t in options.tests):
            test_definitions = "file://" + get_test_definitions(
                ProgressIndicator.get("Downloading test definitions")
            )
            extra_assets.append(test_definitions)

        command = " ".join([shlex.quote(s) for s in options.command])

        definition = options.device.definition(
            bios=options.bios,
            bl1=options.bl1,
            command=command,
            device=options.device,
            dtb=options.dtb,
            kernel=options.kernel,
            ap_romfw=options.ap_romfw,
            mcp_fw=options.mcp_fw,
            mcp_romfw=options.mcp_romfw,
            fip=options.fip,
            overlays=overlays,
            rootfs=options.rootfs,
            rootfs_partition=options.partition,
            scp_fw=options.scp_fw,
            scp_romfw=options.scp_romfw,
            tests=options.tests,
            test_definitions=test_definitions,
            tests_timeout=sum(t.timeout for t in options.tests),
            timeouts=options.timeouts,
            tmpdir=tmpdir,
            tux_boot_args=options.boot_args.replace('"', "")
            if options.boot_args
            else None,
            parameters=options.parameters,
        )
        LOG.debug("job definition")
        LOG.debug(definition)

        context = yaml_load(definition).get("context", {})
        device_dict = options.device.device_dict(context)
        LOG.debug("device dictionary")
        LOG.debug(device_dict)

        (tmpdir / "definition.yaml").write_text(definition, encoding="utf-8")
        (tmpdir / "device.yaml").write_text(device_dict, encoding="utf-8")

    # Use the provided ones
    else:
        # Download if needed and copy to tmpdir
        download(str(options.device_dict), (tmpdir / "device.yaml"))
        download(str(options.definition), (tmpdir / "definition.yaml"))

    # Render the dispatcher.yaml
    (tmpdir / "dispatcher").mkdir()
    dispatcher = (
        templates.dispatchers()
        .get_template("dispatcher.yaml.jinja2")
        .render(prefix=tmpdir.name)
    )
    LOG.debug("dispatcher config")
    LOG.debug(dispatcher)
    (tmpdir / "dispatcher.yaml").write_text(dispatcher, encoding="utf-8")

    # Use a container runtime
    runtime = Runtime.select(options.runtime)()
    runtime.name(tmpdir.name)
    runtime.image(options.image)

    runtime.bind(tmpdir)
    for path in [
        options.ap_romfw,
        options.bios,
        options.bl1,
        options.dtb,
        options.fip,
        options.kernel,
        options.mcp_fw,
        options.mcp_romfw,
        options.rootfs,
        options.scp_fw,
        options.scp_romfw,
    ] + extra_assets:
        if not path:
            continue
        if urlparse(path).scheme == "file":
            runtime.bind(path[7:], ro=True)

    # Forward the signal to the runtime
    def handler(*_):
        runtime.kill()

    signal.signal(signal.SIGHUP, handler)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGQUIT, handler)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGUSR1, handler)
    signal.signal(signal.SIGUSR2, handler)

    # start the pre_run command
    if options.device and options.device.flag_use_pre_run_cmd:
        LOG.debug("Pre run command")
        runtime.bind(tmpdir / "dispatcher" / "tmp", "/var/lib/lava/dispatcher/tmp")
        (tmpdir / "dispatcher" / "tmp").mkdir()
        runtime.pre_run(tmpdir)

    # Build the lava-run arguments list
    args = [
        "lava-run",
        "--device",
        str(tmpdir / "device.yaml"),
        "--dispatcher",
        str(tmpdir / "dispatcher.yaml"),
        "--job-id",
        "1",
        "--output-dir",
        "output",
        str(tmpdir / "definition.yaml"),
    ]

    results = Results(options.tests)
    # Start the writer (stderr or log-file)
    with Writer(options.log_file) as writer:
        # Start the runtime
        with runtime.run(args):
            for line in runtime.lines():
                writer.write(line)
                results.parse(line)
    runtime.post_run()
    if options.results:
        options.results.write_text(json.dumps(results.data))
    return max([runtime.ret(), results.ret()])


def main() -> int:
    # Parse command line
    parser = setup_parser()
    options = parser.parse_args()

    # Setup logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOG.addHandler(handler)
    LOG.setLevel(logging.DEBUG if options.debug else logging.INFO)

    # --tuxmake/--device/--kernel/--modules/--tests and
    # --device-dict/--definition are mutualy exclusive and required
    first_group = bool(
        options.device
        or options.bios
        or options.dtb
        or options.kernel
        or options.modules
        or options.overlays
        or options.partition
        or options.rootfs
        or options.tuxbuild
        or options.tuxmake
        or options.tests
        or options.boot_args
        or options.command
    )
    second_group = bool(options.device_dict or options.definition)
    if not first_group and not second_group:
        parser.error("artefacts or configuration files argument groups are required")
    if first_group and second_group:
        parser.error(
            "artefacts and configuration files argument groups are mutualy exclusive"
        )

    if first_group:
        if options.tuxbuild or options.tuxmake:
            tux = options.tuxbuild if options.tuxbuild else options.tuxmake
            if not options.kernel:
                options.kernel = tux.kernel
            if not options.modules and tux.modules:
                options.modules = tux.modules
            if not options.device:
                options.device = f"qemu-{tux.target_arch}"
            elif options.device == "qemu-armv5":
                if options.tuxbuild:
                    options.dtb = tux.url + "/dtbs/versatile-pb.dtb"
                elif options.tuxmake:
                    if (tux.location / "dtbs" / "versatile-pb.dtb").exists():
                        options.dtb = tux.url + "/dtbs/versatile-pb.dtb"

        if not options.device:
            parser.error("argument --device is required")

        if options.command:
            options.tests.append("command")

        try:
            options.device = Device.select(options.device)()
            # Download only after the device has been found
            if options.device.flag_cache_rootfs:
                options.rootfs = pathurlnone(
                    get_rootfs(
                        options.device,
                        options.rootfs,
                        ProgressIndicator.get("Downloading root filesystem"),
                    )
                )

            options.tests = [
                Test.select(t)(options.timeouts.get(t)) for t in options.tests
            ]
            options.device.validate(**filter_options(options))
        except InvalidArgument as exc:
            parser.error(str(exc))

    # --device-dict/--definition are mandatory
    else:
        if not options.device_dict:
            parser.error("argument --device-dict is required")
        if not options.definition:
            parser.error("argument --definition is required")

    if options.tests:
        tests = [t.name for t in options.tests]
        if sorted(list(set(tests))) != sorted(tests):
            parser.error("each test should appears only once")

    # Create the temp directory
    tmpdir = Path(tempfile.mkdtemp(prefix="tuxrun-"))
    LOG.debug(f"temporary directory: '{tmpdir}'")
    try:
        return run(options, tmpdir)
    except Exception as exc:
        LOG.error("Raised an exception %s", exc)
        raise
    finally:
        with contextlib.suppress(FileNotFoundError, PermissionError):
            shutil.rmtree(tmpdir)


def start():
    if __name__ == "__main__":
        sys.exit(main())


start()
