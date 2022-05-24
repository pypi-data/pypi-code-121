from __future__ import division, print_function, absolute_import
from .version import __version__


from .base import baseops, arrayops, mathops, randomfunc
from .base.baseops import dreplace, dmka
from .base.arrayops import sl, cut, cat, arraycomb
from .base.mathops import nextpow2, prevpow2, ebeo, r2c, c2r, conj, real, imag, abs, pow
from .base.randomfunc import setseed, randgrid, randperm, randperm2d


from .utils.const import *
from .utils.colors import rgb2gray, gray2rgb, DISTINCT_COLORS_HEX, DISTINCT_COLORS_RGB, DISTINCT_COLORS_CMYK, DISTINCT_COLORS_RGB_NORM, BASE_COLORS, TABLEAU_COLORS, CSS4_COLORS
from .utils.colormaps import cmaps, viridis, parula
from .utils.convert import str2list, str2num, str2sec
from .utils.ios import loadyaml, loadjson, loadmat, savemat, loadh5, saveh5, mvkeyh5
from .utils.image import imread, imsave, histeq, imresize
from .utils.file import listxfile, pathjoin, fileparts, readtxt, readnum, readcsv, readsec
from .utils.plot_show import cplot, plots, Plots
from .utils.typevalue import bin2int, peakvalue

from .summary.loss_log import LossLog

from .evaluation.contrast import contrast
from .evaluation.entropy import entropy
from .evaluation.norm import fnorm, pnorm
from .evaluation.error import mse, sse, mae, sae
from .evaluation.snr import snr, psnr
from .evaluation.detection_voc import bbox_iou, calc_detection_voc_ap, calc_detection_voc_prec_rec, eval_detection_voc

from .compression.huffman_coding import HuffmanCoding

from .dsp.ffts import padfft, freq, fftfreq, fftshift, ifftshift, fft, ifft, fftx, ffty, ifftx, iffty
from .dsp.convolution import conv1, cutfftconv1, fftconv1
from .dsp.correlation import corr1, cutfftcorr1, fftcorr1
from .dsp.normalsignals import rect, chirp
from .dsp.interpolation1d import sinc, sinc_table, sinc_interp, interp
from .dsp.interpolation2d import interp2d
from .dsp.function_base import unwrap, unwrap2

from .misc.transform import standardization, scale, quantization, ct2rt, rt2ct, db20
from .misc.mapping_operation import mapping
from .misc.sampling import slidegrid, dnsampling, sample_tensor, shuffle_tensor, split_tensor, tensor2patch, patch2tensor, read_samples
from .misc.bounding_box import plot_bbox, fmt_bbox
from .misc.draw_shapes import draw_rectangle
