
from logging import Logger
from logging import getLogger
from typing import Tuple

from unittest import TestSuite
from unittest import main as unitTestMain

from pyumldiagrams.Defaults import LEFT_MARGIN
from pyumldiagrams.Defaults import TOP_MARGIN
from pyumldiagrams.Definitions import LinePositions

from pyumldiagrams.pdf.PdfCommon import PdfCommon

from pyumldiagrams.Definitions import EllipseDefinition
from pyumldiagrams.Definitions import UmlLineDefinition
from pyumldiagrams.Definitions import UmlLineDefinitions
from pyumldiagrams.Definitions import LineType
from pyumldiagrams.Definitions import Position
from pyumldiagrams.Definitions import Size

from pyumldiagrams.pdf.PdfDiagram import PdfDiagram
from pyumldiagrams.pdf.PdfLine import PdfLine

from tests.TestBase import TestBase
from tests.TestConstants import TestConstants


class TestPdfLine(TestBase):

    V_LEFT_X:   int = 900
    V_RIGHT_X:  int = 1050
    V_TOP_Y:    int = 294
    V_BOTTOM_Y: int = 408

    X_INC: int = 50
    X_DEC: int = 50

    TOP_LINE_LEFT_X:  int = V_LEFT_X  - X_DEC
    TOP_LINE_RIGHT_X: int = V_RIGHT_X + X_INC

    H_LEFT_X:         int = V_RIGHT_X + 300
    H_RIGHT_X:        int = H_LEFT_X  + 200
    H_LEFT_TOP_Y:     int = V_TOP_Y
    H_LEFT_BOTTOM_Y:  int = V_BOTTOM_Y
    H_RIGHT_BOTTOM_Y: int = H_LEFT_BOTTOM_Y

    Y_INC: int = 50
    DASH_LINE_SPACE_LENGTH: int = 4

    ELLIPSE_X: int = V_LEFT_X
    ELLIPSE_Y: int = V_TOP_Y

    ELLIPSE_WIDTH:  int = 200
    ELLIPSE_HEIGHT: int = 200

    ELLIPSE_FILL_STYLE: str = 'D'

    clsLogger: Logger = None

    @classmethod
    def setUpClass(cls):
        TestBase.setUpLogging()
        TestPdfLine.clsLogger = getLogger(__name__)

    def setUp(self):

        self.logger: Logger = TestPdfLine.clsLogger

    def tearDown(self):
        pass

    def testOrthogonalInheritanceLines(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-OrthogonalInheritanceLines{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI)

        self.__drawHorizontalBoundaries(diagram)
        self.__drawVerticalBoundaries(diagram)

        lineDrawer: PdfLine = PdfLine(pdf=diagram._pdf, diagramPadding=diagram._diagramPadding, dpi=diagram._dpi)

        north, south, east, west = self.__createOrthogonalLines(LineType.Inheritance)
        lineDefinitions: UmlLineDefinitions = [
            north, south, east, west
        ]
        for lineDefinition in lineDefinitions:
            lineDrawer.draw(lineDefinition)

        diagram.write()

    def testOrthogonalCompositionLines(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-OrthogonalCompositionLines{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI)

        self.__drawHorizontalBoundaries(diagram)
        self.__drawVerticalBoundaries(diagram)

        lineDrawer: PdfLine = PdfLine(pdf=diagram._pdf, diagramPadding=diagram._diagramPadding, dpi=diagram._dpi)

        north, south, east, west = self.__createOrthogonalLines(LineType.Composition)

        lineDefinitions: UmlLineDefinitions = [
            north, south, east, west
        ]
        for lineDefinition in lineDefinitions:
            lineDrawer.draw(lineDefinition)

        diagram.write()

    def testDiagonalInheritanceLines(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-DiagonalInheritanceLines{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI)
        self.__drawEllipseForDiagonalLines(diagram)

        lineDrawer: PdfLine = PdfLine(pdf=diagram._pdf, diagramPadding=diagram._diagramPadding, dpi=diagram._dpi)

        northEast, northWest, southEast, southWest = self.__createDiagonalLines(LineType.Inheritance)
        definitions: UmlLineDefinitions = [northEast, northWest, southEast, southWest]
        for definition in definitions:
            lineDrawer.draw(definition)
        diagram.write()

    def testDiagonalCompositionLines(self):
        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-DiagonalCompositionLines{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI)
        self.__drawEllipseForDiagonalLines(diagram)

        lineDrawer: PdfLine = PdfLine(pdf=diagram._pdf, diagramPadding=diagram._diagramPadding, dpi=diagram._dpi)

        northEast, northWest, southEast, southWest = self.__createDiagonalLines(LineType.Composition)
        definitions: UmlLineDefinitions = [northEast, northWest, southEast, southWest]
        for definition in definitions:
            lineDrawer.draw(definition)
        diagram.write()

    def testOrthogonalAggregationLines(self):
        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-OrthogonalAggregationLines{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI)

        self.__drawHorizontalBoundaries(diagram)
        self.__drawVerticalBoundaries(diagram)

        lineDrawer: PdfLine = PdfLine(pdf=diagram._pdf, diagramPadding=diagram._diagramPadding, dpi=diagram._dpi)

        north, south, east, west = self.__createOrthogonalLines(LineType.Aggregation)
        lineDefinitions: UmlLineDefinitions = [
            north, south, east, west
        ]
        for lineDefinition in lineDefinitions:
            lineDrawer.draw(lineDefinition)

        diagram.write()

    def testDiagonalAggregationLines(self):

        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-DiagonalAggregationLines{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI)
        self.__drawEllipseForDiagonalLines(diagram)

        lineDrawer: PdfLine = PdfLine(pdf=diagram._pdf, diagramPadding=diagram._diagramPadding, dpi=diagram._dpi)

        northEast, northWest, southEast, southWest = self.__createDiagonalLines(LineType.Aggregation)
        definitions: UmlLineDefinitions = [northEast, northWest, southEast, southWest]
        for definition in definitions:
            lineDrawer.draw(definition)
        diagram.write()

    def testOrthogonalAssociationLines(self):
        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-OrthogonalAssociationLines{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI)

        self.__drawHorizontalBoundaries(diagram)
        self.__drawVerticalBoundaries(diagram)

        lineDrawer: PdfLine = PdfLine(pdf=diagram._pdf, diagramPadding=diagram._diagramPadding, dpi=diagram._dpi)

        north, south, east, west = self.__createOrthogonalLines(LineType.Association)
        lineDefinitions: UmlLineDefinitions = [
            north, south, east, west
        ]
        for lineDefinition in lineDefinitions:
            lineDrawer.draw(lineDefinition)

        diagram.write()

    def testDiagonalAssociationLines(self):
        diagram: PdfDiagram = PdfDiagram(fileName=f'{TestConstants.TEST_FILE_NAME}-DiagonalAssociationLines{TestConstants.TEST_SUFFIX}',
                                         dpi=TestConstants.TEST_DPI)

        self.__drawEllipseForDiagonalLines(diagram)

        lineDrawer: PdfLine = PdfLine(pdf=diagram._pdf, diagramPadding=diagram._diagramPadding, dpi=diagram._dpi)

        northEast, northWest, southEast, southWest = self.__createDiagonalLines(LineType.Association)
        definitions: UmlLineDefinitions = [northEast, northWest, southEast, southWest]
        for definition in definitions:
            lineDrawer.draw(definition)

        diagram.write()

    def __createOrthogonalLines(self, lineType: LineType) -> Tuple[UmlLineDefinition, UmlLineDefinition, UmlLineDefinition, UmlLineDefinition]:

        northLinePositions: LinePositions = [Position(TestPdfLine.V_RIGHT_X, TestPdfLine.V_TOP_Y),
                                             Position(TestPdfLine.V_RIGHT_X, TestPdfLine.V_BOTTOM_Y)]
        north: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=northLinePositions)

        southLinePositions: LinePositions = [Position(TestPdfLine.V_LEFT_X, TestPdfLine.V_BOTTOM_Y),
                                             Position(TestPdfLine.V_LEFT_X, TestPdfLine.V_TOP_Y)]
        south: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=southLinePositions)

        eastLinePositions: LinePositions = [Position(TestPdfLine.H_LEFT_X, TestPdfLine.H_LEFT_TOP_Y + TestPdfLine.Y_INC),
                                            Position(TestPdfLine.H_RIGHT_X, TestPdfLine.H_LEFT_TOP_Y + TestPdfLine.Y_INC)]

        east: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=eastLinePositions)

        westLinePositions: LinePositions = [Position(TestPdfLine.H_RIGHT_X, TestPdfLine.H_RIGHT_BOTTOM_Y),
                                            Position(TestPdfLine.H_LEFT_X, TestPdfLine.H_LEFT_BOTTOM_Y)]
        west: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=westLinePositions)

        return north, south, east, west

    def __createDiagonalLines(self, lineType: LineType) -> Tuple[UmlLineDefinition, UmlLineDefinition, UmlLineDefinition, UmlLineDefinition]:

        pos:  Position          = Position(TestPdfLine.ELLIPSE_X, TestPdfLine.ELLIPSE_Y)

        arrowSize: float = TestPdfLine.ELLIPSE_WIDTH / 2

        center: Position = self.__computeEllipseCenter(pos)
        neDst:  Position = self.__computeNorthEastDestination(center=center, arrowSize=arrowSize)
        seDst:  Position = self.__computeSouthEastDestination(center=center, arrowSize=arrowSize)
        nwDst:  Position = self.__computeNorthWestDestination(center=center, arrowSize=arrowSize)
        swDst:  Position = self.__computeSouthWestDestination(center=center, arrowSize=arrowSize)

        nePositions: LinePositions = [center, neDst]
        nwPositions: LinePositions = [center, nwDst]
        sePositions: LinePositions = [center, seDst]
        swPositions: LinePositions = [center, swDst]

        northEast: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=nePositions)
        northWest: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=nwPositions)
        southEast: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=sePositions)
        southWest: UmlLineDefinition = UmlLineDefinition(lineType=lineType, linePositions=swPositions)

        return northEast, northWest, southEast, southWest

    def __drawHorizontalBoundaries(self, diagram: PdfDiagram):

        x1: int = PdfCommon.toPdfPoints(TestPdfLine.TOP_LINE_LEFT_X, diagram._dpi) + LEFT_MARGIN + diagram.verticalGap
        x2: int = PdfCommon.toPdfPoints(TestPdfLine.TOP_LINE_RIGHT_X, diagram._dpi) + LEFT_MARGIN + diagram.verticalGap
        y2: int = PdfCommon.toPdfPoints(TestPdfLine.V_BOTTOM_Y, diagram._dpi) + TOP_MARGIN + diagram.horizontalGap

        diagram._pdf.dashed_line(x1=x1, y1=y2, x2=x2, y2=y2, space_length=TestPdfLine.DASH_LINE_SPACE_LENGTH)

        y2 = PdfCommon.toPdfPoints(TestPdfLine.V_TOP_Y, diagram._dpi) + TOP_MARGIN + diagram.horizontalGap

        diagram._pdf.dashed_line(x1=x1, y1=y2, x2=x2, y2=y2, space_length=TestPdfLine.DASH_LINE_SPACE_LENGTH)

    def __drawVerticalBoundaries(self, diagram: PdfDiagram):

        x1: int = PdfCommon.toPdfPoints(TestPdfLine.H_LEFT_X, diagram._dpi) + LEFT_MARGIN + diagram.verticalGap
        x2: int = x1
        y1: int = PdfCommon.toPdfPoints(TestPdfLine.H_LEFT_TOP_Y, diagram._dpi) + TOP_MARGIN + diagram.horizontalGap
        y2: int = PdfCommon.toPdfPoints(TestPdfLine.H_LEFT_BOTTOM_Y, diagram._dpi) + TOP_MARGIN + diagram.horizontalGap

        diagram._pdf.dashed_line(x1=x1, y1=y1, x2=x2, y2=y2, space_length=TestPdfLine.DASH_LINE_SPACE_LENGTH)

        x1 = PdfCommon.toPdfPoints(TestPdfLine.H_RIGHT_X, diagram._dpi) + LEFT_MARGIN + diagram.verticalGap
        x2 = x1

        diagram._pdf.dashed_line(x1=x1, y1=y1, x2=x2, y2=y2, space_length=TestPdfLine.DASH_LINE_SPACE_LENGTH)

    def __drawEllipseForDiagonalLines(self, diagram: PdfDiagram):

        eDef: EllipseDefinition = EllipseDefinition()
        pos:  Position          = Position(TestPdfLine.ELLIPSE_X, TestPdfLine.ELLIPSE_Y)
        size: Size              = Size(width=TestPdfLine.ELLIPSE_WIDTH, height=TestPdfLine.ELLIPSE_HEIGHT)

        eDef.position = pos
        eDef.size     = size
        diagram.drawEllipse(eDef)
        diagram.drawRectangle(eDef)

        center: Position = self.__computeEllipseCenter(pos)

        diagram.drawText(center, text=f'({int(center.x)},{int(center.y)})')

    def __computeEllipseCenter(self, ellipsePos: Position) -> Position:

        x: int = ellipsePos.x
        y: int = ellipsePos.y

        centerX: int = x + (TestPdfLine.ELLIPSE_WIDTH // 2)
        centerY: int = y + (TestPdfLine.ELLIPSE_HEIGHT // 2)

        return Position(centerX, centerY)

    def __computeNorthEastDestination(self, center: Position, arrowSize: float) -> Position:
        from math import pi

        radians: float = (pi / 4) * -1.0    # definition of a 45-degree angle
        return self.__computeDestination(center=center, arrowSize=arrowSize, radians=radians)

    def __computeSouthEastDestination(self, center: Position, arrowSize: float) -> Position:
        from math import pi

        radians: float = pi / 4
        return self.__computeDestination(center=center, arrowSize=arrowSize, radians=radians)

    def __computeNorthWestDestination(self, center: Position, arrowSize: float) -> Position:
        from math import pi

        radians: float = (pi * 0.75) * -1.0
        return self.__computeDestination(center=center, arrowSize=arrowSize, radians=radians)

    def __computeSouthWestDestination(self, center: Position, arrowSize: float) -> Position:
        from math import pi

        radians: float = pi * 0.75
        return self.__computeDestination(center=center, arrowSize=arrowSize, radians=radians)

    def __computeDestination(self, center: Position, arrowSize: float, radians: float,) -> Position:

        from math import cos
        from math import sin

        x: int = center.x + round(arrowSize * cos(radians))
        y: int = center.y + round(arrowSize * sin(radians))

        return Position(x, y)


def suite() -> TestSuite:
    """You need to change the name of the test class here also."""
    import unittest

    testSuite: TestSuite = TestSuite()
    # noinspection PyUnresolvedReferences
    testSuite.addTest(unittest.makeSuite(TestPdfLine))

    return testSuite


if __name__ == '__main__':
    unitTestMain()
