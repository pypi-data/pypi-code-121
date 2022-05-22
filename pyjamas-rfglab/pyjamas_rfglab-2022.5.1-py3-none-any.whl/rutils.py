"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import csv
import gzip
from itertools import chain
import os.path
import pickle
import re
from typing import Iterable, List, Optional, Tuple

import matplotlib
import numpy
from PyQt5 import QtGui, QtWidgets
from scipy.spatial import ConvexHull, Delaunay
from scipy.spatial.distance import cdist
import seaborn as sns

import shapely.geometry


class RUtils:
    """
    def qpolygonf2polygon(cls, aqpolygonf: QtGui.QPolygonF) -> shapely.geometry.Polygon
    def qpolygonf2list(cls, aqpolygonf: QtGui.QPolygonF) -> list
    def qpolygonf2ndarray(cls, aqpolygonf: QtGui.QPolygonF) -> numpy.ndarray
    def isperipheralpoint(cls, point_array: numpy.ndarray, index: int, concave_hull: bool = False,
                          alpha: float = -1.) -> bool
    def circumcircle(cls, points: numpy.ndarray, simplex: numpy.ndarray) -> ((numpy.float, numpy.float), numpy.float)
    def circumcircle_radius(cls, points: numpy.ndarray, simplex: numpy.ndarray) -> float
    def squared_norm(cls, v)
    def concave_hull(cls, point_array: numpy.ndarray, alpha: float) -> numpy.ndarray
    def parse_range_list(cls, rl: str) -> List[int]
    def parse_2integer_tuple(cls, rl: str) -> Tuple[int, int]
    def pjsfiducials_to_array(cls, fiducials: List) -> numpy.ndarray
    def func_exp_2params(cls, x: numpy.ndarray, coeffs: Tuple[float, float]) -> numpy.ndarray
    def func_exp_3params(cls, x: numpy.ndarray, coeffs: Tuple[float, float, float]) -> numpy.ndarray
    def residuals(cls, coeffs, model, y, t)
    def extract_file_paths(cls, folder_name: str, extensions: List[str]) -> List[str]
    """

    DEFAULT_PICKLE_PROTOCOL: int = 3

    @classmethod
    def qpolygonf2polygon(cls, aqpolygonf: QtGui.QPolygonF) -> shapely.geometry.Polygon:
        if aqpolygonf is False or type(aqpolygonf) != QtGui.QPolygonF:
            return shapely.geometry.Polygon(None)

        qpointf_list = list(aqpolygonf)

        point_list = [[qpointf.x(), qpointf.y()] for qpointf in qpointf_list]

        # If only two points were provided, duplicate the last point.
        if len(point_list) < 3:
            point_list.append(point_list[-1].copy())

        return shapely.geometry.Polygon(point_list)

    @classmethod
    def qpolygonf2list(cls, aqpolygonf: QtGui.QPolygonF) -> list:
        if aqpolygonf is False or type(aqpolygonf) != QtGui.QPolygonF:
            return list(None)

        qpointf_list = list(aqpolygonf)

        return [[qpointf.x(), qpointf.y()] for qpointf in qpointf_list]

    @classmethod
    def qpolygonf2ndarray(cls, aqpolygonf: QtGui.QPolygonF) -> numpy.ndarray:
        return numpy.asarray(RUtils.qpolygonf2list(aqpolygonf))

    @classmethod
    def isperipheralpoint(cls, point_array: numpy.ndarray, index: int, concave_hull: bool = False,
                          alpha: float = -1.) -> bool:

        """
        Checks if a point is in the convex/concave hull of a point array.
        (aka alpha shape - https://plot.ly/python/alpha-shapes/)
        :param point_array:
        :param index:
        :param concave_hull:
        :param alpha:
        :return:
        """

        if index < 0 or index >= len(point_array):
            return False

        if concave_hull:
            hull = cls.concave_hull(point_array, alpha)

        else:
            hull = ConvexHull(point_array)

        return index in hull.vertices

    @classmethod
    def circumcircle(cls, points: numpy.ndarray, simplex: numpy.ndarray) -> ((numpy.float, numpy.float), numpy.float):
        """
        A circle which passes through all three vertices of a triangle. Also "Circumscribed circle".
        Blatantly stolen from plotly: https://plot.ly/python/alpha-shapes/


        This function returns exactly the same radius value as the circumcircle, with a tiny bit less precision,
        but this one is one order of magnitude slower (100 us vs 10 us).

        :param points: a numpy.ndarray of points
        :param simplex: three indexes into the points array for the three vertices of a triangle
        :return: the center and the radius of the circumcircle for the triangle defined by simplex
        """
        A = [points[simplex[k]] for k in range(3)]  # [pnt1, pnt2, pnt3] of a triangle
        M = [[1.0] * 4]  # [[1.0, 1.0, 1.0, 1.0]]
        M += [[cls.squared_norm(A[k]), A[k][0], A[k][1], 1.0] for k in range(
            3)]  # [[1.0, 1.0, 1.0, 1.0], [norm2_pnt1, pnt1_x, pnt1_y, 1.0], [norm2_pnt2, pnt2_x, pnt2_y, 1.0], [norm2_pnt3, pnt3_x, pnt3_y, 1.0]]
        M = numpy.asarray(M, dtype=numpy.float32)
        S = numpy.array([0.5 * numpy.linalg.det(M[1:, [0, 2, 3]]), -0.5 * numpy.linalg.det(M[1:, [0, 1, 3]])])
        a = numpy.linalg.det(M[1:, 1:])
        b = numpy.linalg.det(M[1:, [0, 1, 2]])
        return S / a, numpy.sqrt(
            b / a + cls.squared_norm(S) / a ** 2)  # center=S/a, radius=numpy.sqrt(b/a+sq_norm(S)/a**2)

    @classmethod
    def circumcircle_radius(cls, points: numpy.ndarray, simplex: numpy.ndarray) -> float:
        """
        Radius of the circumcircle for the triangle defined by the 3 points indexed by the elements in simplex.
        Stolen from https://stackoverflow.com/questions/23073170/calculate-bounding-polygon-of-alpha-shape-from-the-delaunay-triangulation/23073229#comment35336369_23073229

        See also www.mathalino.com/reviewer/derivation-of-formulas/derivation-of-formula-for-radius-of-circumcircle

        This function returns exactly the same value as the circumcircle, with a tiny bit more precision, but this
        one is one order of magnitude faster (10 us vs 100 us).

        :param points: a numpy.ndarray of points
        :param simplex: three indexes into the points array for the three vertices of a triangle
        :return: the center of the circumcircle for the triangle defined by simplex
        """
        pa: numpy.ndarray = points[simplex[0]]
        pb: numpy.ndarray = points[simplex[1]]
        pc: numpy.ndarray = points[simplex[2]]

        a: float = numpy.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2)
        b: float = numpy.sqrt((pb[0] - pc[0]) ** 2 + (pb[1] - pc[1]) ** 2)
        c: float = numpy.sqrt((pc[0] - pa[0]) ** 2 + (pc[1] - pa[1]) ** 2)
        s: float = (a + b + c) / 2.0
        area: float = numpy.sqrt(s * (s - a) * (s - b) * (s - c))

        return a * b * c / (4.0 * area)

    @classmethod
    def squared_norm(cls, v):  # squared norm
        return numpy.linalg.norm(v) ** 2

    @classmethod
    def concave_hull(cls, point_array: numpy.ndarray, alpha: float) -> numpy.ndarray:
        """
        Returns points in the concave hull (with no particular order).

        :param point_array:
        :param alpha:
        :return:
        """

        delaunay_triang = Delaunay(point_array)
        simplices = delaunay_triang.simplices  # indices of the points forming the triangles.

        hull_edges = []

        for thetriangle in simplices:
            radius_circumcircle = cls.circumcircle_radius(point_array, thetriangle)

            if radius_circumcircle < alpha:
                cls.__add_edge_to_concave_hull__(hull_edges, thetriangle[0], thetriangle[1])
                cls.__add_edge_to_concave_hull__(hull_edges, thetriangle[1], thetriangle[2])
                cls.__add_edge_to_concave_hull__(hull_edges, thetriangle[2], thetriangle[0])

        return numpy.asarray(numpy.unique(hull_edges))

    @staticmethod
    def __add_edge_to_concave_hull__(hull_edges: list, idx1: int, idx2: int) -> bool:
        # If we are adding an edge for the second time, that means that it belongs to two triangles, and in that
        # case it does not belong to the hull. Remove it.
        if [idx1, idx2] in hull_edges:
            hull_edges.remove([idx1, idx2])
        elif [idx2, idx1] in hull_edges:
            hull_edges.remove([idx2, idx1])

        # Otherwise, add the edge to the hull.
        else:
            hull_edges.append([idx1, idx2])

        return True

    @staticmethod
    def __parse_range__(r: str) -> Iterable[int]:
        """
        Finds positive integers before and after a hyphen.
        :param r: a string with one hyphen in (e.g. '15-18')
        :return: iterable going from first to last in the string (inclusive).
        """
        if len(r) == 0:
            return []

        parts = r.split("-")
        if len(parts) > 2:
            raise ValueError("Invalid range: {}".format(r))
        return range(int(parts[0]), int(parts[-1]) + 1)

    @classmethod
    def parse_range_list(cls, rl: str) -> List[int]:
        """
        Splits the input chain in comma-separated segments.
        Runs __parse_range__ on each segment.
        Returns a sorted list with all the ranges.

        :param rl: a range-string (e.g.: '0, 2, 4-10, 15').
        :return: a list of sorted indices.
        """
        return sorted(set(chain.from_iterable(map(cls.__parse_range__, rl.split(",")))))

    @classmethod
    def parse_2integer_tuple(cls, rl: str) -> Tuple[int, int]:
        """
        Converts a string representing a two-integer tuple into the tuple itself.
        :param rl: a string representing a 2-element tuple (e.g.: '(0, 23)')).
                   Single element tuples with a comma are valid (e.g.: '(0, )'.
        :return: a 2-element tuple (e.g.: (0, 23)).
        """
        if len(rl) == 0:
            raise ValueError(f"Invalid 2-element tuple: {rl}.")

        parts = rl.split(",")
        if len(parts) != 2:
            raise ValueError(f"Invalid 2-element tuple: {rl}.")

        output: Tuple = ()

        try:
            n1: int = int(parts[0][1:])
        except ValueError:
            raise ValueError(f"Invalid 2-element tuple: {rl}.")

        try:
            n2: int = int(parts[1][:-1])
            output = (n1, n2)
        except ValueError:
            output = (n1, )

        return output


    @classmethod
    def natural_sort(cls, s):
        nsre = re.compile('([0-9]+)')
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(nsre, s)]

    @classmethod
    def point2point_distances(cls, points_orig: numpy.ndarray, points_dest: numpy.ndarray) -> numpy.ndarray:
        return cdist(points_orig, points_dest, 'euclidean')

    @classmethod
    def open_folder_dialog(cls, title: str, starting_folder: str) -> str:
        return QtWidgets.QFileDialog.getExistingDirectory(None, title, starting_folder)

    @classmethod
    def write_dict_csv(cls, filename: Optional[str] = None, adictionary: Optional[dict] = None) -> bool:
        """
        DELETE THIS METHOD?
        :param filename:
        :param adictionary:
        :return:
        """
        if filename == '' or filename is None or filename is False or adictionary is None or adictionary is False:
            return False

        # Make sure file extension is .csv.
        thefile, extension = os.path.splitext(filename)
        if extension != '.csv':
            filename = thefile + '.csv'

        with open(filename, "w") as fh:
            writer = csv.writer(fh)

            for akey, avalue in adictionary.items():
                writer.writerow([akey])  # Putting a string in a list is the way to write the entire string into a single cell. Otherwise, each character in the string is written in a different cell.

                if type(avalue) == list:
                    writer.writerow(avalue)
                else:
                    writer.writerow([avalue])
        return True

    @classmethod
    def read_csv_dict(cls, filename: Optional[str] = None) -> dict:
        """
        DELETE THIS METHOD?
        :param filename:
        :return:
        """
        if filename == '' or filename is None or filename is False:
            return None

        if not os.path.exists(filename):
            return None

        thedict: dict = {}

        with open(filename, "r") as fh:
            reader = csv.reader(fh)

            for akey in reader:
                avalue = next(reader)
                thedict[akey] = [avalue]

        print(thedict)

        return thedict

    @classmethod
    def set_extension(cls, filename: str, extension: str) -> str:
        """
        Generates a string based on filename that concludes in the desired extension.
        If the filename string already had an extension, it will be substituted with
        the provided one.

        :param filename:
        :param extension:
        :return:
        """
        # Make sure file extension is extension.
        thefile, old_ext = os.path.splitext(filename)
        if old_ext != extension:
            return thefile + extension
        else:
            return filename

    @classmethod
    def pickle_this(cls, an_object: object, filename: str, pickle_protocol = DEFAULT_PICKLE_PROTOCOL) -> bool:
        """
        Saves a python object into a file after zipping.
        Sample use: saving scikit-learn classifiers after they have been trained.

        :param an_object: object to zip and pickle.
        :param filename: include the desired extension!
        :return:
        """
        fh = None

        try:
            fh = gzip.open(filename, "wb")
            pickle.dump(an_object, fh, pickle_protocol)

        except (IOError, OSError) as ex:
            if fh is not None:
                fh.close()

            print(ex)
            return False

        return True

    @classmethod
    def pjsfiducials_to_array(cls, fiducials: List) -> numpy.ndarray:
        """
        Converts a list of fiducials from PyJAMAS (a sparse list) into a numpy.ndarray with a constant
        number of elements.

        Empty space in the array is filled with -1 (if we used nans, the array
        would be of type float and take up a lot more space; this is because ndarrays can only
        contain one data type and type(numpy.nan) returns float).

        :param fiducials:
        :return:
        """
        # Find dimension with the most elements.
        n_fiducials_per_slice = [len(a_slice) for a_slice in fiducials]
        max_n_fiducials: int = max(n_fiducials_per_slice)
        n_slices = len(fiducials)


        coordinates: numpy.ndarray = numpy.full((n_slices, max_n_fiducials, 2), -1, dtype=int)

        for a_slice in range(n_slices):
            if n_fiducials_per_slice[a_slice] > 0:
                coordinates[a_slice, 0:n_fiducials_per_slice[a_slice], :] = fiducials[a_slice]

        return coordinates

    @classmethod
    def func_exp_2params(cls, x: numpy.ndarray, coeffs: Tuple[float, float]) -> numpy.ndarray:
        return coeffs[0] * numpy.exp(-coeffs[1] * x)

    @classmethod
    def func_exp_3params(cls, x: numpy.ndarray, coeffs: Tuple[float, float, float]) -> numpy.ndarray:
        return coeffs[0] * numpy.exp(-coeffs[1] * x) + coeffs[2]

    @classmethod
    def residuals(cls, coeffs, model, y, t):
        return y - model(t, coeffs)

    @classmethod
    def extract_file_paths(cls, folder_name: str, extensions: List[str]) -> List[str]:
        """
        Returns a list with the complete path of all the files within folder_name with an extension in extensions.
        The list is sorted in ascending order using sorted.
        :param folder_name: str
        :param extensions: List[str]
        :return: List[str]
        """
        file_list: List[str] = []

        if folder_name == '' or folder_name is False or folder_name == []:
            return file_list

        if extensions == [] or extensions is False:
            return file_list

        for root, dirs, files in os.walk(folder_name):
            for a_file in files:
                file_name, file_ext = os.path.splitext(a_file)

                # Take only non-hidden files with the correct extension.
                if file_name[0] != '.' and file_ext in extensions:
                    file_list.append(os.path.join(root, a_file))

        return sorted(file_list)

    @classmethod
    def bicubic_interpolation(cls, xi, yi, zi, xnew, ynew):
        # check sorting
        if numpy.any(numpy.diff(xi) < 0) and numpy.any(numpy.diff(yi) < 0) and \
                numpy.any(numpy.diff(xnew) < 0) and numpy.any(numpy.diff(ynew) < 0):
            raise ValueError('data are not sorted')

        if zi.shape != (xi.size, yi.size):
            raise ValueError('zi is not set properly use numpy.meshgrid(xi, yi)')

        z = numpy.zeros((xnew.size, ynew.size))

        for n, x in enumerate(xnew):
            for m, y in enumerate(ynew):

                if xi.min() <= x <= xi.max() and yi.min() <= y <= yi.max():

                    i = numpy.searchsorted(xi, x) - 1
                    j = numpy.searchsorted(yi, y) - 1

                    x1 = xi[i]
                    x2 = xi[i + 1]

                    y1 = yi[j]
                    y2 = yi[j + 1]

                    px = (x - x1) / (x2 - x1)
                    py = (y - y1) / (y2 - y1)

                    f00 = zi[i - 1, j - 1]  # row0 col0 >> x0,y0
                    f01 = zi[i - 1, j]  # row0 col1 >> x1,y0
                    f02 = zi[i - 1, j + 1]  # row0 col2 >> x2,y0

                    f10 = zi[i, j - 1]  # row1 col0 >> x0,y1
                    f11 = zi[i, j]  # row1 col1 >> x1,y1
                    f12 = zi[i, j + 1]  # row1 col2 >> x2,y1

                    f20 = zi[i + 1, j - 1]  # row2 col0 >> x0,y2
                    f21 = zi[i + 1, j]  # row2 col1 >> x1,y2
                    f22 = zi[i + 1, j + 1]  # row2 col2 >> x2,y2

                    if 0 < i < xi.size - 2 and 0 < j < yi.size - 2:

                        f03 = zi[i - 1, j + 2]  # row0 col3 >> x3,y0

                        f13 = zi[i, j + 2]  # row1 col3 >> x3,y1

                        f23 = zi[i + 1, j + 2]  # row2 col3 >> x3,y2

                        f30 = zi[i + 2, j - 1]  # row3 col0 >> x0,y3
                        f31 = zi[i + 2, j]  # row3 col1 >> x1,y3
                        f32 = zi[i + 2, j + 1]  # row3 col2 >> x2,y3
                        f33 = zi[i + 2, j + 2]  # row3 col3 >> x3,y3

                    elif i <= 0:

                        f03 = f02  # row0 col3 >> x3,y0

                        f13 = f12  # row1 col3 >> x3,y1

                        f23 = f22  # row2 col3 >> x3,y2

                        f30 = zi[i + 2, j - 1]  # row3 col0 >> x0,y3
                        f31 = zi[i + 2, j]  # row3 col1 >> x1,y3
                        f32 = zi[i + 2, j + 1]  # row3 col2 >> x2,y3
                        f33 = f32  # row3 col3 >> x3,y3             

                    elif j <= 0:

                        f03 = zi[i - 1, j + 2]  # row0 col3 >> x3,y0

                        f13 = zi[i, j + 2]  # row1 col3 >> x3,y1

                        f23 = zi[i + 1, j + 2]  # row2 col3 >> x3,y2

                        f30 = f20  # row3 col0 >> x0,y3
                        f31 = f21  # row3 col1 >> x1,y3
                        f32 = f22  # row3 col2 >> x2,y3
                        f33 = f23  # row3 col3 >> x3,y3


                    elif i == xi.size - 2 or j == yi.size - 2:

                        f03 = f02  # row0 col3 >> x3,y0

                        f13 = f12  # row1 col3 >> x3,y1

                        f23 = f22  # row2 col3 >> x3,y2

                        f30 = f20  # row3 col0 >> x0,y3
                        f31 = f21  # row3 col1 >> x1,y3
                        f32 = f22  # row3 col2 >> x2,y3
                        f33 = f23  # row3 col3 >> x3,y3

                    Z = numpy.array([f00, f01, f02, f03,
                                  f10, f11, f12, f13,
                                  f20, f21, f22, f23,
                                  f30, f31, f32, f33]).reshape(4, 4).transpose()

                    X = numpy.tile(numpy.array([-1, 0, 1, 2]), (4, 1))
                    X[0, :] = X[0, :] ** 3
                    X[1, :] = X[1, :] ** 2
                    X[-1, :] = 1

                    Cr = Z @ numpy.linalg.inv(X)
                    R = Cr @ numpy.array([px ** 3, px ** 2, px, 1])

                    Y = numpy.tile(numpy.array([-1, 0, 1, 2]), (4, 1)).transpose()
                    Y[:, 0] = Y[:, 0] ** 3
                    Y[:, 1] = Y[:, 1] ** 2
                    Y[:, -1] = 1

                    Cc = numpy.linalg.inv(Y) @ R

                    z[n, m] = (Cc @ numpy.array([py ** 3, py ** 2, py, 1]))

        return z

    @classmethod
    def convertPoints2BndBox(cls, points: numpy.ndarray) -> Tuple[int, int, int, int]:
        xmin = float('inf')
        ymin = float('inf')
        xmax = float('-inf')
        ymax = float('-inf')
        for p in points:
            x = p[0]
            y = p[1]
            xmin = min(x, xmin)
            ymin = min(y, ymin)
            xmax = max(x, xmax)
            ymax = max(y, ymax)

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        xmin = max(xmin, 1)
        ymin = max(ymin, 1)
        return int(xmin), int(ymin), int(xmax), int(ymax)

    @classmethod
    def myboxplot(**kwargs) -> (matplotlib.axes.Axes, matplotlib.axes.Axes):
        """
        Draws a box plot with lines representing the mean, boxes representing sem, and error bars showing sd.
        The individual observations for each group are also plotted as a stripplot.

        :param kwargs: as in seaborn.boxplot: https://seaborn.pydata.org/generated/seaborn.boxplot.html
        :return: (ax1, ax2), with ax1 the axes of the boxplot and ax2 the axes of the stripplot.
        """
        medianprops = dict(linestyle='None', linewidth=0)
        meanprops = dict(linestyle='-', linewidth=2.5, color='k')
        ax1 = sns.boxplot(**kwargs, meanline=True, showmeans=True, medianprops=medianprops, meanprops=meanprops)
        ax1.legend(frameon=False)

        grouped_df = kwargs['data'].groupby([kwargs['x']])[kwargs['y']]
        themeans = grouped_df.mean().to_numpy()
        thestds = grouped_df.std().to_numpy()
        thesems = grouped_df.sem().to_numpy()
        themaxs = grouped_df.max().to_numpy()
        themins = grouped_df.min().to_numpy()

        ind_group = 0
        plot_children = ax1.get_children()
        for achild in plot_children:
            # find and redraw boxes
            if type(achild) == matplotlib.patches.PathPatch:
                theboxvertices = achild.get_path().vertices

                for achild2 in plot_children:
                    # find and redraw error bars
                    if type(achild2) == matplotlib.lines.Line2D:
                        thelinevertices = achild2.get_xydata()
                        if thelinevertices.shape == (2, 2) and thelinevertices[:, 0].mean() == ind_group:
                            # vertical line: the y-coordinates of the two points are different.
                            if thelinevertices[0, 1] != thelinevertices[1, 1]:
                                achild2.set_ydata(numpy.array(
                                    [themeans[ind_group] + thestds[ind_group],
                                     themeans[ind_group] - thestds[ind_group]]))
                            # horizontal line and not the mean line
                            elif thelinevertices[0, 1] != themeans[ind_group]:
                                if thelinevertices[0, 1] == themaxs[ind_group]:
                                    achild2.set_ydata(numpy.array([themeans[ind_group] + thestds[ind_group],
                                                                   themeans[ind_group] + thestds[ind_group]]))
                                elif thelinevertices[0, 1] == themins[ind_group]:
                                    achild2.set_ydata(numpy.array([themeans[ind_group] - thestds[ind_group],
                                                                   themeans[ind_group] - thestds[ind_group]]))
                theboxvertices[(0, 1, 4), 1] = themeans[ind_group] - thesems[ind_group]
                theboxvertices[(2, 3), 1] = themeans[ind_group] + thesems[ind_group]
                ind_group += 1

        ax2 = sns.stripplot(x=kwargs['x'], y=kwargs['y'], data=kwargs['data'], color='k', alpha=0.75, size=6,
                            dodge=False,
                            jitter=0.05)
        sns.despine()
        return (ax1, ax2)


class SizedStack(object):

    def __init__(self, max_length: int):
        self.max_length: int = max_length
        self.ls = []

    def push(self, st: object):
        if len(self.ls) == self.max_length:
            self.ls.pop(0)

        self.ls.append(st)

    def get_list(self):
        return self.ls

    def pop(self):
        if len(self.ls) > 0:
            return self.ls.pop()
        else:
            return None
    
    def clear(self):
        self.ls.clear()

    def __repr__(self) -> str:
        return self.ls.__repr__()
