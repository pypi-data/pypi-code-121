#!/usr/bin/env python3

'''Skript to check if the annotations output from two folders are the same (e.g. from  a validation and a detection
run.'''

import os
import re

from bioblu.ds_manage import ds_annotations
from bioblu.ds_manage.ds_annotations import get_annotation_from_line


def find_shortest_list_len(list_1: list, list_2: list):
    return min([len(list_1), len(list_2)])


def compare_annotations(fpath_1: str, fpath_2: str):
    files_1 = sorted(os.listdir(fpath_1))
    files_2 = sorted(os.listdir(fpath_2))
    assert len(files_1) == len(files_2)  # Same number of files
    assert set(files_1) == set(files_2)  # Same file names


if __name__ == '__main__':
    FPATH_DET = '/media/findux/DATA/Documents/Malta_II/datasets/dataset_01_paradise_bay/results/box_comparison/det/labels/'
    FPATH_VAL = '/media/findux/DATA/Documents/Malta_II/datasets/dataset_01_paradise_bay/results/box_comparison/val/labels/'
    # compare_annotations(FPATH_VAL, FPATH_DET)

    test_line = '0 0.0485197 0.792603 0.0257675 0.030137 0.781923\n'
    print(get_annotation_from_line(test_line))