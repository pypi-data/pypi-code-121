"""NanamiLang Meta Type Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from ._exports import export
from .base import Base


class Type(Base):
    """NanamiLang Meta Type"""

    name: str = 'Type'
    _expected_type = str
    _python_reference: str
    purpose = 'NanamiLang Meta Type'

    MetaType = 'MetaType'
    Nil = 'Nil'
    Boolean = 'Boolean'
    String = "String"
    Date = 'Date'
    FloatNumber = 'FloatNumber'
    IntegerNumber = 'IntegerNumber'
    Keyword = 'Keyword'
    HashSet = 'HashSet'
    Vector = 'Vector'
    HashMap = 'Hashmap'
    NException = 'NException'
    Undefined = 'Undefined'
    Macro = 'Macro'
    Function = 'Function'
    Symbol = 'Symbol'
    Py3Object = 'Py3Object'
    Py3Inst = 'Py3Inst'
    Character = 'Character'
    Atom = 'Atom'

    names = [MetaType, Nil, Boolean, String,
             Date, FloatNumber, IntegerNumber,
             Keyword, HashSet, Vector, HashMap,
             NException, Undefined, Macro,
             Function, Symbol, Py3Object, Py3Inst,
             Character, Atom]

    @staticmethod
    def resolve(name: str) -> 'Type' or None:
        """NanamiLang Type, resolve() custom method"""

        return Type(name) if name in Type.names else None

    def origin(self) -> str:
        """NanamiLang Type, origin() method implementation"""

        return 'MetaType'

    @export()
    def instance(self) -> Base:
        """NanamiLang Type, instance() method implementation"""

        return Type(Type.MetaType)

    def reference(self) -> None:
        """NanamiLang Type, reference() method implementation"""

        return None

    # We redefine self.reference() method to return Python 3 NoneType
