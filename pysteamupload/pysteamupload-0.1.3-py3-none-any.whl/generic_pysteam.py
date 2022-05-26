import os
import vdf
import base64
import shutil
import tempfile
import requests
import subprocess
from pathlib import Path
from loguru import logger
from abc import ABCMeta, abstractmethod


class GenericPySteam:
    __metaclass__ = ABCMeta
    steam_cdn_url: str = "https://steamcdn-a.akamaihd.net/client/installer"

    def __init__(self):
        self.root_directory: Path = Path(tempfile.gettempdir(), "SteamCMD")
        if not self.is_steamcmd_available():
            logger.info("SteamCMD seems not installed, downloading it.")
            self.download_steamcmd()
            self.extract_steamcmd()
        self.setup_steam_guard()

    def get_archive_path(self) -> Path:
        # Windows example: C:\Users\rdall\AppData\Local\Temp\SteamCMD\steamcmd.zip
        return Path(self.root_directory, self.get_steamcmd_remote_filename())

    def get_steamcmd_path(self) -> Path:
        # Windows example: C:\Users\rdall\AppData\Local\Temp\SteamCMD\steamcmd.exe
        return Path(self.root_directory, self.get_steamcmd_local_filename())

    def is_steamcmd_available(self) -> bool:
        return self.root_directory.exists() and self.get_steamcmd_path().exists()

    def download_steamcmd(self) -> None:
        """
        Download steamcmd in temp directory to be reused later.
        """
        self.root_directory.mkdir(exist_ok=True)
        url: str = f"{self.steam_cdn_url}/{self.get_steamcmd_remote_filename()}"
        install_dir = self.get_archive_path()
        logger.info(f"Downloading to [{install_dir}]")
        with requests.get(url) as r:
            r.raise_for_status()
            with open(install_dir, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                logger.info("Download is completed.")

    def extract_steamcmd(self) -> None:
        self.extract_steamcmd_archive()
        os.remove(self.get_archive_path())
        logger.info("Extraction is complete.")

    def setup_steam_guard(self) -> None:
        if not self.get_config_vdf_path().exists():
            self._create_config_vdf()
        if not self.get_ssfn_path().exists():
            self._create_ssfn()

    @staticmethod
    def get_config_vdf_filename() -> str:
        return "config.vdf"

    def get_config_vdf_path(self) -> Path:
        return self.root_directory / "config" / self.get_config_vdf_filename()

    def _create_config_vdf(self) -> None:
        config_dir = Path(self.root_directory, "config")
        config_dir.mkdir(exist_ok=True)
        self._create_file_from_base64(
            environ_key="STEAM_CONFIG_VDF_FILE_CONTENT",
            destination=self.get_config_vdf_path(),
            binary_file=False,
        )
        logger.info("config vdf file created")

    @staticmethod
    def get_ssfn_filename() -> str:
        return os.getenv("STEAM_SSFN_FILENAME")

    def get_ssfn_path(self) -> Path:
        return self.root_directory / self.get_ssfn_filename()

    def _create_ssfn(self) -> None:
        self._create_file_from_base64(
            environ_key="STEAM_SSFN_FILE_CONTENT",
            destination=self.get_ssfn_path(),
            binary_file=True,
        )
        logger.info("ssfn file created")

    @staticmethod
    def _create_file_from_base64(environ_key: str, destination: Path, binary_file: bool) -> None:
        try:
            content: bytes = base64.b64decode(s=os.getenv(environ_key))
            with open(destination, "wb" if binary_file else "w") as f:
                f.write(content if binary_file else content.decode())
        except UnicodeDecodeError as exception:
            logger.error(f"Check [{environ_key}] value, unable to decode")
        except Exception as exception:
            logger.error(f"Unable to create [{destination.name}]")

    def call_steamcmd(self, args):
        timeout_in_seconds = 30
        try:
            subprocess_args = (self.get_steamcmd_path(), *args, "+quit")
            subprocess.check_call(subprocess_args, timeout=timeout_in_seconds)
        except subprocess.TimeoutExpired:
            # SteamGuard is probably waiting asking for a 2 factor authentication password
            logger.error(f"SteamCMD timed out ({timeout_in_seconds} seconds)")
        except subprocess.CalledProcessError as exception:
            if exception.returncode != 7:
                logger.exception(exception)

    def create_upload_directory(self) -> None:
        upload_path = self.get_upload_path()
        # Cleanup previous upload (if any)
        shutil.rmtree(upload_path, ignore_errors=True)
        upload_path.mkdir(exist_ok=True)

    def get_upload_path(self) -> Path:
        return Path(self.root_directory, "Upload")

    def create_depot_vdf_file(self, depot_id: str) -> None:
        # Read template
        with open("templates/depot.txt", "r") as f:
            depot_vdf = vdf.load(f)

        # Set depot id
        depot_vdf["DepotBuildConfig"]["DepotID"] = depot_id

        # Dump output
        filename = self.get_upload_path() / "depot.vdf"
        with open(filename, "w") as f:
            vdf.dump(depot_vdf, f, pretty=True)

    def get_app_build_path(self) -> Path:
        return self.get_upload_path() / "app_build.vdf"

    def create_app_build_file(
            self,
            app_id: str,
            depot_id: str,
            build_description: str,
            content_path: Path,
    ) -> None:
        # Read template
        with open("templates/app_build.txt", "r") as f:
            app_build = vdf.load(f)

        # Prepare app build file
        app_build["appbuild"]["appid"] = app_id
        app_build["appbuild"]["desc"] = build_description
        app_build["appbuild"]["buildoutput"] = "Logs"
        app_build["appbuild"]["contentroot"] = str(content_path)
        app_build["appbuild"]["depots"][depot_id] = "depot.vdf"

        # Dump output
        filename = self.get_app_build_path()
        with open(filename, "w") as f:
            vdf.dump(app_build, f, pretty=True)

    def upload(
            self,
            app_id: str,
            depot_id: str,
            build_description: str,
            content_path: Path,
    ) -> None:
        # Prepare vdf files to upload
        self.create_upload_directory()
        self.create_depot_vdf_file(depot_id=depot_id)
        self.create_app_build_file(
            app_id=app_id,
            depot_id=depot_id,
            build_description=build_description,
            content_path=content_path,
        )

        args = (
            f"+login {os.getenv('STEAM_USERNAME')} {os.getenv('STEAM_PASSWORD')}",
            f"+run_app_build {self.get_app_build_path()}"
        )
        self.call_steamcmd(args)

    @abstractmethod
    def get_steamcmd_local_filename(self) -> str:
        pass

    @abstractmethod
    def get_steamcmd_remote_filename(self) -> str:
        pass

    @abstractmethod
    def extract_steamcmd_archive(self) -> None:
        pass
