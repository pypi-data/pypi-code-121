from pathlib import Path
from rich.console import Console
import sys, os


def get_current_app_dir():
    dir = None
    if getattr(sys, 'frozen', False):
        dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        dir = os.path.dirname(os.path.abspath(__file__))
    return Path(dir)


def get_secret_path():
    # find secret next to the distribute file
    path = get_current_app_dir() / 'secret.txt'
    return path


def get_key(secret='', secret_file='', save: bool = False):
    # get env variable
    key = os.getenv('THINGSMATRIX_API_KEY', '')
    if key:
        return key
    key_saved_path = get_secret_path()
    if key_saved_path.exists():
        # read the key that previous saved
        key = Path(key_saved_path).read_text().strip()
        return key
    if secret:
        # provide secret string directly
        key = secret
    elif secret_file:
        # provid secret file path
        key = Path(secret_file).read_text().strip()
    else:
        # console to enter the key
        console = Console()
        key = console.input("Enter your API KEY:\n", password=True)
        ...
    if save:
        # save key to somewhere, if already exists, overwrite it
        file = key_saved_path.open('w+')
        file.writelines(key)
    return key


API_KEY = "eyJ0eXAiOiJBUElLRVkifQ.QzAwMDAwMi5Db21tVERDLmE1NzljMTBlNWIwZmE1NzY"
DOMAIN = "hpdemo.thingsmatrix.io"
API_VERSION = "v2"
COMPANY = "HP"
BASE_URL = f"https://{DOMAIN}/api/{API_VERSION}"

DEVICE_URL = f"{BASE_URL}/devices"
MODEL_BYNAME_URL = f"{BASE_URL}/modules/name/"
GROUP_URL = f"{BASE_URL}/groups"
GROUP_BY_NAME_URL = f"{BASE_URL}/groups/name/"
GROUP_BY_ID_URL = f"{BASE_URL}/groups/"
EVENTS_URL = f"{BASE_URL}/data/events"
REPORTS_URL = f"{BASE_URL}/data/reports"
USER_URL = f"https://{DOMAIN}/api/user"

TEMPLATE_URL = f"{BASE_URL}/configs"

INVENTORY_URL = f"{BASE_URL}/module"
