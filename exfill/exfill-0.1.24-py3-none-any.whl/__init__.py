"""Set path for import
"""

from pathlib import PurePath
from site import addsitedir

addsitedir(PurePath(__file__).parent.__str__())
