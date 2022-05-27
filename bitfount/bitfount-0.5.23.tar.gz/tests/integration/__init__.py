"""Integration tests."""
from pathlib import Path

RESOURCES_DIR: Path = Path(__file__).parent / "resources"
CONFIG_DIR: Path = RESOURCES_DIR / "config"
KEYS_DIR: Path = RESOURCES_DIR / "keys"
PRIVATE_DETAILS_ENV_FILE: Path = RESOURCES_DIR / "private_details.env"
# This is in the project root directory
DEPLOYMENTS_DIRECTORY: Path = Path(__file__).parent.parent.parent / "deployments"
