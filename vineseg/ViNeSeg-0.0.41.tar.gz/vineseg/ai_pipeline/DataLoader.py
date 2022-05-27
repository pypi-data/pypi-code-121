from PIL import Image
import numpy as np
import os
from glob import glob


class Recording:

    def __init__(self
                 , image
                 , name
                 ):
        self._image = image
        self._name = name
        self._label = None
        self._has_label = False
        self._predicition = None
        self._imagePath = None
        self._maskPath = None

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, newImage):
        self._image = newImage

    @property
    def imagePath(self):
        return self._imagePath

    @imagePath.setter
    def imagePath(self, newFilePath):
        self._imagePath = newFilePath

    @property
    def maskPath(self):
        return self._maskPath

    @maskPath.setter
    def maskPath(self, newFilePath):
        self._maskPath = newFilePath

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        self._name = newName

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, newLabel):
        self._has_label = True
        self._label = newLabel

    @property
    def prediction(self):
        return self._prediciton

    @prediction.setter
    def predicition(self, newPrediction):
        self._prediciton = newPrediction

    def has_label(self):
        return self._has_label


def data_loading(path_images, path_labels):
    recordings = []
    len_images = len(path_images)
    len_labels = len(path_labels)
    if len_labels == 0:
        path_labels = [None for _ in range(len_images)]
    for name_image, name_label in zip(path_images, path_labels):
        name = name_image.split("/")
        name = name[-1]
        name = name.split(".")
        name = name[0]
        recording = Recording(None, name)
        recording.imagePath = name_image
        if name_label != None:
            recording.maskPath = name_label
        recordings.append(recording)
    return recordings

def file_name_loading(path_images, path_labels):
    recordings = []
    len_images = len(path_images)
    len_labels = len(path_labels)
    if len_labels == 0:
        path_labels = [None for _ in range(len_images)]
    for name_image, name_label in zip(path_images, path_labels):
        im_frame = Image.open(name_image)
        im_frame = im_frame.convert("L")
        image = np.array(im_frame)
        name = name_image.split("/")
        name = name[-1]
        name = name.split(".")
        name = name[0]
        recording = Recording(image, name)
        recording.filePath = name_image
        if name_label != None:
            label_frame = Image.open(name_label)
            label_frame = label_frame.convert("L")
            label = np.array(label_frame)
            recording.label = label
        recordings.append(recording)
    return recordings


def DataReader( list_path_images
              , list_path_mask
              , validation_frac
              , maximal_number_images: int = 10000
              ):
    number_folders = len(list_path_images)
    path_train_images = []
    path_train_segs = []
    path_val_images = []
    path_val_segs = []
    val_frac = validation_frac
    boolean_file = os.path.isfile(list_path_images[0])
    if boolean_file is True:
        for i in range(number_folders):
            rann = np.random.random()
            if rann < val_frac:
                path_val_images.append(list_path_images[i])
                if list_path_mask != []:
                    path_val_segs.append(list_path_mask[i])
            else:
                path_train_images.append(list_path_images[i])
                if list_path_mask != []:
                    path_train_segs.append(list_path_mask[i])
    else:
        for index_folder in range(number_folders):
            images = sorted(glob(os.path.join(list_path_images[index_folder], "*")))
            if list_path_mask != []:
                segs = sorted(glob(os.path.join(list_path_mask[index_folder], "*")))
            num_total = len(images)
            for i in range(num_total):
                if i > maximal_number_images:
                    break
                rann = np.random.random()
                if rann < val_frac:
                    path_val_images.append(images[i])
                    if list_path_mask != []:
                        path_val_segs.append(segs[i])
                else:
                    path_train_images.append(images[i])
                    if list_path_mask != []:
                        path_train_segs.append(segs[i])
    train_recordings = data_loading(path_train_images, path_train_segs)
    val_recordings = data_loading(path_val_images, path_val_segs)
    return train_recordings, val_recordings
