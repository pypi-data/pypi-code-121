# train.py
import os
import json
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras.preprocessing.image import ImageDataGenerator
from offline_model_builder.content_profile.multiclass_image_classification.common.nn.conv import AlexNet
from offline_model_builder.content_profile.multiclass_image_classification.common.io import HDF5DatasetGenerator
from offline_model_builder.common import PatchPreprocessor
from offline_model_builder.common import SimplePreprocessor
from offline_model_builder.common import MeanPreprocessor
from offline_model_builder.common import ImageToArrayPreprocessor
from config import config as config
import logging as lg

# construct the training image generator for data augmentation
aug = ImageDataGenerator(
    rotation_range = 20, zoom_range = 0.15,
    width_shift_range = 0.2, height_shift_range = 0.2, shear_range = 0.15,
    horizontal_flip = True, fill_mode = "nearest"
)


# load the RGB means for the training set
means = json.loads(open(config.DATASET_MEAN).read())


# initialize the image preprocessors
sp = SimplePreprocessor(config.IMG_HEIGHT, config.IMG_WIDTH)
pp = PatchPreprocessor(config.IMG_HEIGHT, config.IMG_WIDTH)
mp = MeanPreprocessor(means["R"], means["G"], means["B"])
iap = ImageToArrayPreprocessor()


# initialize the training and validation dataset generators
trainGen = HDF5DatasetGenerator(config.TRAIN_HDF5, 64, aug = aug,
                                preprocessors = [pp, mp, iap], classes = config.CLASSES
                                )
valGen = HDF5DatasetGenerator(config.VAL_HDF5, 64,
                              preprocessors = [sp, mp, iap], classes = config.CLASSES
                              )

# initialize optimizer
lg.info("[INFO] compiling model...")
optimizer = Adam(lr = 1e-3)
model = AlexNet.build(width = config.IMG_WIDTH, height = config.IMG_HEIGHT, depth = 3,
                      classes = config.CLASSES, reg = 0.0002)
base_learning_rate = 0.00001
model.compile(optimizer=Adam(lr=base_learning_rate),
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# construct the set of callbacks
path = os.path.sep.join([config.OUTPUT_PATH, "{}.png".format(os.getpid())])
filepath = "20feb/training-{epoch:02d}-{val_accuracy:.2f}.h5"
callbacks = [
    ModelCheckpoint(filepath, monitor='val_accuracy', verbose=1, save_weights_only=True, mode='max',period=5),
    TensorBoard(log_dir='20feb/val_log')
]
# train the network
model.fit(
    trainGen.generator(),
    steps_per_epoch = trainGen.numImages // 64,
    validation_data = valGen.generator(),
    validation_steps = valGen.numImages // 64,
    epochs = config.EPOCH,
    max_queue_size = 128 * 2,
    callbacks = callbacks,
    verbose = 1
)

# save the model to file
lg.info("[INFO] serializing model...")
model.save(config.MODEL_PATH, overwrite = True)
model.save(config.H5_MODEL_PATH)
# close the HDF5 datasets
trainGen.close()
valGen.close()

