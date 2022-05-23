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
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import skimage.io as sio
import skimage.morphology as sm
import skimage.segmentation as ss
import skimage.transform as st
import tensorflow as tf
import tensorflow.keras.backend as kb
import tensorflow.keras.layers as kl
import tensorflow.keras.models as km
import tensorflow.keras.optimizers as ko
import tensorflow.keras.utils as ku
import numpy

import pyjamas.pjscore
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rimage.rimml.rimneuralnet import rimneuralnet
from pyjamas.rutils import RUtils


class UNet(rimneuralnet):

    EROSION_WIDTH: int = 7

    def __init__(self, parameters: Optional[dict] = None):
        super().__init__(parameters)

        self.W_train: numpy.ndarray = None

        output_classes: int = parameters.get('output_classes', UNet.OUTPUT_CLASSES)
        learning_rate: float = parameters.get('learning_rate', UNet.LEARNING_RATE)

        input_size: Tuple[int, int, int] = parameters.get('train_image_size', UNet.TRAIN_IMAGE_SIZE)

        self.epochs: int = parameters.get('epochs', UNet.EPOCHS)
        self.mini_batch_size: int = parameters.get('mini_batch_size', UNet.BATCH_SIZE)

        classifier_representation = parameters.get('classifier')
        if type(classifier_representation) is km.Model:
            self.classifier = classifier_representation
        else:
            if len(input_size) == 2:
                input_size = input_size + (1, )

            self.classifier = self.make_weighted_loss_unet(input_size, output_classes)

        adam = ko.Adam(learning_rate=learning_rate)
        self.classifier.compile(adam, loss=self.pixelwise_loss)

        if type(classifier_representation) is list:
            self.classifier.set_weights(classifier_representation)

        self.step_sz = parameters.get('step_sz', UNet.STEP_SIZE)


    def make_weighted_loss_unet(self, input_shape: Tuple, n_classes: int) -> km.Model:
        _epsilon = tf.convert_to_tensor(kb.epsilon(), numpy.float32)

        # two inputs, one for the image and one for the weight maps
        ip = tf.keras.Input(shape=input_shape, name="image_input")
        # the shape of the weight maps has to be such that it can be element-wise
        # multiplied to the softmax output.
        weight_ip = tf.keras.Input(shape=input_shape[:2] + (n_classes,))

        # adding the layers
        conv1 = kl.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(ip)
        conv1 = kl.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv1)
        conv1 = kl.Dropout(0.1)(conv1)
        mpool1 = kl.MaxPool2D()(conv1)

        conv2 = kl.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool1)
        conv2 = kl.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
        conv2 = kl.Dropout(0.2)(conv2)
        mpool2 = kl.MaxPool2D()(conv2)

        conv3 = kl.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool2)
        conv3 = kl.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
        conv3 = kl.Dropout(0.3)(conv3)
        mpool3 = kl.MaxPool2D()(conv3)

        conv4 = kl.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool3)
        conv4 = kl.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
        conv4 = kl.Dropout(0.4)(conv4)
        mpool4 = kl.MaxPool2D()(conv4)

        conv5 = kl.Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool4)
        conv5 = kl.Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
        conv5 = kl.Dropout(0.5)(conv5)

        up6 = kl.Conv2DTranspose(512, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv5)
        conv6 = kl.Concatenate()([up6, conv4])
        conv6 = kl.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)
        conv6 = kl.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)
        conv6 = kl.Dropout(0.4)(conv6)

        up7 = kl.Conv2DTranspose(256, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv6)
        conv7 = kl.Concatenate()([up7, conv3])
        conv7 = kl.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)
        conv7 = kl.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)
        conv7 = kl.Dropout(0.3)(conv7)

        up8 = kl.Conv2DTranspose(128, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv7)
        conv8 = kl.Concatenate()([up8, conv2])
        conv8 = kl.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)
        conv8 = kl.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)
        conv8 = kl.Dropout(0.2)(conv8)

        up9 = kl.Conv2DTranspose(64, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv8)
        conv9 = kl.Concatenate()([up9, conv1])
        conv9 = kl.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
        conv9 = kl.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
        conv9 = kl.Dropout(0.1)(conv9)

        c10 = kl.Conv2D(n_classes, 1, activation='softmax', kernel_initializer='he_normal', name="unet-activation")(
            conv9)

        # Add a few non trainable layers to mimic the computation of the crossentropy
        # loss, so that the actual loss function just has to perform the
        # aggregation.
        c11 = kl.Lambda(lambda x: x / tf.reduce_sum(x, len(x.get_shape()) - 1, True))(c10)
        c11 = kl.Lambda(lambda x: tf.clip_by_value(x, _epsilon, 1. - _epsilon))(c11)
        c11 = kl.Lambda(lambda x: kb.log(x))(c11)
        weighted_sm = kl.multiply([c11, weight_ip])

        return km.Model(inputs=[ip, weight_ip], outputs=[weighted_sm])

    def pixelwise_loss(self, target, output):
        """
        A custom function defined to simply sum the pixelwise loss.
        This function doesn't compute the crossentropy loss, since that is made a
        part of the model's computational graph itself.
        Parameters
        ----------
        target : tf.tensor
            A tensor corresponding to the true labels of an image.
        output : tf.tensor
            Model output
        Returns
        -------
        tf.tensor
            A tensor holding the aggregated loss.
        """
        return - tf.reduce_sum(target * output,
                               len(output.get_shape()) - 1)

    def fit(self) -> bool:
        self._process_training_data()

        ycat = ku.to_categorical(self.Y_train)
        wmap = numpy.zeros((self.X_train.shape[0], self.train_image_size[0], self.train_image_size[1], 2),
                           dtype=numpy.float32)
        wmap[..., 0] = self.W_train.squeeze()
        wmap[..., 1] = self.W_train.squeeze()

        self.classifier.fit([self.X_train, wmap], ycat, batch_size=self.mini_batch_size, epochs=self.epochs)

        return True

    @classmethod
    def weight_map(cls, binmasks: numpy.ndarray, w0: float = 10., sigma: float = 5., show: bool = False):
        """Compute the weight map for a given mask, as described in Ronneberger et al.
        (https://arxiv.org/pdf/1505.04597.pdf)
        """

        labmasks = sm.label(binmasks)
        n_objs = numpy.amax(labmasks)

        nrows, ncols = labmasks.shape[:2]
        masks = numpy.zeros((n_objs, nrows, ncols))
        distMap = numpy.zeros((nrows * ncols, n_objs))
        X1, Y1 = numpy.meshgrid(numpy.arange(nrows), numpy.arange(ncols))
        X1, Y1 = numpy.c_[X1.ravel(), Y1.ravel()].T
        for i in range(n_objs):
            mask = numpy.squeeze(labmasks == i + 1)
            bounds = ss.find_boundaries(mask, mode='inner')
            X2, Y2 = numpy.nonzero(bounds)
            xSum = (X2.reshape(-1, 1) - X1.reshape(1, -1)) ** 2
            ySum = (Y2.reshape(-1, 1) - Y1.reshape(1, -1)) ** 2
            distMap[:, i] = numpy.sqrt(xSum + ySum).min(axis=0)
            masks[i] = mask
        ix = numpy.arange(distMap.shape[0])
        if distMap.shape[1] == 1:
            d1 = distMap.ravel()
            border_loss_map = w0 * numpy.exp((-1 * (d1) ** 2) / (2 * (sigma ** 2)))
        else:
            if distMap.shape[1] == 2:
                d1_ix, d2_ix = numpy.argpartition(distMap, 1, axis=1)[:, :2].T
            else:
                d1_ix, d2_ix = numpy.argpartition(distMap, 2, axis=1)[:, :2].T
            d1 = distMap[ix, d1_ix]
            d2 = distMap[ix, d2_ix]
            border_loss_map = w0 * numpy.exp((-1 * (d1 + d2) ** 2) / (2 * (sigma ** 2)))
        xBLoss = numpy.zeros((nrows, ncols))
        xBLoss[X1, Y1] = border_loss_map
        # class weight map
        loss = numpy.zeros((nrows, ncols))
        w_1 = 1 - masks.sum() / loss.size
        w_0 = 1 - w_1
        loss[masks.sum(0) == 1] = w_1
        loss[masks.sum(0) == 0] = w_0
        ZZ = xBLoss + loss
        # ZZ = resize(ZZ, outsize, preserve_range=True)
        if show:
            plt.imshow(ZZ)
            plt.colorbar()
            plt.axis('off')
        return ZZ

    def _process_training_data(self) -> bool:
        """
        Loads and scales training data and calculates weight maps.
        :return:
        """
        train_ids = next(os.walk(self.positive_training_folder))[1]

        # Get and resize train images and masks
        self.X_train = numpy.zeros((len(train_ids), self.train_image_size[0], self.train_image_size[1], 1), dtype=numpy.uint16)
        self.Y_train = numpy.zeros((len(train_ids), self.train_image_size[0], self.train_image_size[1], 1), dtype=numpy.bool)
        self.W_train = numpy.zeros((len(train_ids), self.train_image_size[0], self.train_image_size[1], 1), dtype=numpy.float)
        print('Getting and resizing train images and masks ... ')

        for n, id_ in enumerate(train_ids):
            path = self.positive_training_folder + id_
            im_file = path + "/image/" + os.listdir(path + "/image/")[0]
            img = sio.imread(im_file)
            if img.ndim == 3:
                img = img[0, :, :]
            img = numpy.expand_dims(st.resize(img, (self.train_image_size[0], self.train_image_size[1]), order=3,
                                              mode='constant', preserve_range=True), axis=-1)
            self.X_train[n] = img
            msk_file = path + "/mask/" + os.listdir(path + "/mask/")[0]
            mask = numpy.zeros((self.train_image_size[0], self.train_image_size[1], 1), dtype=numpy.bool)
            mask_ = sio.imread(msk_file)
            mask_ = numpy.expand_dims(st.resize(mask_, (self.train_image_size[0], self.train_image_size[1]), order=3,
                                                mode='constant', preserve_range=True), axis=-1)
            mask = numpy.maximum(mask, mask_)
            weights = UNet.weight_map(mask)
            self.Y_train[n] = mask
            self.W_train[n, :, :, 0] = weights

        self.scaler = numpy.amax(self.X_train)
        self.X_train = self.X_train / self.scaler

        return True

    def predict(self, image: numpy.ndarray) -> (numpy.ndarray, numpy.ndarray):
        if image is None or image is False:
            return False

        if image.ndim == 3:
            image = image[0, :, :]

        testImage = image / self.scaler

        image_input = self.classifier.get_layer('image_input').input
        softmax_output = self.classifier.get_layer('unet-activation').output
        predictor = kb.function([image_input], [softmax_output])

        testLabel = numpy.zeros(testImage.shape, dtype=numpy.bool)
        testProb = numpy.zeros(testImage.shape, dtype=numpy.bool)
        half_width = int(self.train_image_size[1] / 2)
        half_height = int(self.train_image_size[0] / 2)

        for animage, therow, thecol in rimutils.generate_subimages(testImage, self.train_image_size[0:2],
                                                                   self.step_sz, True):
            yhat = predictor([numpy.expand_dims(animage, axis=0)])[0]
            yhat = numpy.argmax(yhat[0], axis=-1)
            p = numpy.amax(yhat[0], axis=-1)

            testLabel[(therow - half_height):(therow + half_height),
            (thecol - half_width):(thecol + half_width)] = numpy.logical_or(
                testLabel[(therow - half_height):(therow + half_height), (thecol - half_width):(thecol + half_width)],
                yhat)
            testProb[(therow - half_height):(therow + half_height),
            (thecol - half_width):(thecol + half_width)] = p  # This is not really correct: one should select the probability that makes the pixel get its final value (or an average of those).

        self.object_array = numpy.asarray(rimutils.extract_contours(
            sm.dilation(sm.label(sm.binary_erosion(testLabel, sm.square(UNet.EROSION_WIDTH)), connectivity=1),
                        sm.square(UNet.EROSION_WIDTH))), dtype=object)
        self.prob_array = testProb

        return self.object_array.copy(), self.prob_array.copy()

    def save(self, filename: str) -> bool:
        classifier = self.classifier.get_weights() if self.classifier.weights else self.classifier

        theclassifier = {
            'positive_training_folder': self.positive_training_folder,
            'train_image_size': self.train_image_size,
            'scaler': self.scaler,
            'epochs': self.epochs,
            'mini_batch_size': self.mini_batch_size,
            'learning_rate': kb.eval(self.classifier.optimizer.lr),
            'classifier': self.classifier.get_weights(),
            'step_sz': self.step_sz
        }

        return RUtils.pickle_this(theclassifier, RUtils.set_extension(filename, pyjamas.pjscore.PyJAMAS.classifier_extension))