from core.request import request
import os
import base64
import logging
import sys

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(filename='/tmp/daemondev-config-server.log', format='%(asctime)s-Flask> %(levelname)s-%(message)s', level=logging.INFO)
_logger = logging.getLogger(__name__)
h = logging.StreamHandler(sys.stdout)
h.flush = sys.stdout.flush
_logger.addHandler(h)

configFilesDir = f"{os.path.dirname(os.path.realpath(__file__))}"
repo_name = os.path.basename(os.popen("git rev-parse --show-toplevel").read().strip())
environment = os.getenv("ENVIRONMENT", "local")
debug = os.getenv("DEBUG", False)
config_files_folder = os.getenv("LOCAL_CONFIG_DIR", os.getenv("GLOBAL_CONFIG_DIR", configFilesDir))
allowed_debugable_environmets = ["local", "development", "staging"]

schema = os.getenv("CONFIG_SCHEMA", "https")
config_server = f"{os.getenv('CONFIG_SERVER','config.wecourier4u.com')}"
obj = None
final_local_yaml = ""
project = os.getenv("APPLICATION", os.getenv("PROJECT_NAME", repo_name or "dummy"))

auth = f"{os.getenv('CONFIG_USERNAME', 'w4u')}:{os.getenv('CONFIG_PASSWORD','w4u')}".encode("ascii")
auth = base64.b64encode(auth).decode("utf-8")
url = f"{schema}://{config_server}/{project}-{environment}"

if debug:
    _logger.info(f">>> url: [{url}]")
    _logger.info(f">>> auth: [{auth}]")

custom_headers = {
    "Content-Type": "application/json",
    'Authorization' : f"Bearer {auth}"
}

config = request(url, {}, custom_headers, method="GET")
_logger.info(f">>> response: [{config['app']['name']}]")
