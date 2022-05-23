import logging

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from peek_core_user.tuples.UserDetailTuple import UserDetailTuple
from vortex.Tuple import Tuple
from vortex.Tuple import TupleField
from vortex.Tuple import addTupleType

logger = logging.getLogger(__name__)


@addTupleType
class DeviceWithUserDetailsTuple(Tuple):
    """Field device tokens with logged-ion user details

    This tuple is sent to index peek-core-search for field crew/device
    related searches
    """

    __tupleType__ = userPluginTuplePrefix + "DeviceWithUserDetailsTuple"

    userDetails: UserDetailTuple = TupleField()
    deviceToken: str = TupleField()
