from cerberus.exceptions.exceptions import ServiceNotAllowedException, ClientServiceNotAllowedException, UserServiceNotAllowedException, NullClientConnectionException, InvalidClientConnectionException, ClientConnectionExpiredException
from cerberus.model.KsmUserModel import KsmUserModel
from cerberus.model.KsmServiceModel import KsmServiceModel
from cerberus.management.ConnectionExecuteService import ConnectionExecuteService
from cerberus.management.SessionExecuteService import SessionExecuteService
from cerberus.services.ConnectionService import ConnectionService
from cerberus.services.SessionService import SessionService
from cerberus.services.AbstractService import AbstractService

class AccessControlList(AbstractService):

    def __init__(self, url):
        super(AccessControlList, self).__init__(url)
        self.urlEngine=url

    def validateExecuteService(self,service):
        if isinstance(service, ConnectionExecuteService):
            return AccessControlList(self.urlEngine).validateConnectionExecuteService(service)
        elif isinstance(service, SessionExecuteService):
            return AccessControlList(self.urlEngine).validateSessionExecuteService(service)

    def validateConnectionExecuteService(self,service):
        connection = ConnectionService(self.urlEngine).getValidConnection(service.getRequest().getHeaderRQ().getToken())

        ksmService = KsmServiceModel(self.urlEngine).getServiceByName(service.__class__.__name__)
        if ksmService is None:
            raise ServiceNotAllowedException(service.__class__.__name__)

        ksmClientService = KsmServiceModel(self.urlEngine).getClientServiceById(connection.getClientId(), ksmService.getId())
        if ksmClientService is None:
            print("ksmClientService is None: " + service.__class__.__name__)
            raise ClientServiceNotAllowedException(service.__class__.__name__)

        return connection

    def validateSessionExecuteService(self,service):

        session = SessionService(self.urlEngine).getValidSession(service.getRequest().getHeaderRQ().getToken())
        connectionId = SessionService(self.urlEngine).getConnectionIdBySession(service.getRequest().getHeaderRQ().getToken())
        connection = ConnectionService(self.urlEngine).getValidConnection(connectionId)
        session.setConnection(connection)

        ksmService = KsmServiceModel(self.urlEngine).getServiceByName(service.__class__.__name__)
        if ksmService is None:
            raise ServiceNotAllowedException(service.__class__.__name__)

        ksmClientService = KsmServiceModel(self.urlEngine).getClientServiceById(ksmService.getId(), connection.getClientId())
        if ksmClientService is None:
            raise ClientServiceNotAllowedException(service.__class__.__name__)

        rolesUser = KsmUserModel(self.urlEngine).getRolesByUserId(session.getUserId())
        allowedExecution = False
        if not rolesUser is None:
            for roleUser in rolesUser:
                ksmRoleService = KsmServiceModel(self.urlEngine).getRoleServiceById(ksmService.getId(), roleUser.getRoleId())
                if not ksmRoleService is None:
                    allowedExecution = True

        if allowedExecution == True:
            return session

        ksmUserService = KsmServiceModel(self.urlEngine).getUserServiceById(ksmClientService.getServiceId(), session.getUserId())
        if ksmUserService is None:
            raise UserServiceNotAllowedException(service.__class__.__name__)

        return session
