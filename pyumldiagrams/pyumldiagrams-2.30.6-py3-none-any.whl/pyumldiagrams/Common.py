
from typing import final
from typing import Tuple

from math import pi
from math import atan
from math import cos
from math import sin

from pyumldiagrams.Internal import ArrowPoints
from pyumldiagrams.Internal import DiamondPoints
from pyumldiagrams.Internal import InternalPosition


class Common:

    INHERITANCE_ARROW_HEIGHT: final = 10
    DIAMOND_HEIGHT:           final = 8

    @classmethod
    def computeTheArrowVertices(cls, src: InternalPosition, dest: InternalPosition)  -> ArrowPoints:
        """
        Draw an arrow at the end of the line source-dest.

        Args:
            src:  points of the segment
            dest:  points of the segment

        Returns:
            A list of positions that describes a diamond to draw
        """
        # x1: float = src.x
        # y1: float = src.y
        # x2: float = dest.x
        # y2: float = dest.y
        #
        # deltaX: float = x2 - x1
        # deltaY: float = y2 - y1
        deltaX, deltaY = Common.computeDeltaXDeltaY(src, dest)
        if abs(deltaX) < 0.01:   # vertical segment
            if deltaY > 0:
                alpha = -pi/2
            else:
                alpha = pi/2
        else:
            if deltaX == 0:
                alpha = pi/2
            else:
                alpha = atan(deltaY/deltaX)
        if deltaX > 0:
            alpha += pi

        pi_6: float = pi/6      # radians for 30 degree angle

        alpha1: float = alpha + pi_6
        alpha2: float = alpha - pi_6
        size:   float = Common.INHERITANCE_ARROW_HEIGHT
        x2: float = dest.x
        y2: float = dest.y
        #
        # The names for the left and right points are correct for upward facing arrows
        # They are inverted for downward facing arrows
        #
        arrowTip:   InternalPosition = InternalPosition(x2, y2)
        rightPoint: InternalPosition = InternalPosition(x2 + size * cos(alpha1), y2 + size * sin(alpha1))
        leftPoint:  InternalPosition = InternalPosition(x2 + size * cos(alpha2), y2 + size * sin(alpha2))

        points: ArrowPoints = [rightPoint, arrowTip, leftPoint]

        return points

    @classmethod
    def computeDiamondVertices(cls, src: InternalPosition, dest: InternalPosition) -> DiamondPoints:
        """
        Args:
            src:    The source point
            dest:   The destination point
        """
        pi_6: float = pi/6     # radians for 30 degree angle
        x2:   float = dest.x
        y2:   float = dest.y

        deltaX, deltaY = Common.computeDeltaXDeltaY(src, dest)

        if abs(deltaX) < 0.01:  # vertical segment
            if deltaY > 0:
                alpha = -pi/2
            else:
                alpha = pi/2
        else:
            if deltaX == 0:
                if deltaY > 0:
                    alpha = pi/2
                else:
                    alpha = 3 * pi / 2
            else:
                alpha = atan(deltaY/deltaX)
        if deltaX > 0:
            alpha += pi

        alpha1: float = alpha + pi_6
        alpha2: float = alpha - pi_6
        size:   int   = Common.DIAMOND_HEIGHT

        # noinspection PyListCreation
        points: DiamondPoints = []

        points.append((InternalPosition(x2 + size * cos(alpha1), y2 + size * sin(alpha1))))
        points.append(InternalPosition(x2, y2))
        points.append(InternalPosition(x2 + size * cos(alpha2), y2 + size * sin(alpha2)))
        points.append(InternalPosition(x2 + 2 * size * cos(alpha), y2 + 2 * size * sin(alpha)))

        return points

    @classmethod
    def computeDeltaXDeltaY(cls, src: InternalPosition, dest: InternalPosition) -> Tuple[float, float]:

        x1: float = src.x
        y1: float = src.y
        x2: float = dest.x
        y2: float = dest.y

        deltaX: float = x2 - x1
        deltaY: float = y2 - y1

        return deltaX, deltaY

    @classmethod
    def computeMidPointOfBottomLine(cls, startPos: InternalPosition, endPos: InternalPosition) -> InternalPosition:
        """
        These two coordinates are the two end-points of the bottom leg of the inheritance arrow
        midPoint = (x1+x2/2, y1+y2/2)

        Args:
            startPos: start of line
            endPos:   end of line

        Returns:  Midpoint between startPos - endPos

        """
        x1: float = startPos.x
        y1: float = startPos.y
        x2: float = endPos.x
        y2: float = endPos.y

        midX: float = (x1 + x2) / 2
        midY: float = (y1 + y2) / 2

        return InternalPosition(midX, midY)
