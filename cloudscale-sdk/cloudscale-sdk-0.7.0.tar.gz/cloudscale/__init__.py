import configparser
import logging
import os

from xdg import XDG_CONFIG_HOME

from .error import CloudscaleApiException, CloudscaleException  # noqa F401
from .lib.custom_image import CustomImage
from .lib.flavor import Flavor
from .lib.floating_ip import FloatingIp
from .lib.image import Image
from .lib.network import Network
from .lib.objects_user import ObjectsUser
from .lib.region import Region
from .lib.server import Server
from .lib.server_group import ServerGroup
from .lib.subnet import Subnet
from .lib.volume import Volume
from .log import logger
from .version import __version__

CLOUDSCALE_API_URL = os.getenv("CLOUDSCALE_API_URL", "https://api.cloudscale.ch/v1")
CLOUDSCALE_CONFIG = "cloudscale.ini"


class Cloudscale:
    api_url = CLOUDSCALE_API_URL
    version = __version__

    def __init__(self, api_token: str = "", profile: str = "", debug: bool = False):
        """Cloudscale

        Args:
            api_token (str, optional): API token. Defaults to None.
            profile (str, optional): Section to use in cloudscale.ini. Defaults to None.
            debug (bool, optional): Enable debug logging. Defaults to False.

        Raises:
            CloudscaleException: Exception related to API token handling.
        """
        if debug:
            logger.setLevel(logging.INFO)

        logger.info(f"Started, version: {self.version}")

        if api_token and profile:
            raise CloudscaleException("API token and profile are mutually exclusive")

        # Read ini configs
        self.config = self._read_from_configfile(profile=profile)

        if api_token:
            self.api_token = api_token
        else:
            self.api_token = self.config.get("api_token")

        if not self.api_token:
            raise CloudscaleException("Missing API key")

        logger.info(f"API Token used: {self.api_token[:4]}...")

        # Configure requests timeout
        self.timeout: int = int(self.config.get("timeout", 60))
        logger.debug(f"Timeout is: {self.timeout}")

        # Resource attributes
        self.custom_image = CustomImage(self)
        self.flavor = Flavor(self)
        self.floating_ip = FloatingIp(self)
        self.image = Image(self)
        self.network = Network(self)
        self.objects_user = ObjectsUser(self)
        self.region = Region(self)
        self.server = Server(self)
        self.server_group = ServerGroup(self)
        self.subnet = Subnet(self)
        self.volume = Volume(self)

    def _read_from_configfile(self, profile: str = "") -> dict:
        """Reads from config ini file.

        Args:
            profile (str, optional): Section to read. Defaults to "".

        Raises:
            CloudscaleException: Profile not found.

        Returns:
            dict: Read configs.
        """

        config_file = os.getenv("CLOUDSCALE_CONFIG", CLOUDSCALE_CONFIG)

        paths = (
            os.path.join(XDG_CONFIG_HOME, "cloudscale", config_file),
            os.path.join(os.path.expanduser("~"), ".{}".format(config_file)),
            os.path.join(os.getcwd(), config_file),
        )

        conf = configparser.ConfigParser()
        conf.read(paths)

        if profile:
            if not conf.has_section(profile):
                raise CloudscaleException(
                    "Profile '{}' not found in config files: ({})".format(
                        profile, ", ".join(paths)
                    )
                )
        else:
            profile = os.getenv("CLOUDSCALE_PROFILE", "default")

        logger.info(f"Using profile {profile}")

        if not conf.has_section(profile):
            return dict()

        return dict(conf[profile])
