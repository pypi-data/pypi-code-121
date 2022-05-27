#  -*- coding: utf-8 -*-
"""Tests for the rigid body classes"""
import pytest
import numpy as np
from cv2 import aruco
import sksurgeryarucotracker.algorithms.rigid_bodies as rgbd

# pylint: disable=no-member

def test_rigid_body_init():
    """
    Test class initialises
    """
    #pylint: disable=protected-access
    rigid_body = rgbd.ArUcoRigidBody(rigid_body_name = 'test')

    rigid_body.load_3d_points('data/reference.txt', 'DICT_ARUCO_ORIGINAL')
    pattern_wdth = min(np.ptp([i[:,0] for i in rigid_body._ar_board.objPoints]),
                       np.ptp([i[:,1] for i in rigid_body._ar_board.objPoints]))
    assert pattern_wdth == 49.50

    rigid_body.scale_3d_tags(measured_pattern_width = 10)
    pattern_wdth = min(np.ptp([i[:,0] for i in rigid_body._ar_board.objPoints]),
                       np.ptp([i[:,1] for i in rigid_body._ar_board.objPoints]))
    assert pattern_wdth == 10.00


def test_make_aruco_no_board():
    """
    Test for make aruco board fails when no board entries
    """
    with pytest.raises(ValueError):
        board = np.zeros((0,0),dtype = np.float64)
        rgbd._make_aruco_board(board, aruco.DICT_ARUCO_ORIGINAL) \
                        #pylint: disable=protected-access

def test_make_aruco_wrong_board():
    """
    Test for make aruco board fails when no board is wrong shape
    """
    with pytest.raises(ValueError):
        board = np.zeros((1,4),dtype = np.float64)
        rgbd._make_aruco_board(board, aruco.DICT_ARUCO_ORIGINAL) \
                        #pylint: disable=protected-access


def test_configuration():
    """
    Tests for the configuration routine.
    """
    #should throw a value error if there is no filename
    configuration = {
                        'rigid bodies' : [{}]
                    }
    with pytest.raises(ValueError):
        rgbd.configure_rigid_bodies(configuration)

    #should throw a value error for a made up dictionary
    configuration = {
                        'rigid bodies' : [{
                             'filename' : 'data/reference.txt',
                             'aruco dictionary' : 'made up'
                        }]
                    }
    with pytest.raises(ImportError):
        rgbd.configure_rigid_bodies(configuration)
