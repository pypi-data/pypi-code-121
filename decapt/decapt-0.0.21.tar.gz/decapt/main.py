import argparse
import subprocess
from subprocess import check_call, check_output
import json
import os.path
import logging
from pathlib import Path
import abc
from functools import wraps
import sys
import re

import luxem


here = Path(__file__).parent


def decolog(f):
    @wraps(f)
    def inner(*pargs, **kwargs):
        logging.debug(f"{f.__name__}: {repr(pargs)} {repr(kwargs)}")
        return f(*pargs, **kwargs)

    return inner


def lazy(f):
    f.lazied = ()

    @wraps(f)
    def inner(*pargs, **kwargs):
        if f.lazied:
            return f.lazied[0]
        f.lazied = (f(*pargs, **kwargs),)
        return f.lazied[0]

    return inner


class Sudo:
    def __init__(self):
        self.bg = subprocess.Popen(
            ["sudo", sys.executable, here / "sudobg.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    def _encode(self, o):
        if isinstance(o, dict):
            return {self._encode(k): self._encode(v) for k, v in o.items()}
        elif isinstance(o, (list, tuple)):
            return [self._encode(v) for v in o]
        elif isinstance(o, Path):
            return str(o)
        return o

    def _req(self, *pargs, **kwargs):
        self.bg.stdin.write(
            (json.dumps(self._encode([pargs, kwargs])) + "\n").encode("utf-8")
        )
        self.bg.stdin.flush()
        return json.loads(self.bg.stdout.readline())

    @decolog
    def c(self, *pargs, **kwargs):
        return self._req(*pargs, **kwargs)

    @decolog
    def cc(self, *pargs, **kwargs):
        ret = self._req(*pargs, **kwargs)
        print(ret["out"])
        if ret["code"] != 0:
            raise RuntimeError(ret["err"])

    @decolog
    def co(self, *pargs, **kwargs):
        ret = self._req(*pargs, **kwargs)
        if ret["code"] != 0:
            print(ret["out"])
            raise RuntimeError(ret["err"])
        return ret["out"]


@lazy
def sudo():
    return Sudo()


class Plugin(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def id(self):
        pass

    @abc.abstractmethod
    def installed(self):
        pass

    @abc.abstractmethod
    def install(self, names):
        pass

    @abc.abstractmethod
    def uninstall(self, names):
        pass


DEFAULT_PLUGIN = "apt"


class APTPlugin(Plugin):
    def id(self):
        return "apt"

    @lazy
    def _ignore(self):
        return set(
            check_output(
                [
                    "aptitude",
                    "search",
                    "~prequired",
                    "~pimportant",
                    "~pstandard",
                    "-F%p",
                ]
            )
            .decode("utf-8")
            .splitlines()
            + ["aptitude", "sudo", "python"]
        )

    def base_want(self):
        return self._ignore()

    def installed(self):
        return set(
            check_output(["apt-mark", "showmanual"]).decode("utf-8").splitlines()
        )

    def install(self, names):
        manual = []
        targetted = {}
        for name in names:
            if not isinstance(name, dict):
                name = {"name": name}
            if "path" in name:
                manual.append(name)
            else:
                if name["name"] in self._ignore():
                    logging.debug(f"Package {name} is part of the base system.")
                targetted.setdefault(tuple(name.get("options") or ()), []).append(name)
        for options, packages in targetted.items():
            sudo().cc(
                ["apt-get", "install", "-y"]
                + list(options)
                + [package["name"] for package in packages]
            )
        for package in manual:
            p = Path(package["path"]).expanduser()
            check_call([p / "build.sh"], cwd=p)
            sudo().cc(["apt", "install", "-y", f'./{package["name"]}.deb'], cwd=p)

    def uninstall(self, names):
        sudo().cc(["apt-mark", "auto"] + names)
        sudo().cc(["apt-get", "autoremove", "-y"])


class SnapPlugin(Plugin):
    def id(self):
        return "snap"

    def installed(self):
        try:
            out = set()
            for line in check_output(["snap", "list"]).decode("utf-8").splitlines()[1:]:
                name = line.split()[0]
                if re.search("^core\\d*$", name):
                    continue
                out.add(name)
            return out
        except:
            logging.warning("Failed to get snap packages", exc_info=True)
            return []

    def install(self, names):
        for package in names:
            options = []
            if isinstance(package, dict):
                name = package["name"]
                options = package["options"]
            else:
                name = package
            sudo().cc(["snap", "install", name] + options)

    def uninstall(self, names):
        sudo().cc(["snap", "remove"] + names)


PLUGINS = [
    APTPlugin,
    SnapPlugin,
]


def main():
    parser = argparse.ArgumentParser(
        description="Debianish Linux declarative package management"
    )
    parser.add_argument("-v", "--verbose", action="store_true")

    subparsers = parser.add_subparsers(title="Command", dest="_command")

    com_gen = subparsers.add_parser(
        "generate",
        description="Generate configuration from current explicitly installed packages",  # noqa
    )
    com_gen.add_argument(
        "-f", "--force", help="Overwrite existing configuration", action="store_true",
    )
    com_gen.add_argument(
        "conf", nargs="?", help="Configuration path", default="decapt.luxem"
    )

    com_sync = subparsers.add_parser(
        "sync", description="Install, remove, and upgrade packages. Default command.",
    )
    com_sync.add_argument(
        "-n",
        "--dry-run",
        help="Show changes to be implemented on next sync",
        action="store_true",
    )
    com_sync.add_argument(
        "conf", nargs="?", help="Configuration path", default="decapt.luxem"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    plugins = [plugin() for plugin in PLUGINS]

    command = args._command
    if command:
        args_conf = args.conf
    else:
        command = "sync"
        args_conf = "decapt.luxem"

    if command == "generate":
        conf = dict(installed=[])
        for plugin in plugins:
            for package in plugin.installed():
                if plugin.id() == DEFAULT_PLUGIN:
                    conf["installed"].append(package)
                else:
                    conf["installed"].append(luxem.Typed(plugin.id(), package))
        if not args.force and os.path.exists(args_conf):
            print(f"{args_conf} already exists. Delete it or run with `-f`.")
            return
        with open(args_conf, "w") as out:
            luxem.dump(out, conf, pretty=True)

    elif command == "sync":
        with open(args_conf, "r") as conff:
            conf = luxem.load(conff)[0]
        want = dict()
        add = dict()
        remove = dict()
        for package in conf["installed"]:
            if isinstance(package, luxem.Typed):
                plugin = package.name
                package = package.value
            else:
                plugin = DEFAULT_PLUGIN
            if isinstance(package, dict):
                name = package["name"]
            else:
                name = package
            want.setdefault(plugin, dict())[name] = package
        for plugin in plugins:
            print(f"Scanning current package state for {plugin.id()}...")
            installed = set(plugin.installed())
            plugin_want = want.get(plugin.id(), dict())
            if plugin.id() == "apt":
                plugin_want.update({k: k for k in plugin.base_want()})
            add[plugin.id()] = [plugin_want[p] for p in plugin_want.keys() - installed]
            remove[plugin.id()] = installed - plugin_want.keys()

        for k, v in list(remove.items()):
            remove[k] = list(v)

        print(
            "\nPlan: Adding--\n{}".format(luxem.dumps(add, pretty=True).decode("utf-8"))
        )
        print(
            "\nPlan: Removing--\n{}".format(
                luxem.dumps(remove, pretty=True).decode("utf-8")
            )
        )
        if not args.dry_run:
            for plugin in plugins:
                print(f"Installing packages for {plugin.id()}...")
                plugin_add = add.get(plugin.id(), [])
                if plugin_add:
                    plugin.install(plugin_add)
                print(f"Removing packages for {plugin.id()}...")
                plugin_remove = remove.get(plugin.id(), [])
                if plugin_remove:
                    plugin.uninstall(plugin_remove)

            if not add:
                print("No packages to install.")
            if not remove:
                print("No packages to remove.")

            print("Done")
