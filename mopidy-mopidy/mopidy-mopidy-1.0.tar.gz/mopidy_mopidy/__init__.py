from mopidy import ext, config
import pathlib
from .backend import MopidyMusicBackend

__version__ = '0.1'
import requests
import logging
logger = logging.getLogger("mopidy_mopidy")


class Extension(ext.Extension):
    dist_name = "Mopidy-Mopidy"
    ext_name = "mopidy_mopidy"
    version = __version__


    def get_default_config(self):
        default_config = config.read(pathlib.Path(__file__).parent / "ext.conf")
        return default_config

    def get_config_schema(self):
        schema = super().get_config_schema()
        schema["master"] = config.String()
        schema["name"] = config.String()
        schema["ip"] = config.String()
        schema["frontend"] = config.String()
        return schema

    def validate_config(self, config):
        return True

    def setup(self, registry):
        from .actor import MasterFrontend
        registry.add("backend", MopidyMusicBackend)
        registry.add("frontend", MasterFrontend)
        registry.add("http:app", {"name": self.ext_name, "factory": self.webapp})


    def webapp(self, config, core):
        from .web import MasterApiHandler, MasterApiWebSocketHandler
        logger.error(config)
        return [
            (r"/masterapi/(.+)", MasterApiHandler, {"master": config['mopidy_mopidy']['master'], "name": config['mopidy_mopidy']['name'] }),
            (r"/socketapi/(.*)", MasterApiWebSocketHandler, {"master": config['mopidy_mopidy']['master'], "name": config['mopidy_mopidy']['name']}),
        ]
