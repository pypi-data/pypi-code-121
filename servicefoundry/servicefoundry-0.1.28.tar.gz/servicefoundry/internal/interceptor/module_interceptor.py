import sys
from importlib.abc import MetaPathFinder

import pkg_resources


class FinderInterceptor(MetaPathFinder):
    def __init__(self):
        super().__init__()
        self.modules = set()

    def find_spec(self, fullname, path, target=None):
        if path is None:
            self.modules.add(fullname)
        return None

    def get_modules(self):
        return self.modules


class ModuleInterceptor:
    def __init__(self):
        self.interceptor = FinderInterceptor()
        sys.meta_path.insert(0, self.interceptor)

    def get_dependencies(self):
        dependencies = {}
        intercepted_modules = self.interceptor.get_modules()
        for module in pkg_resources.working_set:
            if module.key in intercepted_modules:
                dependencies[module.key] = module.version
        return dependencies
