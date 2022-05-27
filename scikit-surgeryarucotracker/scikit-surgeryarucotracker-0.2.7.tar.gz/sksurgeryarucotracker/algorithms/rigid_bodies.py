""" Classes and functions for maintaining ArUco rigid bodies """

import numpy
from cv2 import aruco
from sksurgeryarucotracker.algorithms.registration_2d3d import \
                estimate_poses_no_calibration, estimate_poses_with_calibration

#pylint: disable=no-member
def _make_aruco_board(markers, dictionary):
    """
    Makes a cv2.aruco.board from an array of 5 or 4 3D points plus
    marker IDs. First column of markers should be marker ids,
    next 15 or 12 columns are 3d coordinates
    """
    dictionary = aruco.getPredefinedDictionary(dictionary)
    #format of ID first, then 15 or 12 columns
    boardshape=markers.shape

    if boardshape[0] < 1:
        raise ValueError("Marker pattern appears to have no markers")

    try:
        _ = boardshape[1]
    except IndexError:
        markers = markers.reshape(1, boardshape[0])
        boardshape=markers.shape

    if boardshape[1] != 16 and boardshape[1] != 13:
        raise ValueError("Marker pattern should have either 5 or 4 3D points")

    marker_ids = markers[:,0].astype('int')
    markerpoints = markers[:,1:13]
    if boardshape[1] == 16:
        markerpoints = markers[:,4:16].astype('float32')

    return aruco.Board_create(markerpoints, dictionary, marker_ids)


def load_board_from_file(filename, dictionary = aruco.DICT_ARUCO_ORIGINAL):
    """
    loads marker pattern from filename.
    :return: an aruco.board
    :raise ValueError: If the file does not have 16 or 13 columns
    """
    markers = numpy.loadtxt(filename)

    return _make_aruco_board(markers, dictionary)


def configure_rigid_bodies(configuration):
    """
    reads configuration and creates a list of rigid bodies
    together with a list of dictionaries used.
    """
    dictionary_name = configuration.get("aruco dictionary", 'DICT_4X4_50')
    try:
        ar_dictionary_name = getattr(aruco, dictionary_name)
    except AttributeError:
        raise ImportError((f'Failed when trying to import {dictionary_name}'
                            'from cv2.aruco. Check dictionary exists.')) \
                                    from AttributeError
    ar_dicts = []
    ar_dict_names = []
    ar_dicts.append(aruco.getPredefinedDictionary(ar_dictionary_name))
    ar_dict_names.append(dictionary_name)

    rigid_bodies = []
    rigid_body_configs = configuration.get('rigid bodies', [])

    for rigid_body_config in rigid_body_configs:
        rigid_body = ArUcoRigidBody(rigid_body_config.get('name','no name'))
        filename = rigid_body_config.get('filename', None)
        if filename is None:
            raise ValueError('rigid body configuration must include filename')
        dictionary_name = rigid_body_config.get('aruco dictionary',
                                                'DICT_ARUCO_ORIGINAL')
        try:
            ar_dictionary_name = getattr(aruco, dictionary_name)
        except AttributeError:
            raise ImportError((f'Failed when trying to import {dictionary_name}'
                                'from cv2.aruco. Check dictionary exists.')) \
                                        from AttributeError

        rigid_body.load_3d_points(filename, dictionary_name)

        tag_width = rigid_body_config.get('tag width', None)
        if tag_width is not None:
            rigid_body.scale_3d_tags(tag_width)

        rigid_bodies.append(rigid_body)
        if dictionary_name not in ar_dict_names:
            ar_dict_names.append(dictionary_name)
            ar_dicts.append(aruco.getPredefinedDictionary(ar_dictionary_name))

    return ar_dicts, ar_dict_names, rigid_bodies


def single_tag_board(tag_size, marker_id,
                dictionary =
                aruco.getPredefinedDictionary(aruco.DICT_ARUCO_ORIGINAL)):
    """
    Create a board consisting of a single ArUco tag

    :param: tag size in mm
    :param: marker id
    :param: dictionary to use
    """
    tag = numpy.array([[
        -tag_size/2.0, -tag_size/2.0, 0.,
        tag_size/2.0, -tag_size/2.0, 0.,
        tag_size/2.0, tag_size/2.0, 0.,
        -tag_size/2.0, tag_size/2.0, 0.]], dtype=numpy.float32)

    marker_ids = numpy.array([marker_id])
    return aruco.Board_create(tag, dictionary, marker_ids)


