import numpy as np
from astropy.convolution import Gaussian2DKernel, convolve


def smooth(array, num=7, method='mean', wrap=False):
    """
    :param array: Numpy array of numbers
    :param num: Smoothing full-width (should be odd). The smoothing window is
        [i-num/2, i + num/2].
    :param method: 'mean' or 'median'. Default = 'mean'
    :param wrap: If True, the smoothing window will treat the function as cyclical.
        If False (default), the smoothing window cuts off at the edges. For the
        first point, the smoothing window is [0, num/2]
    :return: Smoothed array
    """
    methods = {'mean': np.mean, 'median': np.median}
    func = methods.get(method, None)
    if isinstance(array, np.ndarray) and (func is not None):
        new_array = np.zeros_like(array)
        wid = int(num)//2
        for i in range(array.shape[0]):
            inds = np.linspace(i-wid, i+wid, wid*2+1, dtype=int)
            inds[inds >= len(array)] = inds[inds >= len(array)] - len(array)
            if not wrap:
                inds = inds[(inds >= 0) & (inds < len(array))]
            new_array[i] = func(array[inds])
            
        return new_array
    else:
        raise TypeError


def smooth2d(array, num=1, method='gaussian', wrap=False):
    if method.casefold() == 'gaussian':
        kernel = Gaussian2DKernel(x_stddev=num)
        boundary = 'wrap' if wrap else 'extend'
        smoothed = convolve(array, kernel, boundary=boundary)
    else:
        raise TypeError
    
    return smoothed


# def smooth_sphere(array, longitude, latitude, dphi=np.deg2rad(5), method='mean'):
#     dlon, dlat = (longitude[1] - longitude[0]) / 2, (latitude[1] - latitude[0]) / 2
#     longitude_, latitude_ = np.meshgrid(longitude[:-1] + dlon,
#                                         latitude[:-1] + dlat)
#
#     ptsx = (np.cos(longitude_) * np.cos(latitude_)).flatten()
#     ptsy = (np.sin(longitude_) * np.cos(latitude_)).flatten()
#     ptsz = np.sin(latitude_).flatten()
#     array_ = array.flatten()
#     result = np.zeros_like(array_)
#
#     methods = {'mean': np.mean, 'median': np.median}
#     func = methods.get(method, None)
#     if isinstance(array, np.ndarray) and (func is not None):
#         for i, X in enumerate(zip(ptsx, ptsy, ptsz)):
#             # Compute angle between (x, y, z) and each point in the grid
#             AdotB = ptsx * X[0] + ptsy * X[1] + ptsz * X[2]
#             AdotB[AdotB > 1] = 1
#             AdotB[AdotB < -1] = -1
#             phi = np.arccos(AdotB)
#             use = phi < dphi
#             result[i] = func(array_[use])
#     else:
#         raise TypeError
#
#     return result.reshape(array.shape)
