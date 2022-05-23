"""
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
 *
"""
import logging

from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC
from peek_platform.file_config.PeekFileConfigDocBuildMixin import (
    PeekFileConfigDocBuildMixin,
)
from peek_platform.file_config.PeekFileConfigFrontendDirMixin import (
    PeekFileConfigFrontendDirMixin,
)
from peek_platform.file_config.PeekFileConfigHttpServerMixin import (
    PeekFileConfigHttpMixin,
)
from peek_platform.file_config.PeekFileConfigOsMixin import PeekFileConfigOsMixin
from peek_platform.file_config.PeekFileConfigPeekServerClientMixin import (
    PeekFileConfigPeekServerClientMixin,
)
from peek_platform.file_config.PeekFileConfigPlatformMixin import (
    PeekFileConfigPlatformMixin,
)

logger = logging.getLogger(__name__)


class PeekClientConfig(
    PeekFileConfigABC,
    PeekFileConfigPeekServerClientMixin,
    PeekFileConfigPlatformMixin,
    PeekFileConfigOsMixin,
    PeekFileConfigFrontendDirMixin,
    PeekFileConfigDocBuildMixin,
):
    """
    This class creates a basic client configuration
    """

    def __init__(self):
        super().__init__()
        self.officeHttpServer = PeekFileConfigHttpMixin(self, "office", 8002)
