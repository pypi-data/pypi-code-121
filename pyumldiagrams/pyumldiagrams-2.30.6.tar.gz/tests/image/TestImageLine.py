
from typing import Tuple

from logging import Logger
from logging import getLogger

from unittest import TestSuite
from unittest import main as unitTestMain

from PIL.ImageDraw import ImageDraw

from pyumldiagrams.Definitions import EllipseDefinition
from pyumldiagrams.Definitions import LinePositions
from pyumldiagrams.Definitions import LineType
from pyumldiagrams.Definitions import Position
from pyumldiagrams.Definitions import Size
from pyumldiagrams.Definitions import UmlLineDefinition
from pyumldiagrams.Definitions import UmlLineDefinitions

from pyumldiagrams.Internal import InternalPosition

from pyumldiagrams.image.ImageCommon import ImageCommon
from pyumldiagrams.image.ImageDiagram import ImageDiagram
from pyumldiagrams.image.ImageFormat import ImageFormat
from pyumldiagrams.image.ImageLine import ImageLine

from tests.TestBase import TestBase
from tests.TestConstants import TestConstants

#
# Generally I do not like module variables;  But making them part of the test class
# results in very long method invocations
#
V_LEFT_X:  int = 200
V_RIGHT_X: int = 700

V_TOP_Y:    int = 150
V_BOTTOM_Y: int = 350

X_INC: int = 50
X_DEC: int = -50
Y_DEC: int = -50

Y_INC: int = 50

TOP_LINE_LEFT_X:  int = V_LEFT_X
TOP_LINE_RIGHT_X: int = V_RIGHT_X
TOP_LINE_Y:       int = V_BOTTOM_Y + Y_INC

BOTTOM_LINE_LEFT_X:  int = TOP_LINE_LEFT_X
BOTTOM_LINE_RIGHT_X: int = TOP_LINE_RIGHT_X
BOTTOM_LINE_Y:       int = TOP_LINE_Y + 200

DASH_LINE_SPACE_LENGTH: int = 4

BOUNDARY_LINE_WIDTH: int = 1  # pixels

ELLIPSE_X: int = V_LEFT_X
ELLIPSE_Y: int = V_TOP_Y

ELLIPSE_WIDTH:  int = 300
ELLIPSE_HEIGHT: int = 300


