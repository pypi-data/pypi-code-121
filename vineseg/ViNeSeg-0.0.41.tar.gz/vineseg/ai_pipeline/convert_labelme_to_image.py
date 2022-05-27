import json
from PIL import Image, ImageDraw
import os
import argparse
from glob import glob

parser = argparse.ArgumentParser(description='Prediction for Neuron segmentation.')
parser.add_argument("--path_load_json_files", help="Path to load json files from labeme.")
parser.add_argument("--path_save_masks", help="Path where to store the converted mask images.")
args = parser.parse_args()
FOLDER_LOAD_JSON_FILES = args.path_load_json_files
FOLDER_SAVE_MASK_IMAGES = args.path_save_masks
json_files = sorted(glob(os.path.join(FOLDER_LOAD_JSON_FILES, "*.json")))
for file_name in json_files:
    name = file_name.split("/")
    name = name[-1]
    name = name.split(".")
    name = name[0]
    name = name.split("Img_")
    name = name[-1]
    with open(file_name) as f:
        d = json.load(f)
    imageHeight = d["imageHeight"]
    imageWidth = d["imageWidth"]
    list_neurons = d["shapes"]
    im = Image.new("RGB", (imageHeight, imageWidth), "black")
    draw = ImageDraw.Draw(im)
    for dict_neuron in list_neurons:
        polygon = tuple(tuple(i) for i in dict_neuron["points"])
        draw.polygon(polygon, fill="white")
    image_name = "Seg_" + name
    im.save(FOLDER_SAVE_MASK_IMAGES + image_name +  ".png")