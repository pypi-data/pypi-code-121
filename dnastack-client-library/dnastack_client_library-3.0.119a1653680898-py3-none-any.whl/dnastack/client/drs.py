from concurrent.futures import ThreadPoolExecutor, Future, as_completed

import click
import os
import re
import requests
import threading
import urllib3
from enum import Enum
from typing import Optional, Union, List, Dict
from urllib.parse import urlparse, urljoin

from dnastack.client.service_registry.models import ServiceType
from dnastack.configuration.models import ServiceEndpoint

try:
    import pandas as pd

    _module_pandas_available = True
except ImportError:
    _module_pandas_available = False

from .base_client import BaseServiceClient
from ..exceptions import DRSDownloadException, DRSException

DRS_TYPE_V1_1 = ServiceType(group='org.ga4gh', artifact='drs', version='1.1.0')


class MissingOptionalRequirementError(RuntimeError):
    """ Raised when a optional requirement is not available """


class InvalidDrsUrlError(ValueError):
    """ Raised when the DRS URL is invalid """


class DrsApiError(RuntimeError):
    """ Raised when the DRS server responds an error """


class NoUsableAccessMethodError(RuntimeError):
    """ Raised when there is no usable access methods """


class DRSObject:
    """
    A class for a DRS resource

    :param url: The DRS url
    :raises ValueError if url is not a valid DRS url
    """

    __RE_VALID_DRS_OBJECT_ID = re.compile(r'^[^/#?]+$')

    def __init__(self, url: str):
        try:
            DRSObject.assert_valid_drs_url(url)
        except AssertionError:
            raise InvalidDrsUrlError("The provided url is not a valid DRS url")

        self.__url = url

    @staticmethod
    def get_adapter_type() -> str:
        return 'drs'

    @staticmethod
    def support_service_types() -> List[ServiceType]:
        return [
            ServiceType(group='org.ga4gh', artifact='drs', version='1.1.0'),
        ]

    @property
    def url(self):
        return self.__url

    @property
    def object_id(self) -> str:
        """
        Return the object ID from a drs url

        :param url: A drs url
        :return: The object ID extracted from the URL
        :raises: ValueError if there isn't a valid DRS Object ID
        """
        parsed_url = urlparse(self.url)
        return parsed_url.path.split("/")[-1]

    @property
    def drs_server_url(self) -> str:
        """
        Return the HTTPS server associated with the DRS url

        :param url: A drs url
        :return: The associated HTTPS server url
        """
        parsed_url = urlparse(self.url)
        return urljoin(f'https://{parsed_url.netloc}{"/".join(parsed_url.path.split("/")[:-1])}', 'ga4gh/drs/v1/')

    @staticmethod
    def assert_valid_drs_url(url: str):
        """Returns true if url is a valid DRS url"""
        parsed_url = urlparse(url)
        assert parsed_url.scheme == r'drs', f'The scheme of the given URL ({url}) is invalid.'
        assert len(parsed_url.path) > 2 and parsed_url.path.startswith(
            r'/'), f'The ID is not specified in the URL ({url}).'
        assert DRSObject.__RE_VALID_DRS_OBJECT_ID.search(
            parsed_url.path[1:]), f'The format of the ID ({parsed_url.path[1:]}) is not valid.'


def handle_file_response(download_file: str, data: Union[str, bytes]) -> str:
    # Decode the data to string if it is a FASTA/FASTQ file and the client receives as byte stream """
    if bool(re.search(r"\.(bam|fasta|fna|ffn|faa|frn|fa|fastq)$", download_file, re.I)) and isinstance(data, bytes):
        data = data.decode("utf-8")

    return data


def file_to_dataframe(download_file: str, data: Union[str, bytes]):
    """ Turn into dataframe for FASTA/FASTQ files, otherwise just return raw data """
    if bool(re.search(r"\.(bam|fasta|fna|ffn|faa|frn|fa|fastq)$", download_file, re.I)):
        if not _module_pandas_available:
            raise MissingOptionalRequirementError('pandas')

        data = data.split("\n", maxsplit=1)

        meta = data[0]
        sequence = data[1].replace("\n", "")  # remove newlines

        return pd.DataFrame({"meta": [meta], "sequence": [sequence]})

    return data


