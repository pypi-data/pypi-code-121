import os

import config
from scopeton.decorators import Inject


class DepUtil:
    @Inject()
    def __init__(self, conf: config.ArgsConfig):
        self.conf = conf

    def resolve_full_dir(self, dep_config: config.FileConfig, dep: config.Dependency):
        return os.path.join(dep_config.dep_path, self.conf.lib_path, dep.path)