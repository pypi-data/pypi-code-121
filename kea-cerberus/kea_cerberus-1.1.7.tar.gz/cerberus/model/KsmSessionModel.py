from cerberus.model.AbstractModelResource import AbstractModelResource
from cerberus.entities.entities import KsmSession
from datetime import datetime

class KsmSessionModel(AbstractModelResource):
	"""docstring for KsmSessionModel"""
	def __init__(self, url):
		super(KsmSessionModel, self).__init__(url)
		self.url = url

	def add(self, id, active, connection_id, user_id, authentication_type_id, created_at, updated_at):
		ksmSession = KsmSession(id, active, connection_id, user_id, authentication_type_id, created_at, updated_at)
		self.insert(ksmSession)
		return ksmSession

	def get(self, token):
		ksmSession = self.session.query(KsmSession).filter(KsmSession.id == token).first()
		return ksmSession

	def update(self,token):
		date = datetime.now()
		ksmSession = self.session.query(KsmSession).filter(KsmSession.id == token).update({'active':False,'updated_at':date,'deleted_at':date})
		self.session.commit()
		self.session.close()

	def updateTime(self,token):
		date = datetime.now()
		ksmSession = self.session.query(KsmSession).filter(KsmSession.id == token).update({'updated_at':date})
		self.session.commit()
		self.session.close()