from typing import overload
from typing import TypeVar

WebSocketFrame = TypeVar["com.neovisionaries.ws.client.WebSocketFrame"]

class Websocket_Disconnected:
	"""
	"""
	serverFrame: WebSocketFrame
	clientFrame: WebSocketFrame
	isServer: bool

	@overload
	def __init__(self, serverFrame: WebSocketFrame, clientFrame: WebSocketFrame, isServer: bool) -> None:
		"""

		Args:
			isServer: 
			clientFrame: 
			serverFrame: 
		"""
		pass

	pass


