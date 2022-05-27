from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import h5py
import logging
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import numpy.ma as ma
import os
import pickle
import time
import torch
import torch.nn.functional as F


def saveDataPickle(data, save_results_path, filename):
    path = os.path.join(save_results_path, filename + '.pkl')
    logging.info("Writing file {}.pkl to {}".format(filename, save_results_path))
    with open(path, 'wb') as f:
        pickle.dump(data, f)


def saveItermediateResults(data, args, epoch):
    if not args.engine.saveResultsPath:
        logging.warning('Please specify path to save intermediary results - saveResultsPath')
    else:
        logging.info("Saving results to {}".format(args.engine.saveResultsPath))
        path = os.path.join(args.engine.saveResultsPath)
        save_hdf5(data, path, args, epoch)


def save_hdf5(data, path, args, epoch):
    tim = str(time.time())[:10]
    hf = h5py.File(os.path.join(path, args.engine.filename + "_epoch" + str(epoch) + ".h5"), 'w')
    data = data
    g = hf.create_group(args.engine.inferenceModel + args.engine.state_name)
    for key, value in data.items():
        g.create_dataset(key, data=value)

    hf.close()


def load_hdf5(path):
    hf = h5py.File(path, 'r', swmr=False)
    hf = hf.get('RIMtraining')
    dataset1 = hf.get('estimated')
    dataset2 = hf.get('labels')
    dataset3 = hf.get('mask')
    return dataset1, dataset2, dataset3


def pad(input_image, pad_size):
    padded_image = np.pad(input_image, pad_size, mode='constant')
    return padded_image


def unpad(input_image, padding_mask):

    [_, _, img_dim] = get_data_information(input_image)
    padding_mask_np = (padding_mask)

    if img_dim == 2:
        weighted_img_unpad = input_image[padding_mask_np[0]:-padding_mask_np[1],
                                         padding_mask_np[2]:-padding_mask_np[3]
                                        ]
    if img_dim == 3:
        weighted_img_unpad = input_image[padding_mask_np[0]:-padding_mask_np[1],
                                         padding_mask_np[2]:-padding_mask_np[3],
                                         padding_mask_np[4]:-padding_mask_np[5]
                                        ]

    return weighted_img_unpad


def get_data_information(weighted_image):

    if isinstance(weighted_image, torch.Tensor):
        img_shape = weighted_image.size()
        img_elem = weighted_image.numel()
        img_dim = len(weighted_image.size())
    else:
        img_shape = np.shape(weighted_image)
        img_elem = np.size(weighted_image)
        img_dim = len(np.shape(weighted_image))

    return [img_shape, img_elem, img_dim]


def convert_shape_to_pair(shape_matrix): 
    new_img_shape = np.array(shape_matrix)
    dimension_index = 0
    for dimension in shape_matrix:
        if dimension % 2 == 0:
            new_img_shape[dimension_index] = shape_matrix[dimension_index]
        else:
            new_img_shape[dimension_index] = shape_matrix[dimension_index] - 1

        dimension_index += 1
    
    return new_img_shape


def convert_to_pair_matrix(img_series):
    # Have to fix this
    img_set_pair = []
    for weighted_img in img_series:
        [img_shape, _, img_dim] = get_data_information(weighted_img)
        dim_indx = 0
        new_img_shape = np.array(img_shape)
        for dimension in img_shape:
            if dimension%2 == 0:
                new_img_shape[dim_indx] = img_shape[dim_indx]
            else:
                new_img_shape[dim_indx] = img_shape[dim_indx] -1
            dim_indx += 1
        difference_size = img_shape - new_img_shape

        for i in range(len(difference_size)):
            difference_size[i] = img_shape[i]*(-1) if difference_size[i]==0 else difference_size[i]

        if img_dim == 2:
            img_pair = weighted_img[:-difference_size[0], :-difference_size[1]]
        if img_dim == 3:
            img_pair = weighted_img[:-difference_size[0], :-difference_size[1], :-difference_size[2]]

        img_set_pair.append(img_pair)

    return img_set_pair


def calculate_snr(data, masks, std):
    masked_data = ma.masked_array(data[0], mask= np.logical_not(masks))
    mean_signal = masked_data.mean()

    print("Mean: {}, SNR: {}, in std: {}".format(mean_signal, (mean_signal/std), std))
    return mean_signal/std


