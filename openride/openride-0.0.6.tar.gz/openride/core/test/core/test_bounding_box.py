from openride.core.bounding_box import BoundingBox
from openride.core.numba.transforms import transform_vertices
from openride.core.point import Point
from openride.core.rotation import Rotation
from openride.core.size import Size
from openride.core.test.random_core_generator import get_random
from openride.core.transform import Transform

from shapely import geometry

import numpy as np
import pytest



def test_init():
    b = BoundingBox()
    assert b.position == Point()
    assert b.rotation == Rotation()
    assert b.size == Size()


def test_bird_eye_view_vertices_shape():
    assert BoundingBox().bird_eye_view_vertices.shape == (4,2)


def test_bird_eye_view_vertices_translation():
    v = BoundingBox(Point(1,2,3)).bird_eye_view_vertices
    assert np.all(v == np.array([[2,3],[2,1],[0,1],[0,3]]))


def test_bird_eye_view_vertices_rotation():
    v = BoundingBox(rotation=Rotation(0,0,np.pi/6)).bird_eye_view_vertices
    x = np.sin(np.deg2rad(15))*2**0.5
    assert np.all(pytest.approx(v) == np.array([[x,1+x],[1+x,-x],[-x,-1-x],[-1-x,x]]))


def test_bird_eye_view_vertices_scale():
    v = BoundingBox(size=Size(2,2,2)).bird_eye_view_vertices
    assert np.all(v == np.array([[2,2],[2,-2],[-2,-2],[-2,2]]))


def test_vertices_shape():
    assert BoundingBox().vertices.shape == (8,3)


def test_bounding_box_to_shapely():
    b = BoundingBox()
    assert isinstance(b.to_shapely(), geometry.Polygon)


def test_get_transform():
    b = BoundingBox()
    assert isinstance(b.get_transform(), Transform)


def test_box_transform_identity():
    b = BoundingBox()
    assert b == b.transform(Transform())


def test_box_rotation():
    b = BoundingBox()
    tf = Transform(rotation=Rotation(0,0,np.pi/6))
    assert pytest.approx(b.transform(tf).rotation.yaw) == np.pi/6


def test_box_transform():
    for _ in range(10):
        b = get_random(BoundingBox)
        tf = Transform(Point(*np.random.random(3)*10), Rotation(0,0,np.random.random()*2*np.pi))
        v1 = b.transform(tf).vertices
        v2 = transform_vertices(b.vertices, tf.matrix)
        assert np.all(pytest.approx(v1) == v2)
        