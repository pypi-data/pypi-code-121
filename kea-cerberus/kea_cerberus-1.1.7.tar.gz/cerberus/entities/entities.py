from flask import Flask
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String, DateTime, Boolean

Base = declarative_base()

class KsmConnection(Base):
    __tablename__ = 'ksm_connection'
    id = Column(String(60), primary_key=True)
    active = Column(Boolean, nullable=False)
    client_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def __init__(self, id, active, client_id,created_at, updated_at, deleted_at=None):
       self.id = id
       self.active = active
       self.client_id = client_id
       self.created_at = created_at
       self.updated_at = updated_at
       self.deleted_at = deleted_at

    def getId(self):
       return self.id

    def getActive(self):
       return self.active

    def setActive(self, active):
       self.active = active

    def getClientId(self):
       return self.client_id

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def setUpdatedAt(self, updated_at):
       self.updated_at = updated_at

    def getDeletedAt(self):
       return self.deleted_at

class KsmClient(Base):
    __tablename__ = 'ksm_client'
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(150), nullable=False)

    def getId(self):
       return self.id

    def getUsername(self):
       return self.username

    def getPassword(self):
       return self.password

    def getActive(self):
      return self.active

class KsmSession(Base):
    __tablename__ = 'ksm_session'
    id = Column(String(60), primary_key=True)
    active = Column(Boolean, nullable=False)
    connection_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    authentication_type_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def __init__(self, id, active, connection_id, user_id, authentication_type_id, created_at, updated_at, deleted_at=None):
       self.id = id
       self.active = active
       self.connection_id = connection_id
       self.user_id = user_id
       self.authentication_type_id = authentication_type_id
       self.created_at = created_at
       self.updated_at = updated_at
       self.deleted_at = deleted_at

    def getId(self):
       return self.id

    def getActive(self):
       return self.active
      
    def setActive(self,active):
       self.active = active

    def getConnectionId(self):
       return self.connection_id

    def getUserId(self):
       return self.user_id

    def getAuthenticationTypeId(self):
       return self.authentication_type_id

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def setUpdatedAt(self, updated_at):
       self.updated_at = updated_at

    def getDeletedAt(self):
       return self.deleted_at

    def setDeletedAt(self,deleted_at):
       self.deleted_at = deleted_at
class KsmUserAuthenticationType(Base):
    __tablename__ = 'ksm_user_authentication_type'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    token = Column(String(1500), nullable=False)
    authentication_type_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def getId(self):
       return self.id

    def getUserName(self):
       return self.username

    def getToken(self):
       return self.token

    def getAuthenticationTypeId(self):
       return self.authentication_type_id

    def getUserId(self):
       return self.user_id

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def setId(self, id):
       self.id = id

    def setUserName(self, username):
       self.username = username

    def setToken(self, token):
       self.token = token

    def setAuthenticationTypeId(self, authentication_type_id):
       self.authentication_type_id = authentication_type_id

    def setUserId(self, user_id):
       self.user_id = user_id

    def setCreatedAt(self, created_at):
       self.created_at = created_at

    def setUpdatedAt(self, updated_at):
       self.updated_at = updated_at

    def getDeletedAt(self):
       return self.deleted_at

class KsmRole(Base):
    __tablename__ = 'ksm_role'
    id = Column(Integer, primary_key=True)
    description = Column(String(300), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def getId(self):
       return self.id

    def getDescription(self):
       return self.description

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def getDeletedAt(self):
       return self.deleted_at

class KsmUser(Base):
    __tablename__ = 'ksm_user'
    id = Column(String(60), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def setId(self, id):
       self.id = id

    def getId(self):
       return self.id

    def setCreatedAt(self, created_at):
       self.created_at = created_at

    def setUpdatedAt(self, updated_at):
       self.updated_at = updated_at

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def getDeletedAt(self):
       return self.deleted_at

class KsmRoleUser(Base):
    __tablename__ = 'ksm_role_user'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def getId(self):
       return self.id

    def getRoleId(self):
       return self.role_id

    def getUserId(self):
       return self.user_id

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def getDeletedAt(self):
       return self.deleted_at

    def setRoleId(self, role_id):
       self.role_id = role_id

    def setUserId(self, user_id):
       self.user_id = user_id

    def setCreatedAt(self, created_at):
       self.created_at = created_at

    def setUpdatedAt(self, updated_at):
       self.updated_at = updated_at

class KsmRoleService(Base):
    __tablename__ = 'ksm_role_service'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, nullable=False)
    service_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def getId(self):
       return self.id

    def getRoleId(self):
       return self.role_id

    def getServiceId(self):
       return self.service_id

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def getDeletedAt(self):
       return self.deleted_at

    def setRoleId(self, role_id):
       self.role_id = role_id

    def setServiceId(self, user_id):
       self.service_id = user_id

    def setCreatedAt(self, created_at):
       self.created_at = created_at

    def setUpdatedAt(self, updated_at):
       self.updated_at = updated_at

class KsmSecurityHashType(Base):
    __tablename__ = 'ksm_security_hash_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)

    def getId(self):
       return self.id

    def getName(self):
       return self.name

    def getCreatedAt(self):
       return self.created_at

class KsmSecurityHash(Base):

    __tablename__ = 'ksm_security_hash'
    id = Column(Integer, primary_key=True)
    token = Column(String(255), nullable=False)
    used = Column(Boolean, nullable=False)
    active = Column(Boolean, nullable=False)
    security_hash_type_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def getId(self):
       return self.id

    def getToken(self):
       return self.token

    def getUsed(self):
       return self.used

    def getActive(self):
       return self.active

    def getSecurityHashTypeId(self):
       return self.security_hash_type_id

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def getDeletedAt(self):
       return self.deleted_at

    def setToken(self, token):
       self.token = token

    def setSecurityHashTypeId(self, security_hash_type_id):
       self.security_hash_type_id = security_hash_type_id

    def setUsed(self, used):
       self.used = used

    def setActive(self, active):
       self.active = active

    def setCreatedAt(self, created_at):
       self.created_at = created_at

    def setUpdatedAt(self, updated_at):
       self.updated_at = updated_at

class KsmClientService(Base):

    __tablename__ = 'ksm_client_service'
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, nullable=False)
    service_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def getId(self):
       return self.id

    def getClientId(self):
       return self.client_id

    def getServiceId(self):
       return self.service_id

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def getDeletedAt(self):
       return self.deleted_at

class KsmUserService(Base):

    __tablename__ = 'ksm_user_service'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    service_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def getId(self):
       return self.id

    def getUserId(self):
       return self.user_id

    def getServiceId(self):
       return self.service_id

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def getDeletedAt(self):
       return self.deleted_at

class KsmService(Base):

    __tablename__ = 'ksm_service'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=False)

    def getId(self):
       return self.id

    def getName(self):
       return self.name

    def getDescription(self):
       return self.description

    def getCreatedAt(self):
       return self.created_at

    def getUpdatedAt(self):
       return self.updated_at

    def getDeletedAt(self):
       return self.deleted_at
