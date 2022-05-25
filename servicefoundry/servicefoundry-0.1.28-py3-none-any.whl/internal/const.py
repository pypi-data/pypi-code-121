import os
from pathlib import Path

SERVICE_FOUNDRY_SERVER = (
    os.getenv("SFY_SERVER")
    or "https://sf-server.tfy-ctl-euwe1-devtest.devtest.truefoundry.tech"
)

# Auth related config
# TODO: Call service foundry to get this.
DEFAULT_TENANT_ID = os.getenv("SFY_TENANT_ID") or "895253af-ec9d-4be6-83d1-6f248e644e79"
AUTH_UI = os.getenv("SFY_AUTH_UI") or "https://app.devtest.truefoundry.tech"
AUTH_SERVER = (
    os.getenv("SFY_AUTH_SERVER")
    or "https://auth-server.tfy-ctl-euwe1-devtest.devtest.truefoundry.tech"
)
SESSION_FILE = str(Path.home() / ".truefoundry")

# Build related Config
SERVICE_DEF_FILE_NAME = "servicefoundry.yaml"
TEMPLATE_DEF_FILE_NAME = "template.yaml"
BUILD_DIR = ".servicefoundry"

COMPONENT = "Component"
BUILD_PACK = "BuildPack"
KIND = "kind"

# Polling during login redirect
MAX_POLLING_RETRY = 100
POLLING_SLEEP_TIME_IN_SEC = 4

# Refresh access token cutoff
REFRESH_ACCESS_TOKEN_IN_SEC = 10 * 60

ENTITY_JSON_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
