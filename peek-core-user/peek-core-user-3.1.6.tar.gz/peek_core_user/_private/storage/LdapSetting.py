import logging

from sqlalchemy import Column, Boolean
from sqlalchemy import Integer, String
from vortex.Tuple import Tuple, addTupleType

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user._private.storage.DeclarativeBase import DeclarativeBase

logger = logging.getLogger(__name__)


@addTupleType
class LdapSetting(Tuple, DeclarativeBase):
    """LdapSetting

    This table stores connetions and settings to LDAP servers

    """

    __tupleType__ = userPluginTuplePrefix + "LdapSettingTuple"
    __tablename__ = "LdapSetting"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ldapTitle = Column(String, nullable=False, unique=True)
    ldapDomain = Column(String, nullable=False)
    ldapUri = Column(String, nullable=False)
    ldapCNFolders = Column(String, nullable=True)
    ldapOUFolders = Column(String, nullable=True)
    ldapGroups = Column(String, nullable=True)

    adminEnabled = Column(Boolean, nullable=False, server_default="0")
    desktopEnabled = Column(Boolean, nullable=False, server_default="0")
    mobileEnabled = Column(Boolean, nullable=False, server_default="0")
