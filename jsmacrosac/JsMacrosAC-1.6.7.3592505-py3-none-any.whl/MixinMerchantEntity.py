from typing import overload
from .IMerchantEntity import IMerchantEntity


class MixinMerchantEntity(IMerchantEntity):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_refreshOffers(self) -> None:
		pass

	pass


