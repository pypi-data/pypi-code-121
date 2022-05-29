import abc
import os
import shutil

from typing import List, Generator, Tuple

from pydmt.utils.digester import Digester


class Node(abc.ABC):
    """
    This is a source object which knows how to add his checksum to a checksum
    calculation
    """
    @abc.abstractmethod
    def add_to_digester(self, d: Digester) -> None:
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    @abc.abstractmethod
    def remove(self) -> None:
        pass


class Builder(abc.ABC):
    """
    A Builder is what really builds things in the system.
    A builder knows on which inputs it relies and what
    outputs it generates (sometimes before build and sometimes
    after).
    """

    def get_name(self) -> str:
        """
        Override this to get better names
        :return: the name of this builder
        """
        return f"{self.__class__.__name__}"

    @abc.abstractmethod
    def __init__(self):
        """ initialize your builder here """

    @abc.abstractmethod
    def build(self) -> None:
        """
        this method actually does the building
        Just do whatever you want here. Options are:
        - Write pure python code
        - Call native code
        - Call external programs
        - A combination of the above
        If there are any problems then throw an exception.
        Try not to segfault the interpreter in this method...:)
        """

    @abc.abstractmethod
    def get_sources(self) -> List[Node]:
        """
        return the name of the source files for this builder
        If the builder takes a whole folder the list all the filers in that folder.
        If a built takes all the .py files in a folder then list those.
        In the current implementation this method is not really that important because
        it is not used to calculate the signature of the input to the build.
        The @get_signature method is use for that.
        In the future the get_signature method will go away.
        """
    @abc.abstractmethod
    def get_targets(self) -> List[Node]:
        """
        return list of targets
        """

    @abc.abstractmethod
    def yield_results(self) -> Generator[Tuple[str, str], None, None]:
        """
        Return the signatures and names of results
        :return:
        """

    def get_signature(self) -> str:
        """
        return the sha1 of anything that identifies the sources of the build
        Techically this is the sha1 of the file content of the list of files
        returned from :func:`~get_sources`
        """
        d = Digester()
        for source in self.get_sources():
            source.add_to_digester(d)
        return d.get_hexdigest()

    def get_targets_as_string(self) -> str:
        return ",".join([x.get_name() for x in self.get_targets()])


class File(Node):
    """
    This is a node which is a file
    """
    def __init__(self, filename: str):
        self.filename = filename

    def add_to_digester(self, d: Digester) -> None:
        d.add_file(self.filename)

    def get_name(self):
        return self.filename

    def remove(self):
        os.unlink(self.filename)


class SourceFile(File):
    pass


class TargetFile(File):
    pass


class SourceFiles(Node):
    """
    This is a source of many files
    """
    def __init__(self, filenames: List[str], name: str):
        self.filenames = filenames
        self.name = name

    def add_to_digester(self, d: Digester) -> None:
        d.add_files(self.filenames)

    def get_name(self):
        return self.name

    def remove(self):
        for filename in self.filenames:
            os.unlink(filename)


class Folder(Node):
    """
    This is a node representing a single Folder
    """
    def __init__(self, folder: str):
        self.folder = folder

    def add_to_digester(self, d: Digester) -> None:
        d.add_folders(folders=[self.folder])

    def get_name(self):
        return self.folder

    def remove(self):
        shutil.rmtree(self.folder)


class SourceFolder(Folder):
    pass


class TargetFolder(Folder):
    pass
