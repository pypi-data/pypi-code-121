# Builtin modules
# Local modules
# Program
class BaseRPCError(Exception):
	def __init__(self, typ:str, message:str):
		self.message = "{}: {}".format(typ, message)
		super().__init__(self.message)

class InitializationError(BaseRPCError):
	def __init__(self, message:str):
		super().__init__("Initialization error", message)

class SocketError(BaseRPCError):
	def __init__(self, message:str):
		super().__init__("Socket error", message)

class MessageError(BaseRPCError):
	def __init__(self, message:str):
		super().__init__("Message error", message)

class RequestError(BaseRPCError):
	def __init__(self, message:str):
		super().__init__("Request error", message)

class ResponseError(BaseRPCError):
	def __init__(self, message:str):
		super().__init__("Response error", message)
