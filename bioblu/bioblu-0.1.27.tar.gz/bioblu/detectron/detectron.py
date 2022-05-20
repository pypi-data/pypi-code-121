#!/usr/bin/env python3

import json
import logging
import os
from typing import List, Tuple, Union

import cv2
import numpy as np
import tensorflow as tf
import termcolor
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.data import (
    build_detection_test_loader,
    build_detection_train_loader,
    dataset_mapper,
    MetadataCatalog,
    DatasetCatalog,
)
from detectron2.data import transforms as T
from detectron2.engine import DefaultPredictor, DefaultTrainer
from detectron2.evaluation import COCOEvaluator
from detectron2.evaluation import inference_on_dataset
from detectron2.structures import BoxMode
from detectron2.utils.logger import setup_logger
from detectron2.utils.visualizer import Visualizer

from bioblu.ds_manage import ds_convert


class CustomTrainer(DefaultTrainer):
    """
    Customized child of the DefaultTrainer class so that it accepts customized DataMapper.
    Except from the below method it inherits all other functionalities of the DefaultTrainer class.
    """
    def __init__(self, cfg):
        DefaultTrainer.__init__(self, cfg)  # Init parent DefaultTrainer

    @classmethod
    def build_train_loader(cls, cfg, mapper=None):
        if mapper is None:
            return build_detection_train_loader(cfg)
        return build_detection_train_loader(cfg, mapper=mapper)  # This takes a custom DataMapper now


def load_json(json_fpath: str) -> dict:
    """Returns json data as a dict."""
    with open(json_fpath, 'r') as f:
        data = json.load(f)
    logging.debug(f'Loaded json object (type): {type(data)}')
    return data


def parse_augs(brightness_minmax: Tuple[float, float] = None,
               flip_v: float = None, flip_h: float = None,
               rot_minmax: Tuple[Union[float, int], Union[float, int]] = None) -> list:
    """
    Takes the arguments for the augmentations and returns the detectron-readable augmentations list.
    :param brightness_minmax:
    :param flip_v:
    :param flip_h:
    :param rot_minmax:
    :return:
    """
    augs = []

    if brightness_minmax is not None:
        bmin, bmax = brightness_minmax
        augs.append(T.RandomBrightness(bmin, bmax))
    if flip_v is not None:
        augs.append(T.RandomFlip(prob=flip_v, horizontal=False, vertical=True))
    if flip_h is not None:
        augs.append(T.RandomFlip(prob=flip_h, horizontal=True, vertical=False))
    if rot_minmax is not None:
        augs.append(T.RandomRotation(list(rot_minmax)))

    return augs


def create_detectron_img_dict_list(detectron_json_fpath, bbox_format = BoxMode.XYWH_ABS) -> List[dict]:
    """
    Creates a list of dictionaries to be used in detectron.
    :param detectron_json_fpath:
    :return:
    """
    json_data = load_json(detectron_json_fpath)
    images = json_data.get("images", [])
    logging.debug(f"Images: {images}")
    annotations = json_data.get("annotations", [])
    dict_list = []
    for img in images:
        current_img = {"file_name": img["file_name"],
                       "image_id": img["id"],
                       "width": img["width"],
                       "height": img["height"],
                       "annotations": []}
        for annotation in annotations:
            if annotation["image_id"] == current_img["image_id"]:
                current_img["annotations"].append({"segmentation": [],
                                                   "area": None,  # ToDo: Check if this might have to be box area.
                                                   "iscrowd": 0,
                                                   "category_id": annotation["category_id"],
                                                   "bbox_mode": bbox_format,
                                                   "bbox": annotation["bbox"]})
        dict_list.append(current_img)
    return dict_list


def visualize_detectron_prediction(prediction: dict, save_as=None, show_img=True):
    if show_img or save_as is not None:
        metadata = MetadataCatalog.get("detectron_instances_train")
        metadata.thing_classes = list(prediction["materials_dict"].values())
        img = cv2.imread(prediction["img_fpath"])
        img_name = prediction["img_name"]
        v = Visualizer(img[:, :, ::-1], metadata, scale=1.2)
        out = v.draw_instance_predictions(prediction["instances"].to("cpu"))
        if save_as is not None:
            out_dir = os.path.split(save_as)[0]
            if not os.path.isdir(out_dir):
                os.makedirs(out_dir)
            out.save(save_as)
        if show_img:
            cv2.namedWindow(img_name, cv2.WINDOW_NORMAL)
            cv2.imshow(img_name, out.get_image()[:, :, ::-1])
            cv2.waitKey(0)


