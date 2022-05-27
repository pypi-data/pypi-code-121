""" Classes and functions for 2D to 3D registration """

import numpy as np
from cv2 import aruco

def _marker_size(marker_points):
    """
    Internal function to calculate the size of a marker
    :param marker_points: 2d or 3d points that make up the marker,
        1 row per point

    :return: The size of the marker
    """
    maxs = np.max(marker_points, axis = 0)
    mins = np.min(marker_points, axis = 0)
    size = np.linalg.norm(maxs - mins)
    return size

def estimate_poses_no_calibration(marker_corners, aruco_board):
    """
    Returns tracking data for a camera with no calibration data.
    x and y are the screen pixel coordinates.
    z is based on the size of the tag in pixels, there is no
    rotation. No account is taken of the size of the
    model marker pattern, so it will be bit flakey.
    """
    tracking_rot = np.full((1,3), np.nan, dtype = float)
    tracking_trans = np.full((1,3), np.nan, dtype = float)
    quality = len(marker_corners) / len(aruco_board.ids)

    x_means = []
    y_means = []
    sizes = []

    if len(marker_corners) > 0:
        tracking_rot = np.zeros((1,3), dtype = float)
        tracking_trans = np.zeros((1,3), dtype = float)
        for marker in marker_corners:

            means = np.mean(marker[0], axis=0)
            x_means.append(means[0])
            y_means.append(means[1])
            sizes.append(_marker_size(marker[0]))

        x_mean = np.mean(x_means)
        y_mean = np.mean(y_means)
        size = np.mean(sizes)

        tracking_trans[0][0] = x_mean
        tracking_trans[0][1] = y_mean
        tracking_trans[0][2] = -size

    return tracking_rot, tracking_trans, quality

def estimate_poses_with_calibration(marker_corners2d, marker_ids,
                aruco_board, camera_projection_matrix, camera_distortion):
    """
    Estimate the pose of a single tag or a multi-tag rigid body
    when the camera calibration is known.
    :param marker_corners2d: a list of 2d marker corners, 1 row per tag,
        8 columns per tag
    :param model_points: Matched list of of corresponding model points,
        1 row per tag, 15 columns per tag: corner points and centre point
    :param camera_projection_matrix: a 3x3 camera projection matrix
    :param camera_distortion: camera distortion vector

    :return : a tracking rotation, translation and a quality
    """
    #pylint: disable=no-member
    tracking_rot = np.full((1,3), np.nan, dtype = float)
    tracking_trans = np.full((1,3), np.nan, dtype = float)
    quality = len(marker_ids) / len(aruco_board.ids)

    if len(marker_corners2d) == 0:
        return tracking_rot, tracking_trans, quality

    if len(marker_corners2d) == 1:
        marker_width = aruco_board.objPoints[0][1][0] \
                        - aruco_board.objPoints[0][0][0]
        rvecs, tvecs, _ = \
            aruco.estimatePoseSingleMarkers(marker_corners2d, marker_width,
                                            camera_projection_matrix,
                                            camera_distortion)
        assert len(rvecs) == 1
        return rvecs[0], tvecs[0][0], quality

    rvec = np.empty((1,3), dtype = np.float32)
    tvec = np.empty((1,3), dtype = np.float32)
    markers_used, rvecs, tvecs = \
        aruco.estimatePoseBoard(marker_corners2d, np.array([marker_ids]),
                                    aruco_board,
                                    camera_projection_matrix,
                                    camera_distortion,
                                    rvec,
                                    tvec)

    #marker ids should be presorted, so that all 2d markers are on board
    assert markers_used == len(marker_ids)

    return rvecs[:,0], tvecs, quality
