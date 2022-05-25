#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tuxbake.models import OEBuild
from tuxmake.runtime import Terminated
import signal


def build(**kwargs):
    old_sigterm = signal.signal(signal.SIGTERM, Terminated.handle_signal)
    oebuild = OEBuild(**kwargs)
    try:
        oebuild.prepare()
        oebuild.do_build()
    except (KeyboardInterrupt, Terminated) as ex:
        print("tuxbake Interrupted")
    oebuild.do_cleanup()
    signal.signal(signal.SIGTERM, old_sigterm)
    return oebuild
