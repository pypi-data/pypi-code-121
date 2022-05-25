import math
from typing import List


class Vector3:

    epsilon = 0.03

    def __init__(self, x: float, y: float, z: float, _type: str = ''):
        self._type = 'vector3'
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector3):
            return math.fabs(other.x - self.x) < self.epsilon and \
                   math.fabs(other.y - self.y) < self.epsilon and \
                   math.fabs(other.z - self.z) < self.epsilon
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __repr__(self):
        return f"Vector3<x={self.x}, y={self.y}, z={self.z}>"


class Pose:

    def __init__(self, position: Vector3, rotation: Vector3, name: str = '', axis_angle=None,  _type: str = ''):
        self._type = 'pose'
        self.name = name
        self.position = position
        self.rotation = rotation
        self.axis_angle = AxisAngle.from_rotation_vec(rotation)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Pose):
            return other.name == self.name and other.position == self.position and other.rotation == self.rotation
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"Pose<name={self.name}, position={self.position}, orientation={self.rotation}>"

    def to_dict(self) -> dict:
        return {'x': self.position.x, 'y': self.position.y, 'z': self.position.z,
                'rx': self.rotation.x, 'ry': self.rotation.y, 'rz': self.rotation.z}

    @staticmethod
    def from_dict(pose: dict) -> 'Pose':
        return Pose(Vector3(pose.get('x', 0.0), pose.get('y', 0.0), pose.get('z', 0.0)),
                    Vector3(pose.get('rx', 0.0), pose.get('ry', 0.0), pose.get('rz', 0.0)), name=pose.get('name', ''))

    @staticmethod
    def from_list(pose: List, name: str = "") -> 'Pose':
        return Pose(Vector3(pose[0], pose[1], pose[2]), Vector3(pose[3], pose[4], pose[5]), name=name)

    @staticmethod
    def pose_trans(p1: 'Pose', p2: 'Pose', new_name: str = '') -> 'Pose':
        # from: https://forum.universal-robots.com/t/pose-trans-and-pose-inv-functions-in-urcap/1257 (scroll a bit down)
        res = Pose.matrix_multiply(p1.get_transform_matrix(), p2.get_transform_matrix())

        angle = AxisAngle.from_rotation_matrix([
            [res[0][0], res[0][1], res[0][2]],
            [res[1][0], res[1][1], res[1][2]],
            [res[2][0], res[2][1], res[2][2]]
        ])
        if new_name:
            name = new_name
        elif p1.name:
            name = p1.name
        else:
            name = p2.name

        return Pose(
            Vector3(res[0][3], res[1][3], res[2][3]),
            angle.get_rotation_vector(),
            name
        )

    def get_transform_matrix(self):
        angle = AxisAngle.from_rotation_vec(self.rotation)
        rm = angle.get_rotation_matrix()
        return [
            [rm[0][0], rm[0][1], rm[0][2], self.position.x],
            [rm[1][0], rm[1][1], rm[1][2], self.position.y],
            [rm[2][0], rm[2][1], rm[2][2], self.position.z],
            [0, 0, 0, 1]
        ]

    @staticmethod
    def matrix_multiply(a, b):
        res = [[0 for x in range(len(a))] for y in range(len(b[0]))]
        for i in range(0, len(a)):
            for j in range(0, len(b[0])):
                s = 0
                for k in range(0, len(a[i])):
                    s += a[i][k] * b[k][j]
                res[i][j] = s
        return res


