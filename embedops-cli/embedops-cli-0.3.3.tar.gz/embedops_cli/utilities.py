"""
`embedops_cli.utilities`
=======================================================================
miscellaneous utility functions for parsing and handling build logs
* Author(s): Bryan Siepert
"""
from os import getenv
from re import compile as re_compile
import platform
import logging
from sys import exit as sys_exit
import requests

_logger = logging.getLogger(__name__)

compiler_image_regex = re_compile(
    r"^registry\.embedops\.com\/dojofive\/build-images\/"
    r"(?P<compiler>[^\/\:]+)(?:\:(?P<image_version>[^\/]+))?\/?$"
)


def get_compiler():
    """Return the name of the compiler used to generate the build log from either
    `EMBEDOPS_COMPILER`. If that environment variable is not set, we'll try to parse the compiler
    name from the `<CI_IMAGE_NAME_PLACEHOLDER>`"""
    compiler = getenv("EMBEDOPS_COMPILER", default=None)
    if compiler is None:
        _logger.warning("EMBEDOPS_COMPILER was not set. Checking for CI_REGISTRY_IMAGE")
        # fetch compiler from container name, else None
        image_registry_url = getenv("CI_REGISTRY_IMAGE", default=None)
        if image_registry_url is None:
            _logger.error("CI_REGISTRY_IMAGE could not be found")
            sys_exit(1)
        image_match = compiler_image_regex.match(image_registry_url)
        if image_match is None:
            _logger.error(
                f"The Docker image URL provided in {compiler} is not a valid image registry URL"
            )
            sys_exit(1)

        compiler_image = image_match["compiler"].upper()
        image_version = image_match["image_version"].upper()
        _logger.info(
            f"Found compiler image: {compiler_image} image version: {image_version}"
        )
        if "TI" in compiler_image:
            compiler = "TI"
        elif "GCC" in compiler_image:
            compiler = "GCC"
        elif "IAR" in compiler_image:
            compiler = "IAR"
        else:
            _logger.error(f"Compiler {compiler_image} not recognised")
            sys_exit(1)
    return compiler


def post_dict(
    endpoint_uri, data_dict=None, file_dict=None, json_dict=None, headers=None
):
    """POSTs the given object to the given URL as JSON"""

    req = requests.Request(
        "POST",
        endpoint_uri,
        headers=headers,
        files=file_dict,
        json=json_dict,
        data=data_dict,
    )
    prepared = req.prepare()
    session = requests.Session()

    return session.send(prepared)


def quote_str_for_platform(str_to_quote):
    """Properly quote a string of command line arguments for the current platform"""
    if platform.system() == "Windows":
        # Proper quoting for cmd.exe
        #   The entire argument inside double quotes to be taken literally, except
        #   for double quotes inside the string literal, which must be escaped.
        # To accomplish this, we replace all instances of '"' with '\"'.
        #   Note: '\' must be used to escape itself in the replace pattern.
        str_to_quote = str_to_quote.replace('"', '\\"')
        return f'"{str_to_quote}"'

    # Proper quoting for Bash/zsh/etc.
    #   The entire argument inside single quotes to be taken literally.
    return f"'{str_to_quote}'"
