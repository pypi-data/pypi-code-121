import numpy as np
from scipy.ndimage.measurements import label


def is_too_close_to_diagonal(row_start, column_start, row_end, column_end, resolution):
    return abs(row_start - column_start) < 2 * resolution and \
           abs(row_end - column_end) < 2 * resolution


def find_max_in_connected_components(prediction, chrom1, x0, y0, handler, resolution,
                                     ignore_on_diagonal: bool = False):
    labeled, n_components = label(prediction, np.ones((3, 3), dtype=np.int))
    for num in range(n_components):
        highlighted_region = (labeled == (num + 1)) * prediction
        max_prediction = np.max(highlighted_region)
        max_indices = np.where(highlighted_region == max_prediction)
        max_indices = [(x, y) for x, y in zip(max_indices[0], max_indices[1])]
        for maxIndex in max_indices:
            row_start = (x0 + maxIndex[0]) * resolution
            row_end = row_start + resolution
            column_start = (y0 + maxIndex[1]) * resolution
            column_end = column_start + resolution
            if ignore_on_diagonal and is_too_close_to_diagonal(row_start, column_start, row_end, column_end,
                                                               resolution):
                continue
            if row_start < column_start:
                handler.add_prediction(chrom1, chrom1, row_start, row_end, column_start, column_end, max_prediction)
            else:
                handler.add_prediction(chrom1, chrom1, column_start, column_end, row_start, row_end, max_prediction)


def find_bound_in_connected_components(prediction, chrom1, x0, y0, handler, resolution):
    labeled, n_components = label(prediction, np.ones((3, 3), dtype=np.int))
    for num in range(n_components):
        highlighted_region = (labeled == (num + 1)) * prediction
        max_prediction = np.max(highlighted_region)
        indices = np.where(highlighted_region > 0)
        row_start = int(x0 + np.min(indices[0])) * resolution
        row_end = max(int(x0 + np.max(indices[0])) * resolution, row_start + resolution)
        col_start = int(y0 + np.min(indices[1])) * resolution
        col_end = max(int(y0 + np.max(indices[1])) * resolution, col_start + resolution)
        if col_end - col_start > 10 * (row_end - row_start):
            handler.add_prediction(chrom1, chrom1, row_start, row_end, col_start, col_end, max_prediction)
