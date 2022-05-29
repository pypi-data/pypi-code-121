
from typing import List
from typing import cast
from typing import final

from logging import Logger
from logging import getLogger

from datetime import datetime

from pyumldiagrams.Definitions import ClassDefinition
from pyumldiagrams.Definitions import DiagramPadding
from pyumldiagrams.Definitions import DisplayMethodParameters
from pyumldiagrams.Definitions import EllipseDefinition
from pyumldiagrams.Definitions import FieldDefinition
from pyumldiagrams.Definitions import MethodDefinition
from pyumldiagrams.Definitions import ParameterDefinition
from pyumldiagrams.Definitions import RectangleDefinition
from pyumldiagrams.Definitions import UmlLineDefinition
from pyumldiagrams.Definitions import Fields
from pyumldiagrams.Definitions import Methods


class BaseDiagram:
    """
    Always lays out in portrait mode.  Currently only supports UML classes with methods.  Only supports
    inheritance, composition, and aggregation lines.

    You are allowed to set the gap between UML classes both horizontally and vertically.  Also, you are allowed to
    specify the text font size
    """

    MethodsRepr = List[str]
    FieldsRepr  = List[str]

    DEFAULT_FONT_SIZE: final = 10
    HEADER_FONT_SIZE:  final = 14
    RESOURCE_ENV_VAR:  final = 'RESOURCEPATH'

    clsLogger: Logger = getLogger(__name__)

    def __init__(self, fileName: str, docDisplayMethodParameters: DisplayMethodParameters = DisplayMethodParameters.DISPLAY, dpi: int = 0, headerText: str = ''):
        """

        Args:
            fileName:   Fully qualified file name

            docDisplayMethodParameters: global flag to determine whether or not or display a method's parameters

            dpi: dots per inch for the display we are mapping from;
            Some diagramming documents may not need a value for this since they map directly to display device

            headerText:  The header to place on the page
        """

        self._fileName:   str = fileName

        self._docDisplayMethodParameters: DisplayMethodParameters = docDisplayMethodParameters

        self._dpi:        int = dpi
        self._headerText: str = headerText
        self._fontSize:   int = BaseDiagram.DEFAULT_FONT_SIZE

        self._softwareNameVersion: str = ''
        self._diagramPadding:      DiagramPadding = DiagramPadding()

    @property
    def fontSize(self) -> int:
        """
        The font size to use in the generated UML diagram.  If unchanged the value is `pyumldiagrams.BaseDiagram.BaseDiagram.DEFAULT_FONT_SIZE`
        """
        return self._fontSize

    @fontSize.setter
    def fontSize(self, newSize: int):
        self._fontSize = newSize

    @property
    def horizontalGap(self) -> int:
        """
        The horizontal gap between UML elements.  If not set then the value is
        `pyumldiagrams.Defaults.DEFAULT_HORIZONTAL_GAP`
        """
        return self._diagramPadding.horizontalGap

    @horizontalGap.setter
    def horizontalGap(self, newValue: int):
        self._diagramPadding.horizontalGap = newValue

    @property
    def verticalGap(self) -> int:
        """
        The vertical gap between UML elements.  If not set then the value is
        `pyumldiagrams.Defaults.DEFAULT_VERTICAL_GAP`
        """
        return self._diagramPadding.verticalGap

    @verticalGap.setter
    def verticalGap(self, newValue):
        self._diagramPadding.verticalGap = newValue

    @property
    def headerText(self) -> str:
        """
        The text to display as the header on the generated document
        """
        return self._headerText

    @headerText.setter
    def headerText(self, newValue: str):
        self._headerText = newValue

    @property
    def softwareNameVersion(self) -> str:
        """
        Used to place the software name and version of the application using this library onto the
        generated image EXIF metadata
        """
        return self._softwareNameVersion

    @softwareNameVersion.setter
    def softwareNameVersion(self, newValue: str):
        self._softwareNameVersion = newValue

    @property
    def docTimeStamp(self) -> datetime:
        """
        Must be overridden by implementors
        """
        return cast(datetime, None)

    @docTimeStamp.setter
    def docTimeStamp(self, timeStamp: datetime):
        """
        Must be overridden by implementors

        """
        pass

    def retrieveResourcePath(self, bareFileName: str) -> str:
        """
        Must be overridden by implementors

        Args:
            bareFileName:

        Returns: a fully qualified name
        """
        pass

    def drawClass(self, classDefinition: ClassDefinition):
        """
        Draw the class diagram defined by the input
        Must be overridden by implementors

        Args:
            classDefinition:    The class definition
        """
        pass

    def drawUmlLine(self, lineDefinition: UmlLineDefinition):
        """
        Draw the inheritance, aggregation, or composition lines that describe the relationships
        between the UML classes

        Must be overridden by implementors

        Args:
            lineDefinition:   A UML Line definition
        """
        pass

    def drawEllipse(self, definition: EllipseDefinition):
        """
        Draw a general purpose ellipse

        Args:
            definition:     It's definition
        """
        pass

    def drawRectangle(self, definition: RectangleDefinition):
        """
        Draw a general purpose rectangle

        Args:
            definition:  The rectangle definition
        """
        pass

    def write(self):
        """
        Call this method when you are done with placing the diagram onto a document.
        Must be overridden by implementors
        """
        pass

    def _buildMethods(self, methods: Methods, displayParameters: DisplayMethodParameters) -> MethodsRepr:
        """

        Args:
            methods: The method definitions
            displayParameters:  Determines how to build the method parameter signature

        Returns:  The text version of each method as a list of method representations
        """

        methodReprs: BaseDiagram.MethodsRepr = []

        for methodDef in methods:

            methodRepr: str = self._buildMethod(methodDef, displayParameters)
            methodReprs.append(methodRepr)

        return methodReprs

    def _buildMethod(self, methodDef: MethodDefinition, displayParameters: DisplayMethodParameters) -> str:

        if methodDef.visibility is None:
            methodRepr: str = f'{methodDef.name}'
        else:
            methodRepr: str = f'{methodDef.visibility.value} {methodDef.name}'

        paramRepr: str = ''

        if displayParameters == DisplayMethodParameters.DISPLAY:

            self.clsLogger.debug(f'{methodDef.name} - {len(methodDef.parameters)=}')

            paramRepr = self.__generateParametersString(methodDef, paramRepr)
        elif displayParameters == DisplayMethodParameters.UNSPECIFIED:
            if self._docDisplayMethodParameters == DisplayMethodParameters.DISPLAY:
                paramRepr = self.__generateParametersString(methodDef, paramRepr)

        methodRepr = f'{methodRepr}({paramRepr})'

        return methodRepr

    def _buildFields(self, fields: Fields) -> FieldsRepr:

        fieldsRepr: BaseDiagram.FieldsRepr = []

        for fieldDef in fields:
            fieldRepr: str = self._buildField(fieldDef)
            fieldsRepr.append(fieldRepr)

        return fieldsRepr

    def _buildField(self, fieldDef: FieldDefinition) -> str:

        fieldRepr: str = f'{fieldDef.name}'

        if fieldDef.parameterType != '' and fieldDef.parameterType is not None:
            fieldRepr = f'{fieldRepr}: {fieldDef.parameterType}'

        if fieldDef.defaultValue != '' and fieldDef.defaultValue is not None:
            fieldRepr = f'{fieldRepr} = {fieldDef.defaultValue}'

        return fieldRepr

    def __generateParametersString(self, methodDef, paramRepr):

        nParams:  int = len(methodDef.parameters)
        paramNum: int = 0

        for parameterDef in methodDef.parameters:
            parameterDef = cast(ParameterDefinition, parameterDef)
            paramNum += 1

            paramRepr = f'{paramRepr}{parameterDef.name}'

            if parameterDef.parameterType is None or len(parameterDef.parameterType) == 0:
                paramRepr = f'{paramRepr}'
            else:
                paramRepr = f'{paramRepr}: {parameterDef.parameterType}'

            if parameterDef.defaultValue is None or len(parameterDef.defaultValue) == 0:
                paramRepr = f'{paramRepr}'
            else:
                paramRepr = f'{paramRepr}={parameterDef.defaultValue}'

            if paramNum == nParams:
                paramRepr = f'{paramRepr}'
            else:
                paramRepr = f'{paramRepr}, '

        return paramRepr
