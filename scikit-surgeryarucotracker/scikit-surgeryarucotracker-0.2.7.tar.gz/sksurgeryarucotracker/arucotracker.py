#  -*- coding: utf-8 -*-

"""A class for straightforward tracking with an ARuCo
"""
from time import time
from numpy import array, float32, loadtxt, ravel, float64
from cv2 import aruco
import cv2


from sksurgerycore.baseclasses.tracker import SKSBaseTracker
from sksurgeryarucotracker.algorithms.rigid_bodies import ArUcoRigidBody, \
                configure_rigid_bodies


def _load_calibration(textfile):
    """
    loads a calibration from a text file
    """
    projection_matrix = loadtxt(textfile, dtype=float32, max_rows=3)
    distortion = loadtxt(textfile, dtype=float32, skiprows=3, max_rows=1)

    return projection_matrix, distortion

class ArUcoTracker(SKSBaseTracker):
    """
        Initialises and Configures the ArUco detector

        :param configuration: A dictionary containing details of the tracker.

            video source: defaults to 0

            aruco dictionary: defaults to DICT_4X4_50

            marker size: defaults to 50 mm

            camera projection: defaults to None

            camera distortion: defaults to None

            smoothing buffer: specify a buffer over which to average the
            tracking, defaults to 1

            rigid bodies: a list of rigid bodies to track, each body should
            have a 'name', a 'filename' where the tag geometry is defined,
            and an 'aruco dictionary' to use. Additionally we can include
            'tag width' in mm when the tag has been scaled during printing or
            is displayed on a mobile phone screen or similar

        :raise Exception: ImportError, ValueError
        """

    def __init__(self, configuration):

        self._camera_projection_matrix = configuration.get("camera projection",
                                                           None)
        self._camera_distortion = configuration.get(
                        "camera distortion", array([0.0, 0.0, 0.0, 0.0, 0.0],
                                                   dtype=float32))
        self._state = None

        self._frame_number = 0

        self._debug = configuration.get("debug", False)

        video_source = configuration.get("video source", 0)

        if video_source != 'none':
            self._capture = cv2.VideoCapture()
        else:
            self._capture = None

        self._ar_dicts, self._ar_dict_names, self._rigid_bodies = \
                        configure_rigid_bodies(configuration)

        super().__init__(configuration, self._rigid_bodies)
        self._marker_size = configuration.get("marker size", 50)

        if "calibration" in configuration:
            self._camera_projection_matrix, self._camera_distortion = \
                _load_calibration(configuration.get("calibration"))

        self._check_pose_estimation_ok()

        if video_source != 'none':
            if self._capture.open(video_source):
                #try setting some properties
                if "capture properties" in configuration:
                    props = configuration.get("capture properties")
                    for prop in props:
                        cvprop = getattr(cv2, prop)
                        value = props[prop]
                        self._capture.set(cvprop, value)

                self._state = "ready"
            else:
                raise OSError(f'Failed to open video source {video_source}')
        else:
            self._state = "ready"


    def _check_pose_estimation_ok(self):
        """Checks that the camera projection matrix and camera distortion
        matrices can be used to estimate pose"""
        if self._camera_projection_matrix is None:
            return

        if (self._camera_projection_matrix.shape == (3, 3) and
                (self._camera_projection_matrix.dtype in [float32,
                        float64, float])):
            return

        raise ValueError(('Camera projection matrix needs to be 3x3 and'
                          'float32'), self._camera_projection_matrix.shape,
                          self._camera_projection_matrix.dtype)

    def close(self):
        """
        Closes the connection to the Tracker and
        deletes the tracker device.

        :raise Exception: ValueError
        """
        if self._capture is not None:
            self._capture.release()
            del self._capture
        self._state = None

    def get_frame(self, frame=None):
        """Gets a frame of tracking data from the Tracker device.

        :param frame: an image to process, if None, we use the OpenCV
            video source.
        :return:

            port_numbers: If tools have been defined port numbers are the tool
            descriptions. Otherwise port numbers are the aruco tag ID
            prefixed with aruco

            time_stamps : list of timestamps (cpu clock), one per tool

            frame_numbers : list of framenumbers (tracker clock) one per tool

            tracking : list of 4x4 tracking matrices, rotation and position,

            tracking_quality : list the tracking quality, one per tool.

        :raise Exception: ValueError
        """
        if self._state != "tracking":
            raise ValueError('Attempted to get frame, when not tracking')

        if self._capture is not None:
            _, frame = self._capture.read()

        if frame is None:
            raise ValueError('Frame not set, and capture.read failed')

        port_handles = []
        time_stamps = []
        frame_numbers = []
        tracking_rots = []
        tracking_trans = []
        quality = []
        self._reset_rigid_bodies()

        timestamp = time()

