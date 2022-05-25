from cerberus.dtos.Connection import Connection

class ConnectionMapper():
    def mapToConnection(ksmConnection):
        return Connection(ksmConnection.getId(), ksmConnection.getClientId(), ksmConnection.getActive(), ksmConnection.getCreatedAt(), ksmConnection.getUpdatedAt())
