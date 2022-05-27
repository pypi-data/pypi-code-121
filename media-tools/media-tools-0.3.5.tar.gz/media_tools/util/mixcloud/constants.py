__author__ = 'Lene Preuss <lene.preuss@gmail.com>'

from pathlib import Path


MIXCLOUD_MAX_FILESIZE = 512 * 1024 * 1024
MIXCLOUD_MAX_TAGS = 5
MIXCLOUD_API_UPLOAD_URL = 'https://api.mixcloud.com/upload'
DEFAULT_CROSSFADE_MS = 1000
DEFAULT_MAX_RETRY = 100
DEFAULT_AUDIO_FILE_TYPES = ['flac', 'MP3', 'mp3', 'ogg', 'm4a']
# Mixcloud app:
# https://www.mixcloud.com/developers/Q29uc3VtZXI6MzY3Nw%253D%253D/
ACCESS_TOKEN_FILE = '.mixcloud_access_token'
ACCESS_TOKEN_SEARCH_PATH = (Path('.'), Path.home(), Path.home() / '.config' / 'media-tools')
MP3_KBIT_RATE = 128
