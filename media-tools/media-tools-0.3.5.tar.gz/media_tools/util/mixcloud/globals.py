__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

from pathlib import Path
from typing import Optional

from media_tools.util.mixcloud.authorization_error import AuthorizationError
from media_tools.util.mixcloud.constants import (
    MP3_KBIT_RATE, DEFAULT_CROSSFADE_MS, MIXCLOUD_MAX_FILESIZE, ACCESS_TOKEN_FILE,
    ACCESS_TOKEN_SEARCH_PATH
)
from media_tools.util.mixcloud.mix import Mix
from media_tools.util.mixcloud.mix_path import MixPath
from media_tools.util.mixcloud.multi_mix import MultiMix


def bytes_per_second(mp3_kbit_rate: int = MP3_KBIT_RATE) -> int:
    return mp3_kbit_rate // 8 * 1024 * 2


def create_mix(
        mix_path: MixPath, access_token: str, strict: bool = False,
        crossfade_ms: int = DEFAULT_CROSSFADE_MS
) -> "Mix":
    files, length = mix_path.scan()
    if bytes_per_second() * length < MIXCLOUD_MAX_FILESIZE:
        return Mix(mix_path, strict, crossfade_ms).with_access_token(access_token)
    return MultiMix(
        MixPath(mix_path.basedir, tuple(files)), access_token, length, strict, crossfade_ms
    )


def get_access_token(access_token_path: Optional[Path] = None) -> str:
    error_message = f"""
Authorization token does not exist - please follow the instructions at
https://www.mixcloud.com/developers/#authorization to generate an auth
token and store it under ./{ACCESS_TOKEN_FILE}, ~/{ACCESS_TOKEN_FILE}
or ~/.config/{ACCESS_TOKEN_FILE}.
"""
    if not access_token_path:
        access_token_path = find_access_token(error_message)
    try:
        with access_token_path.open('r') as file:
            return file.read().strip()
    except OSError as error:
        raise AuthorizationError(error_message) from error


def find_access_token(error_message):
    for basedir in ACCESS_TOKEN_SEARCH_PATH:
        if (basedir / ACCESS_TOKEN_FILE).exists():
            return basedir / ACCESS_TOKEN_FILE
    raise AuthorizationError(error_message)
