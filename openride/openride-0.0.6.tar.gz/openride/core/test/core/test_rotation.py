import openride
import numpy as np
import pytest


def test_init():
    r = openride.Rotation(1,2,3)
    assert r.roll == 1 and r.pitch == 2 and r.yaw == 3

def test_post_init():
    r = openride.Rotation(1+2*np.pi,2-2*np.pi,3+10*np.pi)
    assert r.roll == 1 and r.pitch == 2 and r.yaw == 3

def test_rotation_matrix_identity():
    r = openride.Rotation(0,0,0)
    assert np.all(r.matrix == np.eye(3))

def test_rotation_from_identity():
    r = openride.Rotation.from_matrix(np.eye(3))
    assert r.roll == 0 and r.pitch == 0 and r.yaw == 0

def test_rotation_euler_matrix_reciprocal():
    for _ in range(10):
        r1 = openride.Rotation(*np.random.random(3)*2*np.pi)
        r2 = openride.Rotation.from_matrix(r1.matrix)
        assert np.all(pytest.approx(r1.matrix) == r2.matrix)
