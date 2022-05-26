"""A client to download artifacts."""
import contextlib
import ctypes
import errno
import os
import shutil
import tarfile
import zipfile
from typing import Optional

import requests
import structlog

from db_contrib_tool.utils.filesystem import build_bin_path, mkdtemp_in_build_dir

LOGGER = structlog.getLogger(__name__)


class DownloadError(Exception):
    """Errors resulting from download failures."""

    pass


class DownloadClient:
    """A client to download artifacts."""

    def download_from_s3(self, url: str) -> str:
        """
        Download a file from the given URL pointing to an S3 bucket.

        :param url: URL of file to download.
        :return: Path to downloaded file on local filesystem.
        """
        if not url:
            raise DownloadError("Download URL not found")

        LOGGER.info("Downloading", url=url)
        filename = os.path.join(mkdtemp_in_build_dir(), url.split("/")[-1].split("?")[0])

        with requests.get(url, stream=True) as reader:
            with open(filename, "wb") as file_handle:
                shutil.copyfileobj(reader.raw, file_handle)

        return filename

    def extract_archive(self, archive_file: str, install_dir: str) -> str:
        """
        Extract the given archive files content into the specified directory.

        :param archive_file: Path to file to extract.
        :param install_dir: Path of directory to extract into.
        :return: Path to directory file were extracted into.
        """
        LOGGER.info("Extracting archive data.", archive=archive_file, install_dir=install_dir)
        temp_dir = mkdtemp_in_build_dir()
        archive_name = os.path.basename(archive_file)
        _, file_suffix = os.path.splitext(archive_name)

        if file_suffix == ".zip":
            # Support .zip downloads, used for Windows binaries.
            with zipfile.ZipFile(archive_file) as zip_handle:
                zip_handle.extractall(temp_dir)
        elif file_suffix == ".tgz":
            # Support .tgz downloads, used for Linux binaries.
            with contextlib.closing(tarfile.open(archive_file, "r:gz")) as tar_handle:
                tar_handle.extractall(path=temp_dir)
        else:
            raise DownloadError(f"Unsupported file extension {file_suffix}")

        try:
            os.makedirs(install_dir)
        except FileExistsError:
            pass

        _rsync_move_dir(temp_dir, install_dir)
        shutil.rmtree(temp_dir)

        LOGGER.info("Extract archive completed.", installed_dir=install_dir)

        return install_dir

    def symlink_version(
        self, suffix: str, installed_dir: str, link_dir: Optional[str] = None
    ) -> str:
        """
        Symlink the binaries in the 'installed_dir' to the 'link_dir'.

        If `link_dir` is None, link to the physical executable's directory (`bin_dir`).
        """
        bin_dir = build_bin_path(installed_dir)
        if os.path.isdir(bin_dir):
            bin_dir = bin_dir
        else:
            bin_dir = installed_dir

        if link_dir is None:
            link_dir = bin_dir
        else:
            mkdir_p(link_dir)

        for executable in os.listdir(bin_dir):
            if executable.endswith(".dll"):
                LOGGER.debug("Skipping linking DLL", file=executable)
                continue

            executable_name, executable_extension = os.path.splitext(executable)
            if suffix:
                link_name = f"{executable_name}-{suffix}{executable_extension}"
            else:
                link_name = executable

            executable = os.path.join(bin_dir, executable)
            executable_link = os.path.join(link_dir, link_name)

            create_symlink(executable, executable_link)

        LOGGER.info("Symlinks for all executables are created in the directory.", link_dir=link_dir)
        return link_dir


def _rsync_move_dir(source_dir, dest_dir):
    """
    Move dir.

    Move the contents of `source_dir` into `dest_dir` as a subdir while merging with
    all existing dirs.

    This is similar to the behavior of `rsync` but different to `mv`.
    """

    for cur_src_dir, _, files in os.walk(source_dir):
        cur_dest_dir = cur_src_dir.replace(source_dir, dest_dir, 1)
        if not os.path.exists(cur_dest_dir):
            os.makedirs(cur_dest_dir)
        for cur_file in files:
            src_file = os.path.join(cur_src_dir, cur_file)
            dst_file = os.path.join(cur_dest_dir, cur_file)
            if os.path.exists(dst_file):
                # in case of the src and dst are the same file
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.move(src_file, cur_dest_dir)


def mkdir_p(path):
    """Python equivalent of `mkdir -p`."""
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def create_symlink(executable, executable_link):
    """Symlink executable to executable_link."""
    link_method = os.symlink
    if os.name == "nt":
        # os.symlink is not supported on Windows, use a direct method instead.
        def symlink_ms(source, symlink_name):
            """Provide symlink for Windows."""
            csl = ctypes.windll.kernel32.CreateSymbolicLinkW
            csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
            csl.restype = ctypes.c_ubyte
            flags = 1 if os.path.isdir(source) else 0
            if csl(symlink_name, source.replace("/", "\\"), flags) == 0:
                raise ctypes.WinError()

        link_method = symlink_ms

    try:
        link_method(executable, executable_link)
        LOGGER.debug("Symlink created.", executable=executable, executable_link=executable_link)

    except OSError as exc:
        if exc.errno == errno.EEXIST:
            LOGGER.warning("Symlink already exists.", exc=exc)
            if os.name != "nt":
                LOGGER.warning(
                    "Removing old symlink & trying again", executable_link=executable_link
                )
                os.remove(executable_link)
                link_method(executable, executable_link)
                LOGGER.debug(
                    "Symlink created.", executable=executable, executable_link=executable_link
                )
            pass
        else:
            raise
