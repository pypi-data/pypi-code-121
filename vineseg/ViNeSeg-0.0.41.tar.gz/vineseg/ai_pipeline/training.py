import torch
import os.path
import json
import argparse
from pathlib import Path
try: 
    from .monai_models import get_model
    from .DataLoader import DataReader
    from .framework_bench import train, predict
    from .add_channels import channelProcessingInput, channelProcessingOutput
    from .preprocessing_augmentation import (preprocessing
    , augmentation
    , convert_to_tensor
                                            )
    from .util import save_metrics
    from .postprocessing import postprocessing
except ImportError:
    from monai_models import get_model
    from DataLoader import DataReader
    from framework_bench import train, predict
    from add_channels import channelProcessingInput, channelProcessingOutput
    from preprocessing_augmentation import (preprocessing
    , augmentation
    , convert_to_tensor
    , feature_engineering
    )
    from util import save_metrics
    from postprocessing import postprocessing
    
from monai.losses import DiceLoss, FocalLoss, TverskyLoss, DiceCELoss
from monai.metrics import DiceMetric
from monai.utils import progress_bar
from monai.transforms import Compose
from torchcontrib.optim import SWA



def prepare_recordings(recordings):
    prepared_data = [{ "img": recordings[i].imagePath
                     , "seg": recordings[i].maskPath
                     } for i in range(len(recordings))
                    ]
    return prepared_data


def get_optimizer(optimizer_name
                  , model
                  , learning_rate
                  , weight_decay
                  ):
    if optimizer_name == "Adam":
        opt = torch.optim.Adam(model.parameters()
                               , learning_rate
                               )
    if optimizer_name == "AdamW":
        opt = torch.optim.AdamW(model.parameters()
                                , lr=learning_rate
                                , weight_decay=weight_decay
                                )
    if optimizer_name == "SGD":
        opt = torch.optim.SGD( model.parameters()
                             , lr = learning_rate
                             , momentum = 0.9
                             )
    return opt


def get_metrics(list_metric_names):
    if "Dice Metric" in list_metric_names:
        metric = DiceMetric(include_background=True
                            , reduction="mean"
                            )
    return metric


def get_loss_function(loss_name):
    if loss_name == "Dice loss":
        loss_function = DiceLoss( sigmoid=True
                                , reduction ="mean"
                                #, squared_pred=True
                                #, jaccard=True
                                )
    if loss_name == "Dice loss default":
        loss_function = DiceLoss()
    if loss_name == "Focal loss":
        loss_function = FocalLoss(to_onehot_y=True)
    if loss_name == "Tversky loss":
        loss_function = TverskyLoss(sigmoid=True
                                    , reduction="mean"
                                    )
    if loss_name == "Dice focal loss":
        loss_function = DiceLoss(sigmoid=True
                                 , squared_pred=True
                                 , jaccard=True
                                 , reduction="mean"
                                 )
    if loss_name == "Dice CE loss":
        loss_function = DiceCELoss(sigmoid=True, lambda_dice = 1)
    return loss_function


parser = argparse.ArgumentParser(description='Prediction for Neuron segmentation.')
parser.add_argument("--path_config_file", help="Path to config file.")
args = parser.parse_args()
path_config_file = args.path_config_file
with open(path_config_file) as config_file:
    config = json.load(config_file)
# load model with settings
path_load_model = config["path loading model"]
model_type = config["model type"]
path_training_image_folder = config["paths training image folder"]
path_training_masks_folder = config["paths training masks folder"]
path_val_image_folder = config["paths val image folder"]
path_val_masks_folder = config["paths val masks folder"]
input_channels = config["number input channel"]
output_channels = config["number output channel"]
image_size = config["ROI training"]
zoom_factor = config.get("Zoom factor", 1)
caching_factor = config.get("Caching factor", 0)

# set hyperparameters and starting point for training
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
loss_name = config["loss function"]
metric_name = config["metrics"]
optimizer_name = config["optimizer"]
validation_intervall = config["validation intervall"]
epochs = config["epochs"]
batch_size = config["batch size"]
learning_rate = config["learning rate"]
weight_decay = config["weight decay"]
path_save_folder = config["path save model"]
path_logging_results = config["logging training results"]

# log hyperparameter of experiment
swa_model = None
model = get_model(model_type
                  , input_channels
                  , output_channels
                  , device
                  , image_size
                  )
if path_load_model != None:
    swa_model = torch.optim.swa_utils.AveragedModel(model)
    model.load_state_dict(torch.load(path_load_model + "/trained_weights/trained_weights.pth", map_location=device),
                          strict=False)
    swa_model.load_state_dict(
        torch.load(path_load_model + "/trained_weights_swa/trained_weights.pth", map_location=device), strict=True)

# parameters for preprocessing the images and data augmentation
channel_types_input = config["channel types input"]
channel_types_output = config["channel types output"]
preprocessing_steps = config["preprocessing steps"]
postprocessing_steps = config["postprocessing"]
feature_engineering_steps = config["channel types input"]
augmentation_steps = config["augmentation steps"]
augementation_probability = config["augmentation probability"]
ROI_training = config["ROI training"]

# create files. Target directories should not exist.
working_dir = path_save_folder
# create folders with summary and trained weights
Path(working_dir).mkdir(parents=True, exist_ok=False)
with open(working_dir + "/Experiment_parameter.json", 'a') as File:
    json.dump(config, File, indent=2)

Path(working_dir + "/trained_weights").mkdir(parents=True, exist_ok=False)
Path(working_dir + "/trained_weights_swa").mkdir(parents=True, exist_ok=False)

feature_engineering_steps = channelProcessingInput(feature_engineering_steps)
list_feature_engineering_steps = feature_engineering(feature_engineering_steps)
list_preprocessing_steps = preprocessing(preprocessing_steps, zoom_factor)
list_augmentations_steps = augmentation( augmentation_steps
                                       , ROI_training
                                       , augementation_probability
                                       )
list_to_tensor = convert_to_tensor()
trans_train = Compose(list_feature_engineering_steps + list_preprocessing_steps + list_augmentations_steps + list_to_tensor)
trans_val = Compose(list_feature_engineering_steps + list_preprocessing_steps + list_to_tensor)
postprocessing_steps, _ = postprocessing(postprocessing_steps)

loss_function = get_loss_function(loss_name)
metric = get_metrics(metric_name)
opt = get_optimizer(optimizer_name
                    , model
                    , learning_rate
                    , weight_decay
                    )

train_recordings, _ = DataReader( path_training_image_folder
                                 , path_training_masks_folder
                                 , 0
                                 , maximal_number_images = 5000
                                 )
_, val_recordings = DataReader(path_val_image_folder
                               , path_val_masks_folder
                               , 1
                               , maximal_number_images = 5000
                               )

data_train = prepare_recordings(train_recordings)
data_val = prepare_recordings(val_recordings)
model, swa_model, loss_function, opt = train(model
                                             , swa_model
                                             , data_train
                                             , trans_train
                                             , data_val
                                             , trans_val
                                             , epochs
                                             , batch_size
                                             , validation_intervall
                                             , loss_function
                                             , opt
                                             , metric
                                             , postprocessing_steps
                                             , device
                                             , caching_factor
                                             )
torch.save(model.state_dict(), working_dir + "/trained_weights/" + "trained_weights.pth")
if swa_model != None:
    torch.save(swa_model.state_dict(), working_dir + "/trained_weights_swa/" + "trained_weights.pth")
