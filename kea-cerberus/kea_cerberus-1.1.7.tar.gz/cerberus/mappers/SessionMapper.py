from cerberus.dtos.Session import Session
from cerberus.entities.entities import KsmRoleUser

class SessionMapper():
    def mapToSession(ksmSession, connection,roleUser):
        return Session(ksmSession.getId(), ksmSession.getUserId(), ksmSession.getActive(), ksmSession.getAuthenticationTypeId(), roleUser, connection, ksmSession.getCreatedAt(), ksmSession.getUpdatedAt())
