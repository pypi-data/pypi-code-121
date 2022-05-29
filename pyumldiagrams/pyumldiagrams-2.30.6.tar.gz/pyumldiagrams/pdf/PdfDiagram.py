
from typing import final

from logging import Logger
from logging import getLogger

from os import sep as osSep

from datetime import datetime

from pkg_resources import resource_filename

from pyumldiagrams.BaseDiagram import BaseDiagram
from pyumldiagrams.Defaults import DEFAULT_LINE_WIDTH
from pyumldiagrams.Definitions import DisplayMethodParameters
from pyumldiagrams.Internal import SeparatorPosition

from pyumldiagrams.Definitions import ClassDefinition
from pyumldiagrams.Definitions import DiagramPadding
from pyumldiagrams.Definitions import EllipseDefinition
from pyumldiagrams.Definitions import UmlLineDefinition

from pyumldiagrams.Definitions import Position
from pyumldiagrams.Definitions import RectangleDefinition
from pyumldiagrams.Definitions import Size

from pyumldiagrams.pdf.PdfCommon import Coordinates
from pyumldiagrams.pdf.PdfCommon import Dimensions
from pyumldiagrams.pdf.PdfCommon import PdfCommon
from pyumldiagrams.pdf.PdfCommon import PdfShapeDefinition

from pyumldiagrams.pdf.PdfLine import PdfLine
from pyumldiagrams.pdf.FPDFExtended import FPDFExtended


