"""NanamiLang Base Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from nanamilang.shortcuts import \
    ASSERT_IS_CHILD_OF, \
    ASSERT_COLLECTION_NOT_EMPTY, \
    ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF, \
    ASSERT_COLL_LENGTH_IS_EVEN, ASSERT_DICT_CONTAINS_KEYS


class Base:
    """NanamiLang Base Data Type Class"""

    _hashed: int
    name: str = 'Base'
    _expected_type = None
    _python_reference = None

    def __init__(self, reference) -> None:
        """NanamiLang Base DataType, initialize new instance"""

        ASSERT_IS_CHILD_OF(
            reference,
            self._expected_type,
            f'{self.name}: {self._expected_type} was expected!'
        )

        self._set_hash(reference)

        self._additional_assertions_on_init(reference)

        self._python_reference = reference

    def to_py_str(self) -> str:
        """NanamiLang Base Data Type, to Python3 str"""

        return self.format()  # by default, uses format()

    def instance(self) -> 'Base':
        """NanamiLang Base Data Type, instance() virtual"""

        raise NotImplementedError  # <- means: 'virtual method'

    def _set_hash(self, reference) -> None:
        """NanamiLang Base Data Type, default implementation"""

        self._hashed = hash(reference) + id(self.__class__)   #

        # Thus, we try to get a unique hash value per data type

    def _additional_assertions_on_init(self,
                                       reference) -> None:
        """NanamiLang Base Data Type, default implementation"""

        # By default, there are no additional assertions to run

    def hashed(self) -> int:
        """NanamiLang Base Data Type, default implementation"""

        return self._hashed

    def truthy(self) -> bool:
        """NanamiLang Base Data Type, default implementation"""

        # If not overridden in derived class
        # let Python3 make a right choice about reference truthy
        return bool(self.reference())  # by casting it to a bool

    def _init_assert_reference_has_keys(self,
                                        reference: dict,
                                        keys: set) -> None:
        """NanamiLang Base Data Type, "ref" has required keys"""

        ASSERT_DICT_CONTAINS_KEYS(
            reference, keys,
            f'{self.name}: "ref" has no required <{keys}> keys')

    def _init_assert_ref_could_not_be_empty(self,
                                            reference) -> None:
        """NanamiLang Base Data Type, ref could not be empty"""

        ASSERT_COLLECTION_NOT_EMPTY(
            reference, f'{self.name}: "ref" could not be empty')

    def _init_assert_ref_length_must_be_even(self,
                                             reference) -> None:
        """NanamiLang Base Data Type, ref length must be even"""

        ASSERT_COLL_LENGTH_IS_EVEN(
            reference, f'{self.name}: "ref" length must be even')

    def _init_assert_only_base(self, reference) -> None:
        """NanamiLang Base Data Type, it only contains base types"""

        ASSERT_EVERY_COLLECTION_ITEM_IS_CHILD_OF(
            reference,
            Base,
            f'{self.name}: can only contain Nanamilang Data Types!')

    def reference(self):
        """NanamiLang Base Data Type, self._python_reference getter"""

        return self._python_reference

    def origin(self) -> (str or None):
        """NanamiLang Base Data Type, children may have this method"""

        # But default implementation is to return a Python 3 NoneType.

    def format(self, **_) -> str:
        """NanamiLang Base Data Type, format() default implementation"""

        return f'{self._python_reference}'  # <- cast any type to string

    def __str__(self) -> str:
        """NanamiLang Base Data Type, __str__() method implementation"""

        return f'<{self.name}>: {self.format()}'  # <- i.e.: <Base>: foo

    def __repr__(self) -> str:
        """NanamiLang Base Data Type, __repr__() method implementation"""

        return self.__str__()  # <- use the 'self.__str__()' method above
