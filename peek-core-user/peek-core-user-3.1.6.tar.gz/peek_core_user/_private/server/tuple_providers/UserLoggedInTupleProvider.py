import logging

from peek_core_user._private.server.api.UserApi import UserApi
from peek_core_user._private.storage.InternalUserTuple import InternalUserTuple
from peek_core_user._private.storage.UserLoggedIn import UserLoggedIn
from peek_core_user._private.tuples.UserLoggedInTuple import UserLoggedInTuple
from peek_core_user.tuples.UserListItemTuple import UserListItemTuple
from sqlalchemy.orm.exc import NoResultFound
from twisted.internet.defer import Deferred
from vortex.DeferUtil import deferToThreadWrapWithLogger
from vortex.Payload import Payload
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TuplesProviderABC

logger = logging.getLogger(__name__)


class UserLoggedInTupleProvider(TuplesProviderABC):
    def __init__(self, dbSessionCreator, ourApi: UserApi):
        self._dbSessionCreator = dbSessionCreator
        self._ourApi = ourApi

        from peek_core_user.server.UserApiABC import UserApiABC

        assert isinstance(self._ourApi, UserApiABC), "We didn't get a UserApiABC"

    @deferToThreadWrapWithLogger(logger)
    def makeVortexMsg(self, filt: dict, tupleSelector: TupleSelector) -> Deferred:
        deviceToken = tupleSelector.selector["deviceToken"]

        session = self._dbSessionCreator()
        try:
            userLoggedIn = (
                session.query(UserLoggedIn)
                .filter(UserLoggedIn.deviceToken == deviceToken)
                .one()
            )

            internalUserTuple = (
                session.query(InternalUserTuple)
                .filter(InternalUserTuple.userName == userLoggedIn.userName)
                .one()
            )

            userDetails = UserListItemTuple(
                userId=internalUserTuple.userName,
                displayName=internalUserTuple.userTitle,
            )

        except NoResultFound:
            userDetails = None

        finally:
            session.close()

        tuples = [UserLoggedInTuple(deviceToken=deviceToken, userDetails=userDetails)]

        payloadEnvelope = Payload(filt=filt, tuples=tuples).makePayloadEnvelope()
        vortexMsg = payloadEnvelope.toVortexMsg()
        return vortexMsg
