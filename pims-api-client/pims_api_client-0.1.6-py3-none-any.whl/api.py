from .configurator import Configurator
from .methods.attributes import AttributeMethodsExecutor
from .methods.products import ProductsMethodsExecutor


class Api:
    def __init__(self, configurator: Configurator):
        self.configurator = configurator

    @property
    def attributes(self) -> AttributeMethodsExecutor:
        return AttributeMethodsExecutor(self.configurator)

    @property
    def products(self) -> ProductsMethodsExecutor:
        return ProductsMethodsExecutor(self.configurator)