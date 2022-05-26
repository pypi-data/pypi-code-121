from typing import overload


class TPSData:
	recvTime: float
	tps: float

	@overload
	def __init__(self, time: float, tps: float) -> None:
		pass

	pass


