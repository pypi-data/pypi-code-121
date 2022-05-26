import zipfile
from abc import abstractmethod
from pysteamupload.generic_pysteam import GenericPySteam


class WindowsPySteam(GenericPySteam):
    @abstractmethod
    def get_steamcmd_local_filename(self) -> str:
        return "steamcmd.exe"

    @abstractmethod
    def get_steamcmd_remote_filename(self) -> str:
        return "steamcmd.zip"

    @abstractmethod
    def extract_steamcmd_archive(self) -> None:
        with zipfile.ZipFile(self.get_archive_path(), "r") as f:
            f.extractall(path=self.root_directory)