def get_filename_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.path.split("/")[-1]


class DownloadStatus(Enum):
    """An Enum to Describe the current status of a DRS download"""

    SUCCESS = 0
    FAIL = 1


class DrsClient(BaseServiceClient):
    """Client for Data Repository Service"""
    def __init__(self, endpoint: ServiceEndpoint):
        super().__init__(endpoint)

        # A lock to prevent race conditions on exit_codes objects
        self.__output_lock = threading.Lock()
        # lock to prevent race conditions for file output
        self.__exit_code_lock = threading.Lock()

    @staticmethod
    def get_adapter_type():
        return 'drs'

    @staticmethod
    def get_supported_service_types() -> List[ServiceType]:
        return [
            DRS_TYPE_V1_1,
        ]

    def exit_download(self, url: str, status: DownloadStatus, message: str = "", exit_codes: dict = None) -> None:
        """
        Report a file download with a status and message

        :param url: The downloaded resource's url
        :param status: The reported status of the download
        :param message: A message describing the reason for setting the status
        :param exit_codes: A shared dict for all reports used by download_files
        """
        if exit_codes is not None:
            with self.__exit_code_lock:
                exit_codes[status][url] = message

    def get_download_url(self, drs_url: str) -> Optional[str]:
        """
        Get the URL to download the DRS object
        """
        with self.create_http_session(suppress_error=True) as session:
            drs_object = DRSObject(drs_url)
            try:
                object_info_response = session.get(urljoin(drs_object.drs_server_url, f'objects/{drs_object.object_id}'))
            except requests.exceptions.ConnectionError:
                raise DrsApiError(f'Connection Error')
            object_info_status_code = object_info_response.status_code

            if object_info_status_code != 200:
                if object_info_status_code == 404:
                    raise DrsApiError(f"DRS object does not exist")
                elif object_info_status_code == 403:
                    raise DrsApiError("Access Denied")
                else:
                    raise DrsApiError("There was an error getting object info from the DRS Client")

            object_info = object_info_response.json()

            if "access_methods" in object_info and object_info['access_methods']:
                for access_method in object_info["access_methods"]:
                    if access_method["type"] != "https":
                        continue
                    # try to use the access_id to get the download url
                    if "access_id" in access_method.keys():
                        object_access_response = session.get(urljoin(drs_object.drs_server_url,
                                                                         f'objects/{drs_object.object_id}/access/{access_method["access_id"]}'))
                        object_access = object_access_response.json()
                        access_url = object_access["url"]
                        self._logger.debug(f'DRS URL {drs_url} -> {access_url} (via access ID)')

                        return access_url
                    # if we have a direct access_url for the access_method, use that
                    elif "access_url" in access_method.keys():
                        access_url = access_method["access_url"]["url"]
                        self._logger.debug(f'DRS URL {drs_url} -> {access_url} (from access URL)')
                        return access_url

                # we couldn't find a download url, exit unsuccessful
                raise NoUsableAccessMethodError()
            else:
                return None  # next page token, just return

    def download_file(
            self,
            url: str,
            output_dir: str,
            display_progress_bar: bool = False,
            output_buffer_list: Optional[list] = None,
            exit_codes: Optional[dict] = None
    ) -> None:
        """
        Download a single DRS resource and output to a file or list

        :param url: The DRS resource url to download
        :param output_dir: The directory to download output to.
        :param display_progress_bar: Display a progress bar for the downloads to standard output
        :param output_buffer_list: If specified, output downloaded data to the list specified in the argument
        :param exit_codes: A shared dictionary of the exit statuses and messages
        """
        self._logger.debug(f'url => {url}')
        try:
            download_url: Optional[str] = self.get_download_url(url)
        except InvalidDrsUrlError as e:
            self._logger.warning(f'failed to download from {url}: {type(e).__name__}: {e}')
            self.exit_download(
                url,
                DownloadStatus.FAIL,
                f"There was an error while parsing the DRS url ({e})",
                exit_codes,
            )
            return
        except NoUsableAccessMethodError:
            self._logger.warning(f'failed to download from {url}: {type(e).__name__}: {e}')
            self.exit_download(
                url,
                DownloadStatus.FAIL,
                f"Error determining access method",
                exit_codes,
            )
            return
        except DrsApiError as e:
            self._logger.warning(f'failed to download from {url}: {type(e).__name__}: {e}')
            self.exit_download(url, DownloadStatus.FAIL, e.args[0], exit_codes)
            return

        # FIXME return the download URL instead to give a full flexibility to the code.
        http_connection_pool = urllib3.PoolManager()
        chunk_size = 1024

        try:
            download_stream = http_connection_pool.request("GET", download_url, preload_content=False)
        except Exception as e:
            http_connection_pool.clear()
            self.exit_download(
                url,
                DownloadStatus.FAIL,
                f"There was an error downloading [{download_url}] : {e}",
                exit_codes,
            )
            return

        download_filename = get_filename_from_url(download_url)

        if output_buffer_list is not None:
            data = handle_file_response(download_filename, download_stream.read())
            with self.__output_lock:
                try:
                    output_buffer_list.append(file_to_dataframe(download_filename, data))
                except MissingOptionalRequirementError as e:
                    return self.exit_download(
                        url,
                        DownloadStatus.FAIL,
                        f'Optional package not installed: {e}',
                        exit_codes
                    )
        else:
            with open(f"{output_dir}/{download_filename}", "wb+") as dest:
                stream_size = int(download_stream.headers["Content-Length"])
                file_stream = download_stream.stream(chunk_size)
                if display_progress_bar:
                    click.echo(f"Downloading {url} into {output_dir}/{download_filename}...")
                    with click.progressbar(length=stream_size, color=True) as download_progress:
                        for chunk in file_stream:
                            dest.write(chunk)
                            download_progress.length = stream_size
                            download_progress.update(len(chunk))
                else:
                    for chunk in file_stream:
                        dest.write(chunk)
        http_connection_pool.clear()
        self.exit_download(url, DownloadStatus.SUCCESS, "Download Successful", exit_codes)

    def download_files(
            self,
            urls: List[str],
            output_dir: str = os.getcwd(),
            display_progress_bar: bool = False,
            parallel_download: bool = True,
            out: List = None,
    ) -> None:
        """
        Download a list of files and output either to files in the current directory or dump to a specified list

        :param urls: A list of DRS resource urls to download
        :param output_dir: The directory to download output to.
        :param display_progress_bar: Display a progress bar for the downloads to standard output
        :param out: If specified, output downloaded data to the list specified in the argument
        :raises: DRSDownloadException if one or more of the downloads fail
        """
        exit_codes = {status: {} for status in DownloadStatus}
        unique_urls = set(urls)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if parallel_download:
            # Define the maximum number of workers, limited to the number of CPUs.
            max_worker_count = os.cpu_count()
            if max_worker_count < 2:
                max_worker_count = 2

            future_to_url_map: Dict[Future, str] = dict()

            with ThreadPoolExecutor(max_workers=max_worker_count) as pool:
                for url in unique_urls:
                    # FIXME the progress bar needs to work when downloading multiple files.
                    # FIXME make self.download_file to return the data to retain the order of returning value and reduce
                    #  the overhead from locking.
                    future = pool.submit(
                        self.download_file,
                        url=url,
                        output_dir=output_dir,
                        output_buffer_list=out,
                        exit_codes=exit_codes
                    )
                    future_to_url_map[future] = url

            # Wait for all tasks to complete
            for future in as_completed(future_to_url_map.keys()):
                future.result()
        else:
            for url in unique_urls:
                self.download_file(url=url,
                                   output_dir=output_dir,
                                   output_buffer_list=out,
                                   exit_codes=exit_codes,
                                   display_progress_bar=display_progress_bar)

        # at least one download failed, create exceptions
        failed_downloads = [
            DRSException(msg=msg, url=url)
            for url, msg in exit_codes.get(DownloadStatus.FAIL).items()
        ]
        if len(unique_urls) == len(failed_downloads):
            raise DRSDownloadException(failed_downloads)
        elif len(failed_downloads) > 0:
            self._logger.warning(f'{len(failed_downloads)} out of {len(unique_urls)} download(s) failed unexpectedly')
            index = 0
            for failed_download in failed_downloads:
                self._logger.warning(f'Failure #{index}: {failed_download}')
                index += 1


FilesClient = DrsClient
