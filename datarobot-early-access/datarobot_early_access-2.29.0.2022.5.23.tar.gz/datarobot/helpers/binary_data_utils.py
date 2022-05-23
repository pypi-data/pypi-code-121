#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import base64
from concurrent.futures import as_completed, ThreadPoolExecutor
import multiprocessing as mp

import requests
from requests.exceptions import RequestException

from datarobot.enums import DEFAULT_MAX_WAIT, DEFAULT_TIMEOUT, FileLocationType
from datarobot.errors import ContentRetrievalTerminatedError
from datarobot.helpers.image_utils import format_image_bytes, ImageOptions


def get_bytes_for_path(location, continue_on_error=False, **kwargs):
    """Return file content for path as bytes"""
    try:
        with open(location, mode="rb") as f:
            buffer = f.read()
    except OSError:
        buffer = None
        # exception encountered during processing of single row should stop processing
        if not continue_on_error:
            msg = "Process terminated. Could not retrieve resource: {}".format(location)
            raise ContentRetrievalTerminatedError(msg)
    return buffer


def get_bytes_for_url(location, continue_on_error=False, headers=None, **kwargs):
    """Return file content for url as bytes"""
    try:
        response = requests.get(url=location, headers=headers, timeout=DEFAULT_TIMEOUT.READ)
        response.raise_for_status()
        return response.content
    except RequestException:
        # exception encountered during processing of single row should stop processing
        if not continue_on_error:
            msg = "Process terminated. Could not retrieve resource: {}".format(location)
            raise ContentRetrievalTerminatedError(msg)


get_bytes_switcher = {
    FileLocationType.PATH: get_bytes_for_path,
    FileLocationType.URL: get_bytes_for_url,
}


def _get_base64_for_location(
    location, location_type, continue_on_error, image_options=None, **kwargs
):
    """Retrieve content from the specified location and return it as a base64 string"""
    result = None
    get_bytes_method = get_bytes_switcher[location_type]
    content_bytes = get_bytes_method(location, continue_on_error, **kwargs)
    if content_bytes:
        if image_options:
            content_bytes = format_image_bytes(content_bytes, image_options)
        result = base64.b64encode(content_bytes).decode("utf-8")
    # if no content raise exception unless user chosen otherwise
    if not result and not continue_on_error:
        msg = "Process terminated. Could not retrieve resource: {}".format(location)
        raise ContentRetrievalTerminatedError(msg)
    return result


def _get_base64_for_location_indexed(idx, *args, **kwargs):
    """Return indexed result of content from specified location converted to base64 string"""
    return idx, _get_base64_for_location(*args, **kwargs)


def _process_locations(locations, n_threads, **kwargs):
    """Process and return base64 encoded strings for all locations preserving order"""

    # If not specified determine number of threads to use
    if not n_threads:
        try:
            n_threads = mp.cpu_count()
        except Exception:
            n_threads = 4

    if n_threads == 1:
        return [_get_base64_for_location(location, **kwargs) for location in locations]
    else:
        # NOTE: Since results can be returned by threads in any order depending on how long
        # it takes to load and process specific file. To ensure we will preserve order when
        # results are being returned we initialize results array and place results using
        # their indexes.
        results = [None] * len(locations)

        with ThreadPoolExecutor(max_workers=n_threads) as executor:

            futures = []
            for idx, loc in enumerate(locations):
                futures.append(
                    executor.submit(_get_base64_for_location_indexed, idx, loc, **kwargs)
                )

            for future in as_completed(futures, timeout=DEFAULT_MAX_WAIT):
                try:
                    result_idx, result_value = future.result()
                    results[result_idx] = result_value
                except Exception as exc:
                    # clean up and reraise thread exception
                    executor.shutdown(wait=False)
                    for victim in futures:
                        victim.cancel()
                    raise exc

    return results


def get_encoded_image_contents_from_urls(
    urls, custom_headers=None, image_options=None, continue_on_error=False, n_threads=None
):
    """
    Returns base64 encoded string of images located in addresses passed in input collection.
    Input collection should hold data of valid image url addresses reachable from
    location where code is being executed. Method will retrieve image, apply specified
    reformatting before converting contents to base64 string. Results will in same
    order as specified in input collection.

    Parameters
    ----------
    urls: Iterable
        Iterable with url addresses to download images from
    custom_headers: dict
        Dictionary containing custom headers to use when downloading files using a URL. Detailed
        data related to supported Headers in HTTP  can be found in the RFC specification for
        headers: https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        When used, specified passed values will overwrite default header values.
    image_options: ImageOptions class
        Class holding parameters for use in image transformation and formatting.
    continue_on_error: bool
        If one of rows encounters error while retrieving content (i.e. file does not exist) should
        this error terminate process of downloading consecutive files or should process continue
        skipping this file.
    n_threads: int or None
        Number of threads to use for processing. If "None" is passed, the number of threads is
        determined automatically based on the number of available CPU cores. If this is not
        possible, 4 threads are used.

    Raises
    ------
    ContentRetrievalTerminatedError:
        The error is raised when the flag `continue_on_error` is set to` False` and processing has
        been terminated due to an exception while loading the contents of the file.

    Returns
    -------
    List of base64 encoded strings representing reformatted images.
    """
    return _process_locations(
        locations=urls,
        location_type=FileLocationType.URL,
        image_options=image_options or ImageOptions(),
        headers=custom_headers or {},
        continue_on_error=continue_on_error,
        n_threads=n_threads,
    )


