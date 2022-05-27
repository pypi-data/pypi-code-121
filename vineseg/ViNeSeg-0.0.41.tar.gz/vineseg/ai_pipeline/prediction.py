import torch
import os.path
import json
import argparse
from pathlib import Path

from .monai_models import get_model
from .DataLoader import DataReader
from .framework_bench import train, predict
from .add_channels import channelProcessingInput, channelProcessingOutput

from .preprocessing_augmentation import ( preprocessing
                                        , augmentation
                                        , convert_to_tensor
                                        )

from .postprocessing import postprocessing

from monai.losses import DiceLoss, FocalLoss, TverskyLoss
from monai.metrics import DiceMetric
from monai.utils import progress_bar
from monai.transforms import Compose
from torchcontrib.optim import SWA
from .prediction_bench import load_json_and_predict
from .util import save_as_image, convert_to_polygons_and_save



def pred_main( path
             , model
             , maximal_area_neuron_in_pixels = 700
             , minimal_area_neuron_in_pixels = 25
             , zoom_factor = 1
             , caching_factor = 1
             ):
    # load model with settings

    curr_path = os.path.dirname(__file__).replace("\\", "/")
    path_load_folder = curr_path.replace("ai_pipeline", "experiments/" + model + "/")

    path_image_folder = [path]

    # works in this case but not generally
    path_masks = []
    # for p in path_image_folder:
    #    path_masks.append(p.replace("img", "mask"))

    if not os.path.exists(os.path.dirname(path) + "/predictions"):
        os.makedirs(os.path.dirname(path) + "/predictions")

    path_predictions = os.path.dirname(path) + "/predictions/"  # + os.path.basename(path)
    # path_predictions = path_predictions.split("predictions/")[0] + "predictions/"

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    image_size = 512  # should be the same as specified in experiment
    keys = ["img"]
    dict_predictions_default, dict_metrics_default, list_file_paths = load_json_and_predict( path_load_folder
                                                                                           , path_image_folder
                                                                                           , path_masks
                                                                                           , device
                                                                                           , image_size
                                                                                           , zoom_factor
                                                                                           , caching_factor
                                                                                           , keys
                                                                                           )
    save_as_image(dict_predictions_default, path_predictions)
    convert_to_polygons_and_save(dict_predictions_default
                                 , list_file_paths
                                 , path_predictions
                                 , "json"
                                 , maximal_area_neuron_in_pixels
                                 , minimal_area_neuron_in_pixels
                                 )
