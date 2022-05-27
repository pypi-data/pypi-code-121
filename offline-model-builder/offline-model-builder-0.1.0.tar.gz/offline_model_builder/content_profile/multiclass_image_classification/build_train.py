# build_train.py
import os
import cv2
import json
import progressbar
import numpy as np
from imutils import paths
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from offline_model_builder.content_profile.multiclass_image_classification.common.io import HDF5DatasetWriter
from offline_model_builder.common import AspectAwarePreprocessor
from config import config as config
import logging as lg

imagePaths = list(paths.list_images(config.IMAGES_PATH))
imageLabels = [p.split(os.path.sep)[-1].split(".")[0] for p in imagePaths]

le = LabelEncoder()
imageLabels = le.fit_transform(imageLabels)


# perform stratified sampling from the training set to build the
# testing split from the training data
split = train_test_split(imagePaths,
                imageLabels,
                test_size = 0.2,
                stratify = imageLabels,
                random_state = 42
    )
(trainPaths, testPaths, trainLabels, testLabels) = split


# perform another stratified sampling, this time to build the
# validation data
split = train_test_split(trainPaths,
                trainLabels,
                test_size = 0.2,
                stratify = trainLabels,
                random_state = 42
    )
(trainPaths, valPaths, trainLabels, valLabels) = split


# construct a list pairing the training, validation and testing
# image paths along with their corresponding labels and output HDF5 files
datasets = [
        ("train", trainPaths, trainLabels, config.TRAIN_HDF5),
        ("val", valPaths, valLabels, config.VAL_HDF5),
        ("test", testPaths, testLabels, config.TEST_HDF5)
    ]

# initialize the image preprocessor and the lists of RGB channel
# averages
aap = AspectAwarePreprocessor(256, 256)
(R, G, B) = ([], [], [])


# loop over the dataset tuples
for (dType, paths, labels, outputPath) in datasets:
    # create HDF5 writer
    lg.info("[INFO] building {} ...".format(outputPath))
    writer = HDF5DatasetWriter((len(paths), 256, 256, 3), outputPath)
    # initialize the progress bar
    widgets = ["building dataset...", progressbar.Percentage(), " ",
                progressbar.Bar(), " ", progressbar.ETA()]
    pbar = progressbar.ProgressBar(maxval = len(paths), widgets = widgets).start()
    # loop over the image paths
    for (i, (path, label)) in enumerate(zip(paths, labels)):
        # load the image and process it
        image = cv2.imread(path)
        image = aap.preprocess(image)

        # if we are building the training dataset, then compute the
        # mean of each channel in the image, then update the
        # respective lists
        if dType == "train":
            (b, g, r) = cv2.mean(image)[:3]
            R.append(r)
            G.append(g)
            B.append(b)
        # add the iamge and label # to the HDF5 dataset
        writer.add([image], [label])
        pbar.update(i)
    # close the HDF5 writer
    pbar.finish()
    writer.close()


# construct a dictionary of averages, then serialize the means to a 
# JSON file
lg.info("[INFO] serializing means...")
D = {"R": np.mean(R), "G": np.mean(G), "B": np.mean(B)}
f = open(config.DATASET_MEAN, "w")
f.write(json.dumps(D))
f.close()