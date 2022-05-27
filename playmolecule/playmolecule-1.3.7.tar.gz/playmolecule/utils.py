# (c) 2015-2022 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import os
from datetime import datetime
import sys
import shutil
import requests
import tempfile


def get_destination_folder(path, force=False, skip=False):
    if os.path.isdir(path):
        # hacer una con la fecha
        if skip:
            return path
        if force:
            shutil.rmtree(path, ignore_errors=True)
            return path
        else:
            date = datetime.now().strftime("%Y%m%d%H%M%S")
            dirname = os.path.dirname(os.path.abspath(path))
            basename = os.path.basename(os.path.abspath(path))
            new_path = os.path.join(dirname, basename + "_" + date)
            if os.path.isdir(new_path):
                sys.tracebacklimit = None
                raise ValueError("Error creating output folder")
            else:
                return new_path
    else:
        return path


def tempname(suffix="", tmpdir=None, create=False):
    if create:
        file = tempfile.NamedTemporaryFile(delete=False, dir=tmpdir, suffix=suffix)
    else:
        file = tempfile.NamedTemporaryFile(delete=True, dir=tmpdir, suffix=suffix)
    file.close()
    return file.name


def ensurelist(tocheck, tomod=None):
    """Convert np.ndarray and scalars to lists.

    Lists and tuples are left as is. If a second argument is given,
    the type check is performed on the first argument, and the second argument is converted.
    """
    if tomod is None:
        tomod = tocheck
    if type(tocheck).__name__ == "ndarray":
        return list(tomod)
    if isinstance(tocheck, range):
        return list(tocheck)
    if not isinstance(tocheck, list) and not isinstance(tocheck, tuple):
        return [
            tomod,
        ]
    return tomod


def _requestURL(
    mode,
    url,
    headers=None,
    json=None,
    data=None,
    files=None,
    _logger=False,
    conErrMsg=None,
    respErrMsg="Error in API call",
    _throwError=None,
    checkError=True,
):
    if conErrMsg is None:
        conErrMsg = f"Failed to contact the PMWS server at {url}. Please make sure the server is running."

    try:
        if mode == "get":
            rsp = requests.get(url, headers=headers, json=json)
        elif mode == "put":
            rsp = requests.put(url, headers=headers, json=json, data=data)
        elif mode == "post":
            rsp = requests.post(url, headers=headers, json=json, data=data, files=files)
        elif mode == "delete":
            rsp = requests.delete(url, headers=headers, json=json)
        else:
            raise RuntimeError(f"Invalid _requestURL mode {mode}")
    except requests.ConnectionError:
        _throwError(conErrMsg, _logger)
        return None

    rsp.close()

    if checkError and rsp.status_code != requests.codes["ok"]:
        _throwError(f"{respErrMsg}: {rsp.text}", _logger)
        return None

    return rsp


def format_filesize(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


def parse_timestamp_utc(timestamp):
    from dateutil import tz

    from_zone = tz.gettz("UTC")
    try:
        ptime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        ptime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    return ptime.replace(tzinfo=from_zone)


def utc_timestamp_to_local(utc_timestamp):
    from dateutil import tz

    to_zone = tz.tzlocal()
    return utc_timestamp.astimezone(to_zone)