def get_encoded_image_contents_from_paths(
    paths, image_options=None, continue_on_error=False, n_threads=None
):
    """
    Returns base64 encoded string of images located in paths passed in input collection.
    Input collection should hold data of valid image paths reachable from location
    where code is being executed. Method will retrieve image, apply specified
    reformatting before converting contents to base64 string. Results will in same
    order as specified in input collection.

    Parameters
    ----------
    paths: Iterable
        Iterable with path locations to open images from
    image_options: ImageOptions class
        Class holding parameters for image transformation and formatting
    continue_on_error: bool
        If one of rows encounters error while retrieving content (i.e. file does not exist) should
        this error terminate process of downloading consecutive files or should process continue
        skipping this file.
    n_threads: int or None
        Number of threads to use for processing. If "None" is passed, the number of threads is
        determined automatically based on the number of available CPU cores. If this is not
        possible, 4 threads are used.

    Raises
    ------
    ContentRetrievalTerminatedError:
        The error is raised when the flag `continue_on_error` is set to` False` and processing has
        been terminated due to an exception while loading the contents of the file.

    Returns
    -------
    List of base64 encoded strings representing reformatted images.
    """
    return _process_locations(
        locations=paths,
        location_type=FileLocationType.PATH,
        image_options=image_options or ImageOptions(),
        continue_on_error=continue_on_error,
        n_threads=n_threads,
    )


def get_encoded_file_contents_from_paths(paths, continue_on_error=False, n_threads=None):
    """
    Returns base64 encoded string for files located under paths passed in input collection.
    Input collection should hold data of valid file paths locations reachable from
    location where code is being executed. Method will retrieve file and convert its contents
    to base64 string. Results will be returned in same order as specified in input collection.

    Parameters
    ----------
    paths: Iterable
        Iterable with path locations to open images from
    continue_on_error: bool
        If one of rows encounters error while retrieving content (i.e. file does not exist) should
        this error terminate process of downloading consecutive files or should process continue
        skipping this file.
    n_threads: int or None
        Number of threads to use for processing. If "None" is passed, the number of threads is
        determined automatically based on the number of available CPU cores. If this is not
        possible, 4 threads are used.

    Raises
    ------
    ContentRetrievalTerminatedError:
        The error is raised when the flag `continue_on_error` is set to` False` and processing has
        been terminated due to an exception while loading the contents of the file.

    Returns
    -------
    List of base64 encoded strings representing files.
    """
    return _process_locations(
        locations=paths,
        location_type=FileLocationType.PATH,
        continue_on_error=continue_on_error,
        n_threads=n_threads,
    )


def get_encoded_file_contents_from_urls(
    urls, custom_headers=None, continue_on_error=False, n_threads=None
):
    """
    Returns base64-encoded string for files located in the URL addresses passed on input. Input
    collection holds data of valid file URL addresses reachable from location where code is being
    executed. Method will retrieve file and convert its contents to base64 string. Results will
    be returned in same order as specified in input collection.

    Parameters
    ----------
    urls: Iterable
        Iterable containing URL addresses to download images from.
    custom_headers: dict
        Dictionary with headers to use when downloading files using a URL. Detailed data
        related to supported Headers in HTTP  can be found in the RFC specification:
        https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html. When specified,
        passed values will overwrite default header values.
    continue_on_error: bool
        If a row encounters an error while retrieving content (i.e., file does not exist),
        specifies whether the error results in terminating the process of downloading
        consecutive files or the process continues. Skipped files will be marked as missing.
    n_threads: int or None
        Number of threads to use for processing. If "None" is passed, the number of threads is
        determined automatically based on the number of available CPU cores. If this is not
        possible, 4 threads are used.

    Raises
    ------
    ContentRetrievalTerminatedError:
        The error is raised when the flag `continue_on_error` is set to` False` and processing has
        been terminated due to an exception while loading the contents of the file.

    Returns
    -------
    List of base64 encoded strings representing files.
    """
    return _process_locations(
        locations=urls,
        location_type=FileLocationType.URL,
        headers=custom_headers or {},
        continue_on_error=continue_on_error,
        n_threads=n_threads,
    )
