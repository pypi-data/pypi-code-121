from typing import overload
from typing import TypeVar
from .Draw2D import Draw2D
from .PositionCommon_Pos3D import PositionCommon_Pos3D
from .PositionCommon_Pos2D import PositionCommon_Pos2D

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class Draw3D_Surface(Draw2D):
	"""
	Since: 1.6.5 
	"""
	pos: PositionCommon_Pos3D
	rotations: PositionCommon_Pos3D
	zIndexScale: float
	renderBack: bool
	cull: bool

	@overload
	def __init__(self, pos: PositionCommon_Pos3D, rotations: PositionCommon_Pos3D, sizes: PositionCommon_Pos2D, minSubdivisions: int, renderBack: bool, cull: bool) -> None:
		pass

	@overload
	def setPos(self, x: float, y: float, z: float) -> None:
		pass

	@overload
	def setRotations(self, x: float, y: float, z: float) -> None:
		pass

	@overload
	def setSizes(self, x: float, y: float) -> None:
		pass

	@overload
	def getSizes(self) -> PositionCommon_Pos2D:
		pass

	@overload
	def setMinSubdivisions(self, minSubdivisions: int) -> None:
		pass

	@overload
	def getMinSubdivisions(self) -> int:
		pass

	@overload
	def getHeight(self) -> int:
		pass

	@overload
	def getWidth(self) -> int:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def render3D(self, matrixStack: MatrixStack) -> None:
		pass

	@overload
	def render(self, matrixStack: MatrixStack) -> None:
		pass

	pass


