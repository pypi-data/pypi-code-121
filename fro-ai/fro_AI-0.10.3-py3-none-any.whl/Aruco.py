import cv2.aruco as aruco
import numpy as np

default_cameraMatrix = np.array([[392.75533375, 0., 284.73851876],
                                 [0., 413.9101659, 254.38799118], [0., 0.,
                                                                   1.]])
default_distCoeffs = np.array(
    [[0.0290911, -1.24869976, -0.01714862, -0.02837211, 3.59261617]])


class ArucoTracker():
    def __init__(self,
                 car=None,
                 xp=-1.2,
                 zp=3,
                 xd=0,
                 zd=0,
                 target_distance=0.3,
                 output_limit=0.3,
                 marker_size=0.06,
                 cameraMatrix=default_cameraMatrix,
                 distCoeffs=default_distCoeffs) -> None:
        self.aruco_dict = aruco.custom_dictionary(10, 6)
        self.car = car
        self.xp = xp
        self.zp = zp
        self.xd = xd
        self.zd = zd
        self.target_distance = target_distance
        self.output_limit = output_limit
        self.marker_size = marker_size
        self.cameraMatrix = cameraMatrix
        self.distCoeffs = distCoeffs
        self._last_angle = 0
        self._last_z_error = 0

    def detect(self, bgr):
        corners, ids, _ = aruco.detectMarkers(bgr, self.aruco_dict)
        if ids is not None:
            aruco.drawDetectedMarkers(bgr, corners, ids)
        return corners, ids

    def track(self, bgr):
        left_speed = 0
        right_speed = 0
        corners, ids, _ = aruco.detectMarkers(bgr, self.aruco_dict)
        if ids is not None:
            _, tvecs, _ = aruco.estimatePoseSingleMarkers(
                corners, self.marker_size, self.cameraMatrix, self.distCoeffs)

            x_error = tvecs[0][0][0].item()
            z_error = tvecs[0][0][2].item() - self.target_distance
            angle = np.arctan2(x_error, tvecs[0][0][2].item())

            if tvecs[0][0][2] > 0.05:
                aruco.drawDetectedMarkers(bgr, np.array([corners[0]]),
                                          np.array([ids[0]]))
                x_output = self.xp * angle + (angle -
                                              self._last_angle) * self.xd
                z_output = self.zp * z_error + (z_error -
                                                self._last_z_error) * self.zd
                self._last_angle = x_error
                self._last_z_error = z_error
                left_speed = z_output - x_output
                right_speed = z_output + x_output
                left_speed = max(min(left_speed, self.output_limit),
                                 -self.output_limit)
                right_speed = max(min(right_speed, self.output_limit),
                                  -self.output_limit)
            else:
                self._last_angle = 0
                self._last_z_error = 0
        else:
            self._last_angle = 0
            self._last_z_error = 0

        if self.car is not None:
            self.car.set_motors(left_speed, right_speed)
