import torch
import os.path
import json
import argparse
from pathlib import Path
#REMARK @Nicolas: don't add relative imports or main , for that we use prediction.py
from prediction_bench import load_json_and_predict
from util import save_as_image, convert_to_polygons_and_save

parser = argparse.ArgumentParser(description='Prediction for Neuron segmentation.')
parser.add_argument("--path_config_file", help="Path to config file.")
args = parser.parse_args()
path_config_file = args.path_config_file
with open(path_config_file) as config_file:
    config = json.load(config_file)
#load model with settings
path_load_folder = config["path_loading_weights_and_parameters"]
path_image_folder = config["paths_image_folder"]
path_masks = config["paths_masks_folder"]
if path_masks == []:
    keys = ["img"]
else:
    keys = ["img", "seg"]
path_predictions = config["path_save_predictions"]
Path(path_predictions).mkdir(parents = True, exist_ok = True)
maximal_area_neuron_in_pixels = config["maximal_area_neuron_in_pixels"]
minimal_area_neuron_in_pixels = config["minimal_area_neuron_in_pixels"]
zoom_factor = config.get("Zoom factor", 1)
caching_factor = config.get("Caching factor", 1)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
image_size = 512  #should be the same as specified in experiment
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
convert_to_polygons_and_save( dict_predictions_default
                            , list_file_paths
                            , path_predictions
                            , "json"
                            , maximal_area_neuron_in_pixels
                            , minimal_area_neuron_in_pixels
                            )
