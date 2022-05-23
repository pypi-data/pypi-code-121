from datetime import datetime

import logging

from peek_core_user._private.PluginNames import userPluginTuplePrefix
from vortex.Tuple import addTupleType, Tuple, TupleField

logger = logging.getLogger(__name__)


@addTupleType
class UserLoggedInInfoTuple(Tuple):
    __tupleType__ = userPluginTuplePrefix + "UserLoggedInInfoTuple"

    loggedInDateTime: datetime = TupleField()
    userName: str = TupleField()
    deviceToken: str = TupleField()
    vehicle: str = TupleField()
    isFieldLogin: bool = TupleField()
