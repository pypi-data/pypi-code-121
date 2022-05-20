import logging
import os

from scopeton.decorators import Inject

import config
import dep_util
import proc_util


class GitFetcher:
    @Inject()
    def __init__(self, conf: config.ArgsConfig, dep_util: dep_util.DepUtil):
        self.conf = conf
        self.dep_util = dep_util
    def _resolve_lib_path(self, dep_config: config.FileConfig, dep: config.Dependency):
        return os.path.join(dep_config.dep_path or "", self.conf.lib_path)

    def fetch(self, dep_config: config.FileConfig, dep: config.Dependency):
        if not os.path.exists(self._resolve_lib_path(dep_config, dep)):
            os.mkdir(self._resolve_lib_path(dep_config, dep))
        logging.info("Full dir: {}".format(self.dep_util.resolve_full_dir(dep_config, dep)))
        if not os.path.exists(self.dep_util.resolve_full_dir(dep_config, dep)):
            self.download_dep(dep_config, dep)
        else:
            self.update_dep(dep_config, dep)

    def update_dep(self, dep_config: config.FileConfig, dep: config.Dependency):
        if not self.conf.upgrade:
            self.goto_revision(dep_config, dep)
            logging.info("skipping upgrade, see --upgrade, for package: {}".format(dep))
            return
        logging.info("Updating dep: {}".format(dep))
        proc_util.call(self.dep_util.resolve_full_dir(dep_config, dep), ["git", "pull"])
        self.goto_revision(dep_config, dep)

    def download_dep(self, dep_config: config.FileConfig, dep: config.Dependency):
        logging.info("Downloading dep: {}".format(dep))
        proc_util.call(self._resolve_lib_path(dep_config, dep), ["git", "clone", dep.url])
        self.goto_revision(dep_config, dep)

    def goto_revision(self, dep_config: config.FileConfig, dep: config.Dependency):
        if dep.revision is not None:
            logging.info("Checking out the revision: {}".format(dep.revision))
            proc_util.call(self.dep_util.resolve_full_dir(dep_config, dep), ["git", "checkout", dep.revision])


