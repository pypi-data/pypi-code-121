from cerberus.model.AbstractModelResource import AbstractModelResource
from cerberus.entities.entities import KsmConnection
from datetime import datetime

class KsmConnectionModel(AbstractModelResource):
	"""docstring for KsmConnectionModel"""
	def __init__(self, url):
		super(KsmConnectionModel, self).__init__(url)
		self.url = url

	def add(self, token, client):
		ksmConnection = KsmConnection(token, True, client.getId(), datetime.now(), datetime.now())
		self.insert(ksmConnection)
		return ksmConnection

	def get(self, token):
		connection = self.session.query(KsmConnection).filter(KsmConnection.id == token).first()
		return connection