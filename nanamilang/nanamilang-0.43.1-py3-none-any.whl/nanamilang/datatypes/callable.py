"""NanamiLang Callable Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from ._exports import export
from .base import Base
from .type import Type
from .string import String
from .vector import Vector
from .hashmap import HashMap


class Callable(Base):
    """NanamiLang Callable Data Type Class"""

    name = 'Callable'
    _expected_type = dict
    _python_reference: dict

    @export()
    def meta(self) -> HashMap:
        """NanamiLang Callable, meta() method implementation"""

        _meta_ = getattr(self.reference(), 'meta', None)

        if not _meta_:
            return HashMap(tuple())  # <-- return empty hashmap

        _forms_ = tuple(String(_) for _ in _meta_.get('forms'))

        return HashMap(
            (String('forms'), Vector(_forms_),
             String('kind'), String(_meta_.get('kind')),
             String('name'), String(_meta_.get('name')),
             String('docstring'), String(_meta_.get('docstring'))))

    def call(self, args: list) -> Base:
        """NanamiLang Callable, call() method implementation"""

        return self.reference()(args)

    def origin(self) -> str:
        """NanamiLang Callable, origin() method implementation"""

        return self.format()

    def truthy(self) -> bool:
        """NanamiLang Callable, truthy() method implementation"""

        return True

    @export()
    def instance(self) -> Type:
        """NanamiLang Callable, instance() method implementation"""

        return Type(self.name)  # <-------------- Function or Macro

    # We redefine truthy() method to always return True for Callable
