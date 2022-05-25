from flask import Flask
from datetime import datetime
import uuid

from cerberus.model.KsmConnectionModel import KsmConnectionModel
from cerberus.responses.Response import Response
from cerberus.dtos.Connection import Connection
from cerberus.mappers.ConnectionMapper import ConnectionMapper
from cerberus.exceptions.exceptions import InvalidClientConnectionException, ClientConnectionExpiredException
from cerberus.services.AbstractService import AbstractService
from cerberus.exceptions.exceptions import NullClientConnectionException

class ConnectionService(AbstractService):

    def __init__(self, url):
        super(ConnectionService, self).__init__(url)

    def removeConnection(self, token):
        if token is None:
            raise NullClientConnectionException()

        ksmConnection = KsmConnectionModel(self.urlEngine).get(token)
        if ksmConnection is None:
            raise InvalidClientConnectionException()

        ksmConnection.setUpdatedAt(datetime.now())
        ksmConnection.setActive(False)
        KsmConnectionModel(self.urlEngine).update(ksmConnection)
        return ConnectionMapper.mapToConnection(ksmConnection)

    def createConnection(self, client):
        token = str(uuid.uuid4())
        ksmConnection = KsmConnectionModel(self.urlEngine).add(token, client)
        return ConnectionMapper.mapToConnection(ksmConnection)

    def validateConnection(self, token):

        if token is None:
            raise NullClientConnectionException()

        ksmConnection = KsmConnectionModel(self.urlEngine).get(token)
        if ksmConnection is None:
            raise InvalidClientConnectionException()

        if ksmConnection.getActive() == False:
            raise ClientConnectionExpiredException()

        ksmConnection.setUpdatedAt(datetime.now())
        KsmConnectionModel(self.urlEngine).update(ksmConnection)
        return ConnectionMapper.mapToConnection(ksmConnection)

    def getValidConnection(self, token):
        if token is None:
            raise NullClientConnectionException()

        ksmConnection = KsmConnectionModel(self.urlEngine).get(token)

        if ksmConnection is None:
            raise InvalidClientConnectionException()

        if ksmConnection.getActive() == False:
            raise ClientConnectionExpiredException()

        ksmConnection.setUpdatedAt(datetime.now())
        KsmConnectionModel(self.urlEngine).update(ksmConnection)
        return ConnectionMapper.mapToConnection(ksmConnection)
