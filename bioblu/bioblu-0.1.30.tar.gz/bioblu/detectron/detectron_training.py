#!/usr/bin/env python3
import datetime

import argparse
import logging
from bioblu.detectron import detectron
from bioblu.ds_manage import ds_annotations


def main(**kwargs):
    kwargs["materials_dict"] = None
    if kwargs["materials"] is not None:
        kwargs["materials_dict"] = ds_annotations.create_materials_dict(kwargs["materials"])

    augs = detectron.parse_augs(brightness_minmax=kwargs.get("brightness_minmax"),
                                rot_minmax=kwargs.get("rot_minmax"),
                                flip_v=kwargs.get("flip_v"),
                                flip_h=kwargs.get("flip_h"))
    kwargs["augmentations"] = augs

    print("-----------------------------------------------------------------------------------------------------------")
    print("PASSED ARGUMENTS:")
    for k, v in kwargs.items():
        print(f"{k}:\t{v}")
    print("-----------------------------------------------------------------------------------------------------------")

    detectron.run_training(**kwargs)


if __name__ == "__main__":
    loglevel = logging.INFO
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(level=loglevel, format=logformat)
    # logging.disable

    # ToDo: Use None instead of deafaults and then never touch thouse values during training

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--ds-dir", type=str, default=None, dest="yolo_ds_root_dir", help="Path to the yolo-styled dataset root folder.")
    parser.add_argument("-m", "--model-yaml", type=str, default=None, dest="model_yaml", help="Path to the model yaml.")
    parser.add_argument("-o", "--output-dir", type=str, default="", dest="output_dir", help="Path to output dir", )
    parser.add_argument("-mats", "--materials", type=str, default=None, dest="materials", nargs="+", help="Materials (in order of class indices)")
    parser.add_argument("-t", "--json-train", type=str, default=None, dest="json_train")
    parser.add_argument("-v", "--json-val", type=str, default=None, dest="json_val")
    parser.add_argument("-i", "--iterations", type=int, default=None, dest="iterations", help="Number of iterations.")
    parser.add_argument("--ds-savename", type=str, default="ds_catalog_train.json", dest="ds_cfg_savename")
    parser.add_argument("--ds-name-train", type=str, default="instances_detectron_train", dest="ds_name_train")
    parser.add_argument("--ds-name-val", type=str, default="instances_detectron_val", dest="ds_name_val")
    parser.add_argument("--img-size", type=int, nargs=2, default=None, dest="img_size_minmax")
    parser.add_argument("--device", type=str, default="cuda", dest="device")
    parser.add_argument("--filter-out-empties", action="store_true", default=False, dest="filter_out_empty_imgs")
    parser.add_argument("-nd", "--max-detections", type=int, default=2000, dest="max_detections_per_img")
    parser.add_argument("-w", "--workers", type=int, default=None, dest="number_of_workers")
    parser.add_argument("-ni", "--imgs-per-batch", type=int, default=None, dest="imgs_per_batch")
    parser.add_argument("-lr", "--base-lr", type=float, default=None, dest="base_lr", help="Base learning rate.")
    parser.add_argument("-ld", "--lr-decay", default=None, dest="lr_decay", help="Learning rate decay.")
    parser.add_argument("-b", "--roi-batch-size", type=int, default=None, dest="roi_heads_batch_size_per_img", help="ROI heads batch size per image")
    parser.add_argument("-iou", "--roi-heads-iou-thresh", type=float, default=None, dest="roi_heads_iou_thresh")
    parser.add_argument("--roi-heads-nms-thresh", type=float, default=None, dest="roi_heads_nms_thresh")
    parser.add_argument("-ct", "--roi-conf-train", type=float, default=None, dest="roi_heads_score_thresh_train")
    parser.add_argument("-cv", "--roi-conf-test", type=float, default=None, dest="roi_heads_score_thresh_test")
    parser.add_argument("--rpn-nms-thresh", type=float, default=None, dest="rpn_nms_thresh")
    parser.add_argument("--rpn-batch-size-per-img", type=int, default=None, dest="rpn_batch_size_per_img")
    parser.add_argument("--retinanet-score-thresh-test", type=float, default=None, dest="retinanet_score_thresh_test")
    parser.add_argument("--retinanet-nms-thresh-test", type=float, default=None, dest="retinanet_nms_thresh_test")
    parser.add_argument("--retinanet-iou-threshs", type=float, nargs=2, default=None, dest="retinanet_iou_threshs")
    parser.add_argument("-c", "--color-mode", type=str, default=None, dest="color_mode")
    # Augmentations parameters
    parser.add_argument("--rot-minmax", type=float, nargs=2, default=None, dest="rot_minmax")
    parser.add_argument("--brighness-min-max", type=float, nargs=2, default=None, dest="brightness_minmax")
    parser.add_argument("--flipv", type=float, default=None, dest="flip_v")
    parser.add_argument("--fliph", type=float, default=None, dest="flip_h")

    args = parser.parse_args()
    kwargs = vars(args)

    main(**kwargs)
