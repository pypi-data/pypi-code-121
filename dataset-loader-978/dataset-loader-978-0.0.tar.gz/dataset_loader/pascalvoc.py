from dataset_loader.pascal_voc_python.voc_utils import voc_utils as VOC
import os
import torch.nn.functional as F
import torchvision.transforms as transforms
import torch
import warnings
import pandas as pd
from bs4 import BeautifulSoup
#import xml.etree.ElementTree as ET
from more_itertools import unique_everseen
import numpy as np
import matplotlib.pyplot as plt
# import skimage
# from skimage import io


class pascalvoc():

    def __init__(self,base=0,window=1,p='/nas/softechict-nas-2/datasets/VOCdevkit/VOC2012'):
        self.p=p

        #self.img_dir = os.path.join(self.p, 'JPEGImages/')
        #self.ann_dir = os.path.join(self.p, 'Annotations')
        self.set_dir = os.path.join(self.p, 'ImageSets', 'Main')
        self.p = os.path.join(self.p, 'JPEGImages')
        self.name='pascalvoc'
        self.base, self.window = base, window

        self.load_imgs()
        self.img_list = {k: v for k, v in enumerate(sorted(self.images_dict.keys(), \
                                                           key=lambda x:int(x[:-4]))[base:base + window])}

        if len(self.img_list) == 0:
            raise ValueError(f'Empty dataset')
        elif len(self.img_list) < self.window:
            warnings.warn(f'Dataset length lower than window ({len(self.img_list)} < {self.window})')

        self.labs = self.list_image_sets()
        self.GT = {el[1]: f'{el[1]} {self.list_image_sets()[el[0] % 20]}' for el in self.img_list.items()}

        pass

    def list_image_sets(self):

        """
        List all the image sets from Pascal VOC. Don't bother computing
        this on the fly, just remember it. It's faster.
        """
        return [
            'aeroplane', 'bicycle', 'bird', 'boat',
            'bottle', 'bus', 'car', 'cat', 'chair',
            'cow', 'diningtable', 'dog', 'horse',
            'motorbike', 'person', 'pottedplant',
            'sheep', 'sofa', 'train',
            'tvmonitor']

    def load_data(self, cat='val'):

        assert cat in ['train','val','trainval'], \
            'cat must be train, val or trainval'

        self.images_dict = dict()

        for cls in self.list_image_sets():
            f_name = os.path.join(self.set_dir,f'{cls}_{cat}.txt')
            with open(f_name,mode='r') as f:
                txt = f.readlines()

            for r in txt:
                if int(r.split()[-1]) > -1:
                    self.images_dict[f'{r.split()[0]}.jpg'] = self.list_image_sets().index(cls)

    def load_imgs(self):
        self.images_dict = dict()
        for el in os.listdir(self.p):
            self.images_dict[el] = 1

    def train_model(self, model, yr=2012):
        # import torchray.utils
        ...

    def get_img_number(self,img):
        return str(img)


    def transform(self,size=224,normalize=True):
        bgr_mean = [103.939, 116.779, 123.68]

        mean = [m / 255. for m in reversed(bgr_mean)]
        std = [1 / 255.] * 3

        # Note: image should always be downsampled. If image is being
        # upsampled, then this resize function will not match the behavior
        # of skimage.transform.resize in "constant" mode
        # (torch.nn.functional.interpolate uses "edge" padding).
        def resize(x):
            if not isinstance(size, int):
                orig_height, orig_width = size
            else:
                height, width = x.shape[1:3]
                if width < height:
                    orig_width = size
                    orig_height = int(size * height / width)
                else:
                    orig_height = size
                    orig_width = int(size * width / height)
            with torch.no_grad():
                x = F.interpolate(x.unsqueeze(0), (orig_height, orig_width),
                                  mode='bilinear', align_corners=False)
                x = x.squeeze(0)
            return x

        # if normalize:
        #     transform = transforms.Compose([
        #         transforms.ToTensor(),
        #         resize,
        #         transforms.Normalize(mean=mean, std=std),
        #     ])
        # else:
        #     transform = transforms.Compose([
        #         transforms.ToTensor(),
        #         resize,
        #     ])
        if normalize:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Resize(size),
                transforms.CenterCrop(size),
                transforms.Normalize(mean=mean, std=std),
            ])
        else:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Resize(size),
                transforms.CenterCrop(size)
            ])

        return transform

    def apply_transform(self,image,normalize=True,size=224):

        tensor=self.transform(size=size,normalize=normalize)(image).unsqueeze(0)
        return tensor

    def denormalize(self,tensor):
        return tensor
