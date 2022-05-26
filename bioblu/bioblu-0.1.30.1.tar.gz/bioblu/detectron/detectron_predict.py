#!/usr/bin/env python3
import json

import cv2
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
import logging
import numpy as np
import os
import torch
from typing import List, Tuple, Dict

from bioblu.main import IMG_FORMATS
from bioblu.detectron import detectron


def load_model(fpath_model, use_cpu=True) -> dict:
    device_params = {}
    if use_cpu:
        device_params["map_location"] = torch.device('cpu')
    try:
        model = torch.load(fpath_model, **device_params)
    except FileNotFoundError:
        raise FileNotFoundError(f"Model not found: {fpath_model}")
    else:
        return model


def create_img_dict(fpath_img, inference_output_dims_wh: Tuple[int, int] = None) -> Dict:
    assert fpath_img.lower().endswith(IMG_FORMATS)
    _, img_name = os.path.split(fpath_img)
    img = np.array(cv2.imread(fpath_img))
    img_CHW = np.transpose(img, (2, 0, 1))  # Transpose from H, W, C to C, H, W
    img_tensor = torch.tensor(img_CHW)
    logging.debug(f"Loaded image {img_name} as tensor with shape {img_tensor.shape}")

    if inference_output_dims_wh is None:
        channels, img_height, img_width = tuple(img_tensor.shape)
    else:
        assert len(inference_output_dims_wh) == 2
        channels, (img_height, img_width) = 3, inference_output_dims_wh

    out_dict = {"image": img_tensor,
                "img_name": img_name,
                "height": img_height,
                "width": img_width}
    return out_dict


def load_previous_cfg(model_results_dir: str, use_cpu: bool = True, roi_heads_score_test_thresh: float = 0.6,
                      color_mode: str = "BGR"):
    cfg = get_cfg()
    _model_path = os.path.join(model_results_dir, "model_final.pth")
    _cfg_path = os.path.join(model_results_dir, "cfg.yaml")

    cfg.merge_from_file(_cfg_path)

    cfg.INPUT.FORMAT = color_mode.upper()
    cfg.MODEL.WEIGHTS = _model_path
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = roi_heads_score_test_thresh
    cfg.MODEL.DEVICE = "cpu" if use_cpu else "cuda"
    return cfg


def create_predictions_dir(fdir_predictions):
    try:
        os.makedirs(fdir_predictions)
    except FileExistsError:
        raise FileExistsError(f"Predictions output directory already exists: {fdir_predictions}")
    else:
        logging.info(f"Created output dir. {fdir_predictions}")


def load_imgs(fdir, inference_output_dims_wh=None) -> List[dict]:
    """
    Loads all images from one folder into a List[dict]. Can require a lot of memory.
    :param fdir:
    :param inference_output_dims_wh:
    :return:
    """
    files = sorted(os.listdir(fdir))
    imgs = []
    for file in files:
        if file.lower().endswith(IMG_FORMATS):
            img_fpath = os.path.join(fdir, file)
            logging.debug(f"Loading img. {img_fpath}")
            imgs.append(create_img_dict(img_fpath, inference_output_dims_wh))
        else:
            logging.info(f"Skipped  loading img '{file}' because format is not among {IMG_FORMATS}.")
    return imgs


def predict_single_img(fpath_img, model_dir, materials_dict,
                       roi_heads_score_test_thresh=0.6,
                       roi_heads_nms_thresh=0.7,
                       inference_output_dims_wh=None, use_cpu=True,
                       color_mode="RGB"):
    # Create input dict
    input_img = create_img_dict(fpath_img)
    # Load cfg
    cfg = load_previous_cfg(model_dir, use_cpu=use_cpu, roi_heads_score_test_thresh=roi_heads_score_test_thresh, color_mode=color_mode)
    cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = roi_heads_nms_thresh
    # Run prediction
    predictor = DefaultPredictor(cfg)
    result = predictor.model([input_img])[0]
    # Add some more info to the result:
    result["img_name"] = os.path.split(fpath_img)[-1]
    result["img_fpath"] = fpath_img
    result["materials_dict"] = materials_dict
    result["cfg"] = cfg  # Might be a bit overkill to add this to each result.
    return result


