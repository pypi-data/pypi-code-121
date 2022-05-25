from datetime import datetime
import uuid

from cerberus.dtos.SecurityHash import SecurityHash
from cerberus.model.KsmSecurityModel import KsmSecurityModel
from cerberus.mappers.SecurityHashMapper import SecurityHashMapper
from cerberus.exceptions.exceptions import InvalidParamException, RequiredParamException, SecurityHashExpiredException, InvalidSecurityHashException
from cerberus.services.AbstractService import AbstractService

class SecurityHashService(AbstractService):

    def __init__(self, url):
        super(SecurityHashService, self).__init__(url)

    def createHash(self, type):

        if type is None:
            raise RequiredParamException("type")

        ksmSecurityHashType = KsmSecurityModel(self.urlEngine).getSecurityHashType(type)

        if ksmSecurityHashType is None:
            raise InvalidParamException("type")

        ksmSecurityHash = KsmSecurityModel(self.urlEngine).addSecurityHash(type, False, True)

        return SecurityHashMapper.mapToSecurityHash(ksmSecurityHash);

    def validateHash(self, token):

        if token is None:
            raise RequiredParamException("token")

        ksmSecurityHash = KsmSecurityModel(self.urlEngine).getSecurityHash(token)
        if ksmSecurityHash is None:
            raise InvalidSecurityHashException()

        if ksmSecurityHash.getActive() == False or ksmSecurityHash.getUsed() == True:
            raise SecurityHashExpiredException()

        ksmSecurityHash.setUsed(True)
        KsmSecurityModel(self.urlEngine).update(ksmSecurityHash)
        return SecurityHashMapper.mapToSecurityHash(ksmSecurityHash);