def scale_tags(board, measured_pattern_width):
    """
    We can scale the tag on a board,
    which is very useful if you've got the tag
    on your mobile phone.

    :param: the board to scale
    :param measured_pattern_width: Width of the tag in mm
    """

    model_pattern_width = min(numpy.ptp([i[:, 0] for i in board.objPoints]),
                              numpy.ptp([i[:, 1] for i in board.objPoints]))
    scale_factor = measured_pattern_width/model_pattern_width
    scaled_board = []
    for tag in board.objPoints:
        tag *= scale_factor
        scaled_board.append(tag)

    return aruco.Board_create(scaled_board, board.dictionary, board.ids)

class TwoDTags():
    """
    Stores two linked arrays, on of tag IDs and the other
    2D points
    """

    def __init__(self):
        self.points = []
        self.ids = []

    def append_tag(self, tag_id, points):
        """ Adds a tag to the two point list
        :param tag_id: The id of the tag
        :param points: 4 points defining the tag corners
        """
        self.points.append(points)
        self.ids.append(tag_id)


class ArUcoRigidBody():
    """
    Class to handle the loading and registering of ArUco Rigid Bodies
    """

    def __init__(self, rigid_body_name):
        """
        Initialises the RigidBody  class.
        """
        self._ar_board = None
        self._tags_2d = TwoDTags()
        self.name = rigid_body_name
        self._default_tags = None
        self._dictionary_name = "Not Set"

    def reset_2d_points(self):
        """
        Clears 2D point lists.
        """
        self._tags_2d = TwoDTags()

    def set_2d_points(self, two_d_points, tag_ids):
        """
        takes a list of 2 points, and if the id's match 3D points,
        assigns them to a list of 2d points

        :param two_d_points: array of marker corners, 4 for each tag
        :param tag_ids: id for each tag

        :return: tag ids for any assigned tags
        """
        tags_assigned = []
        for index, tag_id in enumerate(tag_ids):
            if tag_id in self._ar_board.ids:
                self._tags_2d.append_tag(tag_id, two_d_points[index])
                tags_assigned.append(tag_id)
        self._default_tags = two_d_points
        return tags_assigned

    def load_3d_points(self, filename, dictionaryname):
        """
        Loads the 3D point geometry from a file

        :param filename: Path of file containing tag data

        """

        self._dictionary_name = dictionaryname
        ar_dictionary_name = getattr(aruco, dictionaryname)
        self._ar_board = load_board_from_file(filename, ar_dictionary_name)

    def add_single_tag(self, tag_size, marker_id, dictionary):
        """
        We can use this to track single ArUco tags rather than
        patterns as long as we know the tag size in mm

        :param: tag size in mm
        :param: marker id/_
        """
        self._ar_board = single_tag_board(tag_size, marker_id, dictionary)

    def scale_3d_tags(self, measured_pattern_width):
        """
        We can scale the tag, which is very useful if you've got the tag
        on your mobile phone.

        :param measured_pattern_width: Width of the tag in mm
        """
        self._ar_board = scale_tags(self._ar_board, measured_pattern_width)

    def get_pose(self, camera_projection_matrix, camera_distortion):
        """
        Estimate the pose of the rigid body, with or without
        camera calibration

        :param: camera_projection_matrix 3x3 projection matrix. If
            None we estimate pose based on pattern size
        :param: 1x5 camera distortion vector
        """
        if camera_projection_matrix is None:
            return estimate_poses_no_calibration(self._tags_2d.points,
                                                 self._ar_board)

        return estimate_poses_with_calibration(
                        self._tags_2d.points, self._tags_2d.ids,
                            self._ar_board,
                            camera_projection_matrix, camera_distortion)

    def get_dictionary_name(self):
        """returns the name of the aruco dictionary in use"""

        return self._dictionary_name
