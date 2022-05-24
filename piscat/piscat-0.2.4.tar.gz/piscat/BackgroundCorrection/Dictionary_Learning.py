"""
__author__ = "Houman Mirzaalian D."

https://github.com/mukheshpugal/dictlearn_gpu
"""
from __future__ import print_function

import matplotlib.pyplot as plt

from piscat.InputOutput.cpu_configurations import CPUConfigurations
from piscat.Preproccessing.patch_genrator import ImagePatching

from tqdm.autonotebook import tqdm
from sklearn.decomposition import MiniBatchDictionaryLearning, DictionaryLearning
from dictlearn_gpu import train_dict
from dictlearn_gpu.utils import dct_dict_1d
from dictlearn_gpu import OmpBatch

import numpy as np
import warnings
warnings.filterwarnings('ignore')


class DictionaryLearning_():

    def __init__(self, video, n_comp=100, n_iter=1, non_zero_coeff=10, alpha=0.3, batch_size=3, transform_algorithm='omp',
                 random_select=None, flag_MiniBatchDictionaryLearning=True):
        self.cpu = CPUConfigurations()
        self.tqdm_disable = True
        self.flag_MiniBatchDictionaryLearning = flag_MiniBatchDictionaryLearning

        self.n_comp = n_comp
        self.n_iter = n_iter
        self.non_zero_coeff = non_zero_coeff
        self.alpha = alpha
        self.original_video = video.astype(np.float64)
        self.video_shape = video.shape
        self.batch_size = batch_size
        self.random_select = random_select
        self.transform_algorithm = transform_algorithm
        self.reconstruction_background = None
        self.diff_video = None
        self.patch = None
        self.patch_gen = None
        self.depth, self.width, self.height = None, None, None
        self.depth_overlap, self.width_overlap, self.height_overlap = None, None, None

    def patch_genrator(self, patch_size=16, strides=4):
        self.patch_gen = ImagePatching()
        self.patch = self.patch_gen.split_weight_matrix(self.original_video, patch_size=patch_size, strides=strides)

    def noisy_patches(self, image):
        image = image.astype(np.float64)
        data = image.reshape(image.shape[0], -1)
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        data -= mean
        data = np.divide(data, std, np.zeros_like(data), where=std != 0)
        return (data, mean, std)

    def ksvd(self, noisy_data):
        if self.flag_MiniBatchDictionaryLearning:
            dic_ = MiniBatchDictionaryLearning(n_components=self.n_comp, alpha=self.alpha, n_iter=self.n_iter,
                                               n_jobs=self.cpu.n_jobs, batch_size=self.batch_size, transform_algorithm=self.transform_algorithm,
                                               transform_n_nonzero_coefs=self.non_zero_coeff)
            dic_.fit(noisy_data)
            return dic_.components_, dic_
        else:
            dic_ = DictionaryLearning(n_components=self.n_comp, alpha=self.alpha, max_iter=self.n_iter, n_jobs=self.cpu.n_jobs)

            dic_.fit(noisy_data)
            return dic_.components_, dic_.error_, dic_

    def ksvd_gpu(self, noisy_data):
        dictionary = dct_dict_1d(n_atoms=self.n_comp, size=noisy_data.shape[0])
        ob = OmpBatch(n_atoms=self.n_comp, sparsity_target=self.non_zero_coeff, batch_size=noisy_data.shape[1])
        decomp = ob.omp_batch(a_0=dictionary.T @ noisy_data, gram=dictionary.T @ dictionary)
        new_dictionary, errors, iters = train_dict(noisy_data, dictionary, sparsity_target=self.non_zero_coeff)
        return new_dictionary, errors, decomp

    def ksvd_kernel(self, i_, dc_correction=False):
        video_patch = self.patch[i_]
        if dc_correction:
            print("---apply dc correction---")
            video_patch = np.divide(video_patch, np.mean(video_patch))

        data_ = video_patch.reshape(video_patch.shape[0], -1)
        if self.random_select is not None:
            num_row = int(self.random_select * data_.shape[0])
            list_selected_idx = np.unique(np.random.randint(0, data_.shape[0], num_row))
            data_selected = data_[list_selected_idx, :]
        if self.flag_MiniBatchDictionaryLearning:
            dict_final, dic = self.ksvd(data_selected)
            code = dic.transform(data_)
            bg_patch_ = np.dot(code, dict_final)
            bg_patch = (bg_patch_.reshape(code.shape[0], video_patch.shape[1], video_patch.shape[2]))
            return bg_patch
        else:
            dict_final, error_iter, dic = self.ksvd(data_selected)
            code = dic.transform(data_)
            bg_patch_ = np.dot(code, dict_final)
            bg_patch = (bg_patch_.reshape(code.shape[0], video_patch.shape[1], video_patch.shape[2]))
            return [bg_patch, error_iter]

    def ksvd_denoising_gpu(self):
        print("\n---apply KSVD on GPU!---")

        if self.patch is not None:
            exp_index_list = []
            pad_non_zero = []
            for i_ in tqdm(range(len(self.patch))):
                video_patch = self.patch[i_]
                data_ = video_patch.reshape(video_patch.shape[0], -1)

                if i_ == 0:
                    big_patch = data_
                else:
                    if data_.shape[1] == big_patch.shape[1]:
                        big_patch = np.concatenate((big_patch, data_), axis=0)
                    else:
                        exp_index_list.append(i_)
                        non_zero = big_patch.shape[1] - data_.shape[1]
                        pad_non_zero.append(non_zero)
                        pad_ = np.zeros((data_.shape[0], non_zero))
                        data_pad = np.concatenate((data_, pad_), axis=1)
                        big_patch = np.concatenate((big_patch, data_pad), axis=0)

            dict_final, dic, decomp = self.ksvd_gpu(big_patch)
            bg_patch_ = dict_final.dot(decomp)

            bg_patch_split = np.split(bg_patch_, len(self.patch), axis=0)

            for pad_, index in zip(pad_non_zero, exp_index_list):
                bg_patch_split[index] = bg_patch_split[index][:, :-pad_]

            cor_patch = []
            for i_, p_ in enumerate(bg_patch_split):
                video_patch = self.patch[i_]
                bg_patch = (p_.reshape(p_.shape[0], video_patch.shape[1], video_patch.shape[2]))
                cor_patch.append(bg_patch)

            self.reconstruction_background = self.patch_gen.reconstruction_weight_matrix(self.video_shape,
                                                                                         new_patch=cor_patch)

            self.diff_video = np.divide(self.original_video, self.reconstruction_background) - 1

            return self.diff_video, self.reconstruction_background

        else:
            print("Patch video is not define!!")

    def ksvd_denoising_cpu(self):
        print("\n---apply KSVD on CPU_new!---")

        if self.patch is not None:
            exp_index_list = []
            pad_non_zero = []
            for i_ in tqdm(range(len(self.patch))):
                video_patch = self.patch[i_]
                data_ = video_patch.reshape(video_patch.shape[0], -1)

                if i_ == 0:
                    big_patch = data_
                else:
                    if data_.shape[1] == big_patch.shape[1]:
                        big_patch = np.concatenate((big_patch, data_), axis=0)
                    else:
                        exp_index_list.append(i_)
                        non_zero = big_patch.shape[1] - data_.shape[1]
                        pad_non_zero.append(non_zero)
                        pad_ = np.zeros((data_.shape[0], non_zero))
                        data_pad = np.concatenate((data_, pad_), axis=1)
                        big_patch = np.concatenate((big_patch, data_pad), axis=0)

            num_row = int(self.random_select * big_patch.shape[0])
            list_selected_idx = np.unique(np.random.randint(0, big_patch.shape[0], num_row))
            data_selected = big_patch[list_selected_idx, :]

            dict_final, dic = self.ksvd(data_selected)
            code = dic.transform(big_patch)
            bg_patch_ = np.dot(code, dict_final)
            # bg_patch = (bg_patch_.reshape(code.shape[0], video_patch.shape[1], video_patch.shape[2]))
            bg_patch_split = np.split(bg_patch_, len(self.patch), axis=0)

            for pad_, index in zip(pad_non_zero, exp_index_list):
                bg_patch_split[index] = bg_patch_split[index][:, :-pad_]

            cor_patch = []
            for i_, p_ in enumerate(bg_patch_split):
                video_patch = self.patch[i_]
                bg_patch = (p_.reshape(p_.shape[0], video_patch.shape[1], video_patch.shape[2]))
                cor_patch.append(bg_patch)

            self.reconstruction_background = self.patch_gen.reconstruction_weight_matrix(self.video_shape,
                                                                                         new_patch=cor_patch)

            self.diff_video = np.divide(self.original_video, self.reconstruction_background) - 1

            return self.diff_video, self.reconstruction_background

        else:
            print("Patch video is not define!!")


    def ksvd_denoising_cpu_(self):
        print("\n---apply KSVD on CPU!---")

        if self.patch is not None:
            bg_patches = [self.ksvd_kernel(x) for x in tqdm(range(len(self.patch)))]

            if self.flag_MiniBatchDictionaryLearning:
                pass
            else:
                temp_ = np.asarray(bg_patches)
                bg_patches = temp_[:, 0]
                error_patchs = temp_[:, 1]
            self.reconstruction_background = self.patch_gen.reconstruction_weight_matrix(self.video_shape,
                                                                                         new_patch=bg_patches)

            self.diff_video = np.divide(self.original_video, self.reconstruction_background) - 1

            return self.diff_video, self.reconstruction_background

        else:
            print("Patch video is not define!!")

    def ksvd_denoising_iter(self, n_iter_min, n_iter_max, stride, dc_correction=False):
        if self.flag_MiniBatchDictionaryLearning:
            mean_error = []
            std_error = []
            n_iter = list(range(n_iter_min, n_iter_max, stride))
            for n_i in tqdm(n_iter, disable=False):
                self.n_iter = n_i
                self.tqdm_disable = True
                if self.patch is not None:
                    bg_patches = [self.ksvd_kernel(x) for x in tqdm(range(len(self.patch)), disable=self.tqdm_disable)]
                    self.reconstruction_background = self.patch_gen.reconstruction_weight_matrix(self.video_shape,new_patch=bg_patches)

                    self.diff_video = np.divide(self.original_video, self.reconstruction_background) - 1

                    diff_ = np.abs(self.original_video - self.reconstruction_background)
                    mean_error.append(np.mean(diff_))
                    std_error.append(np.std(diff_))
                    return self.diff_video, self.reconstruction_background, mean_error, std_error
                else:
                    print("Patch video is not define!!")
        else:
            if self.patch is not None:
                self.n_iter = n_iter_max
                results = [self.ksvd_kernel(x, dc_correction) for x in tqdm(range(len(self.patch)), disable=False)]
                temp_ = np.asarray(results)
                bg_patches = temp_[:, 0]
                error_patchs = temp_[:, 1]
                self.reconstruction_background = self.patch_gen.reconstruction_weight_matrix(self.video_shape, new_patch=bg_patches.tolist())

                self.diff_video = np.divide(self.original_video, self.reconstruction_background) - 1

                return self.diff_video, self.reconstruction_background, error_patchs, None
            else:
                print("Patch video is not define!!")








