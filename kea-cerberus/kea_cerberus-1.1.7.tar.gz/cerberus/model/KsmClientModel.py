from cerberus.model.AbstractModelResource import AbstractModelResource
from cerberus.entities.entities import KsmClient

class KsmClientModel(AbstractModelResource):
	"""docstring for KsmClientModel"""
	def __init__(self, url):
		super(KsmClientModel, self).__init__(url)
		self.url = url

	def getClientByUsername(self, username):
		client = self.session.query(KsmClient).filter(KsmClient.username == username).filter(KsmClient.active == True).first()
		return client
