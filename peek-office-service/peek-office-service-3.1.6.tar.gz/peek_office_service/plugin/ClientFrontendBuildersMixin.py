import logging

import os

from peek_platform.build_doc.DocBuilder import DocBuilder
from peek_platform.build_frontend.WebBuilder import WebBuilder

logger = logging.getLogger(__name__)


class ClientFrontendBuildersMixin:
    def _buildMobile(self, loadedPlugins):
        # --------------------
        # Prepare the Peek Mobile

        from peek_platform import PeekPlatformConfig

        try:
            import peek_office_app

            mobileProjectDir = os.path.dirname(peek_office_app.__file__)

        except:
            logger.warning(
                "Skipping builds of peek-office-app" ", the package can not be imported"
            )
            return

        officeWebBuilder = WebBuilder(
            mobileProjectDir,
            "peek-office-app",
            PeekPlatformConfig.config,
            loadedPlugins,
        )
        yield officeWebBuilder.build()

    def _buildDesktop(self, loadedPlugins):
        # --------------------
        # Prepare the Peek Desktop
        from peek_platform import PeekPlatformConfig

        try:
            import peek_office_app

            desktopProjectDir = os.path.dirname(peek_office_app.__file__)

        except:
            logger.warning(
                "Skipping builds of peek-office-app" ", the package can not be imported"
            )
            return

        officeWebBuilder = WebBuilder(
            desktopProjectDir,
            "peek-office-app",
            PeekPlatformConfig.config,
            loadedPlugins,
        )
        yield officeWebBuilder.build()

    def _buildDocs(self, loadedPlugins):
        # --------------------
        # Prepare the User Docs
        from peek_platform import PeekPlatformConfig

        try:
            import peek_office_doc

            docProjectDir = os.path.dirname(peek_office_doc.__file__)

        except:
            logger.warning(
                "Skipping builds of peek_office_doc" ", the package can not be imported"
            )
            return

        docBuilder = DocBuilder(
            docProjectDir, "peek-office-doc", PeekPlatformConfig.config, loadedPlugins
        )
        yield docBuilder.build()
