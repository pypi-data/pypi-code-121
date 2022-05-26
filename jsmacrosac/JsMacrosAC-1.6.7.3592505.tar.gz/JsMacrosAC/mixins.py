from typing import TypeVar

from .EventContainer import EventContainer
from .BaseEvent import BaseEvent
from .MixinSignEditScreen import MixinSignEditScreen
from .MixinHungerManager import MixinHungerManager
from .MixinRecipeBookWidget import MixinRecipeBookWidget
from .MixinFontManager import MixinFontManager
from .MixinChunkSelection import MixinChunkSelection
from .IMixinEntity import IMixinEntity
from .MixinLivingEntity import MixinLivingEntity
from .MixinMinecraftClient import MixinMinecraftClient
from .MixinPackedIntegerArray import MixinPackedIntegerArray
from .MixinClientPlayNetworkHandler import MixinClientPlayNetworkHandler
from .MixinDisconnectedScreen import MixinDisconnectedScreen
from .MixinMerchantEntity import MixinMerchantEntity
from .MixinSplashOverlay import MixinSplashOverlay
from .MixinTrueTypeFont import MixinTrueTypeFont
from .MixinHorseScreen import MixinHorseScreen
from .MixinCreativeInventoryScreen import MixinCreativeInventoryScreen
from .MixinChatHud import MixinChatHud
from .MixinPalettedContainer import MixinPalettedContainer
from .MixinLoomScreen import MixinLoomScreen
from .MixinItemCooldownManager import MixinItemCooldownManager
from .MixinHandledScreen import MixinHandledScreen
from .MixinClientWorld import MixinClientWorld
from .MixinSoundSystem import MixinSoundSystem
from .MixinBeaconScreen import MixinBeaconScreen
from .MixinPlayerListHud import MixinPlayerListHud
from .MixinItemCooldownEntry import MixinItemCooldownEntry
from .MixinFontStorage import MixinFontStorage
from .MixinBossBarHud import MixinBossBarHud
from .MixinEntity import MixinEntity
from .MixinRecipeBookResults import MixinRecipeBookResults
from .MixinMerchantScreen import MixinMerchantScreen
from .MixinStyleSerializer import MixinStyleSerializer
from .MixinScreen import MixinScreen
from .MixinPalettedContainerData import MixinPalettedContainerData

File = TypeVar["java.io.File"]

