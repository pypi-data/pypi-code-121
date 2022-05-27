from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import logging
import numpy as np
from numpy.random import RandomState 
import torch
from scipy.ndimage import gaussian_filter


def get_rand_seed(tag):
    if tag:
        tim = datetime.datetime.now()
        randseed = tim.hour*10000+tim.minute*100+tim.second+tim.microsecond
        return RandomState(randseed) 
    else:
        return RandomState(11723555)


def smooth_maps(kappa, args):
    if args.engine.signalModel == 'looklocker':
        sigma = [0.4, 0.0, 0.4]
    if args.engine.signalModel == 'fse':
        sigma = [0.4, 0.4]
    kappaSmooth = []
    for i, k_patch in enumerate(kappa):
        kappaSmooth.append([gaussian_filter(k, sigma[i], 0) for k in k_patch]) 
    kappaSmooth = np.moveaxis(np.stack(kappaSmooth), 1, 0)
    return np.stack(kappaSmooth)


def apply_gt_noise(kappa, pngr, args):
    #TODO noise should be proportional per tissue.
    if args.engine.signalModel == 'looklocker':
        k = [0.05, 0.0, 0.1]
        # k = [0.0, 0.0, 0.0]
    if args.engine.signalModel == 'fse':
        k = [0.05, 0.01]
    noisyKappa = []
    for i, kmap in enumerate(kappa):
        patch_kappa = []
        for patch in kmap:
            if not args.dataset.useRandomSeed:
                pngr = get_rand_seed(args.dataset.useRandomSeed)
            noise_map = pngr.normal(0, k[i], np.shape(kmap[0]))
            patch_kappa.append(patch + noise_map)
        noisyKappa.append(patch_kappa)
    return np.stack(noisyKappa)


def add_artefacts(kappa):
    kappa[:,-1, 136,93:99] = 1.2
    kappa[:,-1, 126:132,92] = 1.2
    kappa[:,-1, 130, 84] = 1.2
    kappa[:,-1, 137, 84] = 0.4
    return kappa


class ExtractPatch(object):
    def __init__(self, args):
        self.args = args

    def get_patch(self, data):
        mask = data > 1
        patch_coordinates = self.__getCoordinates__(mask, self.args.dataset.patchSize, self.args.engine.batchSize, self.args.dataset.pngr, self.args.dataset.useRandomSeed)
        patch_data = self.__extractPatch__(patch_coordinates, data)
        return patch_data

    def __find__(self, target, myList, pngr, use_random_seed):
        for _ in range(len(myList)):
            r = pngr.randint(1, int(len(myList)), 1)
            if myList[r] == target and use_random_seed:
                yield r
            elif not use_random_seed:
                yield [int(len(myList)/3)]

    def __getCoordinates__(self, mask_data, patch_size, number_of_patches, pngr, use_random_seed):
        init_patch_coord = []
        end_patch_coord = []
        mask_index_find = self.__find__(1, mask_data.ravel(), pngr, use_random_seed)
        for _ in range(number_of_patches):
            indx = np.unravel_index(next(mask_index_find), mask_data.shape)
            for coord in range(3):
                if indx[coord][0] < patch_size:
                    diff = (patch_size - indx[coord][0]) + 1
                    indx[coord][0] = indx[coord][0] + diff
                if indx[coord][0] > (np.shape(mask_data)[coord]-patch_size):
                    diff = (indx[coord][0] - np.shape(mask_data)[coord] + patch_size) + 1
                    indx[coord][0] = indx[coord][0] - diff
            random_mask_coord_init = [coord - patch_size for coord in indx]
            random_mask_coord_end = [coord + patch_size for coord in random_mask_coord_init]
            init_patch_coord.append(random_mask_coord_init)
            end_patch_coord.append(random_mask_coord_end)
        return init_patch_coord, end_patch_coord

    def __extractPatch__(self, coord_patches, data):
        initial_coord = coord_patches[0]
        end_coord = coord_patches[1]
        all_patches = []
        for c in range(len(initial_coord)):
            patch = data[initial_coord[c][0][0]:end_coord[c][0][0], initial_coord[c][1][0]:end_coord[c][1][0], initial_coord[c][2][0]:end_coord[c][2][0]]
            all_patches.append(patch)
        return np.stack(all_patches)

