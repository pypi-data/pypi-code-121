import numpy as np
import cv2
from skimage.segmentation import find_boundaries
from scipy import ndimage

def additive_blend(im0, im1):

    im0 = np.array(im0)
    im0 = im0/np.percentile(im0, 99)
    im0 = np.clip(im0, 0, 1)

    im1 = np.array(im1)
    im1 = im1/np.percentile(im1, 99)
    im1 = np.clip(im1, 0, 1)

    rgb = np.zeros((*im0.shape, 3))
    rgb[:, :, 0] = im0
    rgb[:, :, 1] = im1

    return rgb


def _rmlead(inp, char='0'):
    for idx, letter in enumerate(inp):
        if letter != char:
            return inp[idx:]


def plot_segmentation(nuc, segmentation):

    rgb_data = cv2.cvtColor(nuc, cv2.COLOR_GRAY2RGB)
    boundaries = np.zeros_like(nuc)
    overlay_data = np.copy(rgb_data)

    boundary = find_boundaries(segmentation, connectivity=0, mode='outer')
    boundaries[boundary > 0] = 1
    boundaries = cv2.dilate(boundaries, np.ones((2,2)))

    overlay_data[boundaries > 0] = (255,0,0)
    return overlay_data

def gaussian_kernel(sz: int, sigx: float, sigy: float, deg: float, normalize=True) -> np.ndarray:
    X, Y = np.meshgrid(np.linspace(-1,1,sz), np.linspace(-1,1,sz))
    GX = 1/(sigx*np.sqrt(2*np.pi))*np.exp(-1/2*(X/sigx)**2)
    GY = 1/(sigy*np.sqrt(2*np.pi))*np.exp(-1/2*(Y/sigy)**2)
    GK = GX*GY
    rGK = ndimage.rotate(GK, deg, reshape=False)
    if normalize:
        rGK /= rGK.sum()
    else:
        rGK /= rGK.max()
    return rGK


def LoG_kernel(sz: int, sig: float):

    X, Y = np.meshgrid(np.linspace(-4,4,sz), np.linspace(-4,4,sz))
    X2_plus_Y2 = X**2 + Y**2
    LoG = (-1)/(np.pi*sig**4)*(1-(X2_plus_Y2/(2*sig**2)))*np.exp(-X2_plus_Y2/(2*sig**2))
    LoG = LoG/abs(LoG.min())
    return LoG

from functools import wraps
from time import time
def timeit(func):
    @wraps(func)
    def wrap(*args, **kw):
        ts = time()
        result = func(*args, **kw)
        te = time()
        print(f'Function {func.__name__!r} executed in {(te-ts):.10f}s')
        return result
    return wrap