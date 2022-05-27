from PIL import Image
import pandas as pd
import numpy as np
import base64

try: 
    from ..label_file import LabelFile
except ImportError:
    import labelme
import csv
import json
from skimage.measure import regionprops, label, regionprops_table, find_contours
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()


def determine_area_of_polygon(polygon_coordinates):
    return Polygon(polygon_coordinates).area


def save_as_image(dict_predictions, path_save):
    for image_name, prediction_mask in dict_predictions.items():
        prediction = Image.fromarray(prediction_mask)
        if prediction.mode != 'RGB':
            prediction = prediction.convert('RGB')
        if path_save is not None:
            prediction.save(path_save + image_name + ".png")


def convert_to_polygons_and_save(dict_predictions
                                 , list_file_paths
                                 , path_save
                                 , save_type
                                 , maximal_area_neuron_in_pixels
                                 , minimal_area_neuron_in_pixels
                                 ):
    counter = 0
    for image_name, prediction_mask in dict_predictions.items():
        imageHeight = prediction_mask.shape[0]
        imageWidth = prediction_mask.shape[1]
        file_path = list_file_paths[counter]
        counter += 1
        labeled_masks = label(prediction_mask)
        probs = regionprops_table(labeled_masks, properties=['coords'])
        ROI_polygons = []
        for prob in probs['coords']:
            if len(prob) >= 3:  # at minimum three points are needed to compute convex hull
                try:
                    hull = ConvexHull(prob)
                    if save_type == "json":
                        ROI_polygon = []
                        for vertices in hull.vertices:
                            ROI_polygon.append([prob[vertices][1], prob[vertices][0]])
                        ROI_polygons.append(ROI_polygon)
                    if save_type == "csv":
                        ROI_polygons.append(prob[hull.vertices])
                except Exception as e:
                    if "Initial simplex is flat" or "input is less than 2-dimensional" in str(e):
                        pass
                    else:
                        raise
        if save_type == "json":
            save_as_json(ROI_polygons
                         , path_save
                         , image_name
                         , file_path
                         , imageHeight
                         , imageWidth
                         , minimal_area_neuron_in_pixels
                         , maximal_area_neuron_in_pixels
                         )
        if save_type == "csv":
            save_as_csv(ROI_polygon, path_save, image_name)


def save_as_json(ROI_polygon
                 , path_save
                 , image_name
                 , file_path
                 , imageHeight
                 , imageWidth
                 , minimal_area_neuron_in_pixels
                 , maximal_area_neuron_in_pixels
                 ):
    try: 
        data = LabelFile.load_image_file(file_path)
    except NameError:
        img = Image.open(file_path)
        if file_path.endswith(".tiff"):
            img = img.convert("RGB")
            img.save(file_path.replace(".tiff", ".png"))
            img = Image.open(file_path.replace(".tiff", ".png"))
        elif file_path.endswith(".tif"):
            img = img.convert("RGB")
            img.save(file_path.replace(".tif", ".png"))
            img = Image.open(file_path.replace(".tif", ".png"))
        data = labelme.LabelFile.load_image_file(file_path)
    image_data = base64.b64encode(data).decode('utf-8')
    json_dict = {"version": "4.5.13"
                , "flags": {}
                , "shapes": []
                , "imagePath": image_name + ".png"
                , "imageData": image_data
                , "imageHeight": imageHeight
                , "imageWidth": imageWidth
                }
    for index, polygon in enumerate(ROI_polygon):
        Neuron_name = "Neuron" + str(index)
        dict_neuron = {}
        dict_neuron["shape_type"] = "polygon"
        area_neuron = determine_area_of_polygon(polygon)
        if area_neuron > maximal_area_neuron_in_pixels:
            dict_neuron["label"] = "Neuron too big"  # Neuron_name
        elif area_neuron < minimal_area_neuron_in_pixels:
            dict_neuron["label"] = "Neuron too small"
        else:
            dict_neuron["label"] = "Neuron"
        dict_neuron["points"] = polygon
        json_dict["shapes"].append(dict_neuron)

    with open(path_save + image_name + '.json', 'w') as f:
        json.dump(json_dict, f, cls=NpEncoder)


def save_as_csv(ROI_polygon, path_save, image_name):
    data = {}
    list_ROI_names = []
    list_dataframes = []
    for index, polygon in enumerate(ROI_polygon):
        ROI_name = "ROI_" + str(index)
        list_dataframes.append(pd.DataFrame({ROI_name: [polygon]}))
        list_ROI_names.append(ROI_name)
        data[ROI_name] = []
        for coordinates in polygon:
            data[ROI_name].append(coordinates)
    list_dataframes = []
    for key, value in data.items():
        current_dataframe = pd.DataFrame({key: np.array(value).tolist()})
        list_dataframes.append(current_dataframe)
    result = pd.concat(list_dataframes, axis=1)
    result.to_csv(path_save + image_name + 'polygons.csv')


def save_metrics(experiment_parameter, dict_metric, path_save):
    with open(path_save + 'result.csv', mode='a') as result_file:
        writer = csv.writer(result_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for parameter_name, parameter_value in experiment_parameter.items():
            writer.writerow([parameter_name, parameter_value])
        for data_name, metric in dict_metric.items():
            writer.writerow([data_name, metric])
        writer.writerow([])