def unpack_2d_tensor(input_tensor: tf.Tensor) -> np.array:
    return np.array([row.detach().numpy() for row in input_tensor])


def serialize_instance(prediction_result: dict) -> dict:
    """Turns a prediction result created by detectron2 into a dict that can be saved as json."""
    # Detectron2 boxes are stored as (x1, y1, x2, y2) tensors.
    instances = prediction_result["instances"]
    prediction_dict = {"img_name": prediction_result.get("img_name"),
                       "img_fpath": prediction_result.get("img_fpath"),
                       "instances": {"pred_boxes": unpack_2d_tensor(instances.get("pred_boxes")).tolist(),
                                     "box_centers": instances.get("pred_boxes").get_centers().detach().numpy().tolist(),
                                     "scores": unpack_2d_tensor(instances.get("scores")).tolist(),
                                     "pred_classes": unpack_2d_tensor(instances.get("pred_classes")).tolist(),
                                     },
                       "cfg": prediction_result.get("cfg"),
                       }
    return prediction_dict


def run_training(yolo_ds_root_dir: str,
                 model_yaml: str,
                 output_dir: str,
                 materials_dict: dict = None,
                 json_train: str = None,
                 json_val: str = None,
                 iterations: int = 2500,
                 ds_cfg_savename: str = "ds_catalog_train.json",
                 ds_name_train: str = "instances_detectron_train",
                 ds_name_val: str = "instances_detectron_val",
                 img_size_minmax: Tuple[int, int] = (1820, 1830),
                 device: str = "cuda",
                 filter_out_empty_imgs: bool = False,
                 max_detections_per_img: int = 2000,
                 number_of_workers: int = 2,
                 imgs_per_batch: int = 2,
                 base_lr: float = 0.00025,
                 lr_decay: list = None,
                 roi_heads_batch_size_per_img: int = 512,
                 roi_heads_iou_thresh: float = 0.5,
                 roi_heads_nms_thresh: float = 0.7,
                 roi_heads_score_thresh_train: float = 0.05,
                 roi_heads_score_thresh_test: float = 0.6,
                 rpn_nms_thresh: float = 0.7,
                 rpn_batch_size_per_img: int = 256,
                 retinanet_score_thresh_test: float = 0.05,
                 retinanet_nms_thresh_test: float = 0.5,
                 retinanet_iou_threshs: list = None,
                 augmentations: list = None,
                 **kwargs):
    """
    :param yolo_ds_root_dir:
    :param model_yaml: Must include parent dir, e.g. "COCO-Detection/faster_rcnn_R_101_C4_3x.yaml".
    :param output_dir:
    :param materials_dict:
    :param json_train: defaults to "{detectron_ds_target_dir}/"annotations/{ds_name_train}.json"
    :param json_val: defaults to "{detectron_ds_target_dir}/"annotations/{ds_name_val}.json"
    :param iterations:
    :param ds_cfg_savename:
    :param ds_name_train: defaults to instances_detectron_train
    :param ds_name_val: defaults to instances_detectron_val
    :param img_size_minmax:
    :param device: "cpu" or "cuda". Defaults to "cuda"
    :param filter_out_empty_imgs:
    :param max_detections_per_img:
    :param number_of_workers:
    :param imgs_per_batch:
    :param base_lr:
    :param lr_decay:
    :param roi_heads_batch_size_per_img:
    :param roi_heads_eval_thresh:
    :param roi_heads_iou_thresh:
    :param roi_heads_nms_thresh:
    :param roi_heads_score_thresh_train:
    :param roi_heads_score_thresh_test:
    :param rpn_nms_thresh:
    :param rpn_batch_size_per_img:
    :param retinanet_score_thresh_test:
    :param retinanet_nms_thresh_test:
    :param retinanet_iou_threshs:
    :param augmentations:
    :return:

    Model options (only for detection, other methods are not listed here):

    COCO-Detection/faster_rcnn_R_101_C4_3x.yaml
    COCO-Detection/faster_rcnn_R_101_DC5_3x.yaml
    COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml
    COCO-Detection/faster_rcnn_R_50_C4_1x.yaml
    COCO-Detection/faster_rcnn_R_50_C4_3x.yaml
    COCO-Detection/faster_rcnn_R_50_DC5_1x.yaml
    COCO-Detection/faster_rcnn_R_50_DC5_3x.yaml
    COCO-Detection/faster_rcnn_R_50_FPN_1x.yaml
    COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml
    COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml
    COCO-Detection/fast_rcnn_R_50_FPN_1x.yaml
    COCO-Detection/fcos_R_50_FPN_1x.py
    COCO-Detection/retinanet_R_101_FPN_3x.yaml
    COCO-Detection/retinanet_R_50_FPN_1x.py
    COCO-Detection/retinanet_R_50_FPN_1x.yaml
    COCO-Detection/retinanet_R_50_FPN_3x.yaml
    COCO-Detection/rpn_R_50_C4_1x.yaml
    COCO-Detection/rpn_R_50_FPN_1x.yaml
    """

    if not os.path.isdir(yolo_ds_root_dir):
        raise FileNotFoundError(f"Yolo style root dir does not exist: {yolo_ds_root_dir}")

    detectron_ds_target_dir = os.path.join(yolo_ds_root_dir.rstrip("/") + "_detectron")

    # Assign default values where arguments are None
    if json_train is None:
        json_train = os.path.join(detectron_ds_target_dir, "annotations", ds_name_train + ".json")
    if json_val is None:
        json_val = os.path.join(detectron_ds_target_dir, "annotations", ds_name_val + ".json")
    if lr_decay is None:
        lr_decay = []
    if augmentations is None:
        augmentations = []
    if retinanet_iou_threshs is None:
        retinanet_iou_thresh = [0.4, 0.5]
    if materials_dict is None:
        materials_dict = {0: "trash"}

    print("------------------------------------ TRAINING SETTINGS ----------------------------------------------------")
    print(f"Training on dataset {yolo_ds_root_dir}")
    print(f"Using model {model_yaml}")
    print(f"Running on device: {device}")
    print(f"Img. size (min, max): {img_size_minmax}")
    print("-----------------------------------------------------------------------------------------------------------")

    ds_convert.cvt_yolo_to_detectron(yolo_ds_root_dir)

    setup_logger()  # Detectron2 logger
    ds_convert.cvt_yolo_to_detectron(yolo_ds_root_dir, materials_dict=materials_dict)
    # Extract image dict lists from jsons
    logging.info("Img. dict lists extracted.")
    # Register classes
    classes = materials_dict
    logging.info("Classes registered.")

    cfg = get_cfg()

    # MODEL
    cfg.merge_from_file(model_zoo.get_config_file(model_yaml))
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(model_yaml)
    cfg.MODEL.DEVICE = device

    # OUTPUT
    cfg.OUTPUT_DIR = output_dir

    # DATASETS
    DatasetCatalog.register(ds_name_train, lambda: create_detectron_img_dict_list(json_train))
    DatasetCatalog.register(ds_name_val, lambda: create_detectron_img_dict_list(json_val))
    MetadataCatalog.get(ds_name_train).set(thing_classes=list(classes.values()))
    MetadataCatalog.get(ds_name_val).set(thing_classes=list(classes.values()))
    cfg.DATASETS.TRAIN = (ds_name_train,)
    cfg.DATASETS.TEST = (ds_name_val,)
    cfg.DATALOADER.NUM_WORKERS = number_of_workers
    cfg.DATALOADER.FILTER_EMPTY_ANNOTATIONS = filter_out_empty_imgs
    cfg.TEST.DETECTIONS_PER_IMAGE = max_detections_per_img  # set max detections per img
    cfg.INPUT.MIN_SIZE_TRAIN = (img_size_minmax[0],)  # minimum image size for the train set
    cfg.INPUT.MAX_SIZE_TRAIN = img_size_minmax[1]  # maximum image size for the train set
    cfg.INPUT.MIN_SIZE_TEST = img_size_minmax[0]  # minimum image size for the test set
    cfg.INPUT.MAX_SIZE_TEST = img_size_minmax[1]  # maximum image size for the test set

    # cfg.DATASETS.PROPOSAL_FILES_TRAIN =     # ToDo: Perhaps add the proposal files?

    # RPN
    cfg.MODEL.RPN.NMS_THRESH = rpn_nms_thresh
    cfg.MODEL.RPN.BATCH_SIZE_PER_IMAGE = rpn_batch_size_per_img

    # ROI_HEADS
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = roi_heads_batch_size_per_img
    cfg.MODEL.ROI_HEADS.NMS_THRESH_TEST = roi_heads_nms_thresh
    cfg.MODEL.ROI_HEADS.IOU_THRESHOLDS = [roi_heads_iou_thresh]
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(materials_dict.keys()) # Number of classes, not num_classes+1!
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TRAIN = roi_heads_score_thresh_train  # 0.5  # set threshold for this model
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = roi_heads_score_thresh_test  # 0.5  # set threshold for this model

    # RETINANET
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = retinanet_score_thresh_test
    cfg.MODEL.RETINANET.NMS_THRESH_TEST = retinanet_nms_thresh_test
    cfg.MODEL.RETINANET.IOU_THRESHOLDS = retinanet_iou_threshs

    # SOLVER
    cfg.SOLVER.IMS_PER_BATCH = imgs_per_batch
    cfg.SOLVER.BASE_LR = base_lr
    cfg.SOLVER.MAX_ITER = iterations
    cfg.SOLVER.STEPS = lr_decay  # [] to not decay learning rate

    logging.info("cfg set up completed.")

    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    logging.info("Output dir created")

    # Save dataset catalog entries:
    dataset_test_out = DatasetCatalog.get(ds_name_train)
    savefile = os.path.join(cfg.OUTPUT_DIR, ds_cfg_savename)
    with open(savefile, "w") as f:
        json.dump(dataset_test_out, f, indent=4)
        logging.info(f"Dataset Catalog (training) saved as {savefile}")

    # save training config cfg to yaml
    cfg_save_path = os.path.join(cfg.OUTPUT_DIR, "cfg.yaml")
    cfg_save_string = cfg.dump()
    with open(cfg_save_path, "w") as f:
        f.write(cfg_save_string)
    print(f"Saved model/training cfg in {cfg_save_path}")

    # Set up trainer
    if augmentations:
        print(f"Setting up CustomTrainer using a DatasetMapper that contains augmentations: {augmentations}")
        trainer = CustomTrainer(cfg)
        mapper_w_augs = dataset_mapper.DatasetMapper(cfg, augmentations=augmentations)
        trainer.build_train_loader(cfg, mapper_w_augs)
    else:
        print("No augmentations provided. Using default trainer.")
        trainer = DefaultTrainer(cfg)

    # Visualise augs


    logging.debug("Done setting up trainer.")
    trainer.resume_or_load(resume=False)

    logging.debug("Starting training.")
    trainer.train()
    print("Done training. Proceeding to evaluation.")

    # ToDo: move evaluation into its own function.
    # Prep evaluation
    # pretrained_model = "/content/drive/MyDrive/colab_outputs/2022-04-30_1030/model_final.pth"
    cfg.MODEL.WEIGHTS = os.path.join(cfg.OUTPUT_DIR, "model_final.pth")  # path to the model we just trained
    print(f"Evaluating model {os.path.join(cfg.OUTPUT_DIR, 'model_final.pth')}")
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = roi_heads_score_thresh_test  # set a custom testing threshold
    predictor = DefaultPredictor(cfg)

    # Evaluate
    evaluator = COCOEvaluator(ds_name_val,
                              tasks=("bbox",),
                              use_fast_impl=False,  # use a fast but unofficial implementation to compute AP
                              output_dir=output_dir)
    val_loader = build_detection_test_loader(cfg, ds_name_val)
    evaluation_results = inference_on_dataset(predictor.model, val_loader, evaluator)
    print(evaluation_results)

    # Save evaluation results
    eval_results_savepath = os.path.join(cfg.OUTPUT_DIR, "evaluation_results.txt")
    with open(eval_results_savepath, "w") as f:
        f.write(json.dumps(evaluation_results, indent=4))
    print("Done training and evaluating.")

    return evaluation_results


