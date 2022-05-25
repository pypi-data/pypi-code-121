
from pydevmgr_ua import UaInterface
from .vltnode import VltNode

class VltInterface(UaInterface):
    Node = VltNode
    pass
