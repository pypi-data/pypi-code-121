from pydevmgr_ua import UaNode
from pydevmgr_core import kjoin, record_class
from .tools import fjoin 
from typing import Optional , Any



class EltNodeConfig(UaNode.Config):
        type: str = "Elt"
        fits_prefix: str = ""


@record_class
class EltNode(UaNode):
    Config = EltNodeConfig
    def __init__(self, *args, fits_key: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fits_key = fits_key or self._config.fits_prefix 
        
    @classmethod
    def new_args(cls, parent, name, config):
        d = super().new_args(parent, name, config)
        d.update(fits_key = fjoin(parent.fits_key, config.fits_prefix))
        return d
