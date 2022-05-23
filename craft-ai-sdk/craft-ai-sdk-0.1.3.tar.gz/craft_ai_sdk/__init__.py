import os

CRAFT_AI_ENVIRONMENT_URL = os.environ.get("CRAFT_AI_ENVIRONMENT_URL")

from .sdk import CraftAiSdk  # noqa: F401, E402
from .exceptions import SdkException  # noqa: F401, E402
