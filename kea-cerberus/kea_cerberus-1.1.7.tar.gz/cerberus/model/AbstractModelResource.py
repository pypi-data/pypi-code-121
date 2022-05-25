from abc import ABC, abstractmethod
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

class AbstractModelResource(ABC):

	def __init__(self, url):
		self.engine = create_engine(url)
		self.session = Session(self.engine)
		self.session.expire_on_commit=False

	def update(self, obj):
		self.session.commit()

	def insert(self, obj):
		self.session.add(obj)
		self.session.commit()
