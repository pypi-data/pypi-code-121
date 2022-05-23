"""Yea test class."""

import configparser
import functools
import itertools
import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

import requests

from yea import context, testcfg, testspec


def run_command(
    cmd_list: List[str],
    timeout: int = 300,
    env: Mapping = os.environ,
) -> int:
    print("INFO: RUNNING=", cmd_list)
    p = subprocess.Popen(cmd_list, env=env)
    try:
        p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("ERROR: TIMEOUT")
        p.kill()
        try:
            p.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            print("ERROR: double timeout")
            sys.exit(1)
    print("INFO: exit=", p.returncode)
    return p.returncode


def download(url: str, fname: str) -> bool:
    err: bool = False
    print(f"INFO: grabbing {fname} from {url}")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(fname, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
    except requests.exceptions.HTTPError as e:
        print("ERROR: url download error", url, e)
        err = True
    return err


def get_config(config: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """
    Recursively parse a "flat" config with column-separated key name definitions
    into a nested dictionary given a prefix.

    Example:
        config = {
            ":rug:ties_room_together": True,
            ":wandb:mock_server:lol": True,
            ":wandb:mock_server:lmao": False,
            ":wandb:mock_server:resistance:object": "Borg",
            ":wandb:mock_server:resistance:is_futile": True,
            ":wandb:foo": "bar",
        }
        prefix = ":wandb:"
        get_config(config, prefix)
        # {
        #     "mock_server": {
        #         "lol": True,
        #         "lmao": False,
        #         "resistance": {
        #             "object": "Borg",
        #             "is_futile": True,
        #         },
        #     },
        #     "foo": "bar",
        # }

    """
    # recursively get config values
    def parse(key: str, value: Any) -> Dict[str, Any]:
        if ":" not in key:
            return {key: value}
        else:
            key, subkey = key.split(":", 1)
            return {key: parse(subkey, value)}

    # recursively merge configs
    def merge(source: Dict[str, Any], destination: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                merge(value, node)
            else:
                destination[key] = value
        return destination

    prefixed_items = {k[len(prefix) :]: v for (k, v) in config.items() if k.startswith(prefix)}
    parsed_items = []
    for k, v in prefixed_items.items():
        parsed_items.append(parse(k, v))

    return functools.reduce(merge, parsed_items) if parsed_items else {}


class YeaTest:
    def __init__(self, *, tname: pathlib.Path, yc: "context.YeaContext") -> None:
        self._tname = tname
        self._yc = yc
        self._args = yc._args
        self._retcode: int
        self._test_cfg: testcfg.TestlibConfig
        self._covrc: Optional[pathlib.Path] = None
        self._time_start: Optional[Union[int, float]] = None
        self._time_end: Optional[Union[int, float]] = None
        self._permute_groups: Optional[List[Any]] = None
        self._permute_items: Optional[Tuple[Any, ...]] = None

    def __str__(self) -> str:
        return f"{self._tname}"

    def _depend_files(self) -> bool:
        err = False
        dep = self._test_cfg.get("depend", {})
        files = dep.get("files", [])
        for fdict in files:
            fn = fdict["file"]
            fs = fdict["source"]
            assert fs.startswith("http"), "only http schemes supported right now"
            err = err or download(fs, fn)
        return err

    def _depend_install(self) -> bool:
        err = False
        req_list = self._test_cfg.get("depend", {}).get("requirements", [])
        options = self._test_cfg.get("depend", {}).get("pip_install_options", [])
        timeout = self._test_cfg.get("depend", {}).get("pip_install_timeout")
        if not (req_list or options):
            return err
        if not options:
            options.append("-qq")
        for req in req_list:
            cmd_list = ["python", "-m", "pip", "install"]
            cmd_list.extend(options)
            if " " in req:
                cmd_list.extend(req.split(" "))
            else:
                cmd_list.append(req)
            exit_code = run_command(cmd_list, timeout=timeout)
            err = err or exit_code != 0
            if err:
                return err
        return False

    def _depend_uninstall(self) -> bool:
        err = False
        req = self._test_cfg.get("depend", {}).get("uninstall", [])
        timeout = self._test_cfg.get("depend", {}).get("pip_uninstall_timeout")
        if not req:
            return err
        fname = ".yea-uninstall.txt"
        with open(fname, "w") as f:
            f.writelines(f"{item}\n" for item in req)
        cmd_list = ["python", "-m", "pip", "uninstall", "-qq", "-y", "-r", fname]
        exit_code = run_command(cmd_list, timeout=timeout)
        if os.path.exists(fname):
            os.remove(fname)
        err = err or exit_code != 0
        return err

    def _depend(self) -> bool:
        tname = self._tname
        print("INFO: DEPEND=", tname)
        tpath = pathlib.Path(tname)
        os.chdir(tpath.parent)
        err = False
        err = err or self._depend_uninstall()
        err = err or self._depend_files()
        err = err or self._depend_install()

        return err

    def _run(self) -> None:
        tname = self._tname
        print("INFO: RUN=", tname)
        program = self._test_cfg.get("command", {}).get("program")
        # test execution mode: default (./module/lib.py) or module (python -m module.lib)
        mode = self._test_cfg.get("command", {}).get("mode")
        tpath = pathlib.Path(tname)
        os.chdir(tpath.parent)
        if program is None:
            cmd = [f"./{tpath.name}"]
        elif mode == "module":
            cmd = ["-m", program.split(".py")[0].replace("/", ".")]
        else:
            cmd = [f"./{program}"]
        cmd_list = ["coverage", "run"]
        if self._covrc:
            cmd_list.extend(["--rcfile", str(self._covrc)])
        cmd_list.extend(cmd)
        cmd_cfg = self._test_cfg.get("command", {})
        args = cmd_cfg.get("args", [])
        timeout = cmd_cfg.get("timeout")
        cmd_list.extend(args)
        env = os.environ.copy()
        elist = self._test_cfg.get("env", [])
        for edict in elist:
            env.update(edict)
        if self._permute_groups and self._permute_items:
            env["YEA_PARAM_NAMES"] = ",".join(self._permute_groups)
            env["YEA_PARAM_VALUES"] = ",".join(map(str, self._permute_items))

        plugins = self._test_cfg.get("plugin", [])
        params = (
            {k: v for (k, v) in zip(self._permute_groups, self._permute_items)}
            if self._permute_groups and self._permute_items
            else None
        )
        if plugins:
            for plugin_name in plugins:
                prefix = f":{plugin_name}:"

                if params is not None:
                    # need to configure the plugin?
                    # get the plugin by its name
                    plug = self._yc._plugs.get_plugin(plugin_name)
                    plugin_params = get_config(params, prefix)
                    if plugin_params:
                        plug.monitors_configure(plugin_params)

                # process vars
                penv = plugin_name.upper()
                pnames = []
                pvalues = []
                for items in self._test_cfg.get("var", []):
                    for k, v in items.items():
                        if k.startswith(prefix):
                            pnames.append(k[len(prefix) :])
                            pvalues.append(v)
                if pnames and pvalues:
                    env[f"YEA_PLUGIN_{penv}_NAMES"] = ",".join(pnames)
                    env[f"YEA_PLUGIN_{penv}_VALUES"] = json.dumps(pvalues)
            env["YEA_PLUGINS"] = ",".join(plugins)

        exit_code = run_command(cmd_list, env=env, timeout=timeout)
        self._retcode = exit_code

    def _load(self) -> None:
        spec = None
        # load yea file if exists
        fname = str(self._tname)
        if fname.endswith(".py"):
            yea_name = fname[:-3] + ".yea"
            if os.path.exists(yea_name):
                spec = testspec.load_yaml_from_file(yea_name)
        elif fname.endswith(".yea"):
            spec = testspec.load_yaml_from_file(fname)
        if not spec:
            docstr = testspec.load_docstring(self._tname)
            spec = testspec.load_yaml_from_docstring(docstr)
        # print("SPEC:", self._tname, spec)
        cfg = testcfg.TestlibConfig(spec)
        # print("TESTCFG", cfg)
        self._test_cfg = cfg

    def _prep(self) -> None:
        """Cleanup and/or populate wandb dir."""
        self._yc.test_prep(self)
        # load file and docstring eval criteria
        self._setup_coverage_file()
        self._setup_coverage_config()

    def _setup_coverage_file(self) -> None:
        # dont mess with coverage_file (for now) if already set
        if self._yc._covfile is not None:
            return
        covfname = f".coverage-{self._yc._pid}-{self.test_id}"
        covfile = self._yc._cachedir.joinpath(covfname)
        os.environ["COVERAGE_FILE"] = str(covfile)

    def _setup_coverage_config(self) -> None:
        # do we have a template?
        template = self._yc._cfg._coverage_config_template
        if not template:
            return
        cov_src = self._yc._cfg._coverage_source
        cov_env = self._yc._cfg._coverage_source_env
        if cov_env is not None:
            cov_env_src = os.environ.get(cov_env)
            if cov_env_src:
                cov_src = cov_env_src
        if cov_src is None:
            return

        # find our sources
        #   source is from tox (set in env)
        #   or set from conf (if not in env)
        if self._yc._cfg._cfroot is None:
            raise RuntimeError("_cf_root not set")
        p = self._yc._cfg._cfroot.joinpath(template)
        if not p.exists():
            raise RuntimeError(f"Coverage config template {p} does not exist")

        cf = configparser.ConfigParser()
        cf.read(p)

        cf["run"]["source"] = cov_src

        covrc_fname = f"yea-covrc-{self._yc._pid}-{self.test_id}.conf"
        covrc = self._yc._cachedir.joinpath(covrc_fname)
        with open(covrc, "w") as configfile:
            cf.write(configfile)

        self._covrc = covrc

    def _fin(self) -> None:
        """Reap anything in wandb dir"""
        self._yc.test_done(self)

    def run(self) -> None:
        self._prep()
        if not self._args.dryrun:
            err = self._depend()
            # TODO: record error instead of assert
            assert not err, "Problem getting test dependencies"
            self._time_start = time.time()
            self._run()
            self._time_end = time.time()
        self._fin()

    def get_permutations(self) -> List["YeaTest"]:
        self._load()
        params = self._test_cfg.get("parametrize")
        if not params:
            return [self]
        groups = params.get("permute", [])
        gnames = []
        glist = []
        for g in groups:
            assert isinstance(g, dict)
            assert len(g) == 1
            k = next(iter(g))
            gnames.append(k)
            v = g[k]
            assert isinstance(v, list)
            glist.append(v)
        items = list(itertools.product(*glist))
        r = []
        for tnum, it in enumerate(items):
            t = YeaTest(tname=self._tname, yc=self._yc)
            t._load()
            t._permute_groups = gnames
            t._permute_items = it
            tpname = f"{tnum}-{'-'.join(map(str, it))}"
            tid = t._test_cfg.get("id")
            if tid:
                t._test_cfg["id"] = f"{tid}.{tpname}"
            r.append(t)
        return r

    @property
    def name(self) -> str:
        root = self._yc._cfg._cfroot
        if root is None:
            raise TypeError("Config root not set")
        b = self._tname.relative_to(root)
        return str(b)

    @property
    def test_id(self) -> Optional[str]:
        tid = str(self._test_cfg.get("id", "")) if self._test_cfg else None
        return tid

    @property
    def _sort_key(self) -> str:
        tid = str(self._test_cfg.get("id", "")) if self._test_cfg else ""
        return tid + ":" + self.name

    @property
    def config(self) -> testcfg.TestlibConfig:
        return self._test_cfg
