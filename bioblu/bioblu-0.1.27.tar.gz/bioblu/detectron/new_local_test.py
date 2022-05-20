#!/usr/bin/env python3

import cv2
import json
import logging
import numpy as np
import os
import random
from typing import List

import detectron2
from detectron2.data.datasets import register_coco_instances
from detectron2.utils.logger import setup_logger
from detectron2 import model_zoo
# from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
# from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import BoxMode
from detectron2.engine import DefaultTrainer
from detectron2.structures import BoxMode

from bioblu.detectron import detectron
from bioblu.ds_manage import ds_annotations
from bioblu.ds_manage import ds_convert

if __name__ == "__main__":

    loglevel = logging.DEBUG
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)
    # logging.disable()

    # Detectron2 logger
    setup_logger()

    # DS setup
    materials_dict = {0: "trash"}
    ds_root_dir = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_04_gnejna_with_duplicates"
    coco_ds = ds_root_dir + "_coco"
    logging.info(f"Yolo ds: {ds_root_dir}")
    logging.info(f"Coco ds: {coco_ds}")

    ds_convert.cvt_yolo_to_detectron(ds_root_dir, coco_ds, materials_dict)

    # Extract image dict lists from jsons
    fpath_json_train = os.path.join(coco_ds, "train/train.json")
    fpath_json_valid = os.path.join(coco_ds, "valid/valid.json")
    fpath_json_test = os.path.join(coco_ds, "test/test.json")

    train_imgs = detectron.create_detectron_img_dict_list(fpath_json_train)
    valid_imgs = detectron.create_detectron_img_dict_list(fpath_json_valid)
    test_imgs = detectron.create_detectron_img_dict_list(fpath_json_test)

    classes = materials_dict.values()

    # ### COPIED FROM TUTORIAL:
    cfg = get_cfg()

    DatasetCatalog.register("category_train", lambda: detectron.create_detectron_img_dict_list(fpath_json_train))
    DatasetCatalog.register("category_valid", lambda: detectron.create_detectron_img_dict_list(fpath_json_valid))
    DatasetCatalog.register("category_test", lambda: detectron.create_detectron_img_dict_list(fpath_json_test))
    MetadataCatalog.get("category_train").set(thing_classes=classes)
    MetadataCatalog.get("category_valid").set(thing_classes=classes)
    MetadataCatalog.get("category_test").set(thing_classes=classes)
    logging.info("Instances registered.")

    # microcontroller_metadata = MetadataCatalog.get("category_train")
    metadata_train = MetadataCatalog.get("category_train")
    metadata_valid = MetadataCatalog.get("category_valid")
    logging.info("Registered metadata.")

    cfg.DATASETS.TRAIN = ("category_train",)
    cfg.DATASETS.TEST = ("category_valid",)
    logging.info("Created TRAIN and TEST cfg.DATASET attributres.")

    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_C4_1x.yaml"))
    logging.debug("Merged from model zoo.")

    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_50_C4_1x.yaml")  # Let training initialize from model zoo
    logging.info("Loaded model weights checkpoint from model zoo.")

    logging.info("Assigning worker numders, batch ims, lr and max iterations.")
    cfg.DATALOADER.NUM_WORKERS = 2
    cfg.SOLVER.IMS_PER_BATCH = 2
    cfg.SOLVER.BASE_LR = 0.00025  # pick a good LR
    cfg.SOLVER.MAX_ITER = 1200    # 300 iterations seems good enough for the tutorial dataset; you will need to train longer for a practical dataset
    cfg.SOLVER.STEPS = []        # do not decay learning rate
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   # faster, and good enough for this toy dataset (default: 512)
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1  # only has one class (ballon). (see https://detectron2.readthedocs.io/tutorials/datasets.html#update-the-config-for-new-datasets)
    # # NOTE: this config means the number of classes, but a few popular unofficial tutorials incorrect uses num_classes+1 here.
    #
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
    logging.debug("Created output dir.")

    # logging.info("Test output:")
    # for d in random.sample(train_imgs, 3):
    #     print("FUCKTHEDUCK")
    #     # img = cv2.imread(d["file_name"])
    #     # visualizer = Visualizer(img[:, :, ::-1], metadata= metadata_train, scale=0.5)
    #     # out = visualizer.draw_dataset_dict(d)
    #     # cv2.imshow("Fig", out.get_image()[:, :, ::-1])

    # trainer = DefaultTrainer(cfg)
    # logging.debug("Set up trainer.")
    # trainer.resume_or_load(resume=False)
    # logging.debug("Starting training.")
    # trainer.train()

    # json_fpath = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_04_gnejna_with_duplicates_COCO/annotations/gnejna_train.json"
    # ds_annotations.save_readable_json(json_fpath, "/home/findux/Desktop/gnejna_train.json")
    # img_dict_list = detectron.create_detectron_img_dict_list(json_fpath)
    # ds_annotations.save_to_json(img_dict_list, "/home/findux/Desktop/img_dict_list.json")