"""Plugins."""

import sys
from typing import Any, Set

from yea import context, ytest

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points  # type: ignore
else:
    from importlib.metadata import entry_points


# TODO: implement YeaPlugin that plugins (such as yea-wandb) will inherit from


class Plugins:
    def __init__(self, yc: "context.YeaContext") -> None:
        self._yc = yc
        self._plugin_list: list = []
        self._find_plugins()
        self._plugs_needed: Set[str] = set()

    def _find_plugins(self) -> None:
        discovered_plugins = entry_points(group="yea.plugins")
        for p in discovered_plugins:
            # print("got", p)
            m = p.load()
            # print("got", m)
            plug = m.init_plugin(self._yc)
            self._plugin_list.append(plug)

    def get_plugin(self, name: str) -> Any:
        for p in self._plugin_list:
            if p._name == name:
                return p

    def monitors_inform(self, tlist: list) -> None:
        for p in self._plugin_list:
            for t in tlist:
                if p.name in t.config.get("plugin", []):
                    self._plugs_needed.add(p.name)

    def monitors_init(self) -> None:
        for p in self._plugin_list:
            if p.name not in self._plugs_needed:
                continue
            p.monitors_init()

    def monitors_start(self) -> None:
        for p in self._plugin_list:
            if p.name not in self._plugs_needed:
                continue
            p.monitors_start()

    def monitors_stop(self) -> None:
        for p in self._plugin_list:
            if p.name not in self._plugs_needed:
                continue
            p.monitors_stop()

    def monitors_reset(self) -> None:
        for p in self._plugin_list:
            if p.name not in self._plugs_needed:
                continue
            p.monitors_reset()

    def test_prep(self, yt: "ytest.YeaTest") -> None:
        # wandb_dir_safe_cleanup()
        for p in self._plugin_list:
            p.test_prep(yt)

    def test_done(self, yt: "ytest.YeaTest") -> None:
        # wandb_dir_safe_cleanup()
        for p in self._plugin_list:
            p.test_done(yt)

    def test_check(self, yt: "ytest.YeaTest") -> list:
        # ctx = self._backend.get_state()
        test_config = yt.config
        result_list = []
        for p in self._plugin_list:
            if p.name not in self._plugs_needed:
                continue
            if p.name not in test_config.get("plugin", []):
                continue
            result = p.test_check(yt, debug=self._yc._args.debug)
            if result:
                result_list.extend(result)
        return result_list