class TestImageLine(TestBase):

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestImageLine.clsLogger = getLogger(__name__)

    def setUp(self):
        self.logger: Logger = TestImageLine.clsLogger

    def tearDown(self):
        pass

    def testOrthogonalInheritanceLines(self):
        diagram: ImageDiagram = ImageDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-OrthogonalInheritanceLines.{ImageFormat.PNG.value}')

        self._drawHorizontalBoundaries(diagram)
        self._drawVerticalBoundaries(diagram)

        lineDrawer: ImageLine = ImageLine(docWriter=diagram._imgDraw, diagramPadding=diagram._diagramPadding)

        north, south, east, west = self._createOrthogonalLines(LineType.Inheritance)
        lineDefinitions: UmlLineDefinitions = [
            north, south, east, west
        ]
        for lineDefinition in lineDefinitions:
            lineDrawer.draw(lineDefinition)

        diagram.write()

    def testDiagonalInheritanceLines(self):

        diagram: ImageDiagram = ImageDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-DiagonalInheritanceLines.{ImageFormat.PNG.value}')
        self.__drawEllipseForDiagonalInheritanceLines(diagram)

        lineDrawer: ImageLine = ImageLine(docWriter=diagram._imgDraw, diagramPadding=diagram._diagramPadding)

        northEast, northWest, southEast, southWest = self.__createDiagonalLines(LineType.Inheritance)

        definitions: UmlLineDefinitions = [northEast, northWest, southEast, southWest]
        for definition in definitions:
            lineDrawer.draw(definition)

        diagram.write()

    def testOrthogonalCompositionLines(self):

        diagram: ImageDiagram = ImageDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-OrthogonalCompositionLines.{ImageFormat.PNG.value}')

        self._drawHorizontalBoundaries(diagram)
        self._drawVerticalBoundaries(diagram)

        lineDrawer: ImageLine = ImageLine(docWriter=diagram._imgDraw, diagramPadding=diagram._diagramPadding)

        north, south, east, west = self._createOrthogonalLines(LineType.Composition)

        lineDefinitions: UmlLineDefinitions = [
            north, south, east, west
        ]
        for lineDefinition in lineDefinitions:
            lineDrawer.draw(lineDefinition)

        diagram.write()

    def testDiagonalCompositionLines(self):

        diagram: ImageDiagram = ImageDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-DiagonalCompositionLines.{ImageFormat.PNG.value}')
        self.__drawEllipseForDiagonalInheritanceLines(diagram)

        lineDrawer: ImageLine = ImageLine(docWriter=diagram._imgDraw, diagramPadding=diagram._diagramPadding)

        northEast, northWest, southEast, southWest = self.__createDiagonalLines(LineType.Composition)
        definitions: UmlLineDefinitions = [northEast, northWest, southEast, southWest]
        for definition in definitions:
            lineDrawer.draw(definition)
        diagram.write()

    def testOrthogonalAggregationLines(self):

        diagram: ImageDiagram = ImageDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-OrthogonalAggregationLines.{ImageFormat.PNG.value}')

        self._drawHorizontalBoundaries(diagram)
        self._drawVerticalBoundaries(diagram)

        lineDrawer: ImageLine = ImageLine(docWriter=diagram._imgDraw, diagramPadding=diagram._diagramPadding)

        north, south, east, west = self._createOrthogonalLines(LineType.Aggregation)
        lineDefinitions: UmlLineDefinitions = [
            north, south, east, west
        ]
        for lineDefinition in lineDefinitions:
            lineDrawer.draw(lineDefinition)

        diagram.write()

    def testDiagonalAggregationLines(self):

        diagram: ImageDiagram = ImageDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-DiagonalAggregationLines.{ImageFormat.PNG.value}')
        self.__drawEllipseForDiagonalInheritanceLines(diagram)

        lineDrawer: ImageLine = ImageLine(docWriter=diagram._imgDraw, diagramPadding=diagram._diagramPadding)

        northEast, northWest, southEast, southWest = self.__createDiagonalLines(LineType.Aggregation)
        definitions: UmlLineDefinitions = [northEast, northWest, southEast, southWest]
        for definition in definitions:
            lineDrawer.draw(definition)
        diagram.write()

    def testOrthogonalAssociationLines(self):
        diagram: ImageDiagram = ImageDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-OrthogonalAssociationLines.{ImageFormat.PNG.value}')

        self._drawHorizontalBoundaries(diagram)
        self._drawVerticalBoundaries(diagram)

        north, south, east, west = self._createOrthogonalLines(LineType.Association)
        lineDefinitions: UmlLineDefinitions = [
            north, south, east, west
        ]
        lineDrawer: ImageLine = ImageLine(docWriter=diagram._imgDraw, diagramPadding=diagram._diagramPadding)

        for lineDefinition in lineDefinitions:
            lineDrawer.draw(lineDefinition)

        diagram.write()

    def testDiagonalAssociationLines(self):

        diagram: ImageDiagram = ImageDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-DiagonalAssociationLines.{ImageFormat.PNG.value}')
        self.__drawEllipseForDiagonalInheritanceLines(diagram)

        lineDrawer: ImageLine = ImageLine(docWriter=diagram._imgDraw, diagramPadding=diagram._diagramPadding)

        northEast, northWest, southEast, southWest = self.__createDiagonalLines(LineType.Association)
        definitions: UmlLineDefinitions = [northEast, northWest, southEast, southWest]
        for definition in definitions:
            lineDrawer.draw(definition)

        diagram.write()

    def _drawHorizontalBoundaries(self, diagram: ImageDiagram):

        imgDraw: ImageDraw = diagram._imgDraw

        startLeftTop:   InternalPosition = self.__toInternal(Position(x=V_LEFT_X, y=V_TOP_Y),    diagram=diagram)
        endLLeftBottom: InternalPosition = self.__toInternal(Position(x=V_LEFT_X, y=V_BOTTOM_Y), diagram=diagram)

        startRightTop:  InternalPosition = self.__toInternal(Position(x=V_RIGHT_X, y=V_TOP_Y),    diagram=diagram)
        endRightBottom: InternalPosition = self.__toInternal(Position(x=V_RIGHT_X, y=V_BOTTOM_Y), diagram=diagram)

        xy = [startLeftTop.x, startLeftTop.y, endLLeftBottom.x, endLLeftBottom.y]
        imgDraw.line(xy=xy, fill=ImageDiagram.DEFAULT_LINE_COLOR, width=BOUNDARY_LINE_WIDTH)

        xy = [startRightTop.x, startRightTop.y, endRightBottom.x, endRightBottom.y]
        imgDraw.line(xy=xy, fill=ImageDiagram.DEFAULT_LINE_COLOR, width=BOUNDARY_LINE_WIDTH)

    def _drawVerticalBoundaries(self, diagram: ImageDiagram):

        imgDraw: ImageDraw = diagram._imgDraw

        topStart: InternalPosition = self.__toInternal(Position(x=TOP_LINE_LEFT_X,  y=TOP_LINE_Y), diagram=diagram)
        topEnd:   InternalPosition = self.__toInternal(Position(x=TOP_LINE_RIGHT_X, y=TOP_LINE_Y), diagram=diagram)

        bottomStart: InternalPosition = self.__toInternal(Position(x=BOTTOM_LINE_LEFT_X,  y=BOTTOM_LINE_Y), diagram=diagram)
        bottomEnd:   InternalPosition = self.__toInternal(Position(x=BOTTOM_LINE_RIGHT_X, y=BOTTOM_LINE_Y), diagram=diagram)

        xy = [topStart.x, topStart.y, topEnd.x, topEnd.y]
        imgDraw.line(xy=xy, fill=ImageDiagram.DEFAULT_LINE_COLOR, width=BOUNDARY_LINE_WIDTH)

        xy = [bottomStart.x, bottomStart.y, bottomEnd.x, bottomEnd.y]
        imgDraw.line(xy=xy, fill=ImageDiagram.DEFAULT_LINE_COLOR, width=BOUNDARY_LINE_WIDTH)

    def _createOrthogonalLines(self, lineType: LineType) -> Tuple[UmlLineDefinition, UmlLineDefinition, UmlLineDefinition, UmlLineDefinition]:

        northLinePositions: LinePositions = [Position(BOTTOM_LINE_LEFT_X + X_INC, TOP_LINE_Y), Position(BOTTOM_LINE_LEFT_X + X_INC, BOTTOM_LINE_Y)]
        north: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=northLinePositions)

        northLinePositions: LinePositions = [Position(BOTTOM_LINE_RIGHT_X + X_DEC, TOP_LINE_Y), Position(BOTTOM_LINE_RIGHT_X + X_DEC, BOTTOM_LINE_Y)]
        south: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=northLinePositions)

        eastLinePositions: LinePositions = [Position(V_LEFT_X, V_TOP_Y + Y_INC), Position(V_RIGHT_X, V_TOP_Y + Y_INC)]
        east: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=eastLinePositions)

        westLinePositions: LinePositions = [Position(V_RIGHT_X, V_BOTTOM_Y + Y_DEC), Position(V_LEFT_X, V_BOTTOM_Y + Y_DEC)]
        west: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=westLinePositions)

        return north, south, east, west

    def __drawEllipseForDiagonalInheritanceLines(self, diagram: ImageDiagram):

        # imgDraw: ImageDraw = diagram._imgDraw

        eDef: EllipseDefinition = EllipseDefinition()
        pos:  Position          = Position(ELLIPSE_X, ELLIPSE_Y)
        size: Size              = Size(width=ELLIPSE_WIDTH, height=ELLIPSE_HEIGHT)

        eDef.position = pos
        eDef.size     = size
        diagram.drawEllipse(eDef)
        diagram.drawRectangle(eDef)

        # center: Position = self.__computeEllipseCenter(pos)
        #
        # diagram.drawText(center, text=f'({int(center.x)},{int(center.y)})')

    def __createDiagonalLines(self, lineType: LineType) -> Tuple[UmlLineDefinition, UmlLineDefinition, UmlLineDefinition, UmlLineDefinition]:

        pos:       Position = Position(ELLIPSE_X, ELLIPSE_Y)
        arrowSize: float    = ELLIPSE_WIDTH / 2

        center: Position = self.__computeEllipseCenter(pos)
        neDst: Position = self.__computeNorthEastDestination(center=center, arrowSize=arrowSize)
        nwDst: Position = self.__computeNorthWestDestination(center=center, arrowSize=arrowSize)
        seDst: Position = self.__computeSouthEastDestination(center=center, arrowSize=arrowSize)
        swDst: Position = self.__computeSouthWestDestination(center=center, arrowSize=arrowSize)

        nePositions: LinePositions = [center, neDst]
        northEast: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=nePositions)

        nwPositions: LinePositions = [center, nwDst]
        northWest: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=nwPositions)

        swPositions: LinePositions = [center, swDst]
        southWest: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=swPositions)

        sePositions: LinePositions = [center, seDst]
        southEast: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=sePositions)

        return northEast, northWest, southEast, southWest

    def __computeEllipseCenter(self, ellipsePos: Position) -> Position:

        x: int = ellipsePos.x
        y: int = ellipsePos.y

        centerX: int = x + (ELLIPSE_WIDTH // 2)
        centerY: int = y + (ELLIPSE_HEIGHT // 2)

        return Position(centerX, centerY)

    def __computeNorthEastDestination(self, center: Position, arrowSize: float) -> Position:
        from math import pi

        radians: float = (pi / 4) * -1.0    # definition of 45-degree angle
        return self.__computeDestination(center=center, arrowSize=arrowSize, radians=radians)

    def __computeNorthWestDestination(self, center: Position, arrowSize: float) -> Position:
        from math import pi

        radians: float = (pi * 0.75) * -1.0
        return self.__computeDestination(center=center, arrowSize=arrowSize, radians=radians)

    def __computeSouthEastDestination(self, center: Position, arrowSize: float) -> Position:
        from math import pi

        radians: float = pi / 4
        return self.__computeDestination(center=center, arrowSize=arrowSize, radians=radians)

    def __computeSouthWestDestination(self, center: Position, arrowSize: float) -> Position:
        from math import pi

        radians: float = pi * 0.75
        return self.__computeDestination(center=center, arrowSize=arrowSize, radians=radians)

    def __computeDestination(self, center: Position, arrowSize: float, radians: float,) -> Position:

        from math import cos
        from math import sin

        return Position(center.x + round(arrowSize * cos(radians)), center.y + round(arrowSize * sin(radians)))

    def __toInternal(self, position: Position, diagram: ImageDiagram) -> InternalPosition:
        verticalGap:   int = diagram.verticalGap
        horizontalGap: int = diagram.horizontalGap

        iPos: InternalPosition = ImageCommon.toInternal(position, verticalGap=verticalGap, horizontalGap=horizontalGap)

        return iPos


def suite() -> TestSuite:
    """You need to change the name of the test class here also."""
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestImageLine))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
