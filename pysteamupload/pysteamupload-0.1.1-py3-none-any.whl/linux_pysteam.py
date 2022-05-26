import tarfile
from abc import abstractmethod
from pysteamupload.generic_pysteam import GenericPySteam


class LinuxPySteam(GenericPySteam):
    @abstractmethod
    def get_steamcmd_local_filename(self) -> str:
        return "steamcmd.sh"

    @abstractmethod
    def get_steamcmd_remote_filename(self) -> str:
        return "steamcmd_linux.tar.gz"

    @abstractmethod
    def extract_steamcmd_archive(self) -> None:
        with tarfile.open(self.get_archive_path(), 'r:gz') as f:
            f.extractall(path=self.root_directory)
