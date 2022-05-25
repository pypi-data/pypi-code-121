from typing import Iterator, Mapping, TypeVar

from .vm_instance_proxy import RemoteShellProxy, VmInstanceProxy

Instance = TypeVar("Instance", VmInstanceProxy, RemoteShellProxy)


class VmInstanceMappingBase(Mapping[str, Instance]):
    # pytype: disable=bad-return-type
    def __getitem__(self, name: str) -> Instance:
        ...

    # pytype: disable=bad-return-type
    def __iter__(self) -> Iterator:
        ...

    # pytype: disable=bad-return-type
    def __len__(self) -> int:
        ...
