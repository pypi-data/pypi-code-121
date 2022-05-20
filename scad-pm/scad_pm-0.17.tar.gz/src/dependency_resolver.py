import logging
import os

from scopeton.decorators import Inject
from scopeton.scope import Scope

import config
import dep_util
import git_util


class DependencyResolver:
    @Inject()
    def __init__(self, scope: Scope, conf: config.ArgsConfig, parser: config.MainConfigParser,
                 fetcher: git_util.GitFetcher, dep_util: dep_util.DepUtil):
        self.conf = conf
        self.parser = parser
        self.scope = scope
        self.fetcher = fetcher
        self.dep_util = dep_util

    def _check_type(self, path: str, file: str):
        if os.path.exists(os.path.join(path, file)):
            return file
        else:
            return None

    def _resolve_file_name(self, path: str, *args):
        for k in args:
            logging.info("trying: {} with {}".format(path, k))
            res = self._check_type(path, k)
            if res:
                return res

    def _do_resolve_deps(self, dep_config: config.FileConfig):
        logging.info("resolving dependencies: {}".format(dep_config))
        for dep in dep_config.dependencies:
            self._resolve_dep(dep_config, dep)

    def _resolve_dep(self, dep_config: config.FileConfig, dep: config.Dependency):
        logging.info("Resolving dependency: {}".format(dep))
        self.fetcher.fetch(dep_config, dep)
        file = self._resolve_file_name(self.dep_util.resolve_full_dir(dep_config, dep), "scad_pm.yaml", "scad.pm")
        if file:
            self.run(self.dep_util.resolve_full_dir(dep_config, dep), file)

    def run(self, path, file=None):
        logging.info("Running with path: {} and file: {}".format(path, file))
        if file is None:
            file = self._resolve_file_name(path, "scad_pm.yaml", "scad.pm")
        parsed = self.parser.parse(os.path.join(path, file))
        parsed.dep_path = path
        self._do_resolve_deps(parsed)
