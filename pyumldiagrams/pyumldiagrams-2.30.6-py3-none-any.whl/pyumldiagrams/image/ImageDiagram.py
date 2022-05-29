
from typing import List
from typing import final
from typing import Union

from logging import Logger
from logging import getLogger

from os import sep as osSep

from pkg_resources import resource_filename

from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont


from pyumldiagrams.BaseDiagram import BaseDiagram
from pyumldiagrams.Definitions import DisplayMethodParameters

from pyumldiagrams.Definitions import TOP_MARGIN
from pyumldiagrams.Definitions import LEFT_MARGIN

from pyumldiagrams.Definitions import ClassDefinition
from pyumldiagrams.Definitions import EllipseDefinition
from pyumldiagrams.Definitions import Position
from pyumldiagrams.Definitions import RectangleDefinition
from pyumldiagrams.Definitions import Size
from pyumldiagrams.Definitions import UmlLineDefinition

from pyumldiagrams.image.ImageCommon import ImageCommon

from pyumldiagrams.Internal import InternalPosition
from pyumldiagrams.Internal import SeparatorPosition

from pyumldiagrams.image.ImageFormat import ImageFormat
from pyumldiagrams.image.ImageLine import ImageLine

ShapeDefinition = Union[EllipseDefinition, RectangleDefinition]


