from appdata import AppDataPaths

app_paths = AppDataPaths("pydle")
app_paths.setup()

from .cli import run
from .game import Pydle
