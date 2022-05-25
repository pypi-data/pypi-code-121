from tifffile import TiffFile, imread, imsave
import numpy as np
import json
import os

import matplotlib.pyplot as plt
import warnings
from tqdm import tqdm
import pandas as pd
import PyPDF2


def extract_windows(array, window_size):
    """
    breaks ND array into windows along 0 dimention, starting from the begining and till the end.
    """
    start = 0
    num_windows = array.shape[0] - window_size + 1

    sub_windows = (
            start +
            np.expand_dims(np.arange(window_size), 0) +
            np.expand_dims(np.arange(num_windows), 0).T
    )
    return array[sub_windows]


def sort_by_len0(zip_to_sort):
    """
    Sorts the zip based on the length and alphabet of the first element in zip_to_sort
    """
    # sorts a list based on the length of the first element in zip
    sorted_zip = sorted(zip_to_sort, key=lambda x: (len(x[0])), reverse=True)
    return sorted_zip

def get_dff(array, window_size):
    """
    subtracts average baseline from an ND array along the 0 dimention.
    window_size must be an odd number.

    The baseline for the first and the last window//2 elements is the same :
    the first or the last value calculated with the full window
    """
    percentile = 8  # 8th percentile
    mean_signal = np.percentile(extract_windows(array, window_size), percentile, axis=1)
    # construct the baseline
    start = window_size // 2
    end = len(array) - window_size // 2
    # add the beginning and end to baseline
    baseline = np.zeros(array.shape)
    baseline[0:start] = mean_signal[0]
    baseline[start:end] = mean_signal
    baseline[end:] = mean_signal[-1]

    return (array - baseline) / baseline, start, end


def get_t_score(movie1, movie2, absolute=False):
    """
    Returns absolute t-score image ( 2D or 3D, depending on input),
    for t-score calculations see for example :
    https://www.jmp.com/en_us/statistics-knowledge-portal/t-test/two-sample-t-test.html
    """
    # TODO : check input dimensions

    avg1 = np.mean(movie1, axis=0)
    avg2 = np.mean(movie2, axis=0)

    var1 = np.var(movie1, axis=0)
    var2 = np.var(movie2, axis=0)
    n1 = movie1.shape[0]
    n2 = movie2.shape[0]

    std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if absolute:
        t_score = np.absolute(avg1 - avg2) / std
    else:
        t_score = (avg1 - avg2) / std

    return t_score


def get_diff(movie1, movie2, absolute=False):
    """
    Returns absolute difference image ( 2D or 3D, depending on input).
    per pixel: calculates the mean image for each movie, subtracts and takes the absolute value.
    """
    # TODO : check input dimensions

    avg1 = np.mean(movie1, axis=0)
    avg2 = np.mean(movie2, axis=0)

    if absolute:
        diff = np.absolute(avg1 - avg2)
    else:
        diff = (avg1 - avg2)

    return diff


def plot_errorbar(ax, mean, e, x=None, color = 'r'):
    if x is None:
        x = np.arange(len(mean))
    ax.errorbar(x, mean, yerr=e, fmt='o', color = color)
    ax.plot(x, mean, color = color)


def get_ax_limits(cycled, mean, e, plot_individual):
    """
    Figures out the tight x and y axis limits
    """
    if plot_individual:
        ymin = np.min(cycled)
        ymax = np.max(cycled)
    else:
        ymin = np.min(mean - e[1, :])
        ymax = np.max(mean + e[0, :])
    xmin = -0.5
    xmax = cycled.shape[1] - 0.5

    return xmin, xmax, ymin, ymax

def merge_pdfs(pdfs, filename):
    """
    Turns a bunch of separate figures (pdfs) into one prf.
    """
    mergeFile = PyPDF2.PdfFileMerger()
    for pdf in pdfs:
        mergeFile.append(PyPDF2.PdfFileReader(pdf, 'rb'))
        os.remove(pdf)
    mergeFile.write(filename)