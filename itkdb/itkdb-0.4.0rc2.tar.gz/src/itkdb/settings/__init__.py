from dotenv import load_dotenv
import os
from simple_settings import settings

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

os.environ.setdefault("SIMPLE_SETTINGS", "itkdb.settings.base")

__all__ = ["settings"]
