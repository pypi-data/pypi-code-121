from importlib_metadata import version

from .address import Address
from .frame import AX25BytestreamDecoder, Control, Frame, FrameType

__author__ = "Masen Furer KF7HVM <kf7hvm@0x26.net>"
__copyright__ = "Copyright 2022 Masen Furer and Contributors"
__license__ = "Apache License, Version 2.0"
__distribution__ = "ax253"
__version__ = version(__distribution__)
__all__ = [
    "Address",
    "AX25BytestreamDecoder",
    "Control",
    "Frame",
    "FrameType",
    "__distribution__",
    "__version__",
]
