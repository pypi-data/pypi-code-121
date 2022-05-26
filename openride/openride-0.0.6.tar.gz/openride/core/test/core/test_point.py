from openride.core.point import Point
from openride.core.rotation import Rotation
from openride.core.transform import Transform

from shapely import geometry

import numpy as np
import pytest



def test_point_init():
    p = Point(1,2,3)
    assert p.x == 1 and p.y == 2 and p.z == 3


def test_point_to_shapely():
    p = Point(1,2,3)
    ps = p.to_shapely()
    assert isinstance(ps, geometry.Point)


def test_transform_identity_point():
    p = Point(0,0,0)
    tf = Transform()
    p2 = p.transform(tf)
    assert p == p2


def test_translate_point():
    p = Point(1,2,3)
    tf = Transform(Point(4,5,6))
    p2 = p.transform(tf)
    assert p2 == Point(5,7,9)


def test_rotate_x_point():
    p = Point(1,1,1)
    tf = Transform(rotation=Rotation(roll=np.pi/2))
    p2 = p.transform(tf)
    assert pytest.approx(p2.x) == 1
    assert pytest.approx(p2.y) == 1
    assert pytest.approx(p2.z) == -1


def test_rotate_y_point():
    p = Point(1,1,1)
    tf = Transform(rotation=Rotation(pitch=np.pi/2))
    p2 = p.transform(tf)
    assert pytest.approx(p2.x) == -1
    assert pytest.approx(p2.y) == 1
    assert pytest.approx(p2.z) == 1


def test_rotate_z_point():
    p = Point(1,1,1)
    tf = Transform(rotation=Rotation(yaw=np.pi/2))
    p2 = p.transform(tf)
    assert pytest.approx(p2.x) == 1
    assert pytest.approx(p2.y) == -1
    assert pytest.approx(p2.z) == 1


def test_add_points():
    p1 = Point(1,2,3)
    p2 = Point(4,5,6)
    assert p1 + p2 == Point(5,7,9)


def test_substract_points():
    p1 = Point(1,2,3)
    p2 = Point(4,5,6)
    assert p1 - p2 == Point(-3,-3,-3)


def test_repr_point():
    assert isinstance(str(Point()), str)