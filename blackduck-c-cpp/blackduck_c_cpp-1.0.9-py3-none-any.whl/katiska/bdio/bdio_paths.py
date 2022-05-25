"""
Copyright (c) 2021 Synopsys, Inc.
Use subject to the terms and conditions of the Synopsys End User Software License and Maintenance Agreement.
All rights reserved worldwide.
"""

import os
import copy
import unicodedata
from typing import Tuple, List

from urllib.parse import quote, unquote

from ..custom_types import ExtendedFullPath

# from https://github.com/google/guava/blob/master/guava/src/com/google/common/net/UrlEscapers.java
PATH_SEGMENT_ENCODING_SAFE_CHARS = "a-zA-Z0-9-._~!$'()*,;&=@:+"
PATH_FRAGMENT_ENCODING_SAFE_CHARS = PATH_SEGMENT_ENCODING_SAFE_CHARS + "/?"

# translates apples to oranges because fun fun and we need some workarounds for BDIO parser bugs.
file_scheme_translation_table = {
    "file": "unknown",  # avoid file:file... as that makes the parser choke
    "7z": "sevenz",  # schemes can't start with a number - doh
    "": "unknown",  # due to bugs we might get an empty scheme
}


def simple_fullpath_to_extended_fullpath(fullpath: List[str]) -> ExtendedFullPath:
    extended_fullpath = []
    for pathpart in fullpath:
        extended_fullpath.append({"type": "file", "path": pathpart})
    return extended_fullpath


def extended_fullpath_to_simple_fullpath(extended_fullpath: ExtendedFullPath) -> List[str]:
    fullpath = list(map(lambda p: p["path"], extended_fullpath))
    return fullpath


def deduplicate_extended_fullpaths(
    extended_fullpaths: List[ExtendedFullPath],
) -> List[ExtendedFullPath]:
    result: List[ExtendedFullPath] = []
    unique_paths = set()
    for extended_fullpath in extended_fullpaths:
        fullpath = tuple(extended_fullpath_to_simple_fullpath(extended_fullpath))
        if fullpath not in unique_paths:
            unique_paths.add(fullpath)
            result.append(extended_fullpath)

    return result


def fullpath_to_bdio_path_uri(extended_fullpath: ExtendedFullPath) -> str:
    """
    Repeatedly URI encode the path parts and prepend with the scheme/type
    see https://blackducksoftware.github.io/bdio/specification#file-paths
    The implementation of that algo is to be found when following:
    https://github.com/blackducksoftware/bdio/blob/master/bdio2/src/main/java/com/blackducksoftware/bdio2/LegacyScanContainerEmitter.java#L172
    https://github.com/blackducksoftware/magpie-libraries/blob/master/magpie/src/main/java/com/blackducksoftware/common/value/HID.java#L499

    :param extended_fullpath: a findlib results extended fullpath
    :return: a BDIO path URI
    """

    def get_path_parts(fullpath_entry, translate_scheme=True) -> Tuple[str, str]:
        path = fullpath_entry["path"]
        if path.endswith(os.sep):  # no trailing / allowed by the spec
            path = path.rstrip(os.sep)
        # TODO: add/remove prefix '/' according to rules in
        # https://blackducksoftware.github.io/bdio/specification#common-file-path-archive-schemes
        # NOTE that those schemes are incomplete! Would need to clarify further rules.
        path = os.path.join(os.sep, path)
        # the Hub chokes on unicode strings which are not normalized so we need to obey
        path = unicodedata.normalize("NFC", path)

        scheme = fullpath_entry["type"]
        if translate_scheme:
            scheme = file_scheme_translation_table.get(scheme, scheme)
        if scheme[0].isdigit():
            raise ValueError("Path type cannot start with a digit - forbidden by BDIO spec.")

        return scheme, path

    extended_fullpath = copy.deepcopy(extended_fullpath)  # content needs some modifications applied

    # BDIO path encoding wants the scheme to be applied to the children of an archive
    # not to itself, as it tells what extractor _was_ used to get to the child file
    # shifting here all the schemes down to the next path-element
    scheme = "file://"  # first entry must always be of scheme "file"
    for path_extended in extended_fullpath:
        current_scheme = path_extended["type"]
        path_extended["type"] = scheme
        scheme = current_scheme

    # first entry has different building rules
    scheme, path = get_path_parts(extended_fullpath[0], translate_scheme=False)
    # first path must not have `/` escaped
    result = scheme + quote(path, safe=PATH_SEGMENT_ENCODING_SAFE_CHARS + "/")

    for path_extended in extended_fullpath[1:]:
        scheme, path = get_path_parts(path_extended)
        result = (
            scheme
            + ":"
            + quote(result, safe=PATH_SEGMENT_ENCODING_SAFE_CHARS)
            + "#"
            + quote(path, safe=PATH_FRAGMENT_ENCODING_SAFE_CHARS)
        )

    return result


def bdio_path_uri_to_fullpath(path_uri: str) -> ExtendedFullPath:
    """
    Decode the BDIO URI into a findlib extended fullpath
    .
    :param path_uri: the BDIO path URI
    :return: a findlib results style extended fullpath
    """
    path_uri_part = path_uri
    extended_fullpath = []
    max_nested_paths = 1000  # to avoid potential infinite loops on malformed paths
    while max_nested_paths > 0:
        if path_uri_part.startswith("file://"):
            scheme = "file"
            path = path_uri_part.replace("file://", "", 1)
            if path.startswith(os.sep) and len(path) > 1:
                path = path.lstrip(os.sep)
            extended_path_part = {"type": scheme, "path": path}
            extended_fullpath.append(extended_path_part)
            break

        try:
            scheme, rest = path_uri_part.split(":", 1)
            path_uri_part, path = rest.split("#")
        except ValueError:
            # not enough values to unpack, the URI is malformed
            break
        path_uri_part = unquote(path_uri_part)
        path = unquote(path)
        if path.startswith(os.sep):
            path = path.lstrip(os.sep)
        extended_path_part = {"type": scheme, "path": path}
        extended_fullpath.append(extended_path_part)  # this is reverse but will be changed later
        max_nested_paths = max_nested_paths - 1

    # shifting the path schemes back up as the encoder shifts them down
    scheme = "file"  # first entry is of scheme "file" because we dropped it during encoding
    for path_extended in extended_fullpath:
        current_scheme = path_extended["type"]
        path_extended["type"] = scheme
        scheme = current_scheme

    # finally reverse the order as the paths were encoded inside out
    return list(reversed(extended_fullpath))