class ImageDiagram(BaseDiagram):

    RESOURCES_PACKAGE_NAME: final = 'pyumldiagrams.image.resources'
    RESOURCES_PATH:         final = f'pyumldiagrams{osSep}image{osSep}resources'

    DEFAULT_IMAGE_WIDTH:  final = 1280    # pixels
    DEFAULT_IMAGE_HEIGHT: final = 1024    # pixels

    DEFAULT_BACKGROUND_COLOR: str = 'LightYellow'
    DEFAULT_LINE_COLOR:       str = 'Black'
    DEFAULT_TEXT_COLOR:       str = 'Black'
    DEFAULT_IMAGE_FORMAT:     str = ImageFormat.PNG.value
    SUFFIX_INDICATOR:         str = '.'

    X_NUDGE_FACTOR:        final = 4
    Y_NUDGE_FACTOR:        final = 6
    FIRST_METHOD_Y_OFFSET: final = 0

    def __init__(self, fileName: str, docDisplayMethodParameters: DisplayMethodParameters = DisplayMethodParameters.DISPLAY, headerText: str = '', imageSize: Size = Size(width=DEFAULT_IMAGE_WIDTH, height=DEFAULT_IMAGE_HEIGHT)):
        """

        Args:
            fileName:  The output file name.  Including the suffix

            docDisplayMethodParameters:  The global value to consult if a class value says UNSPECIFIED

            headerText:  The text to display as a header on the diagram

            imageSize:  The diagram size in pixels
        """

        super().__init__(fileName=fileName, docDisplayMethodParameters=docDisplayMethodParameters, headerText=headerText)

        self.logger: Logger = getLogger(__name__)

        self._img:   Image  = Image.new(mode='RGB',
                                        size=(imageSize.width, imageSize.height),
                                        color=ImageColor.getrgb(ImageDiagram.DEFAULT_BACKGROUND_COLOR))

        self._imgDraw:    ImageDraw = ImageDraw.Draw(self._img)
        self._lineDrawer: ImageLine = ImageLine(docWriter=self._imgDraw, diagramPadding=self._diagramPadding)

        fqPath:     str       = self.retrieveResourcePath('MonoFonto.ttf')
        self._font:       ImageFont = ImageFont.truetype(font=fqPath, size=BaseDiagram.DEFAULT_FONT_SIZE)
        self._headerFont: ImageFont = ImageFont.truetype(font=fqPath, size=BaseDiagram.HEADER_FONT_SIZE)
        #
        # https://www.exiv2.org/tags.html
        #
        # TODO need to write the following EXIF TAGS
        #
        # 74  0112  Orientation    The image orientation viewed in terms of rows and columns.
        # 305 0131  Software       Name and version number of the software package(s) used to create the image
        # 316 013C  HostComputer   The computer and/or operating system in use at the time of image creation.
        # 270:      ImageDescription
        # 37510:    'UserComment'
        #

    def retrieveResourcePath(self, bareFileName: str) -> str:

        try:
            fqFileName: str = resource_filename(ImageDiagram.RESOURCES_PACKAGE_NAME, bareFileName)
        except (ValueError, Exception):
            #
            # Maybe we are in an app
            #
            from os import environ
            pathToResources: str = environ.get(f'{BaseDiagram.RESOURCE_ENV_VAR}')
            fqFileName:      str = f'{pathToResources}/{ImageDiagram.RESOURCES_PATH}/{bareFileName}'

        return fqFileName

    def drawClass(self, classDefinition: ClassDefinition):
        """
        Draw the class diagram defined by the input

        Overrides the empty base definition

        Args:
            classDefinition:    The class definition
        """
        self._drawClassSymbol(classDefinition=classDefinition)

        position: Position = classDefinition.position
        size:     Size     = classDefinition.size

        iPos: InternalPosition = ImageCommon.toInternal(position=position, horizontalGap=self.horizontalGap, verticalGap=self.verticalGap)

        self._drawClassName(classDefinition=classDefinition, rectX=iPos.x, rectY=iPos.y, symbolWidth=size.width)

        separatorPosition: SeparatorPosition = self._drawSeparator(rectX=iPos.x, rectY=iPos.y, shapeWidth=size.width)

        fieldReprs:  BaseDiagram.FieldsRepr  = self._buildFields(classDefinition.fields)

        fieldSeparatorPosition: SeparatorPosition = self._drawFields(fieldReprs=fieldReprs, separatorPosition=separatorPosition)
        methodSeparatorPosition = self._drawSeparator(rectX=iPos.x, rectY=fieldSeparatorPosition.y, shapeWidth=size.width)

        methodReprs: BaseDiagram.MethodsRepr = self._buildMethods(classDefinition.methods, classDefinition.displayMethodParameters)

        if classDefinition.displayMethods is True:
            self._drawMethods(methodReprs=methodReprs, separatorPosition=methodSeparatorPosition)

    def drawUmlLine(self, lineDefinition: UmlLineDefinition):
        """
        Draw the inheritance, aggregation, or composition lines that describe the relationships
        between the UML classes

        Overrides the empty base definition

        Args:
            lineDefinition:   A UML Line definition
        """
        self._lineDrawer.draw(lineDefinition=lineDefinition)

    def drawEllipse(self, definition: EllipseDefinition):
        """
        Draw a general purpose ellipse

        Overrides the empty base definition

        Args:
            definition:     It's definition
        """
        xy = self.__toInternalCoordinates(definition=definition)
        self._imgDraw.ellipse(xy=xy, fill=None, outline=ImageDiagram.DEFAULT_LINE_COLOR, width=1)

    def drawRectangle(self, definition: RectangleDefinition):
        """
        Draw a general purpose rectangle

        Overrides the empty base definition

        Args:
            definition:  The rectangle definition
        """

        xy = self.__toInternalCoordinates(definition=definition)
        self._imgDraw.rectangle(xy=xy, fill=None, outline=ImageDiagram.DEFAULT_LINE_COLOR, width=1)

    def write(self):
        """
        Call this method when you are done with placing the diagram onto the image document.

        Overrides the empty base definition
        """
        if self._headerText is not None and self._headerText != '':

            xy = [LEFT_MARGIN, TOP_MARGIN / 2]
            self._imgDraw.text(xy=xy, fill=ImageDiagram.DEFAULT_TEXT_COLOR, font=self._headerFont, text=self._headerText)

        adjustedFileName: str = self._addSuffix(fileName=self._fileName, suffix=ImageDiagram.DEFAULT_IMAGE_FORMAT)

        self.logger.info(f'{adjustedFileName=}')
        self._img.save(adjustedFileName, ImageDiagram.DEFAULT_IMAGE_FORMAT)

    def _drawClassSymbol(self, classDefinition: ClassDefinition):

        imgDraw: ImageDraw = self._imgDraw

        position: Position = classDefinition.position
        size:     Size     = classDefinition.size

        iPos: InternalPosition = ImageCommon.toInternal(position=position, horizontalGap=self.horizontalGap, verticalGap=self.verticalGap)

        x0 = iPos.x
        y0 = iPos.y
        x1 = x0 + size.width
        y1 = y0 + size.height
        xy = [x0, y0, x1, y1]
        self.logger.debug(f'Class Symbol {xy=}')
        imgDraw.rectangle(xy=xy, fill=None, outline=ImageDiagram.DEFAULT_LINE_COLOR, width=1)

    def _drawClassName(self, classDefinition: ClassDefinition, rectX: float, rectY: float, symbolWidth: float):

        imgDraw: ImageDraw = self._imgDraw

        nameWidth, nameHeight = imgDraw.textsize(text=classDefinition.name, font=self._font)

        textX: float = rectX + ((symbolWidth / 2) - (nameWidth / 2))
        textY: float = rectY + (self._fontSize / 2)

        xy = [textX, textY]
        self.logger.debug(f'ClassName {xy=}')
        imgDraw.text(xy=xy, fill=ImageDiagram.DEFAULT_TEXT_COLOR, font=self._font, text=classDefinition.name)

    def _drawSeparator(self, rectX: float, rectY: float, shapeWidth: float) -> SeparatorPosition:
        """
        Draws the UML separators between the various part of the UML shape
        Does the computation to determine where it drew the separator

        Args:
            rectX: x position of symbol
            rectY: y position of symbol (
            shapeWidth: The width of the symbol

        Returns:  Where it drew the separator
        """
        imgDraw: ImageDraw = self._imgDraw

        separatorX: float = rectX
        separatorY: float = rectY + self._fontSize + ImageDiagram.Y_NUDGE_FACTOR

        endX: float = rectX + shapeWidth

        xy = [separatorX, separatorY, endX, separatorY]
        self.logger.debug(f'Separator {xy=}')
        imgDraw.line(xy=xy, fill=ImageDiagram.DEFAULT_LINE_COLOR, width=1)

        return SeparatorPosition(separatorX, separatorY)

    def _drawFields(self, fieldReprs: BaseDiagram.FieldsRepr, separatorPosition: SeparatorPosition) -> SeparatorPosition:

        imgDraw: ImageDraw = self._imgDraw
        x: float = separatorPosition.x + ImageDiagram.X_NUDGE_FACTOR
        y: float = separatorPosition.y + ImageDiagram.Y_NUDGE_FACTOR
        for fieldRepr in fieldReprs:
            xy = [x, y]
            imgDraw.text(xy=xy, fill=ImageDiagram.DEFAULT_TEXT_COLOR, font=self._font, text=fieldRepr)
            y = y + self._fontSize + 2

        y = (y - self._fontSize) - 2   # Adjust for last addition
        return SeparatorPosition(x=x, y=y)

    def _drawMethods(self, methodReprs: BaseDiagram.MethodsRepr, separatorPosition: SeparatorPosition):

        imgDraw: ImageDraw = self._imgDraw

        x: float = separatorPosition.x + ImageDiagram.X_NUDGE_FACTOR
        y: float = separatorPosition.y + ImageDiagram.FIRST_METHOD_Y_OFFSET

        for methodRepr in methodReprs:

            xy = [x, y]
            imgDraw.text(xy=xy, fill=ImageDiagram.DEFAULT_TEXT_COLOR, font=self._font, text=methodRepr)
            y = y + self._fontSize

    def _addSuffix(self, fileName: str, suffix: str) -> str:

        result = fileName.find(f'{ImageDiagram.SUFFIX_INDICATOR}{suffix}')
        if result == -1:
            adjustedFileName: str = f'{fileName}{ImageDiagram.SUFFIX_INDICATOR}{suffix}'
        else:
            adjustedFileName: str = fileName
        return adjustedFileName

    def __toInternalCoordinates(self, definition: ShapeDefinition) -> List[float]:

        pos:  Position = definition.position
        size: Size     = definition.size

        internalStart: InternalPosition = self.__toInternal(position=pos)
        internalEnd:   InternalPosition = self.__toInternal(position=Position(x=pos.x + size.width, y=pos.y + size.height))

        x1 = internalStart.x
        y1 = internalStart.y
        x2 = internalEnd.x
        y2 = internalEnd.y

        xy = [x1, y1, x2, y2]

        return xy

    def __toInternal(self, position: Position) -> InternalPosition:

        verticalGap:   int = self._diagramPadding.verticalGap
        horizontalGap: int = self._diagramPadding.horizontalGap

        iPos: InternalPosition = ImageCommon.toInternal(position, verticalGap=verticalGap, horizontalGap=horizontalGap)

        return iPos


