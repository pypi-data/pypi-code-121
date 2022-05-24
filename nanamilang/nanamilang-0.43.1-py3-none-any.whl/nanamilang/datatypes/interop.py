"""NanamiLang Python 3 Interop Classes"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang import shortcuts
from ._exports import export
from .base import Base
from .type import Type
from .nil import Nil
from .boolean import Boolean
from .string import String
from .floatnumber import FloatNumber
from .integernumber import IntegerNumber
from .keyword import Keyword
from .hashset import HashSet
from .vector import Vector
from .hashmap import HashMap
from .function import Function
from .symbol import Symbol
from .collection import Collection


class Py3Inst(Base):
    """NanamiLang Python 3 object type"""

    name = 'Py3Inst'
    _expected_type = object
    _python_reference = object
    _object_name: str
    purpose = 'Encapsulate Python 3 object'

    def __init__(self, reference) -> None:
        """Initialize new NanamiLang Py3Inst instance"""

        self._object_name = reference.__class__.__name__

        super().__init__(reference)

    def _set_hash(self, reference) -> None:
        """NanamiLang Py3Inst, overrides self._set_hash"""

        hashed = getattr(reference, 'hashed', None)
        self._hashed = (
            hashed() if hashed else hash(reference.__class__))

        # NOTE: comparing two instances of the same class will
        #       always return true
        # NOTE: also, it's not reasonable to use the instances
        #       in Hash* structs as their hashes aren't unique
        # NOTE: so Py3Object can be equal to Py3Inst sometimes
        #       ,and you need to check (.instance) of instance

        # In order to be compatible with the other data types.

    def get(self,
            symbol: Keyword, default=None
            ) -> ('Py3Inst' or 'Py3Object' or Nil):
        """NanamiLang Py3Inst, returns Py3Inst or Py3Object"""

        if not default:
            default = Nil('nil')

        shortcuts.ASSERT_IS_CHILD_OF(
            symbol,
            Keyword,
            message='Py3Inst.get: symbol name is not a Keyword'
        )

        name = shortcuts.demangle(symbol.reference())

        attribute = getattr(self.reference(), name, None)

        # For now, we implicitly dispatch Py3Inst & Py3Object
        # depending on existence of the '__call__()' attribute

        return (Py3Object(attribute)
                if hasattr(attribute, '__call__')
                else Py3Inst(attribute)) if attribute else default

    def format(self, **_) -> str:
        """NanamiLang Py3Inst, 'format()' method implementation"""

        return f'<{self._object_name}>'

    @export()
    def instance(self) -> Type:
        """NanamiLang Py3Inst, 'instance()' method implementation"""

        return Type(Type.Py3Inst)

    @export()
    def cast(self, to: Keyword) -> Base:
        """NanamiLang Py3Inst, cast Py3Inst tp NanamiLang data type"""

        # As for now, we only support simple data types to cast into

        shortcuts.ASSERT_IS_CHILD_OF(
            to,
            Keyword,
            message='Py3Inst.cast: type name to cast to is not a Keyword'
        )

        conv = lambda: self.reference().decode('utf-8') \
            if isinstance(self.reference(), bytes) else str(self.reference())

        if to.reference() == 'to-auto':
            if isinstance(self.reference(), (str,
                                             bytes)):
                return String(conv())
            if isinstance(self.reference(), bool):
                return Boolean(self.reference())
            if isinstance(self.reference(), float):
                return FloatNumber(self.reference())
            if isinstance(self.reference(), int):
                return IntegerNumber(self.reference())
            return Nil('nil')  # return nil instead of AssertionError raising
        if to.reference() == 'to-string':
            return String(conv())
        if to.reference() == 'to-symbol':
            return Symbol(conv())
        if to.reference() == 'to-keyword':
            return Keyword(conv())
        if to.reference() == 'to-boolean':
            return Boolean(bool(self.reference()))
        if to.reference() == 'to-float-number':
            return FloatNumber(float(self.reference()))
        if to.reference() == 'to-integer-number':
            return IntegerNumber(int(self.reference()))
        # Should only be used when Py3Inst holds 'datatypes.*'
        # For instance, 'eval' function from standard library could use this.
        if (to.reference() == 'to-encapsulated' and
                issubclass(self.reference().__class__, (Base,))):
            return self.reference()  # thus, only return if a valid data type

        raise AssertionError('Py3Inst.cast: could not cast self.reference()')


class Py3Object(Base):
    """NanamiLang Python 3 object instance type"""

    name = 'Py3Object'
    _expected_type = object
    _python_reference = object
    _object_name: str
    purpose = 'Encapsulate Python 3 object instance'

    def __init__(self, reference) -> None:
        """Initialize new NanamiLang Py3Object instance"""

        self._object_name = reference.__name__

        super().__init__(reference)

    @export()
    def function(self) -> Function:
        """NanamiLang Py3Object, converts to a Function"""

        return Function({
            'function_name': self._object_name,
            'function_reference':
                lambda _: self.instantiate(Vector(tuple(_)))
        })

    def _set_hash(self, reference) -> None:
        """NanamiLang Py3Object, overrides self._set_hash"""

        hashed = getattr(reference, 'hashed', None)
        self._hashed = hashed() if hashed else hash(reference)

        # In order to be compatible with the other data types.

    def get(self,
            symbol: Keyword, default=None
            ) -> ('Py3Inst' or 'Py3Object' or Nil):
        """NanamiLang Py3Object, returns Py3Inst or Py3Object"""

        if not default:
            default = Nil('nil')

        shortcuts.ASSERT_IS_CHILD_OF(
            symbol,
            Keyword,
            message='Py3Object.get: symbol name is not a Keyword'
        )

        name = shortcuts.demangle(symbol.reference())

        attribute = getattr(self.reference(), name, None)

        # For now, we implicitly dispatch Py3Inst & Py3Object
        # depending on existence of the '__call__()' attribute

        return (Py3Object(attribute)
                if hasattr(attribute, '__call__')
                else Py3Inst(attribute)) if attribute else default

    def format(self, **_) -> str:
        """NanamiLang Py3Object, 'format()' method implementation"""

        return f'<{self._object_name}>'

    @export()
    def instance(self) -> Type:
        """NanamiLang Py3Object, 'instance()' method implementation"""

        return Type(Type.Py3Object)

    @staticmethod
    def coll2tuple(collection: HashSet or Vector) -> tuple:
        """NanamiLang Py3Object, convert 'HashSet/Vector' to 'tuple'."""

        def recursively(data_type):
            if isinstance(data_type, (Vector, HashSet)):
                return [recursively(item) for item in data_type.items()]
            return data_type.reference()

        return tuple((recursively(item) for item in collection.items()))

    def call(self, args: list) -> 'Py3Inst' or 'Py3Object':
        """Nanamilang Py4Object, 'call()' method implementation"""

        return self.function().call(args)

    @export()
    def instantiate(self, args: Vector) -> Py3Inst:
        """NanamiLang Py3Object, 'instantiate()' method implementation"""

        shortcuts.ASSERT_IS_CHILD_OF(
            args,
            Vector,
            message='Py3Object.instantiate: Vector of the arguments was expected'
        )

        _args = []
        _kwargs = {}

        for idx, arg in enumerate(args.items()):

            if issubclass(arg.__class__, (Collection,)):
                if isinstance(arg, HashSet):
                    _args.append(set(Py3Object.coll2tuple(arg)))
                    continue # <--- explicitly continue for-cycle to prevent bugs
                if isinstance(arg, Vector):
                    _args.append(list(Py3Object.coll2tuple(arg)))
                    continue # <--- explicitly continue for-cycle to prevent bugs
                if isinstance(arg, HashMap):
                    assert len(args.items()) - idx == 1, (
                        'Py3Object.instantiate(): HashMap should be last argument'
                    )
                    for k, v in arg.reference().values():
                        assert isinstance(k, (String, Keyword)), (
                            'Py3Object.instantiate(): the key should be a Keyword'
                        )
                        assert not isinstance(v, HashMap), (
                            'Py3Object.instantiate(): HashMaps are not supported!'
                        )
                        col = Py3Object.coll2tuple(v)
                        if isinstance(v, HashSet):
                            _kwargs[shortcuts.demangle(k.reference())] = set(col)
                        if isinstance(v, Vector):
                            _kwargs[shortcuts.demangle(k.reference())] = list(col)
                    break  # <----- prevent from adding HashMap to positional args

            _args.append(arg.reference())  # <---- add positional method arguments

        return Py3Inst(self.reference()(*_args, **_kwargs))  # <---- invoke method
