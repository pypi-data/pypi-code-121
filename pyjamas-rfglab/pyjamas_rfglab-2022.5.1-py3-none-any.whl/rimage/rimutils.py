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

from enum import Enum, auto
from itertools import tee
import numbers
import os
from typing import List, Optional, Tuple

import cv2
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from networkx import DiGraph
from networkx.generators.classic import empty_graph
import numpy
from PyQt5 import QtGui, QtWidgets
from scipy import ndimage
import scipy.interpolate
from PIL import Image
from skimage import io
from skimage.filters import threshold_local, gaussian
from skimage.measure import find_contours, regionprops
from skimage.morphology import binary_closing, binary_opening, dilation, disk, label, square
from skimage.segmentation import watershed, morphological_geodesic_active_contour
from skimage.transform import rescale, warp, EuclideanTransform
import skimage.util
import warnings

import pyjamas.rannotations.rpolyline as pjsannpol
from pyjamas.rimage.csgraph import csgraph_from_dense


class rimutils:
    # Default sigma to use for the gradient calculation if necessary. This is the same as in dipimage.
    GRADMAG_DEFAULT_SIGMA = 1.0
    FINDSEEDS_DEFAULT_WINSIZE = 32
    BALLOON_ITERS: int = 300

    class RegistrationMethod(Enum):
        CRUDE = auto()
        PIV = auto()
        FLOW = auto()

    class ChannelMethod(Enum):
        CHANNEL: str = "channel"
        SLICE: str = "slice"

    # These are some simple functions, but used in different places in the codebase. To avoid having to change them
    # everywhere if, for instance, one day we decide to use a different method to read a stack, I created class methods
    # for them here.
    @classmethod
    def read_stack(cls, filename: Optional[str] = None, channel_method: Optional[ChannelMethod] = None, index: int = -1) -> numpy.ndarray:
        """
        Reads an image using skimage.io.imread.

        Open CV's imreadmulti can also do this:
        tmp = cv2.imreadmulti(filename, flags=-1)
        self.pjs.slices = np.asarray(tmp[1], dtype=np.uint16)
        But considering the time necessary for the import and the actual instructions to eventually get an ndarray,
        skimage is twice as fast (at least!).
        So now we use scikit-image
        There is a problem with this function, though: if the image is a multipage tiff, it will normally report the
        shape of the resulting ndarray as [Z, rows, cols]
        (http://scikit-image.org/docs/dev/user_guide/numpy_images.html). BUT, if the multipage tiff has 4 pages,
        it gets totally confused, thinks this is a single page colour image, and reads the shape as
        [row, cols, channels], messing everything up ...

        For now, if a 3D stack is read, and the third dimension has a size of 4, we assume it is a 4-page tiff,
        and dimensions are rolled. This means that 3D stacks with only 4 columns will not be properly read.


        :param filename: input file path
        :param channel_method: one of the values in rimutils.ChannelMethods; for a multi-channel sequence, determines whether to open a channel or a slice
        :param index: index of the channel or slice to open (with origin at 0).
        :return: numpy.ndarray with the open image.
        """

        im = io.imread(filename)

        # Multi-channel images: shift the number of channels (im.shape[2]) to the first dimension.
        if im.ndim == 3 and im.shape[2] == 3:
            im = numpy.rollaxis(im, 2)

        # Multi-channel time series.
        elif im.ndim == 4:
            if channel_method is None or channel_method is False:
                channel_method, _ = QtWidgets.QInputDialog.getItem(None, "Multi-channel sequence", "Choose what to open:",
                                                                   [x.value for x in rimutils.ChannelMethod], 0, False)
            else:
                channel_method = channel_method.value

            if channel_method == rimutils.ChannelMethod.CHANNEL.value:
                # shift the number of channels (im.shape[2]) to the first dimension.
                im = numpy.rollaxis(im, 3)

            elif channel_method == rimutils.ChannelMethod.SLICE.value:
                # number of slices (im.shape[0]) goes first, number of channels goes second.
                im = numpy.rollaxis(im, 3, 1)

            if index < 0 or index >= im.shape[0]:
                index, _ = QtWidgets.QInputDialog.getItem(None, "Multi-channel sequence", channel_method,
                                                          [str(x+1) for x in range(im.shape[0])], 0,
                                                          False)
                index = int(index)

            im = im[index-1]

        return im

    @classmethod
    def write_stack(cls, filename: Optional[str] = None, im: Optional[numpy.ndarray] = None) -> bool:
        # We use scikit-image. But scikit-image emits a warning with some fluorescence images that their contrast
        # is low. This bit supresses the warning (https://github.com/scikit-image/scikit-image/issues/543).
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            thefolder, thefile = os.path.split(filename)
            if not os.path.exists(thefolder):
                os.makedirs(thefolder)
            io.imsave(filename, im)

    @classmethod
    def mip(cls, im: Optional[numpy.ndarray] = None) -> numpy.ndarray:
        return numpy.max(im, axis=0)

    @classmethod
    def sip(cls, im: Optional[numpy.ndarray] = None) -> numpy.ndarray:
        return numpy.sum(im, axis=0)

    @classmethod
    def find_seeds(cls, im: numpy.ndarray, window_size: int = FINDSEEDS_DEFAULT_WINSIZE,
                   binary_dilation_radius: int = 0,
                   min_distance_edge: float = -1.0) -> (numpy.ndarray, numpy.ndarray):
        if im is None or im is False:
            return numpy.empty((0))

        _, thresholded_im, thresholded_im_final = cls.local_threshold(im, window_size, binary_dilation_radius)

        # Calculate distance transform.
        distance_im = ndimage.distance_transform_edt(thresholded_im_final)

        # Detect seeds by locally thresholding the distance transform -----------------------------
        if min_distance_edge < 0.0:
            _, max_dist_im, thresholded_dt_final = cls.local_threshold(distance_im, window_size)
            max_dist_im = label(max_dist_im)

        else:
            # Detect seeds by globally thresholding distance transform and calculating centroids of connected components. -------
            max_dist_im = distance_im >= min_distance_edge
            max_dist_im = label(dilation(max_dist_im, square(5)))

        properties_msr = regionprops(max_dist_im)

        coords_maxima = numpy.asarray(
            [[seed_props.centroid[0], seed_props.centroid[1]] for seed_props in properties_msr], dtype=numpy.int16)
        seed_im_bool = numpy.zeros(max_dist_im.shape, dtype=bool)

        try:
            seed_im_bool[coords_maxima[:, 0], coords_maxima[:, 1]] = True
        except IndexError:
            pass
        # End detect seeds by locally thresholding the distance transform -------------------------

        # Detect seeds as the local maxima of the distance transform -----------------------------
        # coords_maxima = peak_local_max(distance_im, labels=label(numpy.invert(thresholded_im)), num_peaks_per_label=1)
        # seed_im_bool = numpy.zeros_like(distance_im, dtype=bool)
        # seed_im_bool[tuple(coords_maxima.T)] = True
        # End detect seeds as the local maxima of the distance transform -------------------------

        seed_im = label(seed_im_bool)

        return coords_maxima, numpy.stack((thresholded_im, distance_im, seed_im))

    @classmethod
    def find_seeds_gwdt(cls, im: numpy.ndarray, window_size: int = FINDSEEDS_DEFAULT_WINSIZE,
                   binary_dilation_radius: int = 0,
                   min_distance_edge: float = 0.0) -> (numpy.ndarray, numpy.ndarray):
        """
        Find seeds using a gradient-weighted distance transform instead of the regular distance transform.

        :param im:
        :param window_size:
        :param binary_dilation_radius:
        :param min_distance_edge:
        :return:
        """
        if im is None or im is False:
            return numpy.empty((0))

        # Calculate distance transform.
        distance_im, thresholded_im = rimutils.distance_transform_gradient_weighted(im, window_size, binary_dilation_radius)
        # Extract the local maxima from the distance transform.
        #cls.write_stack(f"/Users/rodrigo/Documents/WORK/SHUTDOWN/Delete/{str(binary_dilation_radius)}.tif", distance_im)
        max_dist_im = distance_im >= min_distance_edge
        max_dist_im = label(dilation(max_dist_im, square(5)))
        properties_msr = regionprops(max_dist_im)

        coords_maxima = numpy.asarray(
            [[seed_props.centroid[0], seed_props.centroid[1]] for seed_props in properties_msr], dtype=numpy.int16)
        seed_im_bool = numpy.zeros(max_dist_im.shape, dtype=bool)

        try:
            seed_im_bool[coords_maxima[:, 0], coords_maxima[:, 1]] = True
        except IndexError:
            pass

        seed_im = label(seed_im_bool)

        """if output_intermediate:
            #fig, ax = rimutils.figdisplay((thresholded_im.astype(int), distance_im), image_titles=('threshold', 'distance'))
            fig, ax = rimutils.figdisplay(((thresholded_im.astype(int), distance_im), (im, im)), image_titles=(('threshold', 'distance'), ('gray', 'seeds')))
            ax[1, 1].imshow(dilation(maxima_im, square(5)), cmap='jet', alpha=.5)
            plt.show()"""
        return coords_maxima, numpy.stack((thresholded_im, distance_im, seed_im))

    @classmethod
    def figdisplay(cls, image_tuple: Tuple[numpy.ndarray], image_titles: Optional[Tuple[str]] = None, color_map: str = 'gray',
                   display: bool = True, font_size: int = 8) -> (Figure, Axes):
        """

        :param image_tuple:
        :param color_map: see https://matplotlib.org/examples/color/colormaps_reference.html
        :return:
        """
        rows: int = -1
        columns: int = -1

        images = numpy.asarray(image_tuple)

        num_dims = images.ndim
        if num_dims == 2:
            images = numpy.expand_dims(numpy.expand_dims(images, 0), 0)
            num_dims = 4
        elif num_dims == 3:
            images = numpy.expand_dims(images, 0)
            num_dims = 4

        if num_dims == 4:
            rows = images.shape[0]
            columns = images.shape[1]
        elif num_dims == 1:
            rows = images.shape[0]
            maxncols = 0
            for ii in range(rows):
                ndim_row = numpy.ndim(images[ii])
                if ndim_row == 2:
                    row_length = 1
                elif ndim_row == 3:
                    row_length = numpy.asarray(images[ii]).shape[0]
                maxncols = numpy.amax((maxncols, row_length))
            columns = maxncols
        else:
            return ()

        fig, ax = plt.subplots(rows, columns, constrained_layout=True)

        for ii in range(rows):
            image_row = numpy.asarray(images[ii])
            if numpy.ndim(image_row) == 2:
                image_row = numpy.expand_dims(image_row, 0)
            for jj in range(image_row.shape[0]):
                if rows == 1:
                    ax[jj].imshow(image_row[jj], cmap=color_map)
                    ax[jj].axis('off')
                    if image_titles is not None:
                        ax[jj].set_title(image_titles[jj], fontsize=font_size)
                else:
                    ax[ii, jj].imshow(image_row[jj], cmap=color_map)
                    ax[ii, jj].axis('off')
                    ax[ii, jj].set_title(image_titles[ii][jj], fontsize=font_size)

        if display:
            plt.show()
            plt.draw()

        return fig, ax

    @classmethod
    def show(cls, im: numpy.ndarray) -> (Figure, Axes):
        fig, ax = plt.subplots()
        plt.imshow(Image.fromarray(im))
        fig.show()

        return fig, ax

    @classmethod
    def makeGraph(cls, im: Optional[numpy.ndarray] = None):
        rows = numpy.arange(im.shape[0])
        cols = numpy.arange(im.shape[1])
        therows, thecols = numpy.meshgrid(rows, cols)

        therows = numpy.reshape(therows, therows.size)
        thecols = numpy.reshape(thecols, thecols.size)

        all_pixels = numpy.array([(arow, acol) for arow, acol in zip(therows, thecols)])

        # Declaration of the matrix that contains pairs of neighbouring nodes and the cost associated with that edge.
        # This is the fastest way to create a matrix full of infinity values.
        weight_matrix = numpy.empty((all_pixels.shape[0], all_pixels.shape[0])) + numpy.inf

        # Now build the matrix.
        # For each pixel.
        for i, coords in enumerate(all_pixels):
            isrc = rimutils.sub2ind(im.shape, numpy.array([coords[0]]), numpy.array([coords[1]]))

            # Calculate the neighbours and find their pixel ids and coordinates.
            theneighbours = rimutils._N8_(coords[0], coords[1], im.shape)
            theneighbours_ind = rimutils.sub2ind(im.shape, theneighbours[:, 0],
                                                 theneighbours[:, 1])  # Convert all vertices once and use dictionary?

            weight_matrix[isrc, theneighbours_ind] = im[theneighbours[:, 0], theneighbours[:, 1]]

        # And use the matrix to build the graph.
        graph_sparse = csgraph_from_dense(weight_matrix)

        return graph_sparse, weight_matrix

    @classmethod
    def pairwise_noncyclic(cls, iterable):
        "s -> (s0, s1), (s1, s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    @classmethod
    def makeGraphX(cls, im: numpy.ndarray) -> DiGraph:
        """Returns the two-dimensional grid graph corresponding to image im.

        The graph is non periodic and directed.

        The grid graph has each node connected to its eight nearest neighbors.

        Parameters
        ----------
        im: a numpy ndarray representing to convert into a graph.

        Returns
        -------
        NetworkX graph
            The directed grid graph of the specified dimensions.

        """

        G = empty_graph(0, DiGraph())
        rows = range(im.shape[0])
        cols = range(im.shape[1])
        cols_minus1 = range(im.shape[1] - 1)
        G.add_nodes_from((i, j) for i in rows for j in cols)
        G.add_weighted_edges_from(((i, j), (pi, j), im[pi, j])
                                  for pi, i in cls.pairwise_noncyclic(rows) for j in cols)
        G.add_weighted_edges_from(((pi, j), (i, j), im[i, j])
                                  for pi, i in cls.pairwise_noncyclic(rows) for j in cols)
        G.add_weighted_edges_from(((i, j), (i, pj), im[i, pj])
                                  for i in rows for pj, j in cls.pairwise_noncyclic(cols))
        G.add_weighted_edges_from(((i, pj), (i, j), im[i, j])
                                  for i in rows for pj, j in cls.pairwise_noncyclic(cols))
        G.add_weighted_edges_from(((i, j), (pi, j + 1), im[pi, j + 1])
                                  for pi, i in cls.pairwise_noncyclic(rows) for j in cols_minus1)
        G.add_weighted_edges_from(((pi, j + 1), (i, j), im[i, j])
                                  for pi, i in cls.pairwise_noncyclic(rows) for j in cols_minus1)
        G.add_weighted_edges_from(((i, j + 1), (pi, j), im[pi, j])
                                  for pi, i in cls.pairwise_noncyclic(rows) for j in cols_minus1)
        G.add_weighted_edges_from(((pi, j), (i, j + 1), im[i, j + 1])
                                  for pi, i in cls.pairwise_noncyclic(rows) for j in cols_minus1)

        return G

    # 4 neighbours (removing pixels outside the image).
    @classmethod
    def _N4_(cls, row, col, imsize=(numpy.inf, numpy.inf)):
        # asarray vs array: The main difference is that array (by default) will make a copy of the object, while asarray will not unless necessary.
        initial = numpy.array([[row - 1, col], [row + 1, col], [row, col - 1], [row, col + 1]], dtype=numpy.int16)
        big_enough = numpy.logical_and(initial[:, 0] >= 0, initial[:, 1] >= 0)
        small_enough = numpy.logical_and(initial[:, 0] < imsize[0], initial[:, 1] < imsize[1])
        good_rows = numpy.logical_and(big_enough, small_enough)

        return initial[good_rows, :]

    # Diagonal neighbours (removing pixels outside the image).
    @classmethod
    def _ND_(cls, row, col, imsize=(numpy.inf, numpy.inf)):
        # asarray vs array: The main difference is that array (by default) will make a copy of the object, while asarray will not unless necessary.
        initial = numpy.array([[row - 1, col - 1], [row + 1, col - 1], [row + 1, col + 1], [row - 1, col + 1]],
                              dtype=numpy.int16)
        big_enough = numpy.logical_and(initial[:, 0] >= 0, initial[:, 1] >= 0)
        small_enough = numpy.logical_and(initial[:, 0] < imsize[0], initial[:, 1] < imsize[1])
        good_rows = numpy.logical_and(big_enough, small_enough)

        return initial[good_rows, :]

    # 8 neighbours (removing pixels outside the image)
    @classmethod
    def _N8_(cls, row: int, col: int, imsize=(numpy.inf, numpy.inf)) -> numpy.ndarray:
        """
        Finds the 8 neighbours of a set of coordinates, including only neighbours that belong within a certain imsize.

        Alternatively, could be implemented with two calls to _N4_ and _ND_, but that implementations is 4X slower than
        this (presumably because calling functions is expensive):
                return numpy.vstack((rimutils._N4_(row, col, imsize), rimutils._ND_(row, col, imsize)))


        :param row:
        :param col:
        :param imsize:
        :return:
        """
        initial = numpy.array([[row - 1, col], [row + 1, col], [row, col - 1], [row, col + 1],
                               [row - 1, col - 1], [row + 1, col - 1], [row + 1, col + 1], [row - 1, col + 1]],
                              dtype=numpy.int16)
        big_enough = numpy.logical_and(initial[:, 0] >= 0, initial[:, 1] >= 0)
        small_enough = numpy.logical_and(initial[:, 0] < imsize[0], initial[:, 1] < imsize[1])
        good_rows = numpy.logical_and(big_enough, small_enough)

        return initial[good_rows, :]

    # array_shape takes on the format [rows, cols].
    @classmethod
    def sub2ind(cls, array_shape: Tuple[int, int], rows: numpy.ndarray, cols: numpy.ndarray) -> numpy.ndarray:
        ind = rows * array_shape[1] + cols

        if type(ind) == numpy.int:
            ind = numpy.array([ind])

        bad_values = numpy.concatenate(((ind < 0).nonzero(), (ind >= numpy.prod(array_shape)).nonzero()))

        ind[bad_values] = -1

        return ind

    @classmethod
    def ind2sub(cls, array_shape: Tuple[int, int], ind: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        bad_values = numpy.concatenate(((ind < 0).nonzero(), (ind >= numpy.prod(array_shape)).nonzero()))

        rows: numpy.ndarray = numpy.array(ind.astype('int') / array_shape[1], dtype=numpy.int)
        cols: numpy.ndarray = ind % array_shape[1]

        rows[bad_values] = -1
        cols[bad_values] = -1

        return rows, cols

    @classmethod
    def flow(cls, firstslice: numpy.ndarray, secondslice: numpy.ndarray,
             desired_step_sz: numpy.ndarray = numpy.array([16, 16]),
             window_sz: numpy.ndarray = numpy.array([64, 64]), plots: bool = False, gradient_flag: bool = False,
             border_width: numpy.int = 1, calculated_step_sz=None, filter_output: bool = False,
             min_normxcorr: numpy.double = 0.0) -> (numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray):
        """
        Calculates the flow field between firstslice and secondslice using local cross-correlation (PIV).

        :param firstslice: source image (numpy.ndarray).
        :param secondslice: target image (numpy.ndarray).
        :param desired_step_sz: determines the points where the final vector field will be calculated.
        Can take one of three data types:
        (1) numbers.Number: single number indicating the grid spacing; applies to both rows and columns.
        (2) tuple: two-element tuple indicating row- and column- grid spacing.
        (3) numpy.ndarray: points in the grid in row, column coordinates.
        :param window_sz: initial window size (row, col) to calculate cross-correlation between source and target
        images. If the calculated cross-correlation is smaller than min_normxcorr, then the target window size will be
        doubled until the correlation is greater than min_normxcorr or the window size is greater than the image size
        (numpy.ndarray).
        :param plots: plot the vector field or not (bool).
        :param gradient_flag: use the gradient magnitude or the pixel values for the cross-correlation calculations.
        :param border_width: how many rows and columns to remove (numpy.int).
        :param calculated_step_sz: distance between points in the source image where the cross-correlation will be
        calculated [row, col] (numpy.ndarray).
        :param filter_output: find and delete vectors too different from their neighbours (bool).
        :param min_normxcorr: minimum acceptable cross-correlation value (numpy.double).
        :rtype: (numpy.ndarray, numpy.ndarray, numpy.ndarray, numpy.ndarray)
        :return: (Xvaldesired, Yvaldesired, X0desired, Y0desired)
        Xvaldesired: X components of the flow field vectors (numpy.ndarray).
        Yvaldesired: Y components of the flow field vectors (numpy.ndarray).
        Xf: X coordinates where the flow field was calculated (numpy.ndarray).
        Yf: Y coordinates where the flow field was calculated (numpy.ndarray).
        """

        if isinstance(window_sz, numbers.Number):
            window_sz = numpy.array([window_sz, window_sz])

        # points_flag indicates if the user wants to find the flow field at
        # specific points. In that case, one can speed up the analysis a bit.
        points_flag: bool = False

        if isinstance(desired_step_sz, numbers.Number):
            desired_step_sz = numpy.array([desired_step_sz, desired_step_sz])
            points_flag = False
        elif isinstance(desired_step_sz, tuple):
            desired_step_sz = numpy.array([desired_step_sz[0], desired_step_sz[1]])
            points_flag = False
        elif isinstance(desired_step_sz, numpy.ndarray) and desired_step_sz.ndim == 2:
            points_flag = True

        if isinstance(calculated_step_sz, numbers.Number):
            calculated_step_sz = numpy.array([calculated_step_sz, calculated_step_sz])
        elif calculated_step_sz is None:
            calculated_step_sz = numpy.int16(numpy.round(window_sz / 2.))

        if gradient_flag:
            firstimage = ndimage.gaussian_gradient_magnitude(firstslice, sigma=rimutils.GRADMAG_DEFAULT_SIGMA)
            secondimage = ndimage.gaussian_gradient_magnitude(secondslice, sigma=rimutils.GRADMAG_DEFAULT_SIGMA)
        else:
            firstimage = firstslice
            secondimage = secondslice

        sz = firstimage.shape

        ws0 = window_sz  # Store the original window size in case the pyramidal approach is used.

        # First we calculate the flow field using window_sz as window size, and then we interpolate to achieve
        # desired_step_sz.
        Xval: numpy.ndarray = numpy.nan * numpy.ones(
            [int(numpy.floor(firstslice.shape[0] / calculated_step_sz[0])) + 1, int(numpy.floor(
                firstslice.shape[1] / calculated_step_sz[1])) + 1])  # Flow field coordinates at window_sz resolution.
        Yval: numpy.ndarray = numpy.nan * numpy.ones(
            [int(numpy.floor(firstslice.shape[0] / calculated_step_sz[0])) + 1,
             int(numpy.floor(firstslice.shape[1] / calculated_step_sz[1])) + 1])
        # Xval: numpy.ndarray = numpy.nan * numpy.ones(firstimage.shape)
        # Yval: numpy.ndarray = numpy.nan * numpy.ones(firstimage.shape)

        for ii in range(0, sz[0], calculated_step_sz[0]):  # Rows
            for jj in range(0, sz[1], calculated_step_sz[1]):  # Columns
                # Ideally, what follows would be a do ... while ... end loop. Alas, Python (like Matlab) does not have
                # that conditional loop, and that forces me to do some pretty unelegant things ...

                # Initialize to -1 to go into the while loop at least once per pixel.
                max_normxcorr: numpy.double = -1.0

                # The first thing done in the while loop is to double the window size (in case) we come from a previous
                # iteration where the window size was not enough. So before going into the loop, I divide the window
                # size by two. This also needs the 2*window_sz in the condition in the while loop.
                window_sz = ws0 / 2.

                # If the minimum cross-correlations has not been attained and the window size still is small enough ...
                while max_normxcorr < min_normxcorr and 2 * window_sz[0] < sz[0] and 2 * window_sz[1] < sz[1]:
                    # Double interrogation window size.
                    window_sz = window_sz * 2.

                    # Search window size is twice the size of the interrogation window (+1 so that there is a central
                    # pixel).
                    search_ws = 2 * window_sz + 1

                    # Interrogation window (aka. the template).
                    minrowi = int(max(0, ii - numpy.floor(window_sz[0] / 2)))
                    maxrowi = int(min(sz[0] - 1, ii + numpy.floor(window_sz[0] / 2)))
                    mincoli = int(max(0, jj - numpy.floor(window_sz[1] / 2)))
                    maxcoli = int(min(sz[1] - 1, jj + numpy.floor(window_sz[1] / 2)))
                    im1 = firstimage[minrowi:maxrowi + 1, mincoli:maxcoli + 1]

                    # If the user wants to interpolate the vector field in specific points, and none of those points is
                    # in a given interrogation window, just skip the window by leaving the while loop.
                    #thewindow = mplpth.Path(
                    #    numpy.array([[mincoli, minrowi], [mincoli, maxrowi], [maxcoli, maxrowi], [maxcoli, minrowi],
                    #                 [mincoli, minrowi]]),
                    #    closed=True)
                    #if points_flag and numpy.count_nonzero(thewindow.contains_points(desired_step_sz)) == 0:
                    #    max_normxcorr = -1.0
                    #    break
                    # Do this only for the windows that we are interested
                    # in (otherwise everything slows down dramatically).
                    # (that may not be true for the opencv implementation, which is FAAAAAAST!)
                    # First condition: normxcorr2 in Matlab would crash if all the values in the template were equal.
                    # Second condition:  make sure that at least 50% of the
                    # pixels are non-zero (this happens, for instance, when
                    # the images have been rotated). The results are much
                    # better than without this test.
                    if numpy.unique(im1).size == 1 or numpy.count_nonzero(im1) / numpy.prod(im1.shape) < 0.5:
                        continue

                    # Search window (twice as large as the interrogation window).
                    minrows = int(max(0, ii - numpy.floor(search_ws[0] / 2)))
                    maxrows = int(min(sz[0] - 1, ii + numpy.floor(search_ws[0] / 2)))
                    mincols = int(max(0, jj - numpy.floor(search_ws[1] / 2)))
                    maxcols = int(min(sz[1] - 1, jj + numpy.floor(search_ws[1] / 2)))
                    im2 = secondimage[minrows:maxrows + 1, mincols:maxcols + 1]

                    # Calculate and save the crosscorrelation. Converting the images to float32 is a requirement
                    # of cv2.matchTemplate, which will only work with uint8 or float32 images. Even with that
                    # conversion, this is 30X faster than skimage.features.match_template. In fact,
                    # rather than doing a paired cross-correlation, if you simply found im1 in secondimage it would be
                    # three times faster than using skimage with paired cross-correlation ... but ten times slower
                    # than the paired approach implemented in open cv.
                    # I tried all possible comparison methods, and TM_CCOEFF_NORMED provides the greatest dynamic range
                    # to distinguish between high an low correlations.
                    cc = cv2.matchTemplate(im2.astype(numpy.float32), im1.astype(numpy.float32), cv2.TM_CCOEFF_NORMED)

                    # Find the maximum cross-correlation. max_loc contains the (x, y) coordinates (not row, col) where
                    # the upper-left corner of the interrogation window maximizes cross-correlation.
                    _, max_normxcorr, _, max_loc = cv2.minMaxLoc(cc)

                    # Limit travelled distance: if the maximum cross-correlation is too far (e.g. on one of the corners,
                    # this can happen if there are black pixels in the image introduced when rotating them), repeat with
                    # a larger window size.
                    if numpy.linalg.norm(numpy.array([mincols + max_loc[0] - mincoli, minrows + max_loc[1] - minrowi]),
                                         2) >= numpy.mean(window_sz) / 2:
                        max_normxcorr = -1

                # If the cross-correlation was sufficient, ...
                if max_normxcorr >= min_normxcorr:
                    # We subtract the position of the top left corner of the interrogation window (mincoli, minrowi)
                    # from the position where placing the top-left corner of the interrogation window (with respect
                    # to the search window) produced the maximum cross-correlation
                    # (mincols+max_loc[0], minrows+max_loc[1]).
                    Xval[int(numpy.floor(ii / calculated_step_sz[0])), int(
                        numpy.floor(jj / calculated_step_sz[1]))] = mincols + max_loc[0] - mincoli
                    Yval[int(numpy.floor(ii / calculated_step_sz[0])), int(
                        numpy.floor(jj / calculated_step_sz[1]))] = minrows + max_loc[1] - minrowi
                    # Xval[ii, jj] = mincols + max_loc[0] - mincoli
                    # Yval[ii, jj] = minrows + max_loc[1] - minrowi
                else:
                    Xval[int(numpy.floor(ii / calculated_step_sz[0])), int(
                        numpy.floor(jj / calculated_step_sz[1]))] = 0.0
                    Yval[int(numpy.floor(ii / calculated_step_sz[0])), int(
                        numpy.floor(jj / calculated_step_sz[1]))] = 0.0
                    # Xval[ii, jj] = numpy.nan
                    # Yval[ii, jj] = numpy.nan

                # print(f"({int(numpy.floor(ii / calculated_step_sz[0]))}, {int(int(numpy.floor(jj / calculated_step_sz[1])))}) -> {Xval[int(numpy.floor(ii / calculated_step_sz[0])), int(numpy.floor(jj / calculated_step_sz[1]))]}")
                # print("")

        # Generate the coordinates of all the centers of the windows of size window_sz.
        X0, Y0 = numpy.meshgrid(numpy.arange(Xval.shape[1]) * calculated_step_sz[1],
                                numpy.arange(Xval.shape[0]) * calculated_step_sz[0])

        # Remove border measurements to avoid boundary effects.
        Xval = Xval[border_width:-border_width, border_width:-border_width]
        Yval = Yval[border_width:-border_width, border_width:-border_width]
        X0 = X0[border_width:-border_width, border_width:-border_width]
        Y0 = Y0[border_width:-border_width, border_width:-border_width]

        if filter_output:  # Needs checking - straight from Matlab rflow.
            # Filter the output data trying to remove outliers using a normalized median test (see Raffel et al., Chapter 6.1.5).
            mag = numpy.sqrt(Xval * Xval + Yval * Yval)  # Vector magnitude.
            sk = 1  # Filter radius.
            kernel = numpy.ones([2 * sk + 1, 2 * sk + 1])
            kernel[
                sk, sk] = 0  # This is a kernel where all pixels are set to one except for the central pixel, set to zero.

            medians = numpy.nan * numpy.zeros(mag.shape)
            residuals = numpy.nan * numpy.zeros(mag.shape)
            normresiduals = numpy.nan * numpy.zeros(mag.shape)

            # This moves a 3x3 kernel through the "mag" matrix.
            for ii in range(mag.shape[0]):
                miny = max(0, ii - sk)  # Y coordinates.
                maxy = min(mag.shape[0], ii + sk + 1)
                for jj in range(mag.shape[1]):
                    minx = max(0, jj - sk)  # X coordinates.
                    maxx = min(mag.shape[1], jj + sk + 1)

                    tmp, mag[ii, jj] = mag[ii, jj], numpy.nan
                    subw = mag[miny:maxy, minx:maxx]
                    medians[ii, jj] = numpy.nanmedian(subw)
                    mag[ii, jj] = tmp
                    residuals[ii, jj] = numpy.abs(mag[ii, jj] - medians[ii, jj])

            # This moves a 3x3 kernel through the "residuals" matrix, calculated in the previous convolution.
            for ii in range(residuals.shape[0]):
                miny = max(0, ii - sk)  # Y coordinates.
                maxy = min(residuals.shape[0], ii + sk + 1)
                for jj in range(residuals.shape[1]):
                    minx = max(0, jj - sk)  # X coordinates.
                    maxx = min(residuals.shape[1], jj + sk + 1)

                    tmp, residuals[ii, jj] = residuals[ii, jj], numpy.nan
                    subw = residuals[miny:maxy, minx:maxx]
                    medianresidual = numpy.nanmedian(subw)
                    residuals[ii, jj] = tmp
                    normresiduals[ii, jj] = residuals[ii, jj] / (
                            medianresidual + .15)  # Magic number from Raffel et al. Prevents divisions by 0 in static regions.

            # Threshold for small normalized residuals is the value under which 95% of the normalized residuals
            # are included. "histogram" flattens the array.
            thehisto, _ = numpy.histogram(normresiduals, numpy.arange(0, numpy.amax(normresiduals), .5))
            thehisto = thehisto / numpy.prod(normresiduals.shape)  # Histogram of normalized residuals.
            thecumsum = numpy.cumsum(thehisto)  # Cumulative distribution function of residuals.
            th_ind = numpy.argmin(numpy.abs(thecumsum - .95))  # argmin returns the index of the min.
            eps_th = th_ind * .5

            Y_remove, X_remove = numpy.where(normresiduals > eps_th)
            # Xval[Y_remove, X_remove] = numpy.nan
            # Yval[Y_remove, X_remove] = numpy.nan

            # Replace the bad vectors using bivariate spline interpolation (see Raffel et al., 6.2).
            # RectBivariateSpline creates an object that can be called with a couple of coordinates (implements
            # the __call__ method).
            interpXfield = scipy.interpolate.RectBivariateSpline(Y0[:, 0], X0[0, :], Xval)
            interpYfield = scipy.interpolate.RectBivariateSpline(Y0[:, 0], X0[0, :], Yval)

            Xval[Y_remove, X_remove] = interpXfield(Y_remove, X_remove, grid=False)
            Yval[Y_remove, X_remove] = interpYfield(Y_remove, X_remove, grid=False)

        # Generate the origin coordinates for the flow field with the appropriate resolution or use the points given by
        # the user. desired_step_sz == 2 when there is only one row in the size vector.
        if desired_step_sz.size == 2 and not points_flag:
            Xf = numpy.arange(0, sz[1], desired_step_sz[1])
            Yf = numpy.arange(0, sz[0], desired_step_sz[0])
            Xf, Yf = numpy.meshgrid(Xf, Yf, indexing='ij')
        else:
            Xf = desired_step_sz[:, 1]
            Yf = desired_step_sz[:, 0]

        xval = Xval.ravel()
        good_indices = numpy.nonzero(numpy.invert(numpy.isnan(xval)))[0]
        yval = Yval.ravel()
        y0 = Y0.ravel()
        x0 = X0.ravel()

        xval = xval[good_indices]
        yval = yval[good_indices]
        y0 = y0[good_indices]
        x0 = x0[good_indices]

        print("before")
        Xvaldesired = scipy.interpolate.griddata(numpy.vstack((y0, x0)).T, xval, numpy.vstack((Yf, Xf)).T, method='linear', fill_value=0.0)
        print("mid")
        Yvaldesired = scipy.interpolate.griddata(numpy.vstack((y0, x0)).T, yval, numpy.vstack((Yf, Xf)).T, method='linear', fill_value=0.0)
        print("after")

        #Xvaldesired = RUtils.bicubic_interpolation(Y0[:, 0], X0[0, :], Xval, Yf, Xf)
        #Yvaldesired = RUtils.bicubic_interpolation(Y0[:, 0], X0[0, :], Yval, Yf, Xf)

        if plots:
            # Calculate the end point of the flow field vector.
            fig, ax = plt.subplots(1, 1)
            plt.imshow(firstslice)
            # ax.quiver(Y0[:, 0], X0[0, :], Xval, -Yval)
            ax.quiver(Yf, Xf, Xvaldesired, -Yvaldesired)
            # ax.set_ylim(ax.get_ylim()[::-1])
            # ax.set_ylim(ax[1].get_ylim()[::-1])

            plt.show()

        return Xvaldesired, Yvaldesired, Xf, Yf

    @classmethod
    def flow_at_points(cls, firstslice: numpy.ndarray, secondslice: numpy.ndarray, point_array: numpy.ndarray,
             window_sz: numpy.ndarray = numpy.array([64, 64]), gradient_flag: bool = False,
             min_normxcorr: numpy.double = 0.0) -> numpy.ndarray:
        """
        Calculates the flow field between firstslice and secondslice using local cross-correlation (PIV).

        :param firstslice: source image (numpy.ndarray).
        :param secondslice: target image (numpy.ndarray).
        :param point_array: points in the grid where flow will be calculated, in row, column coordinates.
        :param window_sz: initial window size (row, col) to calculate cross-correlation between source and target
        images. If the calculated cross-correlation is smaller than min_normxcorr, then the target window size will be
        doubled until the correlation is greater than min_normxcorr or the window size is greater than the image size
        (numpy.ndarray).
        :param plots: plot the vector field or not (bool).
        :param gradient_flag: use the gradient magnitude or the pixel values for the cross-correlation calculations.
        :param min_normxcorr: minimum acceptable cross-correlation value (numpy.double).
        :rtype: numpy.ndarray
        :return: flow_vectors
        flow_vectors: [row, col] ([Y, X]) components of the flow at point_array points (numpy.ndarray).
        """

        if isinstance(window_sz, numbers.Number):
            window_sz = numpy.array([window_sz, window_sz])

        if gradient_flag:
            firstimage = ndimage.gaussian_gradient_magnitude(firstslice, sigma=rimutils.GRADMAG_DEFAULT_SIGMA)
            secondimage = ndimage.gaussian_gradient_magnitude(secondslice, sigma=rimutils.GRADMAG_DEFAULT_SIGMA)
        else:
            firstimage = firstslice
            secondimage = secondslice

        sz = firstimage.shape

        ws0 = window_sz  # Store the original window size in case the pyramidal approach is used.

        flow_vectors: numpy.ndarray = numpy.zeros(point_array.shape)  # Flow vector components.

        for point_index, apoint in enumerate(point_array):
            ii = apoint[0]  # rows
            jj = apoint[1]  # cols

            # Ideally, what follows would be a do ... while ... end loop. Alas, Python (like Matlab) does not have
            # that conditional loop, and that forces me to do some pretty ugly things ...

            # Initialize to -1 to go into the while loop at least once per pixel.
            max_normxcorr: numpy.double = -1.0

            # The first thing done in the while loop is to double the window size (in case) we come from a previous
            # iteration where the window size was not enough. So before going into the loop, I divide the window
            # size by two. This also needs the 2*window_sz in the condition in the while loop.
            window_sz = ws0 / 2.

            # If the minimum cross-correlations has not been attained and the window size still is small enough ...
            while max_normxcorr < min_normxcorr and 2 * window_sz[0] < sz[0] and 2 * window_sz[1] < sz[1]:
                # Double interrogation window size.
                window_sz = window_sz * 2.

                # Search window size is twice the size of the interrogation window (+1 so that there is a central
                # pixel).
                search_ws = 2 * window_sz + 1

                # Interrogation window (aka. the template).
                minrowi = int(max(0, ii - numpy.floor(window_sz[0] / 2)))
                maxrowi = int(min(sz[0] - 1, ii + numpy.floor(window_sz[0] / 2)))
                mincoli = int(max(0, jj - numpy.floor(window_sz[1] / 2)))
                maxcoli = int(min(sz[1] - 1, jj + numpy.floor(window_sz[1] / 2)))
                im1 = firstimage[minrowi:maxrowi + 1, mincoli:maxcoli + 1]

                # First condition: normxcorr2 in Matlab would crash if all the values in the template were equal.
                # Second condition:  make sure that at least 50% of the
                # pixels are non-zero (this happens, for instance, when
                # the images have been rotated). The results are much
                # better than without this test.
                if numpy.unique(im1).size == 1 or numpy.count_nonzero(im1) / numpy.prod(im1.shape) < 0.5:
                    continue

                # Search window (twice as large as the interrogation window).
                minrows = int(max(0, ii - numpy.floor(search_ws[0] / 2)))
                maxrows = int(min(sz[0] - 1, ii + numpy.floor(search_ws[0] / 2)))
                mincols = int(max(0, jj - numpy.floor(search_ws[1] / 2)))
                maxcols = int(min(sz[1] - 1, jj + numpy.floor(search_ws[1] / 2)))
                im2 = secondimage[minrows:maxrows + 1, mincols:maxcols + 1]

                # Calculate and save the crosscorrelation. Converting the images to float32 is a requirement
                # of cv2.matchTemplate, which will only work with uint8 or float32 images. Even with that
                # conversion, this is 30X faster than skimage.features.match_template. In fact,
                # rather than doing a paired cross-correlation, if you simply found im1 in secondimage it would be
                # three times faster than using skimage with paired cross-correlation ... but ten times slower
                # than the paired approach implemented in open cv.
                # I tried all possible comparison methods, and TM_CCOEFF_NORMED provides the greatest dynamic range
                # to distinguish between high an low correlations.
                cc = cv2.matchTemplate(im2.astype(numpy.float32), im1.astype(numpy.float32), cv2.TM_CCOEFF_NORMED)

                # Find the maximum cross-correlation. max_loc contains the (x, y) coordinates (not row, col) where
                # the upper-left corner of the interrogation window maximizes cross-correlation.
                _, max_normxcorr, _, max_loc = cv2.minMaxLoc(cc)

                # Limit travelled distance: if the maximum cross-correlation is too far (e.g. on one of the corners,
                # this can happen if there are black pixels in the image introduced when rotating them), repeat with
                # a larger window size.
                if numpy.linalg.norm(numpy.array([mincols + max_loc[0] - mincoli, minrows + max_loc[1] - minrowi]),
                                     2) >= numpy.mean(window_sz) / 2:
                    max_normxcorr = -1

            # If the cross-correlation was sufficient, ...
            if max_normxcorr >= min_normxcorr:
                # We subtract the position of the top left corner of the interrogation window (mincoli, minrowi)
                # from the position where placing the top-left corner of the interrogation window (with respect
                # to the search window) produced the maximum cross-correlation
                # (mincols+max_loc[0], minrows+max_loc[1]).
                flow_vectors[point_index, :] = numpy.asarray([minrows + max_loc[1] - minrowi, mincols + max_loc[0] - mincoli])
            else:
                flow_vectors[point_index, :] = numpy.asarray([0, 0])

        return flow_vectors

    @classmethod
    def stretch(cls, image_array: numpy.ndarray, low: int = 0, high: int = 100, minimum: int = 0, maximum: int = 255) \
            -> numpy.ndarray:
        """
        Linear stretch of the contrast of an image.
        :param image_array:
        :param low: lower percentile of the image to be mapped to the minimum value (0)
        :param high: higher percentile (100)
        :param minimum: minimum pixel value in the resulting image (0)
        :param maximum: maximum pixel value (255)
        :return: image_out, an image array.

        Has a sister method in rimcore.
        """

        sc: float = 0.
        to_clip: bool = False

        if low > high:
            high, low = low, high

        # Define output variable.
        image_out: numpy.ndarray = image_array.copy()

        if maximum == minimum:
            image_out[:] = minimum
            return image_out
        else:
            to_clip = low != 0 or high != 100

        # Find the appropriate pixel values for the low and high thresholds.
        if low == 0:
            low = numpy.min(image_array)
        else:
            low = numpy.percentile(image_array, low)

        if high == 100:
            high = numpy.max(image_array)
        else:
            high = numpy.percentile(image_array, high)

        if high == low:
            image_out[:] = (minimum+maximum)/2
            return image_out

        # Determine the scaling factor.
        sc = (maximum - minimum)/(high - low)

        # Linear stretch of image_in.
        if low != 0:
            image_out = image_out - low

        if sc != 1:
            image_out = image_out * sc

        if minimum != 0:
            image_out = image_out + minimum

        if to_clip:
            image_out = numpy.clip(image_out, minimum, maximum)

        return image_out

    @classmethod
    def invert(cls, image_array: numpy.ndarray, image_max: bool = True) -> numpy.ndarray:
        image_out: numpy.ndarray = None

        if image_max:
            theimmax = numpy.amax(image_array)
            image_out = theimmax - image_array
        else:
            image_out = skimage.util.invert(image_array)

        return image_out

    @classmethod
    def gradient(cls, image_array: numpy.ndarray) -> numpy.ndarray:
        """

        :param image_array: input image.
        :return: gradient magnitude.

        This implementation is consistent in its result with the "Find edges" option in ImageJ.
        """

        # Sobel kernels.
        kx: numpy.ndarray = numpy.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
        ky: numpy.ndarray = numpy.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])

        x: numpy.ndarray = numpy.asarray([ndimage.convolve(a_slice.astype(float), kx) for a_slice in image_array])
        y: numpy.ndarray = numpy.asarray([ndimage.convolve(a_slice.astype(float), ky) for a_slice in image_array])

        return numpy.hypot(x, y).astype(numpy.uint16)

    @classmethod
    def local_threshold_segm(cls, im: Optional[numpy.ndarray] = None, window_size: int = FINDSEEDS_DEFAULT_WINSIZE, binary_dilation_radius: int = 0, border_objects: bool = False) -> list:
        """
        Threshold-based segmentation of the image. Uses an adaptive threshold as implemented in
        skimage.filters.threshold_local.

        :param image: image to segment (numpy.ndarray).
        :param window_size: size of the image to calculate the threshold for each pixel (mean value in the window).
        :param border_objects: return objects touching the edge of the image (bool).
        :return: list of contours determined by the adaptive threshold (list).
        """
        if im is None or im is False:
            return numpy.empty((0))

        _, _, thresholded_im_final = cls.local_threshold(im, window_size, binary_dilation_radius)
        labels = label(thresholded_im_final, connectivity=2)

        # Extract contours.
        return cls.extract_contours(labels, border_objects)

    @classmethod
    def local_threshold(cls, im: Optional[numpy.ndarray] = None, window_size: int = FINDSEEDS_DEFAULT_WINSIZE, binary_dilation_radius: int = 0) -> (numpy.ndarray, numpy.ndarray, numpy.ndarray):

        if im is None or im is False:
            return numpy.empty((0))

        # Window size must be an odd number for the skimage local threshold function.
        if window_size % 2 == 0:
            window_size += 1

        # Binarize image using a local threshold.
        threshold_im = threshold_local(im, int(window_size), method='mean')
        thresholded_im = im > threshold_im

        if binary_dilation_radius > 0:
            selem_separation = disk(binary_dilation_radius)
            thresholded_im_morph = binary_closing(thresholded_im, selem_separation)

            # Create a new variable so that we can return the non-inverted binary image as an intermediate representation.
            thresholded_im_final = ~ thresholded_im_morph

        # -4 seems to be a good value for nuclei images.
        elif binary_dilation_radius < 0:
            selem_separation = disk(-binary_dilation_radius)
            thresholded_im_morph = binary_opening(thresholded_im, selem_separation)

            # Create a new variable for consistency with the option with a closing.
            thresholded_im_final = thresholded_im_morph

        else:  # binary_dilation_radius == 0
            thresholded_im_morph = thresholded_im
            thresholded_im_final = thresholded_im_morph

        return thresholded_im, thresholded_im_morph, thresholded_im_final

    @classmethod
    def waterseed(cls, image: Optional[numpy.ndarray] = None, seeds: Optional[numpy.ndarray] = None, border_objects: bool = False) -> list:
        """
        Marker-based segmentation of the image. Uses the watershed, region growing algorithm as implemented in
        skimage.morphology.

        :param image: image to segment (numpy.ndarray).
        :param seeds: (X, Y) coordinates of the seed points (numpy.ndarray).
        :param border_objects: True if border objects need to be preserved, False if deleted.
        :return: list of contours determined by the watershed lines (list). Only polygons not touching the image
        borders are returned.
        """
        contour_list = list([])

        # Build seed image.
        seed_image = numpy.zeros(image.shape)

        try:
            for label, seed_xy in enumerate(seeds):
                seed_image[seed_xy[1], seed_xy[0]] = label + 1
        except:
            print(f'There seems to be an issue with the {str(label)}th of your watershed seeds being too close to or '
                  f'outside the image limits: (row={seed_xy[1]}, col={seed_xy[0]}, image size={image.shape}).')
            return contour_list

        seed_image = dilation(seed_image, disk(3))

        # Run watershed.
        # image_color = cv2.cvtColor(rimutils.stretch(image).astype(numpy.uint8), cv2.COLOR_GRAY2BGR)
        # seed_image = seed_image.astype(numpy.int32)
        # labels = cv2.watershed(image_color, seed_image)

        labels = watershed(image, seed_image, connectivity=2)  # , mask=image)

        # Extract contours.
        return cls.extract_contours(labels, border_objects)

    @classmethod
    def extract_contours(cls, labeled_image: Optional[numpy.ndarray] = None, border_objects: bool = False) -> list:
        """

        :param labeled_image:
        :param border_objects:
        :return:
        """
        contour_list = list([])
        thelabels = numpy.unique(labeled_image)

        for aLabel in thelabels:
            bin_mask = numpy.asarray(labeled_image == aLabel,
                                     dtype=int)  # skimage.segmentation.find_boundaries can also be used for this.
            aContour = find_contours(bin_mask, 0)

            if len(aContour) == 1:  # if find_contours returns more than one contour, the seed has spilled over and filled the background, and find_contours is returning boundaries inside, not outside, the object.

                aContour = aContour[0]

                # Add polygon only if not touching edge.
                if border_objects or not rimutils.border_object(
                    aContour, labeled_image.shape[0], labeled_image.shape[1]
                ):
                    aContour = (numpy.asarray(aContour)[:, ::-1]).tolist()
                    contour_list.append(aContour)

        return contour_list


    @classmethod
    def generate_subimages(cls, image: numpy.ndarray, subimage_sz: Tuple[int, int], step_sz: Tuple[int, int],
                           rowcol: bool = True) \
            -> Tuple[numpy.ndarray, int, int]:
        if image is False or image is None or subimage_sz is False or subimage_sz is None or step_sz is False or \
                step_sz is None:
            return numpy.empty((1, 0), None, None)

        row_rad = int(numpy.floor(subimage_sz[0] / 2))
        col_rad = int(numpy.floor(subimage_sz[1] / 2))
        max_row_range = image.shape[0] - row_rad
        if subimage_sz[0] % 2 == 0:
            max_row_range += 1
        max_col_range = image.shape[1] - col_rad
        if subimage_sz[1] % 2 == 0:
            max_col_range += 1

        for row in range(row_rad, max_row_range, step_sz[0]):
            for col in range(col_rad, max_col_range, step_sz[1]):
                minrow = row - row_rad
                maxrow = row + row_rad
                if subimage_sz[0] % 2 == 1:
                    maxrow += 1

                mincol = col - col_rad
                maxcol = col + col_rad
                if subimage_sz[1] % 2 == 1:
                    maxcol += 1

                if rowcol:
                    yield image[minrow:maxrow, mincol:maxcol], row, col
                else:
                    yield image[minrow:maxrow, mincol:maxcol]

    @classmethod
    def border_object(cls, coordinates: numpy.ndarray, width: int, height: int) -> bool:
        """


        :param coordinates: assumes in x, y pairs (not row, col).
        :param width: number of columns.
        :param height: number of rows.
        :return:

        THIS METHOD IS ABOUT TWICE AS FAST AS interior_object BELOW.
        """
        return any(coordinates[:, 0] == 0) or any(coordinates[:, 1] == 0) or any(
            coordinates[:, 0] == (width - 1)) or any(coordinates[:, 1] == (height - 1))

    @classmethod
    def interior_object(cls, coordinates: numpy.ndarray, width: int, height: int) -> bool:
        return numpy.all((coordinates[:, 0] > 0) & (coordinates[:, 0] < (width - 1)) & (coordinates[:, 1] > 0) & (
                    coordinates[:, 1] < (height - 1)))

    @classmethod
    def shift_image(cls, image: numpy.ndarray, translation_vector: numpy.ndarray) -> numpy.ndarray:
        if image is False or image is None or translation_vector is False or translation_vector is None \
                or len(translation_vector) != 2:
            return numpy.empty((1, 0), None, None)

        translate_transform = EuclideanTransform(translation=-1 * translation_vector)

        return warp(image, inverse_map=translate_transform, order=0, preserve_range=True).astype(type(image[0, 0]))

    @classmethod
    def findshift_crude(cls, image: numpy.ndarray, coordinates: numpy.ndarray,
                        reference_slice_index: int = 0) -> numpy.ndarray:
        """
        Returns the mean displacement of each image slice with respect to a reference slice. coordinates is a 3D array
        with one slice per image slice, and a 2D matrix per slice containing the X Y coordinates of the fiducials.
        Keep in mind that all slices must have the same number of fiducials (can use [-1 -1] pairs to pad the array).

        :param image:
        :param coordinates:
        :param reference_slice_index:
        :return:
        """
        if image is False or image is None or image.ndim < 3 or coordinates is False or coordinates is None:
            return numpy.empty((1, 0), None, None)

        d: numpy.ndarray = numpy.zeros((image.shape[0], 2))

        reference_fiducials = coordinates[reference_slice_index]

        n_fiducials_for_registration = sum(
            a_fiducial[0] != -1 for a_fiducial in reference_fiducials
        )


        for a_slice_index in range(image.shape[0]):
            target_fiducials = coordinates[a_slice_index]

            # If there are fiducials ...
            if target_fiducials[0, 0] > -1:
                d[a_slice_index, :] = numpy.round(numpy.mean(
                    reference_fiducials[0:n_fiducials_for_registration, :] - target_fiducials[
                                                                             0:n_fiducials_for_registration, :],
                    axis=0)).astype(int)

        return d

    @classmethod
    def register(cls, image: numpy.ndarray, coordinates: numpy.ndarray, reference_slice_index: int = 0,
                 method: RegistrationMethod = RegistrationMethod.CRUDE) -> (numpy.ndarray, numpy.ndarray):
        """
        Registers image slices to one reference slice using the coordinates of corresponding fiducials.
        coordinates is a 3D array with one slice per image slice, and a 2D matrix per slice containing
        the X Y coordinates of the fiducials. Keep in mind that all slices must have the same number of
        fiducials (can use [-1 -1] pairs to pad the array).

        Calls findshift_crude or findshift_piv.
        Calls shift_image.

        :param image:
        :param coordinates:
        :param reference_slice_index:
        :param method: one of rimutils.RegistrationMethod[CRUDE | PIV].
        :return:
        """
        if image is False or image is None or image.ndim < 3 or coordinates is False or coordinates is None:
            return numpy.empty((1, 0), None, None)

        registered_image = numpy.ndarray(image.shape)

        if method == cls.RegistrationMethod.CRUDE:
            d = cls.findshift_crude(image, coordinates, reference_slice_index)

            for slice_index, a_slice in enumerate(image):
                registered_image[slice_index] = cls.shift_image(a_slice, d[slice_index])

        elif method in [cls.RegistrationMethod.PIV, cls.RegistrationMethod.FLOW]:
            print("Registration method not implemented yet.")
            registered_image = image.copy()

        return registered_image.astype(image.dtype), d

    @classmethod
    def register_piv(cls, image: numpy.ndarray, coordinates: numpy.ndarray,
                     reference_slice_index: int = 0) -> numpy.ndarray:
        pass

    @classmethod
    def register_flow(cls, image: numpy.ndarray, coordinates: numpy.ndarray,
                     reference_slice_index: int = 0) -> numpy.ndarray:
        pass

    @classmethod
    def kymograph(cls, image: numpy.ndarray, coordinates: numpy.ndarray) -> numpy.ndarray:
        minx, maxx = coordinates[:, 0]
        miny, maxy = coordinates[:, 1]

        minx, miny, maxx, maxy = numpy.int(minx), numpy.int(miny), numpy.int(maxx), numpy.int(maxy)

        cropped_image: numpy.ndarray = image[:, miny:(maxy + 1), minx:(maxx + 1)].copy()

        return numpy.hstack(cropped_image)

    @classmethod
    def mode(cls, image: numpy.ndarray) -> int:
        imhist: numpy.ndarray = numpy.histogram(image, numpy.arange(numpy.max(image) + 2))
        return imhist[1][numpy.argmax(imhist[0])]

    @classmethod
    def qimage2ndarray(cls, theqimage) -> numpy.ndarray:
        # Convert the image to a known format.
        theqimage = theqimage.convertToFormat(QtGui.QImage.Format_RGB32)

        width = theqimage.width()
        height = theqimage.height()

        # Get a pointer to the beginning of the image and copy the data into a numpy array.
        ptr = theqimage.constBits()
        ptr.setsize(theqimage.byteCount())
        thendarray: numpy.ndarray = numpy.array(ptr).reshape(height, width, 4)  # Copies the data

        return thendarray

    @classmethod
    def histogram_figure(cls, image: numpy.ndarray, display: bool = True) -> Figure:
        f = plt.figure()
        plt.hist(image.flatten(), bins='auto', range=(0, image.max()), density=True, facecolor='green')  # arguments are passed to numpy.histogram

        if display:
            plt.show()

        return f

    @classmethod
    def distance_transform_gradient_weighted(cls, im: numpy.ndarray, window_size: int = FINDSEEDS_DEFAULT_WINSIZE, binary_dilation_radius: int = 0, sigma: float = GRADMAG_DEFAULT_SIGMA) -> (numpy.ndarray, numpy.ndarray):
        if im is None or im is False:
            return numpy.empty((0))

        _, thresholded_im, thresholded_im_final = cls.local_threshold(im, window_size, binary_dilation_radius)

        # Calculate distance transform.
        distance_im = ndimage.distance_transform_edt(thresholded_im_final)

        # Calculate gradient image.
        gradient_im = ndimage.gaussian_gradient_magnitude(im, sigma)

        grad_min = gradient_im.min()
        grad_max = gradient_im.max()

        weighted_distance_im = distance_im * numpy.exp(1. - (gradient_im-grad_min) / (grad_max-grad_min))

        return weighted_distance_im, thresholded_im

    @classmethod
    def mask_from_polylines(cls, imsize: Tuple[int, int], polylines: List, brushsz: int = 3) -> numpy.ndarray:
        mask_image = numpy.zeros(imsize, dtype=bool)

        for apoly in polylines:
            # Create a polyline and measure it:
            thepolyline = pjsannpol.RPolyline(apoly)
            _, inside_mask = thepolyline.tomask(imsize, brushsz)
            mask_image[inside_mask[::, 0], inside_mask[::, 1]] = True

        return mask_image

    @classmethod
    def active_contour(cls, an_image: numpy.ndarray, init_ls: numpy.ndarray, balloon_force: float) -> numpy.ndarray:
        if an_image is None or an_image is False:
            return numpy.empty((0))

        return morphological_geodesic_active_contour(an_image, cls.BALLOON_ITERS,
                                                     init_level_set=init_ls, smoothing=1,
                                                     balloon=balloon_force)

    @classmethod
    def gaussian_smoothing(cls, image_array: numpy.ndarray, a_sigma: float = 0.0) -> numpy.ndarray:
        if image_array is None or image_array is False or a_sigma is None or a_sigma is False or a_sigma < 0.0:
            return numpy.empty((0))

        return numpy.asarray(
            [gaussian(a_slice, sigma=a_sigma, preserve_range=True) for a_slice in image_array],
            dtype=numpy.uint16)

    @classmethod
    def rescale(cls, image_array: numpy.ndarray, scale_factor: Tuple[float, float] = (1.0, 1.0)) -> numpy.ndarray:
        if image_array is None or image_array is False or \
                scale_factor is None or scale_factor is False or len(scale_factor) != 2:
            return numpy.empty((0))

        return numpy.asarray(rescale(image_array, (1.,) + scale_factor, anti_aliasing=False, preserve_range=True),
                             dtype=numpy.uint16)
