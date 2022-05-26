import typing

from d3m import deprecate
from d3m.base import primitives
from d3m.primitive_interfaces import base


__all__ = (
    'FileReaderPrimitiveBase',
    'DatasetSplitPrimitiveBase',
    'TabularSplitPrimitiveBase',
)

FileReaderInputs = primitives.FileReaderInputs
FileReaderOutputs = primitives.FileReaderOutputs


class FileReaderHyperparams(primitives.FileReaderHyperparams):
    @deprecate.function(message="use d3m.base.primitives.FileReaderHyperparams class instead")
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)


class FileReaderPrimitiveBase(primitives.FileReaderPrimitiveBase):
    @deprecate.function(message="use d3m.base.primitives.FileReaderPrimitiveBase class instead")
    def __init__(self, *, hyperparams: FileReaderHyperparams) -> None:
        super().__init__(hyperparams=hyperparams)


DatasetSplitInputs = primitives.DatasetSplitInputs
DatasetSplitOutputs = primitives.DatasetSplitOutputs


class DatasetSplitPrimitiveBase(primitives.DatasetSplitPrimitiveBase[base.Params, base.Hyperparams]):
    @deprecate.function(message="use d3m.base.primitives.DatasetSplitPrimitiveBase class instead")
    def __init__(self, *, hyperparams: base.Hyperparams, random_seed: int = 0,
                 docker_containers: typing.Dict[str, base.DockerContainer] = None,
                 volumes: typing.Dict[str, str] = None,
                 temporary_directory: str = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers, volumes=volumes, temporary_directory=temporary_directory)


class TabularSplitPrimitiveParams(primitives.TabularSplitPrimitiveParams):
    @deprecate.function(message="use d3m.base.primitives.TabularSplitPrimitiveParams class instead")
    def __init__(self, other: typing.Dict[str, typing.Any] = None, **values: typing.Any) -> None:
        super().__init__(other, **values)


class TabularSplitPrimitiveBase(primitives.TabularSplitPrimitiveBase[base.Hyperparams]):
    @deprecate.function(message="use d3m.base.primitives.TabularSplitPrimitiveBase class instead")
    def __init__(self, *, hyperparams: base.Hyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed)
