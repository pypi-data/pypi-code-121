"""
Copyright © 2022 Felix P. Kemeth

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the “Software”), to deal in the Software without
restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import pickle

import torch
import numpy as np

from sklearn.decomposition import TruncatedSVD


class Dataset(torch.utils.data.Dataset):
    """PyTorch dataset structure for PDE learning."""

    def __init__(self, start_idx, end_idx, config, path, verbose=False, include_0=False):
        # Load data
        self.save_dir = path+'/dat/'
        # Length of left and right part for which no dt information is available
        self.off_set = int((int(config["kernel_size"])-1)/2)
        self.use_fd_dt = config.getboolean("use_fd_dt")
        self.rescale_dx = float(config["rescale_dx"])
        self.use_param = config.getboolean("use_param")
        self.verbose = verbose
        self.include_0 = include_0
        self.x_data, self.delta_x, self.y_data, self.param = self.load_data(start_idx, end_idx)
        self.n_samples = self.x_data.shape[0]

        self.svd = TruncatedSVD(n_components=int(config["svd_modes"]), n_iter=42, random_state=42)
        # self.svd.fit(self.x_data.reshape(self.n_samples, -1))
        self.svd.fit(self.x_data[::10].reshape(int(self.n_samples/10), -1))

        print('SVD variance explained: '+str(self.svd.explained_variance_ratio_.sum()))

    def load_data(self, start_idx, end_idx):
        """ Load and prepare data."""
        x_data = []
        delta_x = []
        param = []
        for idx in range(start_idx, end_idx):
            if self.include_0:
                p_list = [0, -1, 1]
            else:
                p_list = [-1, 1]
            for p in p_list:
                pkl_file = open(self.save_dir+'/run'+str(idx) + '_p_'+str(p)+'.pkl', 'rb')
                data = pickle.load(pkl_file)
                pkl_file.close()
                x_data.append(data["data"])
                delta_x.append(np.repeat(data["L"]/data["N"], len(data["data"])))
                param.append(np.repeat(data["param"], len(data["data"])))

        # Delta t for temporal finite difference estimation
        self.delta_t = (data["tmax"]-data["tmin"])/data["T"]
        if self.verbose:
            print('Using delta_t of '+str(self.delta_t))

        # Prepare data
        y_data = []
        for idx, data_point in enumerate(x_data):
            if self.use_fd_dt:
                y_data.append((data_point[1:, self.off_set:-self.off_set] -
                               data_point[:-1, self.off_set:-self.off_set])/self.delta_t)
            # If fd is attached to model, remove off set. TODO do fd here.
            x_data[idx] = x_data[idx][:-1]
            delta_x[idx] = delta_x[idx][:-1]
            param[idx] = param[idx][:-1]

        x_data = np.stack((np.concatenate(x_data).real,
                           np.concatenate(x_data).imag), axis=-1)
        y_data = np.stack((np.concatenate(y_data).real,
                           np.concatenate(y_data).imag), axis=-1)
        delta_x = np.concatenate(delta_x, axis=0)*self.rescale_dx
        param = (np.concatenate(param, axis=0) - 1.75)/0.02
        return np.transpose(x_data, (0, 2, 1)), delta_x, np.transpose(y_data, (0, 2, 1)), param

    def get_data(self, split_boundaries=False):
        """Return prepared data."""
        if split_boundaries:
            left_bound = self.x_data[:, :, :self.off_set]
            right_bound = self.x_data[:, :, -self.off_set:]
            return left_bound, self.x_data[:, :, self.off_set:-self.off_set], right_bound, \
                self.delta_x, self.y_data, self.param
        return self.x_data, self.delta_x, self.y_data, self.param

    def __len__(self):
        return self.n_samples

    def __getitem__(self, index):
        _x = torch.tensor(self.x_data[index], dtype=torch.get_default_dtype())
        _dx = torch.tensor(self.delta_x[index], dtype=torch.get_default_dtype())
        _y = torch.tensor(self.y_data[index], dtype=torch.get_default_dtype())
        _p = torch.tensor(self.param[index], dtype=torch.get_default_dtype())
        return _x, _dx, _y, _p
