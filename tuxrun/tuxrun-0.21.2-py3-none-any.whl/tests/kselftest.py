# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2022-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxrun.tests import Test


class KSelfTest(Test):
    devices = ["qemu-*", "fvp-aemva"]
    cmdfile: str = ""
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout
        kwargs["cmdfile"] = (
            self.cmdfile if self.cmdfile else self.name.replace("ltp-", "")
        )

        if "CPUPOWER" in kwargs["parameters"]:
            kwargs["overlays"].append(
                ("cpupower", kwargs["parameters"]["CPUPOWER"], "/")
            )
        if "KSELFTEST" in kwargs["parameters"]:
            kwargs["overlays"].append(
                (
                    "kselftest",
                    kwargs["parameters"]["KSELFTEST"],
                    "/opt/kselftests/default-in-kernel/",
                )
            )

        return self._render("kselftest.yaml.jinja2", **kwargs)


class KSelftestGpio(KSelfTest):
    name = "kselftest-gpio"
    cmdfile = "gpio"
    timeout = 5


class KSelftestIPC(KSelfTest):
    name = "kselftest-ipc"
    cmdfile = "ipc"
    timeout = 5


class KSelftestIR(KSelfTest):
    name = "kselftest-ir"
    cmdfile = "ir"
    timeout = 5


class KSelftestKcmp(KSelfTest):
    name = "kselftest-kcmp"
    cmdfile = "kcmp"
    timeout = 5


class KSelftestKvm(KSelfTest):
    name = "kselftest-kvm"
    cmdfile = "kvm"
    timeout = 15


class KSelftestKexec(KSelfTest):
    name = "kselftest-kexec"
    cmdfile = "kexec"
    timeout = 5


class KSelftestRseq(KSelfTest):
    name = "kselftest-rseq"
    cmdfile = "rseq"
    timeout = 5


class KSelftestRtc(KSelfTest):
    name = "kselftest-rtc"
    cmdfile = "rtc"
    timeout = 5
