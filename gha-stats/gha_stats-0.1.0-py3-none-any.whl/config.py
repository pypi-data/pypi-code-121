import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path.cwd() / ".env")

GH_TOKEN = os.environ.get("GH_TOKEN", ...)
