"""
Base class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

import i18n
import logging

# Make sure localisation is set up before any SDK-specific imports.
from fusion_platform.localise import Localise

Localise.setup()

import fusion_platform


class Base:
    """
    Base class used by all classes within the SDK to set up common elements.
    """

    def __init__(self):
        """
        Initialises the object.
        """

        # Set up localisation.
        Localise.setup()

        # Set up logging.
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(pathname)s:%(funcName)s:%(lineno)d - %(message)s')
        self._logger = logging.getLogger(fusion_platform.FUSION_PLATFORM_LOGGER)
        self._logger.debug('sdk %s (%s): %s', fusion_platform.__version__, fusion_platform.__version_date__, self.__class__.__name__)

    @classmethod
    def main(cls):
        """
        Main entry point when the package is executed from the command line.
        """
        print(i18n.t('fusion_platform.sdk'))
        print(i18n.t('fusion_platform.version', version=fusion_platform.__version__))
        print(i18n.t('fusion_platform.version_date', version_date=fusion_platform.__version_date__))
        print(i18n.t('fusion_platform.support'))


# Main entry point when the file is executed from the command line.
if __name__ == "__main__":
    Base.main()
