VERSION = "2.4.0"
PROJECT_NAME = "dokos-cli"
FRAPPE_VERSION = None
current_path = None
updated_path = None
LOG_BUFFER = []

def set_frappe_version(bench_path="."):
	from .utils.app import get_current_frappe_version

	global FRAPPE_VERSION
	if not FRAPPE_VERSION:
		FRAPPE_VERSION = get_current_frappe_version(bench_path=bench_path)
