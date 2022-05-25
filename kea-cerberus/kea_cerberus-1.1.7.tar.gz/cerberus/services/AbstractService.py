from abc import ABC, abstractmethod

class AbstractService(ABC):

	def __init__(self, url):
		self.urlEngine = url