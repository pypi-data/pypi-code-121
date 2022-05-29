
from pyumldiagrams.Common import Common
from pyumldiagrams.Defaults import LEFT_MARGIN
from pyumldiagrams.Defaults import TOP_MARGIN

from pyumldiagrams.Definitions import Position
from pyumldiagrams.Internal import InternalPosition


class ImageCommon(Common):

    @classmethod
    def toInternal(cls, position: Position, verticalGap: float, horizontalGap: float) -> InternalPosition:
        """
        Assumes a 1 to 1 relationship between display device and the image we are generating.

        Args:
            position:  The original position

            verticalGap:  Account for the vertical gap on the X-axis

            horizontalGap:  Account for the horizontal gap on the Y-axis

        Returns:  The new position adjust for margins and gaps
        """
        adjustedX: float = position.x + LEFT_MARGIN + verticalGap
        adjustedY: float = position.y + TOP_MARGIN  + horizontalGap

        return InternalPosition(x=adjustedX, y=adjustedY)
