import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
from miacag.metrics.metrics_utils import mkDir
import pydicom
from scipy.ndimage import zoom
from mpl_toolkits.axes_grid1 import make_axes_locatable
import SimpleITK as sitk


def resizeVolume(img, output_size):
    factors = (output_size[0]/img.shape[0],
               output_size[1]/img.shape[1])

    new_array = zoom(img, (factors[0], factors[1], 1))
    return new_array

def normalize(img):
    img = (img - np.min(img)) / \
        (np.amax(img)-np.amin(img)) # + 1e-8
    return img

def prepare_cv2_img(img, mask, data_path, 
                    patientID,
                    studyInstanceUID,
                    seriesInstanceUID,
                    SOPInstanceUID,
                    config):
    path = os.path.join(
        config['output_directory'],
        'saliency',
        'mispredictions'
        if config['loaders']['val_method']['misprediction'] == 'True'
        else 'corrects',
        patientID,
        studyInstanceUID,
        seriesInstanceUID,
        SOPInstanceUID)
    mkDir(path)
    img = img[0, 0, :, :, :]
    img = np.expand_dims(img, 2)
   # img2 = pydicom.read_file(data_path[0]).pixel_array
    img2 = sitk.ReadImage(data_path[0])
    img2 = sitk.GetArrayFromImage(img2)
    img2 = np.transpose(img2, (1, 2, 0))
    img2 = np.expand_dims(img2, 2)
    mask = mask[0, 0, :, :, :]
    mask = resizeVolume(mask, (img2.shape[0], img2.shape[1]))
  #  mask = np.expand_dims(mask, 2)
    for i in range(0, img.shape[3]):
        input2d = img[:, :, :, i]
        input2d_2 = img2[:, :, :, i]
        cam, heatmap, input2d_2 = show_cam_on_image(
            input2d_2,
            mask[:, :, i]) # mask[:,:,:,i]

        # input2d = np.flip(np.rot90(np.rot90(np.rot90(input2d))), 1)
        # plt.imshow(input2d, cmap="gray", interpolation="None")
        # plt.colorbar()
        # plt.axis('off')
        # plt.savefig(os.path.join(path, 'input{}.png'.format(i)))
        # plt.clf()

        #input2d_2 = np.flip(np.rot90(np.rot90(np.rot90(input2d))), 1)
        plt.imshow(input2d_2, cmap="gray", interpolation="None")
        plt.colorbar()
        plt.axis('off')
        plt.savefig(os.path.join(path, 'input2{}.png'.format(i)))
        plt.clf()

        plt.imshow(input2d_2, cmap="gray", interpolation="None")
       # plt.colorbar()
        plt.savefig(os.path.join(path, 'input2_no_colormap{}.png'.format(i)))
        plt.clf()


        cam = np.flip(np.rot90(np.rot90(np.rot90(cam))), 1)
        plt.imshow(cam, cmap="jet", interpolation="None")
        plt.colorbar()
        plt.axis('off')
        plt.savefig(os.path.join(path, 'cam{}.png'.format(i)))
        plt.clf()

        heatmap = np.flip(np.rot90(np.rot90(np.rot90(heatmap))), 1)
        plt.imshow(heatmap, cmap="jet", interpolation="None")
        plt.colorbar()
        plt.axis('off')
        plt.savefig(os.path.join(path, 'heatmap{}.png'.format(i)))
        plt.clf()

        plt.imshow(heatmap, cmap="jet", interpolation="None")
        #plt.colorbar()
        plt.axis('off')
        plt.savefig(os.path.join(path, 'heatmap_no_colorbar{}.png'.format(i)))
        plt.clf()

        fig = plt.figure(figsize=(16, 12))
        #ax = plt.gca()
        fig.add_subplot(1, 2, 1)
        # f, axarr = plt.subplots(1, 2)
       # divider = make_axes_locatable(ax)
        plt.imshow(input2d_2, cmap="gray", interpolation="None")
        # cax = divider.append_axes("right", size="5%", pad=0.05)

        #plt.colorbar(im, cax)
        # plt.colorbar()
        plt.axis('off')

        fig.add_subplot(1, 2, 2)
        # f, axarr = plt.subplots(1, 2)
        plt.imshow(heatmap, cmap="jet", interpolation="None")
        #cax = divider.append_axes("right", size="5%", pad=0.05)
        #plt.colorbar(im2, cax)
        #plt.colorbar()
        plt.axis('off')

        plt.savefig(os.path.join(path, 'twoplots{}.png'.format(i)))
        plt.clf()

       # axarr[0, 1].imshow(image_datas[1])

def show_cam_on_image(img, mask):
    img = normalize(img)
    mask = normalize(mask)

    heatmap = cv2.applyColorMap(np.uint8(255 * mask), cv2.COLORMAP_JET)
    heatmap = np.float32(heatmap) / 255
    cam = heatmap + np.float32(img)
    cam = cam / np.max(cam)
    return cam, heatmap, img
