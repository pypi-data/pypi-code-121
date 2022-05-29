from veet.core import paths
from dotenv import load_dotenv
import toml

__version__ = '0.1.0'

load_dotenv()

config = dict()

try:
    config = toml.load(f=f"{paths.PROJECT_PATH}/veet.toml")
except Exception as exception:
    pass