def predict_multiple_imgs(fdir_imgs: str, fdir_model: str, materials_dict: dict = None, save_predictions=False, save_visualisations=False,
                          roi_heads_score_test_thresh=0.6, roi_heads_nms_thresh=0.7,
                          inference_output_dims_wh=None, use_cpu=True, color_mode="RGB"):
    if materials_dict is None:
        materials_dict = {0: "trash"}
    fdir_predictions_out = f"{fdir_imgs}/output"
    if save_predictions or save_visualisations:
        if os.path.isdir(fdir_predictions_out):
            raise FileExistsError(f"Output directory already exists: {fdir_predictions_out}")
        else:
            os.makedirs(fdir_predictions_out)
            logging.info(f"Output dir created: {fdir_predictions_out}")

    input_img_paths = [os.path.join(fdir_imgs, path) for path in
                       sorted(os.listdir(fdir_imgs)) if path.lower().endswith(IMG_FORMATS)]

    # Load model & create predictor
    cfg = load_previous_cfg(fdir_model, use_cpu=use_cpu, roi_heads_score_test_thresh=roi_heads_score_test_thresh,
                            color_mode=color_mode)
    cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = roi_heads_nms_thresh

    predictor = DefaultPredictor(cfg)

    predictions = []
    for img_path in input_img_paths:
        img_name = os.path.split(img_path)[-1]
        logging.info(f"Processing image {img_name}")
        img = cv2.imread(img_path)
        result = predictor(img)
        logging.info(f"Prediction: {detectron.serialize_instance(result)}")
        result["img_name"] = img_name
        result["img_fpath"] = img_path
        result["materials_dict"] = materials_dict
        if save_visualisations:
            img_pred_name = os.path.join(fdir_predictions_out, img_name.split(".")[0] + "_prediction.png")
            logging.debug(f"Save prediction img as {img_pred_name}")
            detectron.visualize_detectron_prediction(result, save_as=img_pred_name, show_img=False)
        predictions.append(result)

    if save_predictions:
        serialised_preds = [detectron.serialize_instance(inst) for inst in predictions]  # Makes them "saveable"
        with open(os.path.join(fdir_predictions_out, "predictions.json"), "w") as f:
            f.write(json.dumps(serialised_preds, indent=4))

    return predictions


if __name__ == "__main__":

    # ToDo: add model to prediction result dict

    print(f"torch: {torch.__version__}")
    os.environ["LRU_CACHE_CAPACITY"] = "1"  # fix memory leak according to https://github.com/pytorch/pytorch/issues/29893

    loglvl = logging.DEBUG
    logger = logging.getLogger(__name__)  # Logger inherits module name
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(format=logformat)
    logger.setLevel(loglvl)

    fdir_model = "/media/findux/DATA/Documents/Malta_II/results/5239_2022-05-07_052041/"
    imgs_fdir = "/home/findux/Desktop/tmp/gnejna_test_paradise_model/"
    imgs_fdir = "/home/findux/Desktop/nonsquare_test/"
    fpath_img = "/home/findux/Desktop/tmp/gnejna_test_paradise_model/Gnejna_DJI_0737_0-1.tif"
    # predict_multiple_imgs(imgs_fdir, fdir_model, materials_dict={0: "trash"}, save_predictions=True, save_visualisations=True)
    # pred = predict_single_img(fpath_img=fpath_img, model_dir=fdir_model, materials_dict={0: "trash"})
    pred = predict_multiple_imgs(imgs_fdir, fdir_model, {0: "trash"}, save_predictions=True, save_visualisations=True)
    print(pred)
    # pred = predict_multiple_imgs(imgs_fdir, fdir_model, {0: "trash"})
    prediction_dict = detectron.serialize_instance(pred)
    with open("/home/findux/Desktop/test.json", 'w') as f:
        f.write(json.dumps(prediction_dict, indent=4))