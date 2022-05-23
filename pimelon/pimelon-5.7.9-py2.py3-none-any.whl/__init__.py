VERSION = "5.7.9"
PROJECT_NAME = "pimelon"
MELON_VERSION = None
current_path = None
updated_path = None
LOG_BUFFER = []


def set_melon_version(pine_path="."):
	from .utils.app import get_current_melon_version

	global MELON_VERSION
	if not MELON_VERSION:
		MELON_VERSION = get_current_melon_version(pine_path=pine_path)