def evaluate_on_ds(model_output_dir: str, fpath_val_json: str, materials_dict=None, device="cpu"):
    if materials_dict is None:
        materials_dict = {0: "trash"}

    fpath_cfg = os.path.join(model_output_dir, "cfg.yaml")
    fpath_weights = os.path.join(model_output_dir, "model_final.pth")

    cfg = get_cfg()
    cfg.merge_from_file(fpath_cfg)
    cfg.MODEL.DEVICE = device
    cfg.MODEL.WEIGHTS = fpath_weights


def evaluate(fpath_model_dir: str, fpath_json_val: str, output_dir, materials_dict: dict = None,
             device: str = "cpu", filter_out_empty_imgs: bool = False, ds_name_val: str = "instances_detectron_val"):

    if materials_dict is None:
        materials_dict = {0: "trash"}

    cfg = get_cfg()
    cfg.merge_from_file(os.path.join(fpath_model_dir, "cfg.yaml"))
    cfg.MODEL.WEIGHTS = os.path.join(fpath_model_dir, "model_final.pth")
    cfg.MODEL.DEVICE = device
    cfg.OUTPUT_DIR = output_dir
    cfg.DATALOADER.FILTER_EMPTY_ANNOTATIONS = filter_out_empty_imgs

    DatasetCatalog.register(fpath_json_val, lambda: create_detectron_img_dict_list(fpath_json_val))
    MetadataCatalog.get(fpath_json_val).set(thing_classes=list(materials_dict.values()))
    cfg.DATASETS.TEST = (fpath_json_val,)

    cfg.OUTPUT_DIR = output_dir
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

    evaluator = COCOEvaluator(fpath_json_val,
                              tasks=("bbox",),
                              use_fast_impl=False,  # use a fast but unofficial implementation to compute AP
                              output_dir=output_dir)
    predictor = DefaultPredictor(cfg)

    val_loader = build_detection_test_loader(cfg, fpath_json_val)
    print(termcolor.colored("Evaluating ...", "green"))

    evaluation_results = inference_on_dataset(predictor.model, val_loader, evaluator)
    print(evaluation_results)
    print("Finished evaluation.")


