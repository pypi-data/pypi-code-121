"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
from typing import List, Optional, Tuple

import tensorflow.keras.preprocessing.image as kpi
import numpy
from sklearn.preprocessing import StandardScaler

import pyjamas.pjscore
from pyjamas.rimage.rimcore import rimage
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rimage.rimml.rimml import rimml
from pyjamas.rimage.rimml.featurecalculator import FeatureCalculator
from pyjamas.rimage.rimml.featurecalculator_sog import FeatureCalculatorSOG
from pyjamas.rimage.rimml.featurecalculator_rowofpixels import FeatureCalculatorROP
from pyjamas.rutils import RUtils


class rimclassifier(rimml):
    DEFAULT_STEP_SZ: Tuple[int, int] = (5, 5)  # For SVM at least, when this parameter equals 1 more objects are
    # recognized than when it equals 5.

    # These define default values for non-maximum supression.
    DEFAULT_IOU_THRESHOLD: float = .33  # When iou_threshold (intersection/union) is small, fewer boxes are left,
    # as boxes with overlap above the threshold are suppressed.
    DEFAULT_PROB_THRESHOLD: float = .95
    DEFAULT_MAX_NUM_OBJECTS: int = 200

    def __init__(self, parameters: Optional[dict] = None):
        super().__init__(parameters)

        self.positive_training_folder: str = parameters.get('positive_training_folder')
        self.negative_training_folder: str = parameters.get('negative_training_folder')
        self.hard_negative_training_folder: str = parameters.get('hard_negative_training_folder', '')

        # Size of training images (rows, columns).
        self.train_image_size: Tuple[int, int] = parameters.get('train_image_size', rimclassifier.TRAIN_IMAGE_SIZE[0:2])

        # Feature calculator.
        self.fc: FeatureCalculator = parameters.get('fc', None)
        if self.fc is None:
            self.fc = FeatureCalculatorSOG() if parameters.get('histogram_of_gradients') else FeatureCalculatorROP()

        self.scaler: StandardScaler = parameters.get('scaler', StandardScaler())

        # Scanning parameters.
        self.step_sz: Tuple[int, int] = parameters.get('step_sz', rimclassifier.DEFAULT_STEP_SZ)  # For SVM at least, when this parameter equals 1 more objects are recognized than when it equals 5.

        # Non-max suppression.
        self.iou_threshold: float = parameters.get('iou_threshold', rimclassifier.DEFAULT_IOU_THRESHOLD)  # When iou_threshold (intersection/union) is small, fewer boxes are left, as boxes with overlap above the threshold are suppressed.
        self.prob_threshold: float = parameters.get('prob_threshold', rimclassifier.DEFAULT_PROB_THRESHOLD) # Boxes below this probability will be ignored.
        self.max_num_objects: int = parameters.get('max_num_objects_dial', rimclassifier.DEFAULT_MAX_NUM_OBJECTS)

        self.good_box_indices: numpy.ndarray = None

        # Classifier features.
        self.features_positive_array: numpy.ndarray = None
        self.features_negative_array: numpy.ndarray = None

        # Test parameters.
        self.object_positions: list = None
        self.object_map: numpy.ndarray = None
        self.box_array: numpy.ndarray = None
        self.prob_array: numpy.ndarray = None

    def save(self, filename: str) -> bool:
        theclassifier = {
            'positive_training_folder': self.positive_training_folder,
            'negative_training_folder': self.negative_training_folder,
            'hard_negative_training_folder': self.hard_negative_training_folder,
            'train_image_size': self.train_image_size,
            'scaler': self.scaler,
            'fc': self.fc,
            'step_sz': self.step_sz,
            'iou_threshold': self.iou_threshold,
            'prob_threshold': self.prob_threshold,
            'max_num_objects_dial': self.max_num_objects,
            'classifier': self.classifier,
            'features_positive_array': self.features_positive_array,
            'features_negative_array': self.features_negative_array,
        }

        return RUtils.pickle_this(theclassifier, RUtils.set_extension(filename, pyjamas.pjscore.PyJAMAS.classifier_extension))

    def compute_features(self, folder: Optional[str] = None, pad: bool = False) -> numpy.ndarray:
        if self.fc is None or self.fc is False or not os.path.exists(folder):
            return numpy.empty((1,))

        features: numpy.ndarray = None

        # List files in the folder.
        thefiles: List[str] = os.listdir(folder)

        # For each file:
        for f in thefiles:

            # If it is not a directory, read the image, calculate the hog features and append to a list.
            # (this is apparently faster than appending to an ndarray:
            # https://stackoverflow.com/questions/22392497/how-to-add-a-new-row-to-an-empty-numpy-array)
            _, ext = os.path.splitext(f)
            if ext not in rimage.image_extensions:
                continue

            thepath = os.path.join(folder, f)

            if os.path.isfile(thepath):
                # Read the file as an image. @todo: this may throw an exception.
                image = rimutils.read_stack(thepath)
                image = numpy.squeeze(image)

                if pad:
                    #n_pad_rows: int = self.train_image_size[0]-image.shape[0]
                    #n_pad_cols: int = self.train_image_size[1]-image.shape[1]

                    #image = numpy.pad(image, ((0, n_pad_rows), (0, n_pad_cols)), mode='median')
                    #image = skit.resize(image, self.train_image_size, mode='wrap', preserve_range=True)
                    image = kpi.smart_resize(numpy.expand_dims(image, axis=2), self.train_image_size)
                    image = numpy.squeeze(image)

                # Calculate features and append to the list.
                self.fc.calculate_features(image)
                if features is None:
                    features = self.fc.gimme_features()
                else:
                    features = numpy.vstack((features, self.fc.gimme_features()))

        return features

    def fit(self) -> bool:
        if self.fc is None or self.fc is False:
            return False

        self.features_positive_array = self.compute_features(self.positive_training_folder, True)
        self.features_negative_array = self.compute_features(self.negative_training_folder, True)

        self.train()
        self.hard_negative_mining()

        return True

    def hard_negative_mining(self) -> bool:
        """

        :return: True if hard negative training completed False if not.
        """
        if self.fc is None or self.fc is False:
            return False

        if self.hard_negative_training_folder == '' or self.hard_negative_training_folder is False:
            return False

        new_negative_features: numpy.ndarray = None

        thefiles = os.listdir(self.hard_negative_training_folder)

        for f in thefiles:
            # If it is not a directory, read the image, calculate the hog features and append to a list.
            # (this is apparently faster than appending to an ndarray:
            # https://stackoverflow.com/questions/22392497/how-to-add-a-new-row-to-an-empty-numpy-array)

            thepath = os.path.join(self.hard_negative_training_folder, f)

            if os.path.isfile(thepath):
                # Read the file as an image.
                image = rimutils.read_stack(thepath)
                image = numpy.squeeze(image)

                subimages = rimutils.generate_subimages(image, self.train_image_size, self.step_sz)

                for subim in subimages:
                    # At each window, extract features.
                    self.fc.calculate_features(subim[0])

                    # Apply classifier.
                    imfeatures: numpy.ndarray = self.fc.gimme_features()
                    theclass = self.classifier.predict(self.scaler.transform(imfeatures))  # do not forget to scale the features before testing!

                    # If classifier (incorrectly) classifies a given image as an object, add feature vector to negative
                    # training set.
                    if theclass == 1:
                        if new_negative_features is None:
                            new_negative_features = imfeatures
                        else:
                            new_negative_features = numpy.vstack((new_negative_features, imfeatures))

        # Re-train your classifier using hard-negative samples as well.
        self.features_negative_array = numpy.vstack((self.features_negative_array, new_negative_features))

        self.train()

        return True

    def train(self) -> bool:
        if self.features_positive_array is False or self.features_positive_array is None or \
                self.features_negative_array is False or self.features_negative_array is None:
            return False

        features_combined = numpy.vstack((self.features_positive_array, self.features_negative_array))
        class_combined = numpy.concatenate((numpy.ones((self.features_positive_array.shape[0],), dtype=int),
                                            -1 * numpy.ones((self.features_negative_array.shape[0],), dtype=int)))

        # todo: remove this if block, scaling can be done by the ImageDataGenerator.
        if self.scaler is not None:
            self.scaler.fit(features_combined)
            features_combined = self.scaler.transform(features_combined)  # doctest: +SKIP

        self.classifier.fit(features_combined, class_combined)
        return True

    def predict(self, image: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        if self.fc is None or self.fc is False or image is None or image is False:
            return False

        image = numpy.squeeze(image)

        row_rad = int(numpy.floor(self.train_image_size[0] / 2))
        col_rad = int(numpy.floor(self.train_image_size[1] / 2))

        self.object_positions: list = []
        self.object_map: numpy.ndarray = numpy.zeros(image.shape)
        box_list: list = []
        prob_list: list = []

        subimages = rimutils.generate_subimages(image, self.train_image_size, self.step_sz)

        for subim, row, col in subimages:
            # At each window, extract descriptors.
            self.fc.calculate_features(subim)

            # Scale features.
            if self.scaler is not None:
                test_features = self.scaler.transform(self.fc.gimme_features())
            else:
                test_features = self.fc.gimme_features()

            # Apply the classifier.
            #theclass, theP = self.classifier.apply(subim)
            theclass = self.classifier.predict(test_features)
            theP = self.classifier.predict_proba(test_features)

            # If there is an object, store the position of the bounding box.
            if theclass[0] == 1:
                minrow = row - row_rad
                maxrow = row + row_rad
                if self.train_image_size[0] % 2 == 1:
                    maxrow += 1

                mincol = col - col_rad
                maxcol = col + col_rad
                if self.train_image_size[1] % 2 == 1:
                    maxcol += 1

                self.object_positions.append([row, col])
                self.object_map[row, col] = 1
                box_list.append([minrow, mincol, maxrow, maxcol])
                prob_list.append(theP[0][1])  # theP[0][0] contains the probability of the other class (-1)

            # print(f"{row}, {col}: class - {theclass[0]}, prob - {theP[0]}")

        self.box_array = numpy.asarray(box_list)
        self.prob_array = numpy.asarray(prob_list)

        return self.box_array.copy(), self.prob_array.copy()

    def non_max_suppression(self, box_array: numpy.ndarray, prob_array: numpy.ndarray, prob_threshold_val: float, iou_threshold_val: float, max_num_objects_val: int) -> numpy.ndarray:
        if box_array is None or box_array is False or len(box_array) == 0:
            return None

        if prob_array is None or prob_array is False or len(prob_array) == 0:
            return None

        if max_num_objects_val is None or max_num_objects_val is False:
            max_num_objects_val = self.max_num_objects
        else:
            self.max_num_objects = max_num_objects_val

        if prob_threshold_val is None or prob_threshold_val is False:
            prob_threshold_val = self.prob_threshold
        else:
            self.prob_threshold = prob_threshold_val

        if iou_threshold_val is None or iou_threshold_val is False:
            iou_threshold_val = self.iou_threshold
        else:
            self.iou_threshold = iou_threshold_val

        # Convert bounding box coordinates to floats, as we will do a bunch of divisions.
        if box_array.dtype.kind == "i":
            box_array = box_array.astype("float")

        # initialize list of picked indexes
        pick: List = []

        # grab the coordinates of the bounding boxes
        x1 = box_array[:, 1]  # min_col
        y1 = box_array[:, 0]  # min_row
        x2 = box_array[:, 3]  # max_col
        y2 = box_array[:, 2]  # max_row

        # Compute the area of the bounding boxes and grab the indexes to sort.
        # If no probabilities are provided, simply sort on the bottom-right y-coordinate.
        # This is not arbitrary, as order will become important to decide if there is overlap or not between boxes.
        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = y2

        idxs = prob_array

        # sort the indexes
        idxs = numpy.argsort(idxs)

        # keep looping while some indexes still remain in the index list
        while len(idxs) > 0:
            # grab the last index in the index list and add the
            # index value to the list of picked indexes
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            # Calculate the coordinates of the intersection between the selected box and all the other ones.
            # The code is vectorized.
            xx1 = numpy.maximum(x1[i], x1[idxs[:last]])
            yy1 = numpy.maximum(y1[i], y1[idxs[:last]])
            xx2 = numpy.minimum(x2[i], x2[idxs[:last]])
            yy2 = numpy.minimum(y2[i], y2[idxs[:last]])

            # Compute the width and height of the intersection.
            w = numpy.maximum(0, xx2 - xx1 + 1)
            h = numpy.maximum(0, yy2 - yy1 + 1)

            # Compute the ratio of intersection over union MODIFY HERE!!!! This is intersection/second box.
            #overlap = (w * h) / area[idxs[:last]]
            intersection_area = w * h
            union_area = area[i] + area[idxs[:last]] - intersection_area
            iou = intersection_area / union_area

            # delete all indexes from the index list that have
            idxs = numpy.delete(idxs, numpy.concatenate(([last], numpy.where(iou > iou_threshold_val)[0])))

        # Make sure only the desired number of objects in selected.
        if len(pick) > max_num_objects_val:
            pick = pick[:max_num_objects_val]

        self.good_box_indices = numpy.asarray(pick)

        # Use probability threshold to select only objects with at least the minimum probability.
        if prob_array is not None:
            self.good_box_indices = self.good_box_indices[numpy.where(prob_array[pick] >= prob_threshold_val)]

        return self.good_box_indices.copy()

    def find_objects(self, image: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        """
        Combine predict and non_max_suppression.

        :param image:
        :return:
        """
        box_array, prob_array = self.predict(image)
        good_box_indices = self.non_max_suppression(box_array, prob_array, self.prob_threshold, self.iou_threshold, self.max_num_objects)

        return box_array[good_box_indices], prob_array[good_box_indices]

    def segment_objects(self, image: numpy.ndarray, window_size: int = rimutils.FINDSEEDS_DEFAULT_WINSIZE,
                        binary_dilation_radius: int = 0, min_distance_edge: float = 0.0) -> numpy.ndarray:
        if self.box_array is None:
            return None

        for detected_object in self.box_array:
            minrow, mincol, maxrow, maxcol = detected_object[0], detected_object[1], detected_object[2], detected_object[3]
            little_image = image[minrow:(maxrow+1), mincol:(maxcol+1)]
            seed_coords, _ = rimutils.find_seeds(little_image, window_size, binary_dilation_radius, min_distance_edge)

        return seed_coords