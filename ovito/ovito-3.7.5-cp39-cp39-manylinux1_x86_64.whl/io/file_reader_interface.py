import ovito.io
import ovito.data
import abc
import traits.api

class FileReaderInterface(traits.api.ABCHasStrictTraits):

    # Abstract methods that can be implemented by sub-classes:
    #
    # def detect(self, filename: str) -> bool: ...
    # def scan(self, filename: str, register_frame: Callable[..., None]) -> None: ...

    # Method that must be implemented by sub-classes:
    @abc.abstractmethod
    def parse(self, data: ovito.data.DataCollection, **kwargs):
        raise NotImplementedError

ovito.io.FileReaderInterface = FileReaderInterface