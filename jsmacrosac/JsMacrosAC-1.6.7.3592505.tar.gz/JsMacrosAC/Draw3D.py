from typing import overload
from typing import List
from typing import TypeVar
from .Draw3D_Box import Draw3D_Box
from .Draw3D_Line import Draw3D_Line
from .Draw3D_Surface import Draw3D_Surface
from .PositionCommon_Pos3D import PositionCommon_Pos3D

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class Draw3D:
	"""Draw2D is cool\n
	Since: 1.0.6 
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def getBoxes(self) -> List[Draw3D_Box]:
		"""
		Since: 1.0.6 
		"""
		pass

	@overload
	def getLines(self) -> List[Draw3D_Line]:
		"""
		Since: 1.0.6 
		"""
		pass

	@overload
	def getDraw2Ds(self) -> List[Draw3D_Surface]:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def addBox(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int, fillColor: int, fill: bool) -> Draw3D_Box:
		"""
		Since: 1.0.6 

		Args:
			fillColor: 
			color: 
			z1: 
			y1: 
			z2: 
			x1: 
			y2: 
			x2: 
			fill: 

		Returns:
			The Draw3D_Box you added. 
		"""
		pass

	@overload
	def addBox(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int, fillColor: int, fill: bool, cull: bool) -> Draw3D_Box:
		"""
		Since: 1.3.1 

		Args:
			fillColor: 
			color: 
			z1: 
			y1: 
			z2: 
			x1: 
			y2: 
			x2: 
			fill: 
			cull: 
		"""
		pass

	@overload
	def addBox(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int, alpha: int, fillColor: int, fillAlpha: int, fill: bool) -> Draw3D_Box:
		"""
		Since: 1.1.8 

		Args:
			fillColor: 
			color: 
			z1: 
			alpha: 
			y1: 
			z2: 
			x1: 
			y2: 
			fillAlpha: 
			x2: 
			fill: 

		Returns:
			the Draw3D_Box you added. 
		"""
		pass

	@overload
	def addBox(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int, alpha: int, fillColor: int, fillAlpha: int, fill: bool, cull: bool) -> Draw3D_Box:
		pass

	@overload
	def removeBox(self, b: Draw3D_Box) -> "Draw3D":
		"""
		Since: 1.0.6 

		Args:
			b: 
		"""
		pass

	@overload
	def addLine(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int) -> Draw3D_Line:
		"""
		Since: 1.0.6 

		Args:
			color: 
			z1: 
			y1: 
			z2: 
			x1: 
			y2: 
			x2: 

		Returns:
			the Draw3D_Line you added. 
		"""
		pass

	@overload
	def addLine(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int, cull: bool) -> Draw3D_Line:
		"""
		Since: 1.3.1 

		Args:
			color: 
			z1: 
			y1: 
			z2: 
			x1: 
			y2: 
			x2: 
			cull: 
		"""
		pass

	@overload
	def addLine(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int, alpha: int) -> Draw3D_Line:
		"""
		Since: 1.1.8 

		Args:
			color: 
			z1: 
			alpha: 
			y1: 
			z2: 
			x1: 
			y2: 
			x2: 

		Returns:
			the Draw3D_Line you added. 
		"""
		pass

	@overload
	def addLine(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float, color: int, alpha: int, cull: bool) -> Draw3D_Line:
		"""
		Since: 1.3.1 

		Args:
			color: 
			z1: 
			alpha: 
			y1: 
			z2: 
			x1: 
			y2: 
			x2: 
			cull: 
		"""
		pass

	@overload
	def removeLine(self, l: Draw3D_Line) -> "Draw3D":
		"""
		Since: 1.0.6 

		Args:
			l: 
		"""
		pass

	@overload
	def addPoint(self, point: PositionCommon_Pos3D, radius: float, color: int) -> Draw3D_Box:
		"""Draws a cube( Draw3D_Box ) with a specific radius( 'side length = 2*radius' )\n
		Since: 1.4.0 

		Args:
			color: point color 
			radius: 1/2 of the side length of the cube 
			point: the center point 

		Returns:
			the Draw3D_Box generated, and visualized 
		"""
		pass

	@overload
	def addPoint(self, x: float, y: float, z: float, radius: float, color: int) -> Draw3D_Box:
		"""Draws a cube( Draw3D_Box ) with a specific radius( 'side length = 2*radius' )\n
		Since: 1.4.0 

		Args:
			color: point color 
			x: x value of the center point 
			y: y value of the center point 
			z: z value of the center point 
			radius: 1/2 of the side length of the cube 

		Returns:
			the Draw3D_Box generated, and visualized 
		"""
		pass

	@overload
	def addPoint(self, x: float, y: float, z: float, radius: float, color: int, alpha: int, cull: bool) -> Draw3D_Box:
		"""Draws a cube( Draw3D_Box ) with a specific radius( 'side length = 2*radius' )\n
		Since: 1.4.0 

		Args:
			color: point color 
			alpha: alpha of the point 
			x: x value of the center point 
			y: y value of the center point 
			z: z value of the center point 
			radius: 1/2 of the side length of the cube 
			cull: whether to cull the point or not 

		Returns:
			the Draw3D_Box generated, and visualized 
		"""
		pass

	@overload
	def addDraw2D(self, x: float, y: float, z: float) -> Draw3D_Surface:
		"""
		Since: 1.6.5 

		Args:
			x: top left 
			y: 
			z: 
		"""
		pass

	@overload
	def addDraw2D(self, x: float, y: float, z: float, width: float, height: float) -> Draw3D_Surface:
		"""
		Since: 1.6.5 

		Args:
			x: 
			width: 
			y: 
			z: 
			height: 
		"""
		pass

	@overload
	def addDraw2D(self, x: float, y: float, z: float, xRot: float, yRot: float, zRot: float) -> Draw3D_Surface:
		"""
		Since: 1.6.5 

		Args:
			zRot: 
			yRot: 
			x: 
			xRot: 
			y: 
			z: 
		"""
		pass

	@overload
	def addDraw2D(self, x: float, y: float, z: float, xRot: float, yRot: float, zRot: float, width: float, height: float) -> Draw3D_Surface:
		"""
		Since: 1.6.5 

		Args:
			zRot: 
			yRot: 
			x: 
			xRot: 
			width: 
			y: 
			z: 
			height: 
		"""
		pass

	@overload
	def addDraw2D(self, x: float, y: float, z: float, xRot: float, yRot: float, zRot: float, width: float, height: float, minSubdivisions: int) -> Draw3D_Surface:
		"""
		Since: 1.6.5 

		Args:
			zRot: 
			yRot: 
			x: 
			xRot: 
			width: 
			y: 
			z: 
			minSubdivisions: 
			height: 
		"""
		pass

	@overload
	def addDraw2D(self, x: float, y: float, z: float, xRot: float, yRot: float, zRot: float, width: float, height: float, minSubdivisions: int, renderBack: bool) -> Draw3D_Surface:
		"""
		Since: 1.6.5 

		Args:
			zRot: 
			yRot: 
			x: 
			xRot: 
			width: 
			y: 
			z: 
			minSubdivisions: 
			renderBack: 
			height: 
		"""
		pass

	@overload
	def addDraw2D(self, x: float, y: float, z: float, xRot: float, yRot: float, zRot: float, width: float, height: float, minSubdivisions: int, renderBack: bool, cull: bool) -> Draw3D_Surface:
		"""
		Since: 1.6.5 

		Args:
			zRot: 
			yRot: 
			x: top left 
			xRot: 
			width: 
			y: 
			z: 
			minSubdivisions: 
			renderBack: 
			height: 
		"""
		pass

	@overload
	def removeDraw2D(self, surface: Draw3D_Surface) -> None:
		"""
		Since: 1.6.5 
		"""
		pass

	@overload
	def register(self) -> "Draw3D":
		"""register so it actually shows up\n
		Since: 1.6.5 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def unregister(self) -> "Draw3D":
		"""
		Since: 1.6.5 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def render(self, matrixStack: MatrixStack) -> None:
		pass

	pass


