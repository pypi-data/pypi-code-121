from cerberus.exceptions.exceptions import InvalidUserSessionException, ServiceNotAllowedException, ClientServiceNotAllowedException, UserServiceNotAllowedException, NullClientConnectionException, InvalidClientConnectionException, ClientConnectionExpiredException
from cerberus.responses.Response import Response
from cerberus.responses.BodyRS import BodyRS
from cerberus.requests.Request import Request
from cerberus.responses.HeaderRS import HeaderRS
from cerberus.acl.AccessControlList import AccessControlList
from cerberus.dtos.Error import Error
class SessionManager():

    def execute(self, service):
        headerRS = HeaderRS(service.getRequest().getHeaderRQ().getToken())
        try:
            cso = AccessControlList.validateExecuteService(service)
            service.beforeExecute(cso)
            bodyRS = service.execute(cso)
            service.afterExecute(cso)
        except (InvalidUserSessionException, ServiceNotAllowedException, ClientServiceNotAllowedException, UserServiceNotAllowedException, NullClientConnectionException, InvalidClientConnectionException, ClientConnectionExpiredException) as e:
            error = Error(e.getCode(), e.getMessage())
            bodyRS = BodyRS(False, error)

        response = Response(headerRS, bodyRS)
        return response