if __name__ == "__main__":
    loglevel = logging.INFO
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)

    # # Evaluation
    # ds_04 = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_04_gnejna_with_duplicates/"
    # ds_convert.cvt_yolo_to_detectron(ds_04)
    # model_dir = "/media/findux/DATA/Documents/Malta_II/results/5343_2022-05-10_122636/"
    # json_val = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_04_gnejna_with_duplicates_detectron/annotations/instances_detectron_val.json"
    # out_dir = "/home/findux/Desktop/out/"
    # evaluate(model_dir, json_val, out_dir)

    # Run training on cluster:

    # # Augmentations & Dataset mapper
    # augmentations = [T.RandomBrightness(0.4, 1.6),
    #                  T.RandomFlip(0.5, horizontal=True, vertical=False),
    #                  T.RandomFlip(0.5, horizontal=False, vertical=True)]
    # ds_root = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_05_mini_gnejna/"
    # model = "COCO-Detection/faster_rcnn_R_50_DC5_1x.yaml"
    # eval_results = run_training(ds_root,
    #                             model,
    #                             "/home/findux/Desktop/aug_out_test/",
    #                             {0: "trash"},
    #                             augmentations=augmentations,
    #                             device="cpu",
    #                             iterations=100,
    #                             roi_heads_batch_size_per_img=128,
    #                             number_of_workers=8)

    # augs = parse_augs((0.3, 1.7), 0.5, 0.5, (0, 20))
    # augs = parse_augs()
    # print(augs)