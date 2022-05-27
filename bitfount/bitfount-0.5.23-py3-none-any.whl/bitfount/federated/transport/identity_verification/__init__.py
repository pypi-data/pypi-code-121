"""Various identity verification related methods and classes."""
from typing import Final

# We run a temporary HTTP listener on this port
# Why 29206? It's unlikely to be in use.
# And it's 'Bitf' (2, 9, 20, 6)
_BITFOUNT_MODELLER_PORT: Final = 29206
_PORT_WAIT_TIMEOUT: Final = 10
