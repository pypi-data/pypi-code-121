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
from peek_platform.file_config.PeekFileConfigOsMixin import PeekFileConfigOsMixin
from peek_platform.file_config.PeekFileConfigPlatformMixin import (
    PeekFileConfigPlatformMixin,
)
from peek_platform.file_config.PeekFileConfigSqlAlchemyMixin import (
    PeekFileConfigSqlAlchemyMixin,
)

logger = logging.getLogger(__name__)


class PeekStorageConfig(
    PeekFileConfigABC,
    PeekFileConfigOsMixin,
    PeekFileConfigPlatformMixin,
    PeekFileConfigSqlAlchemyMixin,
):
    """
    This class creates a server configuration
    """

    def __init__(self):
        super().__init__()
