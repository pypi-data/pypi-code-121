from typing import Tuple, Optional

import numpy as np


def rotation_matrix(angle_radians: float) -> np.ndarray:
    """Returns a 2D rotation matrix."""
    c = np.cos(angle_radians)
    s = np.sin(angle_radians)
    return np.array([[c, -s], [s, c]])


def rotate(coords: np.ndarray, angle_degrees: float) -> np.ndarray:
    """Rotates an array of (x, y) coordinates counterclockwise by
    the specified angle.

    Args:
        coords: Shape (n, 2) array of (x, y) coordinates.
        angle_degrees: The angle by which to rotate the coordinates.

    Returns:
        Shape (n, 2) array of rotated coordinates (x', y')
    """
    coords = np.asarray(coords)
    assert coords.ndim == 2
    assert coords.shape[1] == 2
    R = rotation_matrix(np.radians(angle_degrees))
    return (R @ coords.T).T


def translate(coords: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """Translates the given (x, y) coordinates in the palne by ``(dx, dy)``.

    Args:
        coords: Shape (n, 2) array of (x, y) coordinates.
        dx: Amount by which to translate in the x direction.
        dy: Amount by which to translate in the y direction.

    Returns:
        Shape (n, 2) array of translated coordinates (x', y')
    """
    coords = np.asarray(coords)
    assert coords.ndim == 2
    assert coords.shape[1] == 2
    return coords + np.array([[dx, dy]])


def ellipse(
    a: float,
    b: float,
    points: int = 100,
    center: Tuple[float, float] = (0, 0),
    angle: float = 0,
):
    """Returns the coordinates for an ellipse with major axis a and semimajor axis b,
    rotated by the specified angle about (0, 0), then translated to the specified center.

    Args:
        a: Major axis length
        b: Semi-major axis length
        points: Number of points in the circle
        center: Coordinates of the center of the circle
        angle: Angle (in degrees) by which to rotate counterclockwise about (0, 0)
            **before** translating to the specified center.

    Returns:
        A shape ``(points, 2)`` array of (x, y) coordinates
    """
    x0, y0 = center
    theta = np.linspace(0, 2 * np.pi, points, endpoint=False)
    xs = a * np.cos(theta)
    ys = b * np.sin(theta)
    coords = np.stack([xs, ys], axis=1) + np.array([[x0, y0]])
    if angle:
        coords = rotate(coords, angle)
    return coords


def circle(
    radius: float, points: int = 100, center: Tuple[float, float] = (0, 0)
) -> np.ndarray:
    """Returns the coordinates for a circle with a given radius, centered at the
    specified center.

    Args:
        radius: Radius of the circle
        points: Number of points in the circle
        center: Coordinates of the center of the circle

    Returns:
        A shape ``(points, 2)`` array of (x, y) coordinates
    """
    return ellipse(
        radius,
        radius,
        points=points,
        center=center,
        angle=0,
    )


def box(
    width: float,
    height: Optional[float] = None,
    points_per_side: int = 25,
    center: Tuple[float, float] = (0, 0),
    angle: float = 0,
) -> np.ndarray:
    """Returns the coordinates for a rectangle with a given width and height,
    centered at the specified center.

    Args:
        width: Width of the rectangle (in the x direction).
        height: Height of the rectangle (in the y direction). If None is given,
            then height is set to width and the function returns a square.
        points_per_side: Number of points on each side of the box.
        center: Coordinates of the center of the rectangle.
        angle: Angle (in degrees) by which to rotate counterclockwise about (0, 0)
            **before** translating to the specified center.

    Returns:
        A shape ``(4 * points_per_side, 2)`` array of (x, y) coordinates
    """
    width = abs(width)
    if height is None:
        height = width
    height = abs(height)
    x0, y0 = center
    xs = np.concatenate(
        [
            width / 2 * np.ones(points_per_side),
            np.linspace(width / 2, -width / 2, points_per_side),
            -width / 2 * np.ones(points_per_side),
            np.linspace(-width / 2, width / 2, points_per_side),
        ]
    )
    ys = np.concatenate(
        [
            np.linspace(-height / 2, height / 2, points_per_side),
            height / 2 * np.ones(points_per_side),
            np.linspace(height / 2, -height / 2, points_per_side),
            -height / 2 * np.ones(points_per_side),
        ]
    )
    coords = np.stack([xs, ys], axis=1) + np.array([[x0, y0]])
    if angle:
        coords = rotate(coords, angle)
    return coords


def close_curve(points: np.ndarray) -> np.ndarray:
    """Close a curve (making the start point equal to the end point),
    if it is not already closed.

    Args:
        points: Shape ``(m, n)`` array of ``m`` coordinates in ``n`` dimensions.

    Returns:
        ``points`` with the first point appended to the end if the start point
        was not already equal to the end point.
    """
    if not np.allclose(points[0], points[-1]):
        points = np.concatenate([points, points[:1]], axis=0)
    return points
