# -*- coding: utf-8 -*-

from collections import namedtuple
from operator import itemgetter
from pprint import pformat
import numpy as np


class Node(namedtuple('Node', 'location left_child right_child')):
    def __repr__(self):
        return pformat(tuple(self))


class KDTree():
    def __init__(self, points):
        self.tree = self._make_kdtree(points)
        if len(points) > 0:
            self.k = len(points[0])
        else:
            self.k = None

    def _make_kdtree(self, points, depth=0):
        if not points:
            return None

        k = len(points[0])
        axis = depth % k

        points.sort(key=itemgetter(axis))
        median = len(points) // 2

        return Node(
            location=points[median],
            left_child=self._make_kdtree(points[:median], depth + 1),
            right_child=self._make_kdtree(points[median + 1:], depth + 1))

    def find_nearest(self,
                     point,
                     root=None,
                     axis=0,
                     dist_func=lambda x, y: np.linalg.norm(x - y)):

        if root is None:
            root = self.tree
            self._best = None

        # 若不是叶节点，则继续向下走
        if root.left_child or root.right_child:
            new_axis = (axis + 1) % self.k
            if point[axis] < root.location[axis] and root.left_child:
                self.find_nearest(point, root.left_child, new_axis)
            elif root.right_child:
                self.find_nearest(point, root.right_child, new_axis)

        # 回溯：尝试更新 best
        dist = dist_func(root.location, point)
        if self._best is None or dist < self._best[0]:
            self._best = (dist, root.location)

        # 若超球与另一边超矩形相交
        if abs(point[axis] - root.location[axis]) < self._best[0]:
            new_axis = (axis + 1) % self.k
            if root.left_child and point[axis] >= root.location[axis]:
                self.find_nearest(point, root.left_child, new_axis)
            elif root.right_child and point[axis] < root.location[axis]:
                self.find_nearest(point, root.right_child, new_axis)

        return self._best

if __name__ == '__main__':
    point_list = [(2, 3), (5, 4), (9, 6), (4, 7), (8, 1), (7, 2)]
    kdtree = KDTree(point_list)

    point = np.array([5, 5])
    print(kdtree.find_nearest(point))