class AxisAngle:

    def __init__(self, angle: float, x: float, y: float, z: float, _type: str = ''):
        self._type = "axis_angle"
        self.angle = angle
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def from_rotation_vec(rotation: Vector3) -> 'AxisAngle':
        angle = math.sqrt(math.pow(rotation.x, 2) + math.pow(rotation.y, 2) + math.pow(rotation.z, 2))
        if angle == 0:
            y = z = 0
            x = 1
        else:
            x = rotation.x / angle
            y = rotation.y / angle
            z = rotation.z / angle
        return AxisAngle(angle, x, y, z)

    @staticmethod
    def from_rotation_matrix(m) -> 'AxisAngle':
        epsilon = 0.01
        epsilon2 = 0.1
        if math.fabs(m[0][1] - m[1][0]) < epsilon and math.fabs(m[0][2] - m[2][0]) < epsilon and math.fabs(m[1][2] - m[2][1]) < epsilon:
            if math.fabs(m[0][1] + m[1][0]) < epsilon2 and math.fabs(m[0][2] + m[2][0]) < epsilon2 and math.fabs(m[1][2] + m[2][1]) < epsilon2 and math.fabs(m[0][0] + m[1][1] + m[2][2] - 3) < epsilon2:
                return AxisAngle(0, 1, 0, 0)

            angle = math.pi
            xx = (m[0][0] + 1) / 2
            yy = (m[1][1] + 1) / 2
            zz = (m[2][2] + 1) / 2
            xy = (m[0][1] + m[1][0]) / 4
            xz = (m[0][2] + m[2][0]) / 4
            yz = (m[1][2] + m[2][1]) / 4

            if xx > yy and xx > zz:
                if xx < epsilon:
                    x = 0
                    y = 0.7071
                    z = 0.7071
                else:
                    x = math.sqrt(xx)
                    y = xy / x
                    z = xz / x
            elif yy > zz:
                if yy < epsilon:
                    x = 0.7071
                    y = 0
                    z = 0.7071
                else:
                    y = math.sqrt(yy)
                    x = xy / y
                    z = yz / y
            else:
                if zz < epsilon:
                    x = 0.7071
                    y = 0.7071
                    z = 0
                else:
                    z = math.sqrt(zz)
                    x = xz / z
                    y = yz / z
            return AxisAngle(angle, x, y, z)
        s = math.sqrt(
            (m[2][1] - m[1][2]) * (m[2][1] - m[1][2]) +
            (m[0][2] - m[2][0]) * (m[0][2] - m[2][0]) +
            (m[1][0] - m[0][1]) * (m[1][0] - m[0][1])
        )
        if math.fabs(s) < 0.001:
            s = 1

        angle = math.acos((m[0][0] + m[1][1] + m[2][2] - 1) / 2)
        x = (m[2][1] - m[1][2]) / s
        y = (m[0][2] - m[2][0]) / s
        z = (m[1][0] - m[0][1]) / s
        return AxisAngle(angle, x, y, z)

    def get_rotation_vector(self) -> Vector3:
        return Vector3(self.x * self.angle, self.y * self.angle, self.z * self.angle)

    def get_rotation_matrix(self) -> List[List[float]]:
        if self.angle == 0:
            return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

        c = math.cos(self.angle)
        s = math.sin(self.angle)
        t = 1.0 - c

        m00 = c + self.x * self.x * t
        m11 = c + self.y * self.y * t
        m22 = c + self.z * self.z * t

        tmp1 = self.x * self.y * t
        tmp2 = self.z * s
        m10 = tmp1 + tmp2
        m01 = tmp1 - tmp2

        tmp1 = self.x * self.z * t
        tmp2 = self.y * s
        m20 = tmp1 + tmp2
        m02 = tmp1 - tmp2

        tmp1 = self.y * self.z * t
        tmp2 = self.x * s
        m21 = tmp1 + tmp2
        m12 = tmp1 - tmp2

        return [[m00, m01, m02], [m10, m11, m12], [m20, m21, m22]]


class Poses:

    def __init__(self, poses: List[Pose], connected: bool = False, _type: str = ''):
        self._type = 'poses'
        self.connected = connected
        self.poses = poses

    def add(self, pose: Pose):
        self.poses.append(pose)

    def convert_and_add_unity_pose(self, pose: Pose):
        self.poses.append(Pose(
            Vector3(pose.position.x, pose.position.z, pose.position.y),
            pose.rotation,  # TODO: add some conversion?
            pose.name
        ))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Poses):
            return other.connected == self.connected and other.poses == self.poses
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"Poses<connected={self.connected}, poses={self.poses}>"
