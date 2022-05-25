import inspect
import sys
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
from importlib.metadata import entry_points
from importlib.util import find_spec


class ProxyLoader(Loader):
    def __init__(self, fullname, loader):
        self._fullname = fullname
        self._loader = loader

    def create_module(self, spec):
        return self._loader.create_module(spec)

    def exec_module(self, mod):
        sys.modules[self._fullname] = mod
        return self._loader.exec_module(mod)


class NoopLoader(Loader):
    def __init__(self, mod):
        self._mod = mod

    def create_module(self, spec):
        return self._mod

    def exec_module(self, mod):
        pass


class ModuleLoader(MetaPathFinder):
    def __init__(self, ep_name: str):
        caller = inspect.currentframe().f_back
        self._module_name = caller.f_globals['__name__']

        self._redirects = {
            f'{self._module_name}.{ep.name}': ep.value
            for ep in entry_points().get(ep_name, [])
        }

    # noinspection PyUnusedLocal
    def find_spec(self, fullname, path, target=None):
        target = self._redirects.get(fullname)
        if target:
            mod = sys.modules.get(target)
            if mod is None:
                spec = find_spec(target)
                spec.loader = ProxyLoader(fullname, spec.loader)
                return spec
            else:
                return ModuleSpec(fullname, NoopLoader(mod))
        elif fullname.startswith(self._module_name):
            raise ImportError(
                f'Cannot import {fullname} - is {fullname[len(__name__) + 1:]} a valid and installed?'
            )

    @classmethod
    def uninstall(cls):
        if sys.meta_path:
            for i in range(len(sys.meta_path) - 1, -1, -1):
                if type(sys.meta_path[i]).__name__ == cls.__name__:
                    del sys.meta_path[i]

    def install(self):
        self.uninstall()
        sys.meta_path.append(self)
