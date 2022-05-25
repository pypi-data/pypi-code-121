# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from scipy import interpolate


def check_diff(diff, thresh):
    return np.any(diff[np.isfinite(diff)] > thresh)


class Tables(object):
    """
    This class has been written to handle operations involving building tabulated data.
    For some of the calculations this is often useful. These tables can then be accessed
    through interpolation routines rather than doing the full calculations repeatedly.
    """

    def __init__(self):

        pass

    # TODO: Tables -> Think about where to set the limits
    def interp_grid(self, func, params):
        """
        Determines the gridpoints used for creating a tabulated version of
        a function.
        :param func: function to determine the grid for
        :param params: parameters defining the limits, accuracy and method for the
                       generation of the interpolation grid (set through the respective
                       enrich_params)
        :return truth: true function values at the gridpoints
        :return x, y: gridpoints
        :return diff: difference between interpolated and true values at the means of
                      gridpoints
        :return x_fine, y_fine: fine grid used to determine the interpolation error for
                                x, y
        """

        dim = params["calc"]["dim"]

        if dim == 1:
            pass
        elif dim == 1.5:
            truth, x, y, diff, x_fine, y_fine = self.get_grid_15d(func, params)
        elif dim == 2:
            truth, x, y, diff, x_fine, y_fine = self.get_grid_2d(func, params)

        return truth, x, y, diff, x_fine, y_fine

    def get_grid_15d(self, func, params):
        """
        Determines the interpolation grid for a 1.5D interpolation i.e. for a 2D
        function.
        We fix a grid in one variable and interpolate in the other. If adaptive is true,
        it refines the grid until the interpolation error is below the tolerance. If
        adaptive is false, then the input grid is returned
        together with an estimate of the interpolation error for this grid.
        :param func: function to determine the grid for
        :param params: parameters defining the limits, accuracy and method for the
                       generation of the interpolation grid (set through the respective
                       enrich_params)
        :return truth: true function values at the gridpoints
        :return x, y: gridpoints
        :return diff: difference between interpolated and true values at the means of
                      gridpoints
        :return x_fine, y_fine: fine grid used to determine the interpolation error for
                                x, y
        """

        x_coarse = np.logspace(
            params["limits"]["xmin"], params["limits"]["xmax"], params["calc"]["nx"]
        )
        gridtype = params["calc"]["gridtype"]
        if gridtype == "log":
            y_coarse = np.logspace(
                params["limits"]["ymin"], params["limits"]["ymax"], params["calc"]["ny"]
            )
        else:
            y_coarse = np.linspace(
                params["limits"]["ymin"], params["limits"]["ymax"], params["calc"]["ny"]
            )

        diff, truth, x, y, x_fine, y_fine = self.interp_error_15d(
            func, gridtype, x_coarse, y_coarse
        )

        if params["calc"]["adaptive"]:
            pass
        else:
            if check_diff(diff, 1e-5):
                print(
                    "Interpolation failed to reach relative accuracy of 10^-5. "
                    "Try choosing a finer interpolation grid."
                )
                print("Maximal relative error: ", np.amax(diff))

        return truth, x, y, diff, x_fine, y_fine

    def get_grid_2d(self, func, params):
        """
        Determines the interpolation grid for a 2D interpolation. If adaptive is true,
        it refines the grid until the interpolation error is below the tolerance. If
        adaptive is false, then the input grid is returned together with an estimate of
        the interpolation error for this grid.
        :param func: function to determine the grid for
        :param params: parameters defining the limits, accuracy and method for the
                       generation of the interpolation grid (set through the respective
                       enrich_params)
        :return truth: true function values at the gridpoints
        :return x, y: gridpoints
        :return diff: difference between interpolated and true values at the means of
                      gridpoints
        :return x_fine, y_fine: fine grid used to determine the interpolation error for
                                x, y
        """

        x_coarse = np.logspace(
            params["limits"]["xmin"], params["limits"]["xmax"], params["calc"]["nx"]
        )
        gridtype = params["calc"]["gridtype"]
        tol = params["calc"]["tol"]

        if gridtype == "log":
            y_coarse = np.logspace(
                params["limits"]["ymin"], params["limits"]["ymax"], params["calc"]["ny"]
            )
        else:
            y_coarse = np.linspace(
                params["limits"]["ymin"], params["limits"]["ymax"], params["calc"]["ny"]
            )

        diff, truth, x, y, x_fine, y_fine = self.interp_error(
            func, gridtype, x_coarse, y_coarse
        )

        if params["calc"]["adaptive"]:
            while check_diff(diff, tol):
                # y_ind, x_ind = np.where(diff>tol)
                # Only refine in x where the error is really due to x
                reldiff_subx = diff / np.mean(diff, axis=1)[:, np.newaxis]
                # reldiff_suby = diff/np.mean(diff, axis=0)[np.newaxis,:]
                mask = (diff > tol) & (reldiff_subx >= 1.0)
                y_ind, x_ind = np.where(mask)
                x_ind.flags.writeable = True
                y_ind.flags.writeable = True
                xmask1 = x_ind % 2 == 0
                xmask2 = x_ind % 2 == 1
                ymask1 = y_ind % 2 == 0
                ymask2 = y_ind % 2 == 1
                x_ind[xmask1] = x_ind[xmask1] / 2.0
                x_ind[xmask2] = (x_ind[xmask2] - 1.0) / 2.0
                y_ind[ymask1] = y_ind[ymask1] / 2.0
                y_ind[ymask2] = (y_ind[ymask2] - 1.0) / 2.0
                # We need to round up (ceil) because insert always inserts the value
                # before the index
                x_ind = np.sort(
                    np.ceil(np.unique(np.hstack((x_ind - 0.5, x_ind + 0.5))))
                ).astype("int")
                mask = (x_ind > 0) * (x_ind < x.shape[0])
                x_ind = x_ind[mask]
                x = self.update_grid(x_ind, x, gridtype=gridtype)
                y_ind = np.sort(
                    np.ceil(np.unique(np.hstack((y_ind - 0.5, y_ind + 0.5))))
                ).astype("int")
                mask = (y_ind > 0) * (y_ind < y.shape[0])
                y_ind = y_ind[mask]
                y = self.update_grid(y_ind, y, gridtype=gridtype)
                diff, truth, x, y, x_fine, y_fine = self.interp_error(
                    func, gridtype, x, y
                )

        else:
            if check_diff(diff, 1e-5):
                print(
                    "Interpolation failed to reach relative accuracy of 10^-5. "
                    "Try choosing a finer interpolation grid."
                )
                print("Maximal relative error: ", np.amax(diff))

        return truth, x, y, diff, x_fine, y_fine

    def interp_error_15d(self, func, gridtype, x, y):
        """
        Calculates the interpolation error for interpolation at the midpoints of the
        grid where interpolation has been performed for interpolation in 1.5D.
        :param func: function to interpolate
        :param x: x grid on which to perform interpolation
        :param y: y grid on which to perform interpolation
        :return diff: relative difference between interpolation and exact value
        :param func_vals: true function values at the input grid
        :param x, y: input grid
        :param x_fine, y_fine: finer grid used to estimate the interpolation error
        """

        func_vals = func(x, y)
        x_means = self.grid_means(x, gridtype)
        x_fine = np.sort(np.hstack((x, x_means)))
        truth = func(x_fine, y)
        for i in range(y.shape[0]):
            if i == 0:
                interp_vals = np.interp(x_fine, x, func_vals[i])
            else:
                interp_vals = np.vstack(
                    (interp_vals, np.interp(x_fine, x, func_vals[i]))
                )
        diff = np.abs(interp_vals - truth) / truth

        return diff, func_vals, x, y, x_fine, y

    def interp_error(self, func, gridtype, x, y=None):
        """
        Calculates the interpolation error for interpolation at the
        midpoints of the grid where interpolation has been performed.
        This is designed to work for 1D and 2D interpolations.
        :param func: function to interpolate
        :param x: x grid on which to perform interpolation
        :param y: y grid on which to perform interpolation
        :return diff: relative difference between interpolation and exact value
        :param func_vals: true function values at the input grid
        :param x, y: input grid
        :param x_fine, y_fine: finer grid used to estimate the interpolation error
        """

        # TODO: This currently only works for 2D interpolations

        if y is None:
            pass
        else:
            func_vals = func(x, y)
            if gridtype == "log":
                interp_func = interpolate.RectBivariateSpline(
                    np.log10(y), np.log10(x), func_vals
                )
            else:
                interp_func = interpolate.RectBivariateSpline(y, np.log10(x), func_vals)

            x_means = self.grid_means(x, gridtype)[::2]
            y_means = self.grid_means(y, gridtype)[::2]

            if gridtype == "log":
                interp_vals = interp_func(np.log10(y_means), np.log10(x_means))
            else:
                interp_vals = interp_func(y_means, np.log10(x_means))
            truth = func(x_means, y_means)
            diff = np.abs(interp_vals - truth) / truth

            x_fine = np.sort(np.hstack((x, x_means)))
            y_fine = np.sort(np.hstack((y, y_means)))
            return diff, func_vals, x, y, x_fine, y_fine

    def update_grid(self, ind, grid, gridtype):
        """
        Refines an input grid at the positions given in ind, i.e. these are the grid
        points between which the interpolation error is too large.
        :param ind: input grid indices where the interpolation error exceeds the
                    tolerance
        :param grid: input grid (1D)
        :param gridtype: type of grid, i.e. lin or log
        :return grid: refined grid with added midpoint between all the points indicated
                      by ind
        """

        if gridtype == "log":
            grid = np.insert(
                grid, ind, 10 ** ((np.log10(grid[ind - 1]) + np.log10(grid[ind])) / 2.0)
            )
        else:
            grid = np.insert(grid, ind, (grid[ind - 1] + grid[ind]) / 2.0)

        return grid

    def grid_means(self, grid, gridtype):
        """
        Returns the midpoints of an input grid. This is used to determine the
        interpolation error on the refined grid.
        :param grid: input grid (1D)
        :param gridtype: type of grid, i.e. lin or log
        :return grid_means: means of the input grid
        """

        if gridtype == "log":
            grid_means = 10 ** ((np.log10(grid[:-1]) + np.log10(grid[1:])) / 2.0)
        else:
            grid_means = (grid[:-1] + grid[1:]) / 2.0

        return grid_means
