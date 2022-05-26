from typing import TypeVar

from .EventContainer import EventContainer
from .BaseEvent import BaseEvent
from .FChat import FChat
from .FWrapper import FWrapper
from .FPlayer import FPlayer
from .FRequest import FRequest
from .FTime import FTime
from .FKeyBind import FKeyBind
from .FHud import FHud
from .FJsMacros import FJsMacros
from .FFS import FFS
from .FReflection import FReflection
from .FClient import FClient
from .FWorld import FWorld
from .FGlobalVars import FGlobalVars
from .FPositionCommon import FPositionCommon

File = TypeVar["java.io.File"]



Chat = FChat()
JavaWrapper = FWrapper()
Player = FPlayer()
Request = FRequest()
Time = FTime()
KeyBind = FKeyBind()
Hud = FHud()
JsMacros = FJsMacros()
FS = FFS()
Reflection = FReflection()
Client = FClient()
World = FWorld()
GlobalVars = FGlobalVars()
PositionCommon = FPositionCommon()
context = EventContainer()
file = File()
event = BaseEvent()
