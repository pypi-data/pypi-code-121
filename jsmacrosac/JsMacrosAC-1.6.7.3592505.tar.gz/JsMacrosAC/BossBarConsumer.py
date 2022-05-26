from typing import overload
from typing import TypeVar

BossBar_Style = TypeVar["net.minecraft.entity.boss.BossBar.Style"]
Text = TypeVar["net.minecraft.text.Text"]
BossBarS2CPacket_Consumer = TypeVar["net.minecraft.network.packet.s2c.play.BossBarS2CPacket.Consumer"]
UUID = TypeVar["java.util.UUID"]
BossBar_Color = TypeVar["net.minecraft.entity.boss.BossBar.Color"]

class BossBarConsumer(BossBarS2CPacket_Consumer):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def add(self, uuid: UUID, name: Text, percent: float, color: BossBar_Color, style: BossBar_Style, darkenSky: bool, dragonMusic: bool, thickenFog: bool) -> None:
		pass

	@overload
	def remove(self, uuid: UUID) -> None:
		pass

	@overload
	def updateProgress(self, uuid: UUID, percent: float) -> None:
		pass

	@overload
	def updateName(self, uuid: UUID, name: Text) -> None:
		pass

	@overload
	def updateStyle(self, id: UUID, color: BossBar_Color, style: BossBar_Style) -> None:
		pass

	@overload
	def updateProperties(self, uuid: UUID, darkenSky: bool, dragonMusic: bool, thickenFog: bool) -> None:
		pass

	pass


