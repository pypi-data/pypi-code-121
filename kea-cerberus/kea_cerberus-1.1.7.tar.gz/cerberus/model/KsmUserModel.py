from cerberus.model.AbstractModelResource import AbstractModelResource
from cerberus.entities.entities import KsmUserAuthenticationType, KsmUser, KsmRole, KsmRoleUser
from cerberus.exceptions.exceptions import FirebaseUserNotFoundException


class KsmUserModel(AbstractModelResource):
	"""docstring for KsmUserModel"""
	def __init__(self, url):
		super(KsmUserModel, self).__init__(url)
		self.url = url

	def addUser(self, id, createdAt, updatedAt):
		ksmUser = KsmUser()
		ksmUser.setId(id)
		ksmUser.setCreatedAt(createdAt)
		ksmUser.setUpdatedAt(updatedAt)
		self.insert(ksmUser)
		return ksmUser

	def getUserAuthenticationType(self, userName, authenticationTypeId):
		kuat = self.session.query(KsmUserAuthenticationType).filter(KsmUserAuthenticationType.username == userName).filter(KsmUserAuthenticationType.authentication_type_id == authenticationTypeId).first()
		return kuat

	def getUserAuthenticationTypeByUsername(self, userName):
		kuat = self.session.query(KsmUserAuthenticationType).filter(KsmUserAuthenticationType.username == userName).first()
		return kuat

	def getUserAuthenticationTypeByUserId(self, userId, authenticationTypeId):
		kuat = self.session.query(KsmUserAuthenticationType).filter(KsmUserAuthenticationType.user_id == userId).filter(KsmUserAuthenticationType.authentication_type_id == authenticationTypeId).first()
		return kuat

	def addUserAuthenticationType(self,authenticationTypeId, userId, userName, token, createdAt, updatedAt):
		ksmUserAuthenticationType = KsmUserAuthenticationType()
		ksmUserAuthenticationType.setAuthenticationTypeId(authenticationTypeId)
		ksmUserAuthenticationType.setUserId(userId)
		ksmUserAuthenticationType.setUserName(userName)
		ksmUserAuthenticationType.setCreatedAt(createdAt)
		ksmUserAuthenticationType.setUpdatedAt(updatedAt)
		ksmUserAuthenticationType.setToken(token)
		self.insert(ksmUserAuthenticationType)
		return ksmUserAuthenticationType

	def getUserById(self,id):
		ksmUser = self.session.query(KsmUser).filter(KsmUser.id == id).first()
		return ksmUser

	def addUserRole(self, id, roleId, createdAt, updatedAt):
		
		ksmRoleUser = KsmRoleUser()
		ksmRoleUser.setUserId(id)
		ksmRoleUser.setRoleId(roleId)
		ksmRoleUser.setCreatedAt(createdAt)
		ksmRoleUser.setUpdatedAt(updatedAt)
		self.insert(ksmRoleUser)
		return ksmRoleUser

	def getRoleById(self,id):
		ksmUser = self.session.query(KsmRole).filter(KsmRole.id == id).first()
		return ksmUser

	def getRolesByUserId(self,userId):
		rolesUser = self.session.query(KsmRoleUser).filter(KsmRoleUser.user_id == userId).all()
		return rolesUser
