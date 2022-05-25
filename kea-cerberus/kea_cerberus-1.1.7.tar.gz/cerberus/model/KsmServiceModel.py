from cerberus.model.AbstractModelResource import AbstractModelResource
from cerberus.entities.entities import KsmService, KsmClientService, KsmUserService, KsmRoleService

class KsmServiceModel(AbstractModelResource):
	"""docstring for KsmServiceModel"""
	def __init__(self, url):
		super(KsmServiceModel, self).__init__(url)
		self.url = url

	def getServiceByName(self, name):
		ksmService = self.session.query(KsmService).filter(KsmService.name == name).first()
		return ksmService

	def getClientServiceById(self, serviceId, clientId):
		ksmClientService = self.session.query(KsmClientService).filter(KsmClientService.client_id == clientId).filter(KsmClientService.service_id == serviceId).first()
		return ksmClientService

	def getUserServiceById(self, serviceId, userId):
		ksmUserService = self.session.query(KsmUserService).filter(KsmUserService.user_id == userId).filter(KsmUserService.service_id == serviceId).first()
		return ksmUserService

	def getRoleServiceById(self, serviceId, roleId):
		ksmRoleService = self.session.query(KsmRoleService).filter(KsmRoleService.role_id == roleId).filter(KsmRoleService.service_id == serviceId).first()
		return ksmRoleService
