from nwon_baseline.typings import BoundingBoxCoordinates, BoundingBoxTuple


def bounding_box_coordinates_from_tuple(box: BoundingBoxTuple):
    """
    The box is expected to be a Tuple with coordinates (x1, y1, x2, y2)
    """

    left, top, right, bottom = box
    return BoundingBoxCoordinates(
        top=top,
        right=right,
        bottom=bottom,
        left=left,
    )


def bounding_box_tuple_from_coordinates(
    box: BoundingBoxCoordinates,
) -> BoundingBoxTuple:
    """
    The box returned is a Tuple with coordinates (x1, y1, x2, y2)
    """

    return BoundingBoxTuple((box.left, box.top, box.right, box.bottom))
