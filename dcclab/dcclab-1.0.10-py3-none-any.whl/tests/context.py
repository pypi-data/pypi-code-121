import os
import sys

moduleDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, moduleDir)

from pathlib import Path, PureWindowsPath
import tempfile
from dcclab import *

dataDir = Path('./testData')
tmpDir = Path("{0}/{1}".format(tempfile.gettempdir(), "testfiles"))
tmpDir.mkdir( parents=True, exist_ok=True )

