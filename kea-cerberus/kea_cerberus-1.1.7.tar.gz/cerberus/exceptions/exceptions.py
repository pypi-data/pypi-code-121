

class AbstractException(Exception):

    __code=0;
    __message='';

    def __init__(self, code, message):
        Exception.__init__(self,message)
        self.__code = code;
        self.__message = message;

    def getCode(self):
        return self.__code

    def getMessage(self):
        return self.__message

    def to_dict(self):
        rv = dict()
        rv['code'] = self.__code
        rv['message'] = self.__message
        return rv

class InvalidClientCredentialsException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2001, "The client credentials are invalid.")

class InvalidClientConnectionException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2003, "The client information is invalid.")

class NullParamsException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,1010, "The params are required.")

class RequiredParamException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,1011, "The %s param is required." % args[0])

class InternalErrorException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,5000, "Internal Error Exception. %s" % args[0])

class InvalidUserCredentialsException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2007, "The user credentials are invalid.")

class NotFoundUserException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,1021, "User Not found exception.")

class NullClientConnectionException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2002, "Client connection not found.")

class NullClientSessionException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2003, "Client session not found.")

class ClientConnectionExpiredException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2004, "The client connection has expired.")

class ClientSessionExpiredException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2005, "The client session has expired.")

class UserCredentialsExpiredException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2018, "The user credentials has expired.")

class MaxUserSessionException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2010, "Too many user sessions.")

class InvalidUserSessionException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2016, "The invalid user's session exception.")

class InvalidParamException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,1000, "The param is invalid: %s " % args[0])

class UserAlreadyExistException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,5010, "The user already exists.")

class NotFoundRoleException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,1031, "Not found role exception.")

class InvalidSecurityHashException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,1200, "Security hash is invalid.")

class SecurityHashExpiredException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,1204, "Security hash has expired.")

class ClientServiceNotAllowedException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2015, "The client not allowed %s service." % args[0])

class ServiceNotAllowedException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2015, "The service not allowed %s." % args[0])

class UserServiceNotAllowedException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,2018, "User not allowed to execute %s service." % args[0])

class FirebaseUserNotFoundException(AbstractException):
    def __init__(self,*args,**kwargs):
        AbstractException.__init__(self,3000, "User not found.")
