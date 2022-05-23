import sys
if '-m' not in sys.argv:
    from .head import Head
    from .tail import Tail

__all__ = ['Head', 'Tail']
