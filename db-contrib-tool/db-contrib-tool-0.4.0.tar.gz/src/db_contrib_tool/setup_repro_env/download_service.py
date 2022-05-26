"""A service for downloading artifacts."""

import os
import time
from typing import Dict, List, NamedTuple, Optional

import inject
import structlog

from db_contrib_tool.clients.download_client import DownloadClient, DownloadError
from db_contrib_tool.clients.file_service import FileService
from db_contrib_tool.utils import is_windows

LOGGER = structlog.get_logger(__name__)


class DownloadOptions(NamedTuple):
    """
    Options describing how downloads should occur.

    * download_binaries: Should the binaries be downloaded.
    * download_symbols: Should the debug symbols be downloaded.
    * download_artifacts: Should the build artifacts be downloaded.
    * download_python_venv: Should the python virtualenv be downloaded.
    * install_dir: Directory to install downloaded artifacts.
    * link_dir: Directory to link downloaded files to.
    """

    download_binaries: bool
    download_symbols: bool
    download_artifacts: bool
    download_python_venv: bool

    install_dir: str
    link_dir: str


class ArtifactDownloadService:
    """A service for downloading artifacts."""

    @inject.autoparams()
    def __init__(self, download_client: DownloadClient, file_service: FileService) -> None:
        """
        Initialize the service.

        :param download_client: Client to perform download actions.
        :param file_service: Client to perform filesystem actions.
        """
        self.download_client = download_client
        self.file_service = file_service
        self.is_windows = is_windows()
        self.retry_time_secs = 1.0

    def download_and_extract(
        self,
        urls: Dict[str, str],
        bin_suffix: str,
        path_prefix: str,
        download_options: DownloadOptions,
    ) -> Optional[str]:
        """
        Download and extract artifacts from the given URLs.

        :param urls: URLs with artifacts to download.
        :param bin_suffix: _description_
        :param path_prefix: _description_
        :param download_options: Details about how to download artifacts.
        :return: Directory extracted artifacts where linked to.
        """
        url_list = self.find_urls_to_download(urls, download_options)
        install_dir = os.path.join(download_options.install_dir, path_prefix)
        linked_dir = self.setup_mongodb(
            url_list,
            download_options.download_binaries,
            install_dir,
            download_options.link_dir,
            bin_suffix,
        )
        return linked_dir

    def find_urls_to_download(
        self, urls: Dict[str, str], download_options: DownloadOptions
    ) -> List[str]:
        """
        Collect the urls to download based on the given options.

        :param urls: Known URLs.
        :param download_options: Options describing which URLs to target.
        :return: List of URLs that should be downloaded.
        """
        download_list = []
        if download_options.download_binaries:
            binaries_url = urls.get("Binaries")
            if binaries_url is not None:
                download_list.append(binaries_url)
            else:
                raise DownloadError("Binaries download requested but not URL available")

        if download_options.download_artifacts:
            artifacts_url = urls.get("Artifacts")
            if artifacts_url is not None:
                download_list.append(artifacts_url)
            else:
                raise DownloadError("Evergreen artifacts download requested but not URL available")

        if download_options.download_symbols:
            symbols_url = (
                urls.get(" mongo-debugsymbols.tgz")
                or urls.get("mongo-debugsymbols.tgz")
                or urls.get(" mongo-debugsymbols.zip")
                or urls.get("mongo-debugsymbols.zip")
            )
            if symbols_url is not None:
                download_list.append(symbols_url)
            else:
                raise DownloadError("Symbols download requested but not URL available")

        if download_options.download_python_venv:
            python_venv_url = urls.get("Python venv (see included README.txt)") or urls.get(
                "Python venv (see included venv_readme.txt)"
            )
            if python_venv_url is not None:
                download_list.append(python_venv_url)
            else:
                raise DownloadError("Python venv download requested but not URL available")

        return download_list

    def setup_mongodb(
        self,
        urls: List[str],
        create_symlinks: bool,
        install_dir: str,
        link_dir: str,
        bin_suffix: str,
    ) -> Optional[str]:
        """
        Download artifacts from the given URLs, extract them, and create symlinks.

        :param urls: List of artifact URLs to download.
        :param create_symlinks: Should symlinks be created to downloaded artifacts.
        :param install_dir: Directory to extract artifacts to.
        :param link_dir: Directory to create symlinks in.
        :param bin_suffix: _description_
        :return: Directory symlinks were created in.
        """
        for url in urls:
            try:
                self.try_download(url, install_dir)
            except Exception:
                LOGGER.warning(
                    "Setting up tarball failed with error, retrying once...", exc_info=True
                )
                time.sleep(self.retry_time_secs)
                self.try_download(url, install_dir)

        if create_symlinks:
            if self.is_windows:
                LOGGER.info(
                    "Linking to install_dir on Windows; executable have to live in different "
                    "working directories to avoid DLLs for different versions clobbering each other"
                )
                link_dir = self.download_client.symlink_version(bin_suffix, install_dir, None)
            else:
                link_dir = self.download_client.symlink_version(bin_suffix, install_dir, link_dir)
            return link_dir
        return None

    def try_download(self, target_url: str, install_dir: str) -> None:
        """
        Attempt to download the given URL.

        :param target_url: URL to download.
        :param install_dir: Location to extract the contents of the downloaded URL.
        """
        tarball = self.download_client.download_from_s3(target_url)
        self.download_client.extract_archive(tarball, install_dir)
        self.file_service.delete_file(tarball)
