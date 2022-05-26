from typing import overload
from typing import List
from typing import TypeVar
from .RenderCommon_Text import RenderCommon_Text
from .RenderCommon_Rect import RenderCommon_Rect
from .RenderCommon_Item import RenderCommon_Item
from .RenderCommon_Image import RenderCommon_Image
from .RenderCommon_RenderElement import RenderCommon_RenderElement
from .TextHelper import TextHelper
from .ItemStackHelper import ItemStackHelper
from .MethodWrapper import MethodWrapper

T = TypeVar("T")
MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class IDraw2D:
	"""
	Since: 1.2.7 
	"""

	@overload
	def getWidth(self) -> int:
		"""
		Since: 1.2.7 

		Returns:
			screen width 
		"""
		pass

	@overload
	def getHeight(self) -> int:
		"""
		Since: 1.2.7 

		Returns:
			screen height 
		"""
		pass

	@overload
	def getTexts(self) -> List[RenderCommon_Text]:
		"""
		Since: 1.2.7 

		Returns:
			text elements 
		"""
		pass

	@overload
	def getRects(self) -> List[RenderCommon_Rect]:
		"""
		Since: 1.2.7 

		Returns:
			rect elements 
		"""
		pass

	@overload
	def getItems(self) -> List[RenderCommon_Item]:
		"""
		Since: 1.2.7 

		Returns:
			item elements 
		"""
		pass

	@overload
	def getImages(self) -> List[RenderCommon_Image]:
		"""
		Since: 1.2.7 

		Returns:
			image elements 
		"""
		pass

	@overload
	def getElements(self) -> List[RenderCommon_RenderElement]:
		"""
		Since: 1.2.9 

		Returns:
			a read only copy of the list of all elements added by scripts. 
		"""
		pass

	@overload
	def removeElement(self, e: RenderCommon_RenderElement) -> T:
		"""removes any element regardless of type.\n
		Since: 1.2.9 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def reAddElement(self, e: RenderCommon_RenderElement) -> RenderCommon_RenderElement:
		"""re-add an element you removed with IDraw2D#removeElement(xyz.wagyourtail.jsmacros.client.api.sharedclasses.RenderCommon.RenderElement)\n
		Since: 1.2.9 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def addText(self, text: str, x: int, y: int, color: int, shadow: bool) -> RenderCommon_Text:
		"""
		Since: 1.2.7 

		Args:
			color: text color 
			shadow: include shadow layer 
			x: screen x 
			y: screen y 
			text: 

		Returns:
			added text 
		"""
		pass

	@overload
	def addText(self, text: str, x: int, y: int, color: int, zIndex: int, shadow: bool) -> RenderCommon_Text:
		"""
		Since: 1.4.0 

		Args:
			color: text color 
			shadow: include shadow layer 
			x: screen x 
			y: screen y 
			text: 
			zIndex: z-index 

		Returns:
			added text 
		"""
		pass

	@overload
	def addText(self, text: str, x: int, y: int, color: int, shadow: bool, scale: float, rotation: float) -> RenderCommon_Text:
		"""
		Since: 1.2.7 

		Args:
			color: text color 
			shadow: include shadow layer 
			rotation: text rotation (as degrees) 
			x: screen x 
			y: screen y 
			scale: text scale (as double) 
			text: 

		Returns:
			added text 
		"""
		pass

	@overload
	def addText(self, text: str, x: int, y: int, color: int, zIndex: int, shadow: bool, scale: float, rotation: float) -> RenderCommon_Text:
		"""
		Since: 1.4.0 

		Args:
			color: text color 
			shadow: include shadow layer 
			rotation: text rotation (as degrees) 
			x: screen x 
			y: screen y 
			scale: text scale (as double) 
			text: 
			zIndex: z-index 

		Returns:
			added text 
		"""
		pass

	@overload
	def addText(self, text: TextHelper, x: int, y: int, color: int, shadow: bool) -> RenderCommon_Text:
		"""
		Since: 1.2.7 

		Args:
			color: text color 
			shadow: include shadow layer 
			x: screen x 
			y: screen y 
			text: 

		Returns:
			added text 
		"""
		pass

	@overload
	def addText(self, text: TextHelper, x: int, y: int, color: int, zIndex: int, shadow: bool) -> RenderCommon_Text:
		"""
		Since: 1.4.0 

		Args:
			color: text color 
			shadow: include shadow layer 
			x: screen x 
			y: screen y 
			text: 
			zIndex: z-index 

		Returns:
			added text 
		"""
		pass

	@overload
	def addText(self, text: TextHelper, x: int, y: int, color: int, shadow: bool, scale: float, rotation: float) -> RenderCommon_Text:
		"""
		Since: 1.2.7 

		Args:
			color: text color 
			shadow: include shadow layer 
			rotation: text rotation (as degrees) 
			x: screen x 
			y: screen y 
			scale: text scale (as double) 
			text: 

		Returns:
			added text 
		"""
		pass

	@overload
	def addText(self, text: TextHelper, x: int, y: int, color: int, zIndex: int, shadow: bool, scale: float, rotation: float) -> RenderCommon_Text:
		"""
		Since: 1.4.0 

		Args:
			color: text color 
			shadow: include shadow layer 
			rotation: text rotation (as degrees) 
			x: screen x 
			y: screen y 
			scale: text scale (as double) 
			text: 
			zIndex: z-index 

		Returns:
			added text 
		"""
		pass

	@overload
	def removeText(self, t: RenderCommon_Text) -> T:
		"""
		Since: 1.2.7 

		Args:
			t: 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int) -> RenderCommon_Image:
		"""
		Since: 1.2.7 

		Args:
			imageY: the top-most coordinate of the texture region 
			textureWidth: the width of the entire texture 
			imageX: the left-most coordinate of the texture region 
			x: screen x, top left corner 
			width: width on screen 
			y: screen y, top left corner 
			regionHeight: the height the texture region 
			id: image id, in the form 'minecraft:textures' path'd as found in texture packs, ie 'assets/minecraft/textures/gui/recipe_book.png' becomes 'minecraft:textures/gui/recipe_book.png' 
			regionWidth: the width the texture region 
			textureHeight: the height of the entire texture 
			height: height on screen 

		Returns:
			added image 
		"""
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, zIndex: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int) -> RenderCommon_Image:
		"""
		Since: 1.4.0 

		Args:
			imageY: the top-most coordinate of the texture region 
			textureWidth: the width of the entire texture 
			imageX: the left-most coordinate of the texture region 
			x: screen x, top left corner 
			width: width on screen 
			y: screen y, top left corner 
			regionHeight: the height the texture region 
			id: image id, in the form 'minecraft:textures' path'd as found in texture packs, ie 'assets/minecraft/textures/gui/recipe_book.png' becomes 'minecraft:textures/gui/recipe_book.png' 
			regionWidth: the width the texture region 
			textureHeight: the height of the entire texture 
			height: height on screen 
			zIndex: z-index 

		Returns:
			added image 
		"""
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> RenderCommon_Image:
		"""
		Since: 1.2.7 

		Args:
			imageY: the top-most coordinate of the texture region 
			textureWidth: the width of the entire texture 
			imageX: the left-most coordinate of the texture region 
			rotation: the rotation of the texture (as degrees) 
			x: screen x, top left corner 
			width: width on screen 
			y: screen y, top left corner 
			regionHeight: the height the texture region 
			id: image id, in the form 'minecraft:textures' path'd as found in texture packs, ie 'assets/minecraft/textures/gui/recipe_book.png' becomes 'minecraft:textures/gui/recipe_book.png' 
			regionWidth: the width the texture region 
			textureHeight: the height of the entire texture 
			height: height on screen 

		Returns:
			added image 
		"""
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, zIndex: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> RenderCommon_Image:
		"""
		Since: 1.4.0 

		Args:
			imageY: the top-most coordinate of the texture region 
			textureWidth: the width of the entire texture 
			imageX: the left-most coordinate of the texture region 
			rotation: the rotation of the texture (as degrees) 
			regionWidth: the width the texture region 
			textureHeight: the height of the entire texture 
			x: screen x, top left corner 
			width: width on screen 
			y: screen y, top left corner 
			regionHeight: the height the texture region 
			id: image id, in the form 'minecraft:textures' path'd as found in texture packs, ie 'assets/minecraft/textures/gui/recipe_book.png' becomes 'minecraft:textures/gui/recipe_book.png' 
			height: height on screen 
			zIndex: z-index 

		Returns:
			added image 
		"""
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, zIndex: int, color: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> RenderCommon_Image:
		"""
		Since: 1.6.5 

		Args:
			color: 
			imageY: 
			textureWidth: 
			imageX: 
			rotation: 
			regionWidth: 
			textureHeight: 
			x: 
			width: 
			y: 
			regionHeight: 
			id: 
			height: 
			zIndex: 
		"""
		pass

	@overload
	def addImage(self, x: int, y: int, width: int, height: int, zIndex: int, alpha: int, color: int, id: str, imageX: int, imageY: int, regionWidth: int, regionHeight: int, textureWidth: int, textureHeight: int, rotation: float) -> RenderCommon_Image:
		"""
		Since: 1.6.5 

		Args:
			color: 
			imageY: 
			textureWidth: 
			imageX: 
			rotation: 
			regionWidth: 
			textureHeight: 
			alpha: 
			x: 
			width: 
			y: 
			regionHeight: 
			id: 
			height: 
			zIndex: 
		"""
		pass

	@overload
	def removeImage(self, i: RenderCommon_Image) -> T:
		"""
		Since: 1.2.7 

		Args:
			i: 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int) -> RenderCommon_Rect:
		"""
		Since: 1.2.7 

		Args:
			color: as hex, with alpha channel 
			y1: 
			x1: 
			y2: 
			x2: 

		Returns:
			added rect 
		"""
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int, alpha: int) -> RenderCommon_Rect:
		"""
		Since: 1.2.7 

		Args:
			color: as hex 
			alpha: alpha channel 0-255 
			y1: 
			x1: 
			y2: 
			x2: 

		Returns:
			added rect 
		"""
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int, alpha: int, rotation: float) -> RenderCommon_Rect:
		"""
		Since: 1.2.7 

		Args:
			color: as hex 
			alpha: alpha channel 0-255 
			rotation: as degrees 
			y1: 
			x1: 
			y2: 
			x2: 

		Returns:
			added rect 
		"""
		pass

	@overload
	def addRect(self, x1: int, y1: int, x2: int, y2: int, color: int, alpha: int, rotation: float, zIndex: int) -> RenderCommon_Rect:
		"""
		Since: 1.4.0 

		Args:
			color: as hex 
			alpha: alpha channel 0-255 
			rotation: as degrees 
			y1: 
			x1: 
			y2: 
			x2: 
			zIndex: z-index 

		Returns:
			added rect 
		"""
		pass

	@overload
	def removeRect(self, r: RenderCommon_Rect) -> T:
		"""
		Since: 1.2.7 

		Args:
			r: 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, id: str) -> RenderCommon_Item:
		"""
		Since: 1.2.7 

		Args:
			x: left most corner 
			y: top most corner 
			id: item id 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, id: str) -> RenderCommon_Item:
		"""
		Since: 1.4.0 

		Args:
			x: left most corner 
			y: top most corner 
			id: item id 
			zIndex: z-index 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, id: str, overlay: bool) -> RenderCommon_Item:
		"""
		Since: 1.2.7 

		Args:
			overlay: should include overlay health and count 
			x: left most corner 
			y: top most corner 
			id: item id 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, id: str, overlay: bool) -> RenderCommon_Item:
		"""
		Since: 1.4.0 

		Args:
			overlay: should include overlay health and count 
			x: left most corner 
			y: top most corner 
			id: item id 
			zIndex: z-index 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, id: str, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		"""
		Since: 1.2.7 

		Args:
			overlay: should include overlay health and count 
			rotation: rotation of item 
			x: left most corner 
			y: top most corner 
			scale: scale of item 
			id: item id 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, id: str, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		"""
		Since: 1.4.0 

		Args:
			overlay: should include overlay health and count 
			rotation: rotation of item 
			x: left most corner 
			y: top most corner 
			scale: scale of item 
			id: item id 
			zIndex: z-index 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, item: ItemStackHelper) -> RenderCommon_Item:
		"""
		Since: 1.2.7 

		Args:
			item: from inventory as helper 
			x: left most corner 
			y: top most corner 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, item: ItemStackHelper) -> RenderCommon_Item:
		"""
		Since: 1.4.0 

		Args:
			item: from inventory as helper 
			x: left most corner 
			y: top most corner 
			zIndex: z-index 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, item: ItemStackHelper, overlay: bool) -> RenderCommon_Item:
		"""
		Since: 1.2.7 

		Args:
			item: from inventory as helper 
			overlay: should include overlay health and count 
			x: left most corner 
			y: top most corner 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, item: ItemStackHelper, overlay: bool) -> RenderCommon_Item:
		"""
		Since: 1.4.0 

		Args:
			item: from inventory as helper 
			overlay: should include overlay health and count 
			x: left most corner 
			y: top most corner 
			zIndex: z-index 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, item: ItemStackHelper, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		"""
		Since: 1.2.7 

		Args:
			item: from inventory as helper 
			overlay: should include overlay health and count 
			rotation: rotation of item 
			x: left most corner 
			y: top most corner 
			scale: scale of item 

		Returns:
			added item 
		"""
		pass

	@overload
	def addItem(self, x: int, y: int, zIndex: int, item: ItemStackHelper, overlay: bool, scale: float, rotation: float) -> RenderCommon_Item:
		"""
		Since: 1.4.0 

		Args:
			item: from inventory as helper 
			overlay: should include overlay health and count 
			rotation: rotation of item 
			x: left most corner 
			y: top most corner 
			scale: scale of item 
			zIndex: z-index 

		Returns:
			added item 
		"""
		pass

	@overload
	def removeItem(self, i: RenderCommon_Item) -> T:
		"""
		Since: 1.2.7 

		Args:
			i: 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def setOnInit(self, onInit: MethodWrapper) -> T:
		"""
		Since: 1.2.7 

		Args:
			onInit: calls your method as a Consumer IDraw2D#T 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def setOnFailInit(self, catchInit: MethodWrapper) -> T:
		"""
		Since: 1.2.7 

		Args:
			catchInit: calls your method as a Consumer String 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def render(self, matrixStack: MatrixStack) -> None:
		"""internal

		Args:
			matrixStack: 
		"""
		pass

	pass


