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

from datetime import datetime
import os
from typing import Optional

import nbformat as nbf
from nbformat.notebooknode import NotebookNode
import numpy
from PyQt5 import QtWidgets

import pyjamas.dialogs as dialogs
from pyjamas.pjscore import PyJAMAS
from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rimage.rimml.rimclassifier import rimclassifier
import pyjamas.rimage.rimml.rimlr as rimlr
import pyjamas.rimage.rimml.rimsvm as rimsvm
import pyjamas.rimage.rimml.rimunet as rimunet
from pyjamas.rutils import RUtils



class RCBClassifiers(RCallback):
    COLAB_NOTEBOOK_APPENDIX: str = '_colab_notebook'

    def cbCreateLR(self, parameters: Optional[dict] = None, wait_for_thread: bool = False) -> bool:
        """
        Create a logistic regression classifier.

        :param parameters: dictionary containing the parameters to create a logistic regression classifier; a dialog opens if this parameter is set to None; keys are:

            ``positive_training_folder``:
                path to the folder containing positive training images, formatted as a string
            ``negative_training_folder``:
                path to the folder containing negative training images, formatted as a string
            ``hard_negative_training_folder``:
                path to the folder containing hard negative training images, formatted as a string
            ``histogram_of_gradients``:
                use the distribution of gradient orientations as image features, True or False
            ``train_image_size``:
                the number of rows and columns in the positive and negative training images, formatted as a tuple of two integers
            ``step_sz``:
                number of pixel rows and columns to skip when scanning test images for target structures, formatted as a tuple of two integers
            ``misclass_penalty_C``:
                penalty for misclassification of training samples, formatted as a float
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if the classifier was successfully created, False otherwise.
        """
        continue_flag = True

        if parameters is None or parameters is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.logregression.LRDialog()
            ui.setupUi(dialog)

            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            parameters = ui.parameters()

            dialog.close()

        if continue_flag:
            self.pjs.batch_classifier.image_classifier = rimlr.lr(parameters)
            self.launch_thread(self.pjs.batch_classifier.fit, {'stop': True}, finished_fn=self.finished_fn,
                               stop_fn=self.stop_fn, wait_for_thread=wait_for_thread)

            return True

        else:
            return False

    def cbCreateUNet(self, parameters: Optional[dict] = None, wait_for_thread: bool = False) -> bool:  # Handle IO errors.
        """
        Create a convolutional neural network with UNet architecture.

        :param parameters: dictionary containing the parameters to create a UNet; a dialog opens if this parameter is set to None; keys are:

            ``positive_training_folder``:
                path to the folder containing positive training images, formatted as a string
            ``train_image_size``:
                the number of rows and columns in the network input (train images will be scaled to this size) formatted as a tuple of two integers, both of the integers must be divisible by 16.
            ``step_sz``:
                number of pixel rows and columns to divide test images into, each subimage will be scaled to the network input size and processed, formatted as a tuple of two integers
            ``epochs``:
                maximum number of iterations over the training data, as an int
            ``learning_rate``:
                step size when updating the weights, as a float
            ``mini_batch_size``:
                size of mini batches, as an int
            ``erosion_width``:
                width of the erosion kernel to apply to the labeled image produced by the UNet, to separate touching objects, as an int
            ``generate_notebook``:
                whether a Jupyter notebook to create and train the UNet (e.g. in Google Colab) should be generated, as a bool (if True, the UNet will NOT be created)
            ``notebook_path``:
                where to store the Jupyter notebook if it must be created
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if the classifier was successfully created, False otherwise.
        """
        continue_flag = True

        if parameters is None or parameters is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.neuralnet.NeuralNetDialog()
            ui.setupUi(dialog)

            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            parameters = ui.parameters()

            dialog.close()

        if continue_flag:
            self.pjs.batch_classifier.image_classifier = rimunet.UNet(parameters)

            if not parameters.get('generate_notebook'):
                self.launch_thread(self.pjs.batch_classifier.fit, {'stop': True}, finished_fn=self.finished_fn,
                                   stop_fn=self.stop_fn, wait_for_thread=wait_for_thread)
            else:
                self._generate_unet_notebook(parameters)

            return True

        else:
            return False

    def _generate_unet_notebook(self, parameters: dict) -> bool:
        # Follow scheme of path generation from measure notebook from rcbbatchprocess._save_notebook
        path = parameters.get('notebook_path')

        # Create filename
        thenow = datetime.now()
        filename = thenow.strftime(
            f"{thenow.year:04}{thenow.month:02}{thenow.day:02}_{thenow.hour:02}{thenow.minute:02}{thenow.second:02}")
        filepath = path + filename if path.endswith('/') else path + '/' + filename

        fname = RUtils.set_extension(filepath+RCBClassifiers.COLAB_NOTEBOOK_APPENDIX, PyJAMAS.notebook_extension)

        nb: NotebookNode = self._save_unet_notebook(fname, parameters)

        nb['metadata'].update({'language_info': {'name': 'python'}})

        with open(fname, 'w', encoding="utf-8") as f:
            nbf.write(nb, f)

        return True

    def _save_unet_notebook(self, filepath: str, parameters: dict) -> NotebookNode:
        nb: NotebookNode = nbf.v4.new_notebook()
        nb['cells'] = []

        filename = filepath[filepath.rfind(os.sep) + 1:]

        text = f"""# PyJAMAS notebook for Google Colab {filename}"""
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        text =  f"Use the following folder structure:\n" \
                f"\n" \
                f"train/\n" \
                f"\n\ttrain_folder_name_1/\n" \
                f"\t\timage/\n" \
                f"\t\t\ttrain_image_name_1.tif\n" \
                f"\t\tmask/\n" \
                f"\t\t\ttrain_image_name_1.tif\n" \
                f"\n" \
                f"\t.\n" \
                f"\t.\n" \
                f"\t.\n" \
                f"\n\ttrain_folder_name_n/\n" \
                f"\t\timage/\n" \
                f"\t\t\ttrain_image_name_n.tif\n" \
                f"\t\tmask/\n" \
                f"\t\t\ttrain_image_name_n.tif\n" \
                f"\n" \
                f"test/\n" \
                f"\n\ttest_folder_name_1/\n" \
                f"\t\timage/\n" \
                f"\t\t\ttest_image_name_1.tif\n" \
                f"\t\tmask/\n" \
                f"\t\t\ttest_image_name_1.tif\n" \
                f"\n" \
                f"\t.\n" \
                f"\t.\n" \
                f"\t.\n" \
                f"\n\ttest_folder_name_m/\n" \
                f"\t\timage/\n" \
                f"\t\t\ttest_image_name_m.tif\n" \
                f"\t\tmask/\n" \
                f"\t\t\ttest_image_name_m.tif\n" \
                f"\n" \
                f"Zip up the data into a file (e.g. testtrain.zip) and upload the file into /content in a google colab runtime.\n" \
                f"Then change into the /content folder and unzip the data."
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        code = f"!cd /content"
        nb['cells'].append(nbf.v4.new_code_cell(code))

        code = f"!unzip testtrain.zip"
        nb['cells'].append(nbf.v4.new_code_cell(code))

        text = """We import the packages necessary to run and plot the analysis:"""
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        code =  f"import os\n" \
                f"import pickle\n" \
                f"import gzip\n" \
                f"from tqdm import tqdm\n" \
                f"import numpy as np\n" \
                f"from skimage import draw\n" \
                f"from skimage.io import imread, imshow, imread_collection, concatenate_images\n" \
                f"from skimage.transform import resize\n" \
                f"from skimage.morphology import label\n" \
                f"from skimage.segmentation import find_boundaries\n" \
                f"from joblib import Parallel, delayed\n" \
                f"import matplotlib.pyplot as plt\n" \
                f"%matplotlib inline\n" \
                f"import sys\n" \
                f"import random\n" \
                f"import warnings\n" \
                f"import pandas as pd\n" \
                f"from itertools import chain\n" \
                f"import tensorflow as tf\n" \
                f"from tensorflow.keras.metrics import MeanIoU\n" \
                f"from tensorflow.keras.models import Model, load_model\n" \
                f"from tensorflow.keras.layers import Input\n" \
                f"from tensorflow.keras.layers import Dropout, Lambda\n" \
                f"from tensorflow.keras.layers import Conv2D, Conv2DTranspose\n" \
                f"from tensorflow.keras.layers import MaxPooling2D\n" \
                f"from tensorflow.keras.layers import Lambda\n" \
                f"from tensorflow.keras.layers import concatenate\n" \
                f"from tensorflow.keras.layers import multiply\n" \
                f"from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint\n" \
                f"from tensorflow.keras.optimizers import Adam\n" \
                f"from tensorflow.keras.preprocessing import image\n" \
                f"from tensorflow.keras import backend as K\n" \
                f"from tensorflow.keras import layers as L"
        nb['cells'].append(nbf.v4.new_code_cell(code))

        text = f"Set some parameters:"
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        rows, cols = parameters.get('train_image_size', rimunet.UNet.TRAIN_IMAGE_SIZE[0:2])
        code =  f"BATCH_SIZE = {parameters.get('mini_batch_size', rimunet.UNet.BATCH_SIZE)}\n" \
                f"EPOCHS = {parameters.get('epochs', rimunet.UNet.EPOCHS)}\n" \
                f"LEARNING_RATE = {parameters.get('learning_rate', rimunet.UNet.LEARNING_RATE)}\n" \
                f"IMG_WIDTH = {cols}\n" \
                f"IMG_HEIGHT = {rows}\n" \
                f"IMG_CHANNELS = 1\n" \
                f"TRAIN_PATH = '/content/train/'\n" \
                f"TEST_PATH = '/content/test/'\n" \
                f"MODEL_FILE_NAME = '{RUtils.set_extension(filename, PyJAMAS.classifier_extension)}'\n" \
                f"PICKLE_PROTOCOL = {RUtils.DEFAULT_PICKLE_PROTOCOL}\n" \
                f"warnings.filterwarnings('ignore', category=UserWarning, module='skimage')\n" \
                f"seed = 42\n" \
                f"random.seed(seed)\n" \
                f"np.random.seed(seed)"
        nb['cells'].append(nbf.v4.new_code_cell(code))

        text = f"Define weight function:"
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        code = """def weight_map(binmasks, w0=10, sigma=5, show=False):
    \"\"\"Compute the weight map for a given mask, as described in Ronneberger et al.
    (https://arxiv.org/pdf/1505.04597.pdf)
    \"\"\"

    labmasks = label(binmasks)
    n_objs = np.amax(labmasks)

    nrows, ncols = labmasks.shape[:2]
    masks = np.zeros((n_objs, nrows, ncols))
    distMap = np.zeros((nrows * ncols, n_objs))
    X1, Y1 = np.meshgrid(np.arange(nrows), np.arange(ncols))
    X1, Y1 = np.c_[X1.ravel(), Y1.ravel()].T
    for i in tqdm(range(n_objs)):
        mask = np.squeeze(labmasks == i + 1)
        bounds = find_boundaries(mask, mode='inner')
        X2, Y2 = np.nonzero(bounds)
        xSum = (X2.reshape(-1, 1) - X1.reshape(1, -1)) ** 2
        ySum = (Y2.reshape(-1, 1) - Y1.reshape(1, -1)) ** 2
        distMap[:, i] = np.sqrt(xSum + ySum).min(axis=0)
        masks[i] = mask
    ix = np.arange(distMap.shape[0])
    if distMap.shape[1] == 1:
        d1 = distMap.ravel()
        border_loss_map = w0 * np.exp((-1 * (d1) ** 2) / (2 * (sigma ** 2)))
    else:
        if distMap.shape[1] == 2:
            d1_ix, d2_ix = np.argpartition(distMap, 1, axis=1)[:, :2].T
        else:
            d1_ix, d2_ix = np.argpartition(distMap, 2, axis=1)[:, :2].T
        d1 = distMap[ix, d1_ix]
        d2 = distMap[ix, d2_ix]
        border_loss_map = w0 * np.exp((-1 * (d1 + d2) ** 2) / (2 * (sigma ** 2)))
    xBLoss = np.zeros((nrows, ncols))
    xBLoss[X1, Y1] = border_loss_map
    # class weight map
    loss = np.zeros((nrows, ncols))
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
    return ZZ"""
        nb['cells'].append(nbf.v4.new_code_cell(code))

        text = """Resize images and normalize intensities:"""
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        code = """# Get train and test IDs
train_ids = next(os.walk(TRAIN_PATH))[1]
test_ids = next(os.walk(TEST_PATH))[1]

X_train = np.zeros((len(train_ids), IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), dtype=np.uint16)
Y_train = np.zeros((len(train_ids), IMG_HEIGHT, IMG_WIDTH, 1), dtype=bool)
W_train = np.zeros((len(train_ids), IMG_HEIGHT, IMG_WIDTH, 1), dtype=float)
print('Getting and resizing train images and masks ... ')
sys.stdout.flush()
for n, id_ in tqdm(enumerate(train_ids), total=len(train_ids)):
    path = TRAIN_PATH + id_
    im_file = path+"/image/"+os.listdir(path+"/image/")[0]
    img = imread(im_file)
    if img.ndim == 3:
        img = img[0,:,:]
    img = np.expand_dims(resize(img, (IMG_HEIGHT, IMG_WIDTH), mode='constant', preserve_range=True),axis=-1)
    X_train[n] = img
    msk_file = path+"/mask/"+os.listdir(path+"/mask/")[0]
    mask = np.zeros((IMG_HEIGHT, IMG_WIDTH, 1), dtype=bool)
    mask_ = imread(msk_file)
    mask_ = np.expand_dims(resize(mask_, (IMG_HEIGHT, IMG_WIDTH), mode='constant', 
                                      preserve_range=True), axis=-1)
    mask = np.maximum(mask, mask_)
    weights = weight_map(mask)
    Y_train[n] = mask
    W_train[n, :, :, 0] = weights

# Get and resize test images
X_test = np.zeros((len(test_ids), IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), dtype=np.uint16)
Y_test = np.zeros((len(test_ids), IMG_HEIGHT, IMG_WIDTH, 1), dtype=bool)
print('Getting and resizing test images ... ')
sys.stdout.flush()
for n, id_ in tqdm(enumerate(test_ids), total=len(test_ids)):
    path = TEST_PATH + id_
    im_file = path+"/image/"+os.listdir(path+"/image/")[0]
    img = imread(im_file)
    if img.ndim == 3:
        img = img[0,:,:]
    img = np.expand_dims(resize(img, (IMG_HEIGHT, IMG_WIDTH), mode='constant', preserve_range=True),axis=-1)
    X_test[n] = img
    msk_file = path+"/mask/"+os.listdir(path+"/mask/")[0]
    mask = np.zeros((IMG_HEIGHT, IMG_WIDTH, 1), dtype=bool)
    mask_ = imread(msk_file)
    mask_ = np.expand_dims(resize(mask_, (IMG_HEIGHT, IMG_WIDTH), mode='constant', 
                                      preserve_range=True), axis=-1)
    mask = np.maximum(mask, mask_)
    Y_test[n] = mask

# Normalize intensities.
themax = np.amax(np.concatenate((X_train, X_test)))
X_train = X_train/themax
X_test = X_test/themax"""
        nb['cells'].append(nbf.v4.new_code_cell(code))

        code = """# Tensors for the model to work with
ycat = tf.keras.utils.to_categorical(Y_train)
wmap = np.zeros((X_train.shape[0], IMG_HEIGHT, IMG_WIDTH, 2), dtype=np.float32)
wmap[..., 0] = W_train.squeeze()
wmap[..., 1] = W_train.squeeze()"""
        nb['cells'].append(nbf.v4.new_code_cell(code))

        text = """Define loss function and build UNet:"""
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        code = """_epsilon = tf.convert_to_tensor(K.epsilon(), np.float32)

def my_loss(target, output):
    \"\"\"
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
    \"\"\"
    return - tf.reduce_sum(target * output,
                           len(output.get_shape()) - 1)


def make_weighted_loss_unet(input_shape, n_classes):
    # two inputs, one for the image and one for the weight maps
    ip = tf.keras.Input(shape=input_shape, name="image_input")
    # the shape of the weight maps has to be such that it can be element-wise
    # multiplied to the softmax output.
    weight_ip = tf.keras.Input(shape=input_shape[:2] + (n_classes,))

    # adding the layers
    conv1 = L.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(ip)
    conv1 = L.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv1)
    conv1 = L.Dropout(0.1)(conv1)
    mpool1 = L.MaxPool2D()(conv1)

    conv2 = L.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool1)
    conv2 = L.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
    conv2 = L.Dropout(0.2)(conv2)
    mpool2 = L.MaxPool2D()(conv2)

    conv3 = L.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool2)
    conv3 = L.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
    conv3 = L.Dropout(0.3)(conv3)
    mpool3 = L.MaxPool2D()(conv3)

    conv4 = L.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool3)
    conv4 = L.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
    conv4 = L.Dropout(0.4)(conv4)
    mpool4 = L.MaxPool2D()(conv4)

    conv5 = L.Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(mpool4)
    conv5 = L.Conv2D(1024, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
    conv5 = L.Dropout(0.5)(conv5)

    up6 = L.Conv2DTranspose(512, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv5)
    conv6 = L.Concatenate()([up6, conv4])
    conv6 = L.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)
    conv6 = L.Conv2D(512, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)
    conv6 = L.Dropout(0.4)(conv6)

    up7 = L.Conv2DTranspose(256, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv6)
    conv7 = L.Concatenate()([up7, conv3])
    conv7 = L.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)
    conv7 = L.Conv2D(256, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv7)
    conv7 = L.Dropout(0.3)(conv7)

    up8 = L.Conv2DTranspose(128, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv7)
    conv8 = L.Concatenate()([up8, conv2])
    conv8 = L.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)
    conv8 = L.Conv2D(128, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv8)
    conv8 = L.Dropout(0.2)(conv8)

    up9 = L.Conv2DTranspose(64, 2, strides=2, kernel_initializer='he_normal', padding='same')(conv8)
    conv9 = L.Concatenate()([up9, conv1])
    conv9 = L.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    conv9 = L.Conv2D(64, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv9)
    conv9 = L.Dropout(0.1)(conv9)

    c10 = L.Conv2D(n_classes, 1, activation='softmax', kernel_initializer='he_normal', name="unet-activation")(conv9)

    # Add a few non trainable layers to mimic the computation of the crossentropy
    # loss, so that the actual loss function just has to peform the
    # aggregation.
    c11 = L.Lambda(lambda x: x / tf.reduce_sum(x, len(x.get_shape()) - 1, True))(c10)
    c11 = L.Lambda(lambda x: tf.clip_by_value(x, _epsilon, 1. - _epsilon))(c11)
    c11 = L.Lambda(lambda x: K.log(x))(c11)
    weighted_sm = L.multiply([c11, weight_ip])

    model = Model(inputs=[ip, weight_ip], outputs=[weighted_sm])
    return model"""
        nb['cells'].append(nbf.v4.new_code_cell(code))

        text = """Create and train UNet:"""
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        code =  f"model = make_weighted_loss_unet((IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), 2)\n" \
                f"adam = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)\n" \
                f"model.compile(adam, loss=my_loss)\n" \
                f"history = model.fit([X_train, wmap], ycat, batch_size=BATCH_SIZE, epochs=EPOCHS)\n" \
                f"plt.plot(history.history['loss'])"
        nb['cells'].append(nbf.v4.new_code_cell(code))

        text = """Save and download the model (can be loaded into PyJAMAS):"""
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        code = """theclassifier = {
    'positive_training_folder': TRAIN_PATH,
    'train_image_size': (IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS),
    'scaler': themax,
    'epochs': EPOCHS,
    'mini_batch_size': BATCH_SIZE,
    'learning_rate': LEARNING_RATE,
    'classifier': model.get_weights(),
}

try:
    fh = gzip.open('/content/'+MODEL_FILE_NAME, "wb")
    pickle.dump(theclassifier, fh, PICKLE_PROTOCOL)

except (IOError, OSError) as ex:
    if fh is not None:
        fh.close()

fh.close()

from google.colab import files
files.download('/content/'+MODEL_FILE_NAME)"""
        nb['cells'].append(nbf.v4.new_code_cell(code))

        text = """Grab output layers for testing here in the notebook:"""
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        code = f"image_input = model.get_layer('image_input').input\n" \
               f"softmax_output = model.get_layer('unet-activation').output\n" \
               f"predictor = K.function([image_input], [softmax_output])"
        nb['cells'].append(nbf.v4.new_code_cell(code))

        text = """Sample test for the first image in the test set (set ind=i for the (i+1)th image):"""
        nb['cells'].append(nbf.v4.new_markdown_cell(text))

        code =  f"ind = 0\n" \
                f"testImage = X_test[ind]\n" \
                f"yhat = predictor([testImage.reshape((1, IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS))])[0]\n" \
                f"yhat = np.argmax(yhat[0], axis=-1)\n" \
                f"testLabel = Y_test[ind]\n" \
                f"weightImage = weight_map(testLabel)\n" \
                f"fig, (ax1, ax2, ax3, ax4) = plt.subplots(nrows=1, ncols=4, figsize=(50, 400))\n" \
                f"ax1.imshow(np.squeeze(testImage), cmap=plt.cm.gray)\n" \
                f"ax2.imshow(np.squeeze(yhat), cmap=plt.cm.gray)\n" \
                f"ax3.imshow(np.squeeze(testLabel), cmap=plt.cm.gray)\n" \
                f"ax4.imshow(np.squeeze(weightImage), cmap=plt.cm.gray)"
        nb['cells'].append(nbf.v4.new_code_cell(code))

        return nb

    def cbCreateSVM(self, parameters: Optional[dict] = None, wait_for_thread: bool = False) -> bool:  # Handle IO errors.
        """
        Create a support vector machine classifier.

        :param parameters: dictionary containing the parameters to create a logistic regression classifier; a dialog opens if this parameter is set to None; keys are:

            ``positive_training_folder``:
                path to the folder containing positive training images, formatted as a string
            ``negative_training_folder``:
                path to the folder containing negative training images, formatted as a string
            ``hard_negative_training_folder``:
                path to the folder containing hard negative training images, formatted as a string
            ``histogram_of_gradients``:
                use the distribution of gradient orientations as image features, True or False
            ``train_image_size``:
                the number of rows and columns in the positive and negative training images, formatted as a tuple of two integers
            ``step_sz``:
                number of pixel rows and columns to skip when scanning test images for target structures, formatted as a tuple of two integers
            ``misclass_penalty_C``:
                penalty for misclassification of training samples, formatted as a float
            ``kernel_type``:
                type of kernel ('linear' or 'rbf')
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if the classifier was successfully created, False otherwise.
        """


        continue_flag = True

        if parameters is None or parameters is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.svm.SVMDialog()
            ui.setupUi(dialog)

            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            parameters = ui.parameters()

            dialog.close()

        if continue_flag:
            self.pjs.batch_classifier.image_classifier = rimsvm.svm(parameters)
            self.launch_thread(self.pjs.batch_classifier.fit, {'stop': True}, finished_fn=self.finished_fn,
                               stop_fn=self.stop_fn, wait_for_thread=wait_for_thread)

            return True

        else:
            return False

    def cbApplyClassifier(self, firstSlice: Optional[int] = None, lastSlice: Optional[int] = None,
                          wait_for_thread: bool = False) -> bool:    # Handle IO errors.
        """
        Apply the current classifier to detect objects in the open image.

        :param firstSlice: slice number for the first slice to use (minimum is 1); a dialog will open if this parameter is None.
        :param lastSlice: slice number for the last slice to use; a dialog will open if this parameter is None.
        :param wait_for_thread: True if PyJAMAS must wait for the thread running this operation to complete, False otherwise.
        :return: True if the classifier is applied, False if the process is cancelled.
        """
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.timepoints.TimePointsDialog()

            lastSlice = 1 if self.pjs.n_frames == 1 else self.pjs.slices.shape[0]
            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice)

            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            firstSlice, lastSlice = ui.parameters()

            dialog.close()
        else:
            continue_flag = True

        if continue_flag:
            if firstSlice <= lastSlice:
                theslicenumbers = numpy.arange(firstSlice - 1, lastSlice, dtype=int)
            else:
                theslicenumbers = numpy.arange(lastSlice - 1, firstSlice, dtype=int)

            self.launch_thread(self.apply_classifier, {'theslices': theslicenumbers, 'progress': True, 'stop': True},
                               finished_fn=self.finished_fn,  progress_fn=self.progress_fn, stop_fn=self.stop_fn,
                               wait_for_thread=wait_for_thread)

            return True
        else:
            return False

    def apply_classifier(self, theslices: numpy.ndarray, progress_signal: ThreadSignals, stop_signal: ThreadSignals) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        if stop_signal is not None:
            stop_signal.emit("Applying classifier ...")

        self.pjs.batch_classifier.predict(self.pjs.slices, theslices, progress_signal)

        # For every slice ...
        for index in theslices:
            if type(self.pjs.batch_classifier.image_classifier) in [rimlr.lr, rimsvm.svm]:
                self.add_classifier_boxes(self.pjs.batch_classifier.box_arrays[index], index, False)
            elif type(self.pjs.batch_classifier.image_classifier) is rimunet.UNet:
                self.add_neuralnet_polylines(self.pjs.batch_classifier.object_arrays[index], index, False)
            else:
                self.pjs.statusbar.showMessage(f"Wrong classifier type.")
                return False

        return True

    def add_neuralnet_polylines(self, polylines: Optional[numpy.ndarray] = None, slice_index: Optional[int] = None,
                                paint: bool = True) -> bool:  # The first slice_index should be 0.
        if polylines is None or polylines is False or polylines == []:
            return False

        if slice_index is None or slice_index is False:
            slice_index = self.pjs.curslice

        for aPoly in polylines:
            self.pjs.addPolyline(aPoly, slice_index, paint=paint)

        return True

    def add_classifier_boxes(self, boxes: Optional[numpy.ndarray] = None, slice_index: Optional[int] = None,
                             paint: bool = True) -> bool:  # The first slice_index should be 0.
        if boxes is None or boxes is False or boxes == []:
            return False

        if slice_index is None or slice_index is False:
            slice_index = self.pjs.curslice

        for aBox in boxes:
            # Boxes stored as [minrow, mincol, maxrow, maxcol]
            self.pjs.addPolyline([[aBox[1], aBox[0]], [aBox[3], aBox[0]], [aBox[3], aBox[2]],
                                  [aBox[1], aBox[2]], [aBox[1], aBox[0]]], slice_index, paint=paint)

        return True

    def cbNonMaxSuppression(self, parameters: Optional[dict] = None, firstSlice: Optional[int] = None,
                            lastSlice: Optional[int] = None) -> bool:
        """
        Apply non-maximum suppression to remove redundant objects from an image.

        :param parameters: dictionary containing the parameters for non-maximum suppression; a dialog will open if this parameter is None; keys are:

            ``prob_threshold``:
                lower threshold for the probability that a detected object represents an instance of the positive training set (returned by the classifier), as a float
            ``iou_threshold``:
                maximum value for the intersection-over-union ratio for the area of two detected objects, as a float; 0.0 prevents any overlaps between objects, 1.0 allows full overlap
            ``max_num_objects``:
                maximum number of objects present in the image, as an integer; objects will be discarded from lowest to highest probability of the object representing an instance of the positive training set
        :param firstSlice: slice number for the first slice to use (minimum is 1); a dialog will open if this parameter is None.
        :param lastSlice: slice number for the last slice to use; a dialog will open if this parameter is None.
        :return: True if non-maximum suppression is applied, False if the process is cancelled.
        """

        if self.pjs.batch_classifier is None or type(self.pjs.batch_classifier.image_classifier) is rimunet.UNet:

            return False

        continue_flag = True

        if parameters is None or parameters is False:
            dialog = QtWidgets.QDialog()
            ui = dialogs.nonmax_suppr.NonMaxDialog(self.pjs)
            ui.setupUi(dialog)
            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted

            if continue_flag:
                parameters = ui.parameters()

            dialog.close()

        if not continue_flag:
            return False

        if (firstSlice is None or firstSlice is False) and (lastSlice is None or lastSlice is False):
            dialog = QtWidgets.QDialog()
            ui = dialogs.timepoints.TimePointsDialog()
            ui.setupUi(dialog, dialogs.timepoints.TimePointsDialog.firstSlice,
                       dialogs.timepoints.TimePointsDialog.lastSlice)

            dialog.exec_()
            dialog.show()

            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted

            if continue_flag:
                firstSlice, lastSlice = ui.parameters()

            dialog.close()

        if firstSlice <= lastSlice:
            theslicenumbers = numpy.arange(firstSlice - 1, lastSlice, dtype=int)
        else:
            theslicenumbers = numpy.arange(lastSlice - 1, firstSlice, dtype=int)

        self.pjs.batch_classifier.non_max_suppression(
            parameters.get('prob_threshold', rimclassifier.DEFAULT_PROB_THRESHOLD),
            parameters.get('iou_threshold', rimclassifier.DEFAULT_IOU_THRESHOLD),
            parameters.get('max_num_objects', rimclassifier.DEFAULT_MAX_NUM_OBJECTS),
            theslicenumbers
        )

        for index in theslicenumbers:
            self.pjs.annotations.cbDeleteSliceAnn(index)
            self.pjs.classifiers.add_classifier_boxes(self.pjs.batch_classifier.box_arrays[index][self.pjs.batch_classifier.good_box_indices[index]], index, True)

        self.pjs.repaint()

        return True


