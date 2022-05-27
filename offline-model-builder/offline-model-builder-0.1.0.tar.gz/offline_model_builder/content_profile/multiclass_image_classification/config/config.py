# config.py

# define the paths to the iamges directory
IMAGES_PATH = '../multiclass_image_classification/data/data'

# since we do not have validation data or access to the testing
# labels we need to make a number of images from the training data
# and use them instead


# define the path to the output training, validation and testing
# HDF5 files
TRAIN_HDF5 = "../multiclass_image_classification/checkpoint/train.hdf5"
VAL_HDF5 = "../multiclass_image_classification/checkpoint/val.hdf5"
TEST_HDF5 = "../multiclass_image_classification/checkpoint/test.hdf5"

# path to the output model file
MODEL_PATH = "../multiclass_image_classification/checkpoint/alexnet.model"
H5_MODEL_PATH = '/Users/sadashiv/Project/multiclass_image_classification/checkpoint/multi_class_image_classification.h5'

# define the path to the dataset mean
DATASET_MEAN = "../multiclass_image_classification/checkpoint/multiclass_image_mean.json"

# define the path to the output directory used for storing plots,
# classification reports, etc
OUTPUT_PATH = "../multiclass_image_classification/checkpoint/checkpoint/"
CLASSES = 11
EPOCH = 10
TF_LITE_MODEL_PATH = '../multiclass_image_classification/checkpoint/model.tflite'

IMG_HEIGHT = 227
IMG_WIDTH = 227

CLASS_NAMES = ['action','animation','children','entertainment','fifa_world_cup','fight','horror', 'islam','romance','soccer','travel']