class PdfDiagram(BaseDiagram):
    """

    Always lays out in portrait mode.  Currently, only supports UML classes with methods.  Only supports
    inheritance, composition, aggregation, and association lines.

    You are allowed to set the gap between UML classes both horizontally and vertically.  Also, you are allowed to
    specify the text font size
    """
    FPDF_DRAW: str = 'D'

    RESOURCES_PACKAGE_NAME: final = 'pdf.resources'
    RESOURCES_PATH:         final = f'pdf{osSep}resources'

    X_NUDGE_FACTOR: final = 4
    Y_NUDGE_FACTOR: final = 4

    FIRST_METHOD_Y_OFFSET: final = 7

    def __init__(self, fileName: str, dpi: int, docDisplayMethodParameters: DisplayMethodParameters = DisplayMethodParameters.DISPLAY, headerText: str = ''):
        """

        Args:
            fileName:    Fully qualified file name
            dpi:         dots per inch for the display we are mapping from
            docDisplayMethodParameters:  The global value to consult if a class value says UNSPECIFIED
            headerText:  The header to place on the page
        """
        super().__init__(fileName=fileName, docDisplayMethodParameters=docDisplayMethodParameters, dpi=dpi, headerText=headerText)
        # self._fileName: str = fileName
        # self._dpi:      int = dpi
        self.logger: Logger = getLogger(__name__)

        pdf = FPDFExtended(headerText=headerText)
        pdf.add_page()

        pdf.set_display_mode(zoom='default', layout='single')

        pdf.set_line_width(DEFAULT_LINE_WIDTH)

        pdf.set_creator('Humberto A. Sanchez II - The Great')
        pdf.set_author('Humberto A. Sanchez II - The Great')

        pdf.set_font('Arial', size=BaseDiagram.DEFAULT_FONT_SIZE)
        pdf.headerText = headerText

        self._pdf:      FPDFExtended = pdf
        self._fontSize: int          = BaseDiagram.DEFAULT_FONT_SIZE

        diagramPadding:   DiagramPadding = DiagramPadding()
        self._lineDrawer: PdfLine = PdfLine(pdf=pdf, diagramPadding=diagramPadding, dpi=dpi)

        self._diagramPadding: DiagramPadding = diagramPadding

    @property
    def docTimeStamp(self) -> datetime:
        """
        Overrides the empty base implementation
        """
        return self._pdf.creation_date

    @docTimeStamp.setter
    def docTimeStamp(self, timeStamp: datetime):
        """
        Overrides the empty base implementation
        """
        self._pdf.creation_date = timeStamp

    def retrieveResourcePath(self, bareFileName: str) -> str:
        """
        Overrides the empty base implementation

        Args:
            bareFileName:

        Returns: a fully qualified name
        """
        try:
            fqFileName: str = resource_filename(PdfDiagram.RESOURCES_PACKAGE_NAME, bareFileName)
        except (ValueError, Exception):
            #
            # Maybe we are in an app
            #
            from os import environ
            pathToResources: str = environ.get(f'{BaseDiagram.RESOURCE_ENV_VAR}')
            fqFileName:      str = f'{pathToResources}/{PdfDiagram.RESOURCES_PATH}/{bareFileName}'

        return fqFileName

    def drawClass(self, classDefinition: ClassDefinition):
        """
        Draw the class diagram defined by the input

        Args:
            classDefinition:    The class definition
        """

        position:      Position = classDefinition.position
        verticalGap:   int      = self._diagramPadding.verticalGap
        horizontalGap: int      = self._diagramPadding.horizontalGap

        coordinates: Coordinates = PdfCommon.convertPosition(pos=position, dpi=self._dpi, verticalGap=verticalGap, horizontalGap=horizontalGap)
        x: int = coordinates.x
        y: int = coordinates.y
        self.logger.debug(f'x,y: ({x},{y})')

        methodReprs: BaseDiagram.MethodsRepr = self._buildMethods(classDefinition.methods, classDefinition.displayMethodParameters)
        fieldReprs:  BaseDiagram.FieldsRepr  = self._buildFields(classDefinition.fields)

        symbolWidth: int = self._drawClassSymbol(classDefinition, rectX=x, rectY=y)

        separatorPosition: SeparatorPosition = self._drawSeparator(rectX=x, rectY=y, shapeWidth=symbolWidth)
        fieldSeparatorPosition: SeparatorPosition = self._drawFields(fieldReprs=fieldReprs, separatorPosition=separatorPosition)

        methodSeparatorPosition: SeparatorPosition = self._drawSeparator(rectX=x, rectY=fieldSeparatorPosition.y, shapeWidth=symbolWidth)

        if classDefinition.displayMethods is True:
            self._drawMethods(methodReprs=methodReprs, separatorPosition=methodSeparatorPosition)

    def drawUmlLine(self, lineDefinition: UmlLineDefinition):
        """
        Draw the inheritance, aggregation, or composition lines that describe the relationships
        between the UML classes

        Args:
            lineDefinition:   A UML Line definition
        """
        self._lineDrawer.draw(lineDefinition=lineDefinition)

    def drawEllipse(self, definition: EllipseDefinition):
        """
        Draw a general purpose ellipse

        Args:
            definition:     It's definition
        """

        pdfShapeDefinition: PdfShapeDefinition = self.__convertDefinition(definition)

        x:      int = pdfShapeDefinition.coordinates.x
        y:      int = pdfShapeDefinition.coordinates.y
        width:  int = pdfShapeDefinition.dimensions.width
        height: int = pdfShapeDefinition.dimensions.height

        self._pdf.ellipse(x=x, y=y, w=width, h=height, style=definition.renderStyle.value)

    def drawRectangle(self, definition: RectangleDefinition):
        """
        Draw a general purpose rectangle

        Args:
            definition:  The rectangle definition

        """
        pdfShapeDefinition: PdfShapeDefinition = self.__convertDefinition(definition)

        x:      int = pdfShapeDefinition.coordinates.x
        y:      int = pdfShapeDefinition.coordinates.y
        width:  int = pdfShapeDefinition.dimensions.width
        height: int = pdfShapeDefinition.dimensions.height

        self._pdf.rect(x=x, y=y, w=width, h=height, style=definition.renderStyle.value)

    def drawText(self, position: Position, text: str):
        """
        Draw text at the input position.  The method will appropriately convert the
        position to PDF points

        Args:
            position:  The display's x, y position
            text:   The text to display
        """

        coordinates: Coordinates = PdfCommon.convertPosition(position, dpi=self._dpi, verticalGap=self.verticalGap, horizontalGap=self.horizontalGap)
        self._pdf.text(x=coordinates.x, y=coordinates.y, txt=text)

    def write(self):
        """
        Call this method when you are done with placing the diagram onto a PDF document.
        """
        self._pdf.output(self._fileName)

    def _drawClassSymbol(self, classDefinition: ClassDefinition, rectX: int, rectY: int) -> int:
        """
        Draws the UML Class symbol.

        Args:
            classDefinition:    The class definition
            rectX:      x position
            rectY:      y position

        Returns:  The computed UML symbol width
        """

        symbolWidth:  int = classDefinition.size.width
        symbolHeight: int = classDefinition.size.height

        size: Size = Size(width=symbolWidth, height=symbolHeight)

        dimensions: Dimensions = self.__convertSize(size=size)
        convertedWidth:  int = dimensions.width
        convertedHeight: int = dimensions.height
        #
        # The docs for rect are incorrect;  style is string
        # noinspection PyTypeChecker
        self._pdf.rect(x=rectX, y=rectY, w=convertedWidth, h=convertedHeight, style=PdfDiagram.FPDF_DRAW)

        nameWidth: int = self._pdf.get_string_width(classDefinition.name)
        textX: int = rectX + ((symbolWidth // 2) - (nameWidth // 2))
        textY: int = rectY + self._fontSize

        self._pdf.text(x=textX, y=textY, txt=classDefinition.name)

        return convertedWidth

    def _drawSeparator(self, rectX: int, rectY: int, shapeWidth: int) -> SeparatorPosition:
        """
        Draws the UML separator between the class name and the start of the class definition
        Does the computation to determine where it drew the separator

        Args:
            rectX: x position of symbol
            rectY: y position of symbol
            shapeWidth: The width of the symbol

        Returns:  Where it drew the separator

        """

        separatorX: int = rectX
        separatorY: int = rectY + self._fontSize + PdfDiagram.Y_NUDGE_FACTOR

        endX: int = rectX + shapeWidth

        self._pdf.line(x1=separatorX, y1=separatorY, x2=endX, y2=separatorY)

        return SeparatorPosition(separatorX, separatorY)

    def _drawMethods(self, methodReprs: BaseDiagram.MethodsRepr, separatorPosition: SeparatorPosition):

        x: int = separatorPosition.x + PdfDiagram.X_NUDGE_FACTOR
        y: int = separatorPosition.y + PdfDiagram.Y_NUDGE_FACTOR + PdfDiagram.FIRST_METHOD_Y_OFFSET

        for methodRepr in methodReprs:

            self._pdf.text(x=x, y=y, txt=methodRepr)

            y = y + self._fontSize

    def _drawFields(self, fieldReprs: BaseDiagram.FieldsRepr, separatorPosition: SeparatorPosition) -> SeparatorPosition:

        x: int = separatorPosition.x + PdfDiagram.X_NUDGE_FACTOR
        y: int = separatorPosition.y + PdfDiagram.Y_NUDGE_FACTOR + 8

        for fieldRepr in fieldReprs:
            self._pdf.text(x=x, y=y, txt=fieldRepr)
            y = y + self._fontSize + 2

        y = y - self._fontSize - 2  # adjust for last addition

        return SeparatorPosition(x=x, y=y)

    def __convertDefinition(self, definition: RectangleDefinition) -> PdfShapeDefinition:
        """

        Args:
            definition:

        Returns: A description of the shape
        """
        coordinates: Coordinates = PdfCommon.convertPosition(definition.position, dpi=self._dpi, verticalGap=self.verticalGap, horizontalGap=self.horizontalGap)
        dimensions:  Dimensions = self.__convertSize(definition.size)

        return PdfShapeDefinition(coordinates=coordinates, dimensions=dimensions)

    def __convertSize(self, size: Size) -> Dimensions:

        width:  int = PdfCommon.toPdfPoints(size.width, self._dpi)
        height: int = PdfCommon.toPdfPoints(size.height, self._dpi)

        return Dimensions(width=width, height=height)
