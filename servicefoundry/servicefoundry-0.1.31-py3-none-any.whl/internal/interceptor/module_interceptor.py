import importlib
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


def get_version_from_attr(module_name):
    try:
        module = importlib.import_module(module_name)
        return module.__version__
    except:
        return None


class ModuleInterceptor:
    def __init__(self):
        self.interceptor = FinderInterceptor()
        sys.meta_path.insert(0, self.interceptor)

    def get_dependencies(self):
        dependencies = {}
        intercepted_modules = self.interceptor.get_modules()
        for module in pkg_resources.working_set:
            module_name = module.key
            if module_name in intercepted_modules:
                dependencies[module_name] = module.version
                # version = get_version_from_attr(module_name)
                # if version is None:
                #     dependencies[module_name] = module.version
                # else:
                #     dependencies[module_name] = version
        return dependencies