# class VisdomLinePlotter(object):
#     """Plots to Visdom"""
#     def __init__(self, env_name='main'):
#         self.viz = Visdom()
#         self.env = env_name
#         self.plots = {}
#     def plot(self, var_name, split_name, title_name, x, y):
#         if var_name not in self.plots:
#             self.plots[var_name] = self.viz.line(X=np.array([x,x]), Y=np.array([y,y]), env=self.env, opts=dict(
#                 legend=[split_name],
#                 title=title_name,
#                 xlabel='Iteration',
#                 ylabel=var_name
#             ))
#         else:
#             self.viz.line(X=np.array([x]), Y=np.array([y]), env=self.env, win=self.plots[var_name], name=split_name, update = 'append')


def imagebrowse_slider(cube, cube2=[], axis=0, vmin_=0, vmax_=2, kwargs=[]):
    """
    Display a 3d ndarray with a slider to move along the third dimension.

    Extra keyword arguments are passed to imshow
    """
    import matplotlib.pyplot as plt
    from matplotlib.widgets import Slider, Button, RadioButtons
    from matplotlib.colors import Normalize


    colors = ['blue', 'black', 'red']
    cm = LinearSegmentedColormap.from_list('error_map', colors, N=100)
    # my_norm_scale = MidpointNormalize(midpoint=1.0, vmin=0.2, vmax=2.5)
    
    # check dim
    if not cube.ndim == 3:
        raise ValueError("cube should be an ndarray with ndim == 3")

    # generate figure
    fig = plt.figure()
    ax = plt.subplot(111)
    fig.subplots_adjust(left=0.25, bottom=0.25)

    # select first image
    s = [slice(0, 1) if i == axis else slice(None) for i in range(3)]
    im = cube[s].squeeze()
    if not len(cube2) == 0:
        im2 = cube2[s].squeeze()


    if kwargs == 'plot':
        # PLOT curve
        l1_l, l2_l = [], []
        for i in range(20):
            l1, = ax.plot(im[:, i], 'b--', linewidth=0.3)
            l1_l.append(l1)
            if not len(cube2) == 0:
                l2, = ax.plot(im2[:, i], 'r')
                l2_l.append(l2)
    else:
        # Display image
        l1 = ax.imshow(im, vmin=vmin_, vmax=vmax_, cmap='gray')


    axcolor = 'lightgoldenrodyellow'
    ax_slider = fig.add_axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)

    slider = Slider(ax_slider, 'Axis %i index' % axis, 0, cube.shape[axis] - 1,
                    valinit=2, valfmt='%i')

    def update(val):
        ind = int(slider.val)
        s = [slice(ind, ind + 1) if i == axis else slice(None)
                 for i in range(3)]
        im = cube[s].squeeze()
        if not len(cube2) == 0:
            im2 = cube2[s].squeeze()

        if kwargs == 'plot':
            for i in range(20):
                y_data1 = im[:, i]
                x_data = np.linspace(0, len(y_data1), len(y_data1));
                l1_l[i].set_data(x_data, y_data1)
                if not len(cube2) == 0:
                    y_data2 = im2[:, i]    
                    l2_l[i].set_data(x_data, y_data2)
        else:
            l1.set_data(im)

        ax.relim()
        ax.autoscale_view(True,True,True)
        fig.canvas.draw()

    slider.on_changed(update)
    plt.show()


def plot_scatter(x1,x2):
    fig, ax = plt.subplots(1,len(x1))
    for m in range(len(x1)):
        ax[m].plot(x1[m],x2[m], 'kx', markersize=2, alpha=0.7)
        ax[m].plot([0,np.max(x1[m])], [0,np.max(x1[m])], 'k--', linewidth=0.5)

    plt.show()


def visualise_h5_image(imagePath):
    data = load_hdf5(imagePath)
    estimated = data[0][0]
    label = data[1]
    mask = data[2]

    fig, ax = plt.subplots(1,3)
    ax[0].imshow(estimated[2], cmap='CMRmap', vmin=0, vmax=2.2)
    ax[1].imshow(label[2], cmap='CMRmap', vmin=0, vmax=2.2)
    ax[2].imshow(mask[2], cmap='CMRmap', vmin=0, vmax=2.2)

    plt.show()

