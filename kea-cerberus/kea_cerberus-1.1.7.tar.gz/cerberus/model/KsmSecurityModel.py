from cerberus.model.AbstractModelResource import AbstractModelResource
from cerberus.entities.entities import KsmSecurityHash, KsmSecurityHashType
from datetime import datetime
import uuid

class KsmSecurityModel(AbstractModelResource):
	"""docstring for KsmSecurityModel"""
	def __init__(self, url):
		super(KsmSecurityModel, self).__init__(url)
		self.url = url

	def getSecurityHashType(self, type):
		ksmSecurityHashType = self.session.query(KsmSecurityHashType).filter(KsmSecurityHashType.id == type).first()
		return ksmSecurityHashType

	def addSecurityHash(self, type, used, active):
		createdAt = datetime.now()
		ksmSecurityHash = KsmSecurityHash()
		ksmSecurityHash.setToken(str(uuid.uuid4()))
		ksmSecurityHash.setUsed(used)
		ksmSecurityHash.setActive(active)
		ksmSecurityHash.setSecurityHashTypeId(type)
		ksmSecurityHash.setCreatedAt(createdAt)
		ksmSecurityHash.setUpdatedAt(createdAt)
		self.insert(ksmSecurityHash)
		return ksmSecurityHash

	def getSecurityHash(self, token):
		ksmSecurityHash = self.session.query(KsmSecurityHash).filter(KsmSecurityHash.token == token).first()
		return ksmSecurityHash