'''
    def list_image_sets(self):
        """
        List all the image sets from Pascal VOC. Don't bother computing
        this on the fly, just remember it. It's faster.
        """
        return [
            'aeroplane', 'bicycle', 'bird', 'boat',
            'bottle', 'bus', 'car', 'cat', 'chair',
            'cow', 'diningtable', 'dog', 'horse',
            'motorbike', 'person', 'pottedplant',
            'sheep', 'sofa', 'train',
            'tvmonitor']

    def imgs_from_category(self,cat_name, dataset):
        """
        Summary

        Args:
            cat_name (string): Category name as a string (from list_image_sets())
            dataset (string): "train", "val", "train_val", or "test" (if available)

        Returns:
            pandas dataframe: pandas DataFrame of all filenames from that category
        """
        filename = os.path.join(self.set_dir, cat_name + "_" + dataset + ".txt")
        df = pd.read_csv(
            filename,
            delim_whitespace=True,
            header=None,
            names=['filename', 'true'])
        return df

    def imgs_from_category_as_list(self,cat_name, dataset):
        """
        Get a list of filenames for images in a particular category
        as a list rather than a pandas dataframe.

        Args:
            cat_name (string): Category name as a string (from list_image_sets())
            dataset (string): "train", "val", "train_val", or "test" (if available)

        Returns:
            list of srings: all filenames from that category
        """
        df = self.imgs_from_category(cat_name, dataset)
        df = df[df['true'] == 1]
        return df['filename'].values

    def annotation_file_from_img(self,img_name):
        """
        Given an image name, get the annotation file for that image

        Args:
            img_name (string): string of the image name, relative to
                the image directory.

        Returns:
            string: file path to the annotation file
        """
        return os.path.join(self.ann_dir, img_name) + '.xml'

    def load_annotation(self,img_filename):
        """
        Load annotation file for a given image.

        Args:
            img_name (string): string of the image name, relative to
                the image directory.

        Returns:
            BeautifulSoup structure: the annotation labels loaded as a
                BeautifulSoup data structure
        """
        xml = ""
        with open(self.annotation_file_from_img(img_filename)) as f:
            xml = f.readlines()
        xml = ''.join([line.strip('\t') for line in xml])
        return BeautifulSoup(xml)

    # TODO: implement this
    def get_all_obj_and_box(self,objname, img_set):
        img_list = self.imgs_from_category_as_list(objname, img_set)

        for img in img_list:
            annotation = self.load_annotation(img)

    def load_img(self,img_filename):
        """
        Load image from the filename. Default is to load in color if
        possible.

        Args:
            img_name (string): string of the image name, relative to
                the image directory.

        Returns:
            np array of float32: an image as a numpy array of float32
        """
        img_filename = os.path.join(self.img_dir, img_filename + '.jpg')
        img = skimage.img_as_float(io.imread(
            img_filename)).astype(np.float32)
        if img.ndim == 2:
            img = img[:, :, np.newaxis]
        elif img.shape[2] == 4:
            img = img[:, :, :3]
        return img

    def load_imgs(self,img_filenames):
        """
        Load a bunch of images from disk as np array.

        Args:
            img_filenames (list of strings): string of the image name, relative to
                the image directory.

        Returns:
            np array of float32: a numpy array of images. each image is
                a numpy array of float32
        """
        return np.array([self.load_img(fname) for fname in img_filenames])

    def _load_data(self,category, data_type=None):
        """
        Loads all the data as a pandas DataFrame for a particular category.

        Args:
            category (string): Category name as a string (from list_image_sets())
            data_type (string, optional): "train" or "val"

        Raises:
            ValueError: when you don't give "train" or "val" as data_type

        Returns:
            pandas DataFrame: df of filenames and bounding boxes
        """
        if data_type is None:
            raise ValueError('Must provide data_type = train or val')
        to_find = category
        filename = os.path.join('.', 'csvs/') + \
                   data_type + '_' + \
                   category + '.csv'
        if os.path.isfile(filename):
            return pd.read_csv(filename)
        else:
            try:
                os.mkdir('csvs')
            except:
                pass
            train_img_list = self.imgs_from_category_as_list(to_find, data_type)
            data = []
            for item in train_img_list:
                anno = self.load_annotation(item)
                objs = anno.findAll('object')
                for obj in objs:
                    obj_names = obj.findChildren('name')
                    for name_tag in obj_names:
                        if str(name_tag.contents[0]) == category:
                            fname = anno.findChild('filename').contents[0]
                            bbox = obj.findChildren('bndbox')[0]
                            xmin = int(bbox.findChildren('xmin')[0].contents[0])
                            ymin = int(bbox.findChildren('ymin')[0].contents[0])
                            xmax = int(bbox.findChildren('xmax')[0].contents[0])
                            ymax = int(bbox.findChildren('ymax')[0].contents[0])
                            data.append([fname, xmin, ymin, xmax, ymax])
            df = pd.DataFrame(
                data, columns=['fname', 'xmin', 'ymin', 'xmax', 'ymax'])
            df.to_csv(filename)
            return df

    def get_image_url_list(self,category, data_type=None):
        """
        For a given data type, returns a list of filenames.

        Args:
            category (string): Category name as a string (from list_image_sets())
            data_type (string, optional): "train" or "val"

        Returns:
            list of strings: list of all filenames for that particular category
        """
        df = self._load_data(category, data_type=data_type)
        image_url_list = list(
            unique_everseen(list(self.img_dir + df['fname'])))
        return image_url_list

    def get_masks(self,cat_name, data_type, mask_type=None):
        """
        Return a list of masks for a given category and data_type.

        Args:
            cat_name (string): Category name as a string (from list_image_sets())
            data_type (string, optional): "train" or "val"
            mask_type (string, optional): either "bbox1" or "bbox2" - whether to
                sum or add the masks for multiple objects

        Raises:
            ValueError: if mask_type is not valid

        Returns:
            list of np arrays: list of np arrays that are masks for the images
                in the particular category.
        """
        # change this to searching through the df
        # for the bboxes instead of relying on the order
        # so far, should be OK since I'm always loading
        # the df from disk anyway
        # mask_type should be bbox1 or bbox
        if mask_type is None:
            raise ValueError('Must provide mask_type')
        df = self._load_data(cat_name, data_type=data_type)
        # load each image, turn into a binary mask
        masks = []
        prev_url = ""
        blank_img = None
        for row_num, entry in df.iterrows():
            img_url = os.path.join(self.img_dir, entry['fname'])
            if img_url != prev_url:
                if blank_img is not None:
                    # TODO: options for how to process the masks
                    # make sure the mask is from 0 to 1
                    max_val = blank_img.max()
                    if max_val > 0:
                        min_val = blank_img.min()
                        # print "min val before normalizing: ", min_val
                        # start at zero
                        blank_img -= min_val
                        # print "max val before normalizing: ", max_val
                        # max val at 1
                        blank_img /= max_val
                    masks.append(blank_img)
                prev_url = img_url
                img = self.load_img(img_url)
                blank_img = np.zeros((img.shape[0], img.shape[1], 1))
            bbox = [entry['xmin'], entry['ymin'], entry['xmax'], entry['ymax']]
            if mask_type == 'bbox1':
                blank_img[bbox[1]:bbox[3], bbox[0]:bbox[2]] = 1.0
            elif mask_type == 'bbox2':
                blank_img[bbox[1]:bbox[3], bbox[0]:bbox[2]] += 1.0
            else:
                raise ValueError('Not a valid mask type')
        # TODO: options for how to process the masks
        # make sure the mask is from 0 to 1
        max_val = blank_img.max()
        if max_val > 0:
            min_val = blank_img.min()
            # print "min val before normalizing: ", min_val
            # start at zero
            blank_img -= min_val
            # print "max val before normalizing: ", max_val
            # max val at 1
            blank_img /= max_val
        masks.append(blank_img)
        return np.array(masks)

    def get_imgs(self,cat_name, data_type=None):
        """
        Load and return all the images for a particular category.

        Args:
            cat_name (string): Category name as a string (from list_image_sets())
            data_type (string, optional): "train" or "val"

        Returns:
            np array of images: np array of loaded images for the category
                and data_type.
        """
        image_url_list = self.get_image_url_list(cat_name, data_type=data_type)
        imgs = []
        for url in image_url_list:
            imgs.append(self.load_img(url))
        return np.array(imgs)

    def display_image_and_mask(self,img, mask):
        """
        Display an image and it's mask side by side.

        Args:
            img (np array): the loaded image as a np array
            mask (np array): the loaded mask as a np array
        """
        plt.figure(1)
        plt.clf()
        ax1 = plt.subplot(1, 2, 1)
        ax2 = plt.subplot(1, 2, 2)
        ax1.imshow(img)
        ax1.set_title('Original image')
        ax2.imshow(mask)
        ax2.set_title('Mask')
        plt.show(block=False)

    def cat_name_to_cat_id(self,cat_name):
        """
        Transform a category name to an id number alphabetically.

        Args:
            cat_name (string): Category name as a string (from list_image_sets())

        Returns:
            int: the integer that corresponds to the category name
        """
        cat_list = self.list_image_sets()
        cat_id_dict = dict(zip(cat_list, range(len(cat_list))))
        return cat_id_dict[cat_name]

    def display_img_and_masks(
            self,img, true_mask, predicted_mask, block=False):
        """
        Display an image and it's two masks side by side.

        Args:
            img (np array): image as a np array
            true_mask (np array): true mask as a np array
            predicted_mask (np array): predicted_mask as a np array
            block (bool, optional): whether to display in a blocking manner or not.
                Default to False (non-blocking)
        """
        m_predicted_color = predicted_mask.reshape(
            predicted_mask.shape[0], predicted_mask.shape[1])
        m_true_color = true_mask.reshape(
            true_mask.shape[0], true_mask.shape[1])
        # m_predicted_color = predicted_mask
        # m_true_color = true_mask
        # plt.close(1)
        plt.figure(1)
        plt.clf()
        plt.axis('off')
        f, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, num=1)
        # f.clf()
        ax1.get_xaxis().set_ticks([])
        ax2.get_xaxis().set_ticks([])
        ax3.get_xaxis().set_ticks([])
        ax1.get_yaxis().set_ticks([])
        ax2.get_yaxis().set_ticks([])
        ax3.get_yaxis().set_ticks([])

        ax1.imshow(img)
        ax2.imshow(m_true_color)
        ax3.imshow(m_predicted_color)
        plt.draw()
        plt.show(block=block)

    def load_data_multilabel(self,data_type=None):
        """
        Returns a data frame for all images in a given set in multilabel format.

        Args:
            data_type (string, optional): "train" or "val"

        Returns:
            pandas DataFrame: filenames in multilabel format
        """
        if data_type is None:
            raise ValueError('Must provide data_type = train or val')
        filename = os.path.join(self.set_dir, data_type + ".txt")
        cat_list = self.list_image_sets()
        df = pd.read_csv(
            filename,
            delim_whitespace=True,
            header=None,
            names=['filename'])
        # add all the blank rows for the multilabel case
        for cat_name in cat_list:
            df[cat_name] = 0
        for info in df.itertuples():
            index = info[0]
            fname = info[1]
            anno = self.load_annotation(fname)
            objs = anno.findAll('object')
            for obj in objs:
                obj_names = obj.findChildren('name')
                for name_tag in obj_names:
                    tag_name = str(name_tag.contents[0])
                    if tag_name in cat_list:
                        df.at[index, tag_name] = 1
        return df
'''