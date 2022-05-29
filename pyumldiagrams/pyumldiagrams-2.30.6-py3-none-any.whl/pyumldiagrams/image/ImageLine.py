
from typing import Any
from typing import List
from typing import Union
from typing import final

from logging import Logger
from logging import getLogger

from PIL.ImageDraw import ImageDraw

from pyumldiagrams.image.ImageCommon import ImageCommon

from pyumldiagrams.IDiagramLine import IDiagramLine
from pyumldiagrams.UnsupportedException import UnsupportedException

from pyumldiagrams.Definitions import DiagramPadding
from pyumldiagrams.Definitions import LineType
from pyumldiagrams.Definitions import Position
from pyumldiagrams.Definitions import UmlLineDefinition
from pyumldiagrams.Definitions import LinePositions

from pyumldiagrams.Internal import ArrowPoints
from pyumldiagrams.Internal import DiamondPoints
from pyumldiagrams.Internal import InternalPosition


class ImageLine(IDiagramLine):

    DEFAULT_LINE_COLOR: final = 'Black'
    LINE_WIDTH:         final = 1

    PILPoints     = List[float]
    PolygonPoints = PILPoints       # syntactic sugar

    def __init__(self, docWriter: Any, diagramPadding: DiagramPadding):

        super().__init__(docMaker=docWriter, diagramPadding=diagramPadding, dpi=0)

        self.logger: Logger = getLogger(__name__)

        self._imgDraw: ImageDraw = docWriter

    def draw(self, lineDefinition: UmlLineDefinition):
        """
        Draw the line described by the input parameter

        Args:
            lineDefinition:  Describes the line to draw
        """
        linePositions: LinePositions = lineDefinition.linePositions
        lineType:      LineType      = lineDefinition.lineType

        if lineType == LineType.Inheritance:
            self._drawInheritanceArrow(linePositions=linePositions)
        elif lineType == LineType.Composition:
            self._drawCompositionSolidDiamond(linePositions=linePositions)
        elif lineType == LineType.Aggregation:
            self._drawAggregationDiamond(linePositions=linePositions)
        elif lineType == LineType.Association:
            self._drawAssociation(linePositions=linePositions)
        else:
            raise UnsupportedException(f'Line definition type not supported: `{lineType}`')

    def _drawInheritanceArrow(self, linePositions: LinePositions):
        """
        Must account for the margins and gaps between drawn shapes
        Must convert from screen coordinates to point coordinates
        Draw the arrow first
        Compute the mid-point of the bottom line of the arrow
        That is where the line ends

        Args:
            linePositions  The points that describe the line
        """
        lastIdx:       int = len(linePositions) - 1
        beforeLastIdx: int = lastIdx - 1
        internalSrc: InternalPosition = self.__toInternal(linePositions[beforeLastIdx])
        internalDst: InternalPosition = self.__toInternal(linePositions[lastIdx])

        points:  ArrowPoints             = ImageCommon.computeTheArrowVertices(internalSrc, internalDst)
        polygon: ImageLine.PolygonPoints = self.__toPolygonPoints(points)

        self._imgDraw.polygon(xy=polygon, outline=ImageLine.DEFAULT_LINE_COLOR)

        newEndPoint: InternalPosition    = ImageCommon.computeMidPointOfBottomLine(points[0], points[2])
        xy:          ImageLine.PILPoints = self.__toPILPoints(linePositions=linePositions, newEndPoint=newEndPoint)

        self._imgDraw.line(xy=xy, fill=ImageLine.DEFAULT_LINE_COLOR, width=ImageLine.LINE_WIDTH)

    def _drawCompositionSolidDiamond(self, linePositions: LinePositions):

        lastIdx:       int = len(linePositions) - 1
        beforeLastIdx: int = lastIdx - 1
        internalSrc:  InternalPosition = self.__toInternal(linePositions[beforeLastIdx])
        internalDst:  InternalPosition = self.__toInternal(linePositions[lastIdx])

        points:  DiamondPoints           = ImageCommon.computeDiamondVertices(internalSrc, internalDst)
        polygon: ImageLine.PolygonPoints = self.__toPolygonPoints(points)

        self._imgDraw.polygon(xy=polygon, outline=ImageLine.DEFAULT_LINE_COLOR)

        newEndPoint: InternalPosition = points[3]
        xy:          ImageLine.PILPoints = self.__toPILPoints(linePositions=linePositions, newEndPoint=newEndPoint)

        self._imgDraw.line(xy=xy, fill=ImageLine.DEFAULT_LINE_COLOR, width=ImageLine.LINE_WIDTH)

    def _drawAggregationDiamond(self, linePositions: LinePositions):

        lastIdx:       int = len(linePositions) - 1
        beforeLastIdx: int = lastIdx - 1
        internalSrc:  InternalPosition = self.__toInternal(linePositions[beforeLastIdx])
        internalDst:  InternalPosition = self.__toInternal(linePositions[lastIdx])

        points:  DiamondPoints           = ImageCommon.computeDiamondVertices(internalSrc, internalDst)
        polygon: ImageLine.PolygonPoints = self.__toPolygonPoints(points)

        self._imgDraw.polygon(xy=polygon, outline=ImageLine.DEFAULT_LINE_COLOR, fill='black')

        newEndPoint: InternalPosition = points[3]
        xy:          ImageLine.PILPoints = self.__toPILPoints(linePositions=linePositions, newEndPoint=newEndPoint)

        self._imgDraw.line(xy=xy, fill=ImageLine.DEFAULT_LINE_COLOR, width=ImageLine.LINE_WIDTH)

    def _drawAssociation(self, linePositions: LinePositions):

        lastIdx:     int                  = len(linePositions) - 1
        internalDst: InternalPosition    = self.__toInternal(linePositions[lastIdx])
        xy:          ImageLine.PILPoints = self.__toPILPoints(linePositions=linePositions, newEndPoint=internalDst)

        self._imgDraw.line(xy=xy, fill=ImageLine.DEFAULT_LINE_COLOR, width=ImageLine.LINE_WIDTH)

    def __toInternal(self, position: Position) -> InternalPosition:

        verticalGap:   int = self._diagramPadding.verticalGap
        horizontalGap: int = self._diagramPadding.horizontalGap

        iPos: InternalPosition = ImageCommon.toInternal(position, verticalGap=verticalGap, horizontalGap=horizontalGap)

        return iPos

    def __toPolygonPoints(self, points: Union[ArrowPoints, DiamondPoints]) -> PolygonPoints:

        polygon: ImageLine.PolygonPoints = []

        for point in points:
            polygon.append(int(point.x))
            polygon.append(int(point.y))

        return polygon

    def __toPILPoints(self, linePositions: LinePositions, newEndPoint: InternalPosition) -> PILPoints:

        linePositionsCopy: LinePositions = linePositions[:-1]  # Makes a copy

        xy: ImageLine.PILPoints = []
        for externalPosition in linePositionsCopy:
            internalPosition: InternalPosition = self.__toInternal(externalPosition)
            xy.append(internalPosition.x)
            xy.append(internalPosition.y)

        xy.append(newEndPoint.x)
        xy.append(newEndPoint.y)

        return xy