# Issue #46: Switching to opencv-headless, so you can't use GUI.
#        if self._debug:
#            cv2.imshow('frame', frame)

        temporary_rigid_bodies = []
        for dict_index, ar_dict in enumerate(self._ar_dicts):
            #pylint: disable=no-member
            marker_corners, marker_ids, _ = \
                    aruco.detectMarkers(frame, ar_dict)
            if not marker_corners:
                continue

            if self._debug:
                aruco.drawDetectedMarkers(frame, marker_corners)

            assigned_marker_ids = []
            for rigid_body in self._rigid_bodies:
                if rigid_body.get_dictionary_name() == \
                                self._ar_dict_names[dict_index]:
                    assigned_marker_ids.extend(rigid_body.set_2d_points(
                                    marker_corners, marker_ids))

            #find any unassigned tags and create a rigid body for them
            for index, marker_id in enumerate(marker_ids):
                if marker_id[0] not in ravel(assigned_marker_ids):
                    temp_rigid_body = ArUcoRigidBody(
                                    str(self._ar_dict_names[dict_index]) +
                                    ":" + str(marker_id[0]))
                    temp_rigid_body.add_single_tag(self._marker_size,
                                    marker_id[0], ar_dict)
                    temp_rigid_body.set_2d_points([marker_corners[index]],
                                    marker_id)
                    temporary_rigid_bodies.append(temp_rigid_body)

        for rigid_body in self._rigid_bodies + temporary_rigid_bodies:
            rb_rot, rb_trans, rbquality = rigid_body.get_pose(
                             self._camera_projection_matrix,
                             self._camera_distortion)
            port_handles.append(rigid_body.name)
            time_stamps.append(timestamp)
            frame_numbers.append(self._frame_number)
            tracking_rots.append(rb_rot)
            tracking_trans.append(rb_trans)
            quality.append(rbquality)

        self.add_frame_to_buffer(port_handles, time_stamps,
                    frame_numbers,
                    tracking_rots, tracking_trans, quality,
                    rot_is_quaternion = False)

        self._frame_number += 1
        return self.get_smooth_frame(port_handles)

    def get_tool_descriptions(self):
        """ Returns tool descriptions """
        return "No tools defined"

    def start_tracking(self):
        """
        Tells the tracking device to start tracking.
        :raise Exception: ValueError
        """
        if self._state == "ready":
            self._state = "tracking"
        else:
            raise ValueError('Attempted to start tracking, when not ready')

    def stop_tracking(self):
        """
        Tells the tracking devices to stop tracking.
        :raise Exception: ValueError
        """
        if self._state == "tracking":
            self._state = "ready"
        else:
            raise ValueError('Attempted to stop tracking, when not tracking')

    def _reset_rigid_bodies(self):
        """
        clears 2d points from all rigid bodies
        """
        for rigid_body in self._rigid_bodies:
            rigid_body.reset_2d_points()

    def has_capture(self):
        """
        :Returns true if the tracker has it's own opencv source otherwise false
        """
        if self._capture is None:
            return False
        return True
