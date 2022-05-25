from abc import ABC, abstractmethod

class AbstractService(ABC):

	def __init__(self, context):
		self.context = context