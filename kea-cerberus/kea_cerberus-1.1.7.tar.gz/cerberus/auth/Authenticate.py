from cerberus.responses.FirebaseUserRS import FirebaseUserRS
from flask import Flask

from cerberus.responses.Response import Response
from cerberus.responses.BodyRS import BodyRS
from cerberus.responses.LoginClientRS import LoginClientRS
from cerberus.responses.SessionRS import SessionRS
from cerberus.responses.HeaderRS import HeaderRS
from cerberus.responses.CreateUserRS import CreateUserRS
from cerberus.responses.CreateUserAccessTokenRS import CreateUserAccessTokenRS
from cerberus.model.KsmClientModel import KsmClientModel
from cerberus.dtos.AuthenticationType import AuthenticationType
from cerberus.dtos.Error import Error
from cerberus.dtos.SecurityHash import SecurityHash
from cerberus.services.ConnectionService import ConnectionService
from cerberus.services.SessionService import SessionService
from cerberus.services.UserService import UserService
from cerberus.mappers.HeaderMapper import HeaderMapper
from cerberus.services.SecurityHashService import SecurityHashService

from cerberus.exceptions.exceptions import InvalidClientCredentialsException, InvalidUserCredentialsException, NotFoundUserException
from cerberus.exceptions.exceptions import InvalidClientConnectionException, ClientConnectionExpiredException, RequiredParamException, NullClientConnectionException
from cerberus.exceptions.exceptions import UserCredentialsExpiredException, InternalErrorException, MaxUserSessionException, InvalidUserSessionException, InvalidParamException
from cerberus.exceptions.exceptions import NotFoundRoleException, UserAlreadyExistException, SecurityHashExpiredException, InvalidSecurityHashException,FirebaseUserNotFoundException
from cerberus.utils.SecurityUtils import SecurityUtils

class Authenticate():

    def __init__(self, url):
        self.urlEngine = url

    #Method to create client connection
    def login(self, username, password):
        bodyRS = LoginClientRS(True)
        headerRS = HeaderRS()

        try:
            if username is None:
                raise RequiredParamException("username")

            if password is None:
                raise RequiredParamException("password")

            client = KsmClientModel(self.urlEngine).getClientByUsername(username)

            if client is None:
                raise InvalidClientCredentialsException()

            isValid = SecurityUtils().verify(username, password, client.getPassword())
            if not isValid:
                raise InvalidClientCredentialsException()

            connection = ConnectionService(self.urlEngine).createConnection(client)
            headerRS = HeaderRS(connection.getToken(), connection.getCreatedAt(), connection.getUpdatedAt())
            bodyRS.setConnection(connection)


        except (RequiredParamException, InvalidClientCredentialsException) as e:
            error = Error(e.getCode(), e.getMessage())
            bodyRS = LoginClientRS(False, error)

        response = Response(headerRS, bodyRS)
        return response

    def logout(self, request):
        bodyRS = BodyRS(True)
        headerRS = HeaderRS()

        try:
            connection = ConnectionService(self.urlEngine).removeConnection(request.getHeaderRQ().getToken())
            headerRS = HeaderRS(connection.getToken(), connection.getCreatedAt(), connection.getUpdatedAt())
        except (NullClientConnectionException, InvalidClientCredentialsException) as e:
            error = Error(e.getCode(), e.getMessage())
            bodyRS = BodyRS(False, error)

        response = Response(headerRS, bodyRS)
        return response

    def validate(self, request):
        bodyRS = BodyRS(True)
        headerRS = HeaderRS()

        try:
            connection = ConnectionService(self.urlEngine).validateConnection(request.getHeaderRQ().getToken())
            headerRS = HeaderRS(connection.getToken(), connection.getCreatedAt(), connection.getUpdatedAt())
        except (NullClientConnectionException, InvalidClientCredentialsException) as e:
            error = Error(e.getCode(), e.getMessage())
            bodyRS = BodyRS(False, error)

        response = Response(headerRS, bodyRS)
        return response

    #Method to create user connection
    def loginUser(self, request,firebaseCredential=None):
        headerRS = HeaderRS()
        sessionRS = SessionRS(True)
        loginUserRQ = request.getBodyRQ()

        #Validate request inputs
        #bodyRS = new BodyRS()
        #bodyRS = Util.validateRQ(loginUserRQ)

        #if bodyRS is None:
        #    response.setBodyRS(bodyRS)
        #    response.setHeaderRS(new HeaderRS(request.getHeaderRQ().getToken()))
        #    return response

        try:
            # Valid Connection Token
            connection = ConnectionService(self.urlEngine).validateConnection(request.getHeaderRQ().getToken())

            if loginUserRQ.getAuthenticationTypeId() == AuthenticationType.LOCAL:
                session = SessionService(self.urlEngine).createSessionByLocalAuth(connection, loginUserRQ.getUserName(), loginUserRQ.getToken())
            elif loginUserRQ.getAuthenticationTypeId() == AuthenticationType.GOOGLE:
                session = SessionService(self.urlEngine).createSessionByGoogleAuth(connection, loginUserRQ.getUserName(), loginUserRQ.getToken(),firebaseCredential=firebaseCredential)
            elif loginUserRQ.getAuthenticationTypeId() == AuthenticationType.FACEBOOK:
                session = SessionService(self.urlEngine).createSessionByFacebookAuth(connection, loginUserRQ.getToken())
            elif loginUserRQ.getAuthenticationTypeId() == AuthenticationType.TOKEN:
                session = SessionService(self.urlEngine).createSessionByTokenAuth(connection, loginUserRQ.getUserName(), loginUserRQ.getToken())
            else:
                raise InvalidParamException("AuthenticationTypeId")

            sessionRS.setSession(session)
            #sessionRS.getRoles().addAll(userServiceLocal.getUserRoles(session.getUserId()))
            headerRS = HeaderMapper.mapToHeader(session)

        except (InvalidSecurityHashException, SecurityHashExpiredException, InvalidParamException, UserCredentialsExpiredException, NullClientConnectionException, InvalidClientConnectionException, ClientConnectionExpiredException, InternalErrorException, InvalidUserCredentialsException, NotFoundUserException, MaxUserSessionException, InvalidUserSessionException) as e:
            error = Error(e.getCode(), e.getMessage())
            sessionRS = SessionRS(False, error)

        response = Response(headerRS, sessionRS)
        return response

    def createUser(self, request,firebaseCredential):
        headerRS = HeaderRS()
        try:
            createUserRQ = request.getBodyRQ()

            SecurityHashService(self.urlEngine).validateHash(createUserRQ.getSecurityToken().getBodyRS().getSecurityHash().getToken())

            user = UserService(self.urlEngine).createUser(createUserRQ.getUserName(), createUserRQ.getToken(), createUserRQ.getAuthenticationTypeId(), createUserRQ.getRoleId(),firebaseCredential)
            headerRS = HeaderRS(request.getHeaderRQ().getToken())

            createUserRS = CreateUserRS(True)
            createUserRS.setUser(user)
        except  (InternalErrorException , NotFoundRoleException , UserAlreadyExistException) as e:
            error = Error(e.getCode(), e.getMessage())
            createUserRS = CreateUserRS(False, error)


        response = Response(headerRS, createUserRS)
        return response

    def createUserCreateToken(self, request):
        headerRS = HeaderRS()
        try:
            securityHash = SecurityHashService(self.urlEngine).createHash(SecurityHash.CREATE_USER_TOKEN)
            headerRS = HeaderRS(request.getHeaderRQ().getToken())
            createUserAccessTokenRS = CreateUserAccessTokenRS(True)
            createUserAccessTokenRS.setSecurityHash(securityHash)
        except  (InternalErrorException , NotFoundRoleException , UserAlreadyExistException) as e:
            error = Error(e.getCode(), e.getMessage())
            createUserAccessTokenRS = CreateUserAccessTokenRS(False, error)

        response = Response(headerRS, createUserAccessTokenRS)
        return response

    def createUserAccessToken(self, request):
        headerRS = HeaderRS()
        try:
            createUserAccessTokenRQ = request.getBodyRQ()
            securityHash = UserService(self.urlEngine).createUserAccessToken(createUserAccessTokenRQ.getEmail())
            headerRS = HeaderRS(request.getHeaderRQ().getToken())
            createUserAccessTokenRS = CreateUserAccessTokenRS(True)
            createUserAccessTokenRS.setSecurityHash(securityHash)
        except  (InternalErrorException , NotFoundRoleException , UserAlreadyExistException) as e:
            error = Error(e.getCode(), e.getMessage())
            createUserAccessTokenRS = CreateUserAccessTokenRS(False, error)

        response = Response(headerRS, createUserAccessTokenRS)
        return response

    def validateFirebaseUser(self,uid):
        headerRS = HeaderRS()
        try:
            firebaseUser = UserService(self.urlEngine).isUserCreated(uid)
        except (FirebaseUserNotFoundException) as e:
            firebaseUser = FirebaseUserRS(False,Error(e.getCode(),e.getMessage()))

        return Response(headerRS,firebaseUser)
