""" Global hash-based addresses and a supporting class.

PHashAddress: a base class for hierarchy of addresses.
It supports two-part addressed, containing a human-readable prefix
and a hash ID.

PValueAddress (inherited from PHashAddress): an address of an immutable value.

PFuncSnapshotAddress (inherited from PHashAddress): an address of
a function snapshot (version).

PFuncOutputAddress (inherited from PHashAddress): an address of
a function execution result.

KwArgsDict (inherited from dict): s class that encapsulates
keyword arguments for a function call.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import sys
from typing import Any, Callable
from joblib.hashing import NumpyHasher, Hasher

from pythagoras.global_objects import safe_chars
from pythagoras.utils import get_long_infoname, buid_context, replace_unsafe_chars
from pythagoras._dependency_discovery import _all_dependencies_one_func


class PHashAddress(ABC):
    """A globally unique address, includes a human-readable prefix and a hash."""

    prefix: str
    hash_id: str
    _hash_type: str = "sha256"

    @staticmethod
    def _build_prefix(x: Any) -> str:
        """Create a short human-readable summary of an object."""

        prfx = get_long_infoname(x)

        if (hasattr(x, "shape")
                and hasattr(x.shape, "__iter__")
                and callable(x.shape.__iter__)
                and not callable(x.shape)):

            prfx += "_shape_"
            for n in x.shape:
                prfx += str(n) + "_x_"
            prfx = prfx[:-3]

        elif (hasattr(x, "__len__")
              and callable(x.__len__)):
            prfx += "_len_" + str(len(x))

        clean_prfx = replace_unsafe_chars(prfx, "_")

        return clean_prfx

    @staticmethod
    def _build_hash_id(x: Any) -> str:
        """Create a URL-safe hashdigest for an object."""

        if 'numpy' in sys.modules:
            hasher = NumpyHasher(hash_name=PHashAddress._hash_type)
        else:
            hasher = Hasher(hash_name=PHashAddress._hash_type)
        return hasher.hash(x) #TODO: switch to Base32


    def __iter__(self):
        """An iterator allows converting address into a sequence of strings.

        It enables automatic conversion into SimpleDictKey, hence
        PHashAddress can be used as a key for SimplePersistentDict objects.
        """
        def step() -> str:
            yield self.prefix
            yield self.hash_id

        return step()

    def __eq__(self, other) -> bool:
        """Return self==other. """
        return ( isinstance(other, self.__class__)
                and self.prefix  == other.prefix
                and self.hash_id == other.hash_id )

    def __ne__(self, other) -> bool:
        """Return self!=other. """
        return not self.__eq__(other)

    def __len__(self) -> int:
        """Return len(self), always equals to 2. """
        return 2

    @abstractmethod
    def __repr__(self):
        raise NotImplementedError


class PValueAddress(PHashAddress):
    """A globally unique address of an immutable value: a prefix + a hash code.

    PValueAddress is a universal global identifier of any (constant) value.
    Using only the value's hash should (theoretically) be enough to
    uniquely address all possible data objects that the humanity  will create
    in the foreseeable future (see, for example ipfs.io).

    However, an address also includes a prefix. It makes it more easy
    for humans to interpret an address, and further decreases collision risk.
    """

    def __init__(self, x: Any):
        if isinstance(x, PValueAddress):
            self.prefix = x.prefix
            self.hash_id = x.hash_id
        else:
            assert not isinstance(x,PHashAddress), (
                "PValueAddress is the only PHashAddress which is allowed "
                +"to be converted to PValueAddress")
            self.prefix = self._build_prefix(x)
            self.hash_id = self._build_hash_id(x)

    def __repr__(self):
        return f"PHashAddress( prefix={self.prefix} , hash_id={self.hash_id} )"


class PFuncSnapshotAddress(PHashAddress):
    """ Globally unique address of a function snapshot (version).

        PFuncSnapshotAddress is a universal global identifier of a function.
        It contains a hash value for the cloudized function's source code,
        combined with the source code of all other cloudized functions that
        the function is using, as well as its "requires" list
        (a list of required modules with their versions).
        A change in the source code, or a change in the "requires" list
        results in the creation of a new hash, hence, a new address.

        An address also includes a prefix, which makes it more simple
        for humans to interpret an address,
        and further decreases collision risk.

        For the sake of debuggability,
        the first time a new PFuncSnapshotAddress is created,
        it writes a new entry to P_Cloud.function_snapshots store,
        which serves as a journal that records details of
        all PFuncSnapshotAddress-s.
        """

    def __init__(self, f:Callable):
        """Create an address of a cloudized function's snapshot.

        Actual calculation happens only the first time the constructor
        is called. Then the address is stored in the .func_snapshot_address
        attribute of the cloudized function.
        """
        assert callable(f)
        assert hasattr(f,"p_cloud")
        assert hasattr(f,"__wrapped__")
        assert f.__name__ in f.p_cloud.cloudized_functions
        if hasattr(f,"func_snapshot_address"):
            self.prefix = f.func_snapshot_address.prefix
            self.hash_id = f.func_snapshot_address.hash_id
            return
        cloud = f.p_cloud
        self.prefix = self._build_prefix(f)

        dependencies = _all_dependencies_one_func(
            f.__name__, f.p_cloud.cloudized_functions)
        dependencies = sorted(dependencies)
        f.original_source_with_dependencies = ""

        for f_depend in dependencies:
            f.original_source_with_dependencies += (
                    cloud.cloudized_functions[f_depend].original_source+"\n\n")

        self.hash_id = self._build_hash_id(
            (cloud.install_requires, cloud.python_requires
             , f.original_source_with_dependencies))
        f.func_snapshot_address = self
        if not self in cloud.func_snapshots:
            new_snapshot = dict(
                install_requires = cloud.install_requires
                , python_requires = cloud.python_requires
                , source = f.original_source
                , source_with_dependencies = f.original_source_with_dependencies
                , first_use_context = buid_context(
                    cloud.base_dir, cloud.baseline_timezone)
                )
            cloud.func_snapshots[self] = new_snapshot

    def __repr__(self):
        return (f"PFuncSnapshotAddress( prefix={self.prefix} ,"
               + f" hash_id={self.hash_id} )")


class KwArgsDict(dict):
    """ A class that encapsulates keyword arguments for a function call."""

    def __init__(self,*args, **kargs): # TODO: check if we need *args here
        super().__init__(*args, **kargs)

    def pack(self, *, cloud) -> KwArgsDict:
        """ Replace values in a dict with their hash addresses.

        This function also "normalizes" the dictionary by sorting keys
        in order to always get the same hash values
        for the same lists of arguments.
        """
        packed_copy = KwArgsDict()
        for k in sorted(self.keys()):
            value = self[k]
            if isinstance(value,PValueAddress):
                packed_copy[k] = value
            else:
                key = PValueAddress(value)
                packed_copy[k] = key
                if key not in cloud.value_store:
                    cloud.value_store[key] = value
        return packed_copy

    def unpack(self,*,cloud) -> KwArgsDict:
        """ Restore values based on their hash addresses."""
        unpacked_copy = KwArgsDict()
        for k,v in self.items():
            if isinstance(v, PValueAddress):
                unpacked_copy[k] = cloud.value_store[v]
            else:
                unpacked_copy[k] = v
        return unpacked_copy


class PFuncOutputAddress(PHashAddress):
    """A globally unique address of a function execution result.

    PFuncOutputAddress is a universal global identifier of a value,
    which was (or will be) an output of a cloudized function execution.
    Assuming a function is pure, we only need function's PFuncSnapshotAddress
    and arguments' values to build a "signature",
    which serves as a unique key for the output object.
    The hash component of an address is a hash of this unique key.

    An address also includes a prefix, which makes it easy for humans
    to interpret the address, and further decreases collision risk.
    """

    def __init__(self, f:Callable, arguments:KwArgsDict):
        f_base_address =  PFuncSnapshotAddress(f)
        assert isinstance(arguments, KwArgsDict)
        self.prefix = f_base_address.prefix
        self.hash_id = self._build_hash_id(
            (f_base_address.hash_id, arguments.pack(cloud=f.p_cloud)))

    def __repr__(self):
        return (f"PFuncOutputAddress( prefix={self.prefix} ,"
               + f" hash_id={self.hash_id} )")