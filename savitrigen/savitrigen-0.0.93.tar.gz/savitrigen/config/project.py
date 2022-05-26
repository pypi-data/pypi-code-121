from dataclasses import dataclass, field
from .backend import BackendConfig
from .frontend import FrontendConfig

from savitrigen.guideline import check_plugin_naming

@dataclass
class Product(object):
    name:str
    group:str

@dataclass
class Meta(object):
    version:str
    alias:str
    product:Product
    _product:Product = field(init=False, repr=False)

    @property
    def product(self) -> Product:
        return self._product

    @product.setter
    def product(self, value:dict) -> None:
        self._product = Product(**value)


@dataclass
class ProjectConfig(object):
    meta:dict
    _meta:dict = field(init=False, repr=False)
    plugins:list[str]
    _plugins:list[str] = field(init=False, repr=False)

    backend:BackendConfig = None
    frontend:FrontendConfig = None

    @property
    def meta(self) -> Meta:
        return self._meta

    @meta.setter
    def meta(self, value:dict) -> None:
        self._meta = Meta(**value)

    @property
    def plugins(self) -> list[str]:
        return self._plugins

    @plugins.setter
    def plugins(self, plugins:list[str]) -> None:
        if not isinstance(plugins, list):
            self._plugins = []
            return

        for p in plugins:
            check_plugin_naming(p)

        self._plugins = plugins
