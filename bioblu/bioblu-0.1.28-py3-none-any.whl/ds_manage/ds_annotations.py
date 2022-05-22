#!/usr/bin/env python3

import base64
import cv2
import datetime
import glob
import io
from itertools import permutations
import json
import logging
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from pathlib import Path
import PIL
from PIL import Image
from PIL import UnidentifiedImageError
import re
import shutil
from typing import List, Set, Union, Tuple

# from bioblu.ds_manage import ds_split
from bioblu.ds_manage import bbox_conversions
from bioblu.main import YOLO_IMG_FORMATS

# from bioblu.ds_manage.bbox_conversions import coco_to_voc, coco_to_yolo, coco_to_labelme
# from bioblu.ds_manage.bbox_conversions import labelme_to_coco, labelme_to_voc, labelme_to_yolo
# from bioblu.ds_manage.bbox_conversions import voc_to_yolo, voc_to_coco, voc_to_labelme
# from bioblu.ds_manage.bbox_conversions import yolo_to_voc, yolo_to_coco, yolo_to_labelme


# ToDo: 1.) make the show_annotation script use class for color and add a label to each annotation.
#       2.) in create_yolo_annotation_txt_files(): Make this more generalizable, using list of categories and boxes.
#           Should include the possibility to receive empty bbox and category lists, only fname.


class BoxFormatError(Exception):
    def __init__(self):
        error_message = "Wrong BBox format."
        super().__init__(error_message)


# ToDo: Turn this into a dataclass?
class BBox:
    def __init__(self, bbox: List, material: str, bbox_format: str, img_width: int, img_height: int,
                 img_fpath=None, confidence=None):
        """

        :param bbox:
        :param material:
        :param bbox_format: can be one of: 'yolo', 'coco', 'voc', 'labelme'
        :param img_width:
        :param img_height:
        :param img_fpath:
        :param confidence:
        """
        self._BBOX_TYPE_OPTIONS = {'yolo', 'coco', 'voc', 'labelme'}
        self.material = material
        if bbox_format.lower() in self._BBOX_TYPE_OPTIONS:
            self.bbox_format = bbox_format.lower()
        else:
            raise ValueError(f'Invalid bbox type {type}. Possible bbox types: {self._BBOX_TYPE_OPTIONS}')
        self.bbox = bbox
        if self.bbox_format == "labelme":
            self.bbox = bbox_conversions.fix_labelme_point_order(self.bbox)
        self.img_width = img_width
        self.img_height = img_height
        self.img_dims_wh = (self.img_width, self.img_height)
        self.img_path = img_fpath
        self.img_name = None
        if self.img_path is not None:
            self.img_name = os.path.split(self.img_path)[-1]
        self.confidence = confidence

    @property  # Basically like a getter method, i.e. a dynamically-updating attribute.
    def box_center_xy(self) -> Tuple[int, int]:
        """
        Absolute center position in pixels (x, y). NOT relative to img size!
        :return:
        """
        assert self.bbox_format in self._BBOX_TYPE_OPTIONS
        _old_box_format = self.bbox_format
        if self.bbox_format != "voc":
            self.to_voc()
        xmin, ymin, xmax, ymax = self.bbox
        center = (int((xmin + xmax) * 0.5), int((ymin + ymax) * 0.5))
        return center

    # ToDo: Maybe change these conversions so that they are not happening in place, but return the new BBox object.
    def to_yolo(self):
        """Changes the bbox format."""
        if self.bbox_format != 'yolo':
            if self.bbox_format == 'voc':
                self.bbox = bbox_conversions.voc_to_yolo(self.bbox, self.img_width, self.img_height)
            elif self.bbox_format == 'coco':
                self.bbox = bbox_conversions.coco_to_yolo(self.bbox, self.img_width, self.img_height)
            elif self.bbox_format == 'labelme':
                self.bbox = bbox_conversions.labelme_to_yolo(self.bbox, self.img_width, self.img_height)
            self.bbox_format = 'yolo'
        else:
            print('Already in yolo format.')

    def to_voc(self):
        """Changes the bbox format."""
        if self.bbox_format != 'voc':
            if self.bbox_format == 'coco':
                self.bbox = bbox_conversions.coco_to_voc(self.bbox)
            elif self.bbox_format == 'labelme':
                self.bbox = bbox_conversions.labelme_to_voc(self.bbox)
            elif self.bbox_format == 'yolo':
                self.bbox = bbox_conversions.yolo_to_voc(self.bbox, self.img_width, self.img_height)
            self.bbox_format = 'voc'
        else:
            print('Already in voc format.')

    def to_coco(self):
        """Changes the bbox format."""
        if self.bbox_format != 'coco':
            if self.bbox_format == 'labelme':
                self.bbox = bbox_conversions.labelme_to_coco(self.bbox)
            elif self.bbox_format == 'voc':
                self.bbox = bbox_conversions.voc_to_coco(self.bbox)
            elif self.bbox_format == 'yolo':
                self.bbox = bbox_conversions.yolo_to_coco(self.bbox, self.img_width, self.img_height)
            self.bbox_format = 'coco'
        else:
            print('Already in coco format.')

    def to_labelme(self):
        """Changes the bbox format."""
        if self.bbox_format != 'labelme':
            if self.bbox_format == 'coco':
                self.bbox = bbox_conversions.coco_to_labelme(self.bbox)
            elif self.bbox_format == 'voc':
                self.bbox = bbox_conversions.voc_to_labelme(self.bbox)
            elif self.bbox_format == 'yolo':
                self.bbox = bbox_conversions.yolo_to_labelme(self.bbox, self.img_width, self.img_height)
            self.bbox_format = 'labelme'
        else:
            print('Already in labelme format.')

    def format_is_labelme(self) -> bool:
        if self.bbox_format == "labelme":
            return True
        else:
            return False

    def format_is_yolo(self) -> bool:
        if self.bbox_format == "yolo":
            return True
        else:
            return False

    def format_is_coco(self) -> bool:
        if self.bbox_format == "coco":
            return True
        else:
            return False

    def format_is_voc(self) -> bool:
        if self.bbox_format == "voc":
            return True
        else:
            return False

    def __str__(self):
        return f"{self.bbox_format} BBox. Material: {self.material}. Coords: {self.bbox}. " \
               f"Confidence: {self.confidence}. Image: {self.img_path}"


# ToDo: Turn this into a dataclass?
class LabelmeAnnotation:
    def __init__(self, abs_img_fpath: str = None, annotations: List[BBox] = None, flags=None, version=None):
        """
        :param abs_img_fpath:
        :param annotations:
        :param flags:
        :param version:
        """
        self.version = version
        self.full_img_path = abs_img_fpath
        self.flags = flags
        if self.flags is None:
            self.flags = {}

        self.shapes = []
        if not annotations:
            self.shapes = []
        else:
            for box in annotations:
                if not box.format_is_labelme():
                    print("WARNING: Original box is not in labelme format!")
                    box.to_labelme()
                if not box.img_path == abs_img_fpath:
                    print(f"WARNING: inconsistent paths:\nabs_img_fpath: {abs_img_fpath}\nbbox path: {box.img_path}")
                self.shapes.append(box)

        self.img_dims_wh = None
        self.img_data = None
        if self.full_img_path:
            self.img_data = encode_img_for_labelme(self.full_img_path)
            self.img_dims_wh = Image.open(self.full_img_path).size
            self.img_name = os.path.split(self.full_img_path)[-1]

    def to_json(self, target_dir):
        bbox_dicts = []
        for box in self.shapes:
            bbox_dicts.append(convert_bbox_to_shape_dict(box))
        out_dict = {"version": self.version,
                    "flags": self.flags,
                    "shapes": bbox_dicts,
                    "lineColor": [0, 255, 0, 128],
                    "fillColor": [255, 0, 0, 128],
                    "imagePath": self.img_name,
                    "imageData": self.img_data,
                    "imageHeight": self.img_dims_wh[1],
                    "imageWidth": self.img_dims_wh[0]
                    }
        target_path = os.path.join(target_dir, self.img_name.split('.')[-2]) + ".json"
        with open(target_path, 'w') as f:
            f.write(json.dumps(out_dict))

    def add_box(self, box: BBox):
        if not box.format_is_labelme():
            raise BoxFormatError
        else:
            self.shapes.append(box)


def add_set_column(annotations: pd.DataFrame, split_dict: dict, index_column_name='file_name') -> pd.DataFrame:
    # ToDo: refactor this into ds_split
    """
    Adds a column "set" to the annotations pd.df that has the values "train", "val" and "test", depending on which set
    the corresponding image belongs to.

    :param annotations: annotations dataframe
    :param split_dict: dict containing as key the set ("train", "val" or "test") and as values e.g. file names used to identify which set an image belongs to.
    :return: pd.DataFrame
    """
    for k, v in split_dict.items():
        for _img_name in v:
            annotations.loc[annotations[index_column_name] == _img_name, 'set'] = k
    return annotations


def all_imgs_have_yolo_annotation(fdir) -> bool:
    """
    Checks whether all image files in the folder have a corresponding .txt file.
    :param fdir:
    :return:
    """
    # Get names of files
    img_files = [os.path.split(fpath)[-1] for fpath in sorted(os.listdir(fdir)) if fpath.lower().endswith(YOLO_IMG_FORMATS)]
    img_names = [fpath.split('.')[0] for fpath in img_files]
    txt_files = [os.path.split(fpath)[-1] for fpath in sorted(os.listdir(fdir)) if fpath.lower().endswith(".txt")]
    txt_names = [fpath.split('.')[0] for fpath in txt_files]
    assert len(img_names) == len(set(img_names))
    # Check if they correspond
    for img in img_names:
        if img not in txt_names:
            print(f"Image {img} does not have a corresponding txt file.")
            return False
    # Check the reverse (only if more txt files than img files):
    if len(txt_names) > len(img_names):
        for txt in txt_names:
            if txt not in img_names:
                logging.debug(f"[ WARNING ] Text file {txt}.txt does not have a corresponding image file!")
    return True


def all_x_have_y(fdir: str, ext_x: str, ext_y: str):
    """
    Checks if all files (in folder fdir) with the extension ext_x have a corresponding file with the extension ext_y.
    :param fdir:
    :param ext_x:
    :param ext_y:
    :return:
    """
    flag = True
    x_files = [os.path.split(fpath)[-1] for fpath in sorted(os.listdir(fdir)) if fpath.lower().endswith(ext_x.lower())]
    x_names = [file.split('.')[0] for file in x_files]
    y_files = [os.path.split(fpath)[-1] for fpath in sorted(os.listdir(fdir)) if fpath.lower().endswith(ext_y.lower())]
    y_names = [file.split('.')[0] for file in y_files]
    for x in x_names:
        if x not in y_names:
            print(f"{x}.{ext_x} does not have a corresponding {x}.{ext_y}")
            flag = False
    return flag

def box_is_sliced(box: BBox,
                  vertical_cut_locations: List[int] = None,
                  horizontal_cut_locations: List[int] = None) -> bool:
    """
    Returns true if the BBox is cut by the lines provided.
    :param box: A BBox with the BBox.bbox_format "labelme"
    :param vertical_cut_locations:
    :param horizontal_cut_locations:
    :return:
    """
    if not box.format_is_labelme():
        box.to_labelme()

    [TLx, TLy], [BRx, BRy] = box.bbox
    # Check for vertical cuts:
    for vcut in vertical_cut_locations:
        if TLx < vcut < BRx:
            return True
    # Check for horizontal cuts:
    for hcut in horizontal_cut_locations:
        if TLy < hcut < BRy:
            return True
    # If none of the above triggered:
    return False


def convert_bbox_to_shape_dict(box: BBox) -> dict:
    """
    Transforms a BBox with the BBox.bbox_format "labelme" to a dict as used in the "shapes" list as used in a json
    anotation file created by labelme.
    :param box: BBox (using BBox.bbox_format "labelme"
    :return: dict with the keys ["label", "line_color", "fill_color", "points", "shape_type", "flags"]
    """
    if not box.format_is_labelme():
        raise BoxFormatError
    _shape = {"label": box.material,
              "line_color": None,
              "fill_color": None,
              "points": box.bbox,
              "shape_type": "rectangle",
              "flags": {}}
    return _shape


def count_yolo_annotations(fdir, yolo_format=True) -> int:
    """
    Counts all annotations in the folder and subfolders. Annotation format: yolo txt files. (Maybe make this flexible)
    """

    total_annotations = 0
    processed_files = 0
    for root, dir, files in os.walk(fdir):
        txt_files = []
        if yolo_format:
            if os.path.split(root)[-1] in ['train', 'test', 'valid']:
                txt_files = [file for file in files if file.endswith(".txt")]
        else:
            txt_files = [file for file in files if file.endswith(".txt")]

        if txt_files:
            for txt_file in txt_files:
                txt_filepath = os.path.join(root, txt_file)
                logging.info(f"Reading annotations from file: {txt_filepath}")
                with open(txt_filepath, 'r') as f:
                    annotation_lines = f.readlines()
                if annotation_lines:  # i.e. if there are annotations in the image.
                    total_annotations += len(annotation_lines)
                processed_files += 1
    print(f"{processed_files} annotations files processed.")
    return total_annotations


def create_coco_materials_dicts(materials_dict: dict) -> List[dict]:
    """
    Creates a list of material dicts as used in coco annotation files.
    :param materials_dict: unidirectional {index: material_name}
    :return:
    """
    coco_materials = []
    for index, material in materials_dict.items():
        coco_materials.append({"id": index,
                               "name": material,
                               "supercategory": material,
                               })
    return coco_materials


def cut_annotated_img_INCOMPLETE(img_fpath: str, annotations_fpath: str, vertical_cut_count: int,
                                 horizontal_cut_count: int,
                                 save_excluded_boxes_at_custom_location=None, materials_dict=None, show_preview=False):
    """
    Cuts an annotated image while keeping annotations that do not overlap with the cuts. Saves annotations as
    labelme-json files.
    :param img_fpath:
    :param annotations_fpath:
    :param vertical_cut_count:
    :param horizontal_cut_count:
    :param save_excluded_boxes_at_custom_location:
    :param materials_dict: {i, material)
    :return:
    """
    fname_main = os.path.split(img_fpath)[-1].split('.')[-2]
    assert fname_main == os.path.split(annotations_fpath)[-1].split('.')[-2]
    annotations = load_yolo_annotations(annotations_fpath, img_fpath, materials_dict=materials_dict)
    # Convert label types (in place):
    [box.to_labelme() for box in annotations]

    img_dims = Image.open(img_fpath).size
    img_width, img_height = img_dims
    logging.info(f"Width: {img_width} | Height: {img_height}")

    lm_annotation = LabelmeAnnotation(abs_img_fpath=img_fpath, annotations=annotations)
    vert_cut_locs, horz_cut_locs = get_cut_locations(vertical_cut_count, horizontal_cut_count, img_dims)

    if show_preview:
        show_planned_cuts(img_fpath, vert_cut_locs, horz_cut_locs, annotations_fpath)
        plt.show()

    sliced_boxes = []
    for box in annotations:
        assert box.format_is_labelme()
        if box_is_sliced(box, vertical_cut_locations=vert_cut_locs, horizontal_cut_locations=horz_cut_locs):
            logging.info("Box is sliced")
            sliced_boxes.append(box)
            # add a functionality that identifies which cuts are slicing the box.
        else:
            box_location_yx = get_box_location(box, vertical_cut_count, horizontal_cut_count)
            # ToDo: recalculate box dimensions for the new image
            # ToDo:  add new boxes into a dict {tile_yx: [boxes]} (if key in keys, append, else create). Or use setdefault
        # ToDo: cut the image
        # -

    logging.info(f"{len(sliced_boxes)} sliced box(es).")


def decode_labelme_imgdata(encoded_img: str) -> PIL.Image:
    """
    Decodes labelimg imageData to a
    :param encoded_img:
    :return:
    """
    img_bytes = base64.b64decode(encoded_img)
    img_decoded = Image.open(io.BytesIO(img_bytes))
    return img_decoded


def convert_bbox_coco_to_yolo_bbox(coco_bbox: list, img_width: int, img_height: int):
    """
    DEPRECATED.
    Use bbox_conversions module instead.

    Converts a bbox list from coco to yolo format
    :param coco_bbox:
    :param img_width:
    :param img_height:
    :return:
    """
    _bbox_x, _bbox_y, _bbox_width, _bbox_height = coco_bbox
    bbox_center_x_normalised = (_bbox_x + 0.5 * _bbox_width) / img_width
    bbox_center_y_normalised = (_bbox_y + 0.5 * _bbox_height) / img_height
    bbox_width_normalised = (_bbox_width / img_width)
    bbox_height_normalised = (_bbox_height / img_height)
    return [bbox_center_x_normalised, bbox_center_y_normalised, bbox_width_normalised, bbox_height_normalised]


def convert_df_coco_bbox_annotations_to_yolo(annotations_df: pd.DataFrame):
    """
    Converts annotations in a dataframe from coco to yolo style.
    :param annotations_df: Needs columns 'bbox', 'img_width', 'img_height'
    :return:
    """
    yolo_boxes = []
    for i, line in annotations_df.iterrows():
        _coco_bbox = line['bbox']
        _img_width, _img_height = line['img_width'], line['img_height']
        _yolo_bbox = bbox_conversions.coco_to_yolo(_coco_bbox, _img_width, _img_height)
        yolo_boxes.append(_yolo_bbox)
    annotations_df['yolo_bbox'] = yolo_boxes
    return annotations_df


def copy_image_files(img_source_dir: str, target_dirs: dict, annotations_df: pd.DataFrame):
    """
    Copies images according to a dictionary that contains target directories (for train, val and test), and an
    annotations_df dataframe that has info on which image belong to which set.
    ToDo: Now, "file_name" actually means "image_name". Change this so that it works on a name w/o exts.
    :param img_source_dir:
    :param target_dirs: dict: {'images':{<sets>: <setpath>}
    :param annotations_df: requires columns 'file_name', 'set'.
    :return:
    """
    print("Copying img files...")
    annotations_df_reduced = annotations_df.drop_duplicates(subset='file_name')
    assert len(annotations_df_reduced['file_name']) == \
           len(set(annotations_df['file_name'])) == \
           len(set(annotations_df_reduced['file_name']))

    for i, _img_name in enumerate(annotations_df_reduced['img_name']):
        _current_set = annotations_df_reduced.loc[annotations_df_reduced['img_name'] == _img_name, 'set'].values[0]
        logging.debug(f"{i}: {_img_name}:\t{_current_set}")
        _source_path = os.path.join(img_source_dir, _img_name)
        _target_path = os.path.join(target_dirs['images'][_current_set], _img_name)
        logging.debug(f'Copying {_img_name} from {_source_path} to {_target_path}')
        shutil.copyfile(_source_path, _target_path)
    logging.info(f'Copied {i + 1} images.')
    print('Done copying.')


def copy_yolo_files(source_dir: str, target_dirs: dict, annotations_df: pd.DataFrame):
    print("Copying img files...")
    annotations_df_reduced = annotations_df.drop_duplicates(subset='file_name')
    assert len(annotations_df_reduced['file_name']) == \
           len(set(annotations_df['file_name'])) == \
           len(set(annotations_df_reduced['file_name']))

    for i, _img_name in enumerate(annotations_df_reduced['img_name']):
        _current_set = annotations_df_reduced.loc[annotations_df_reduced['img_name'] == _img_name, 'set'].values[0]
        logging.debug(f"{i}: {_img_name}:\t{_current_set}")
        _source_path = os.path.join(source_dir, _img_name)
        _target_path = os.path.join(target_dirs['images'][_current_set], _img_name)
        logging.debug(f'Copying {_img_name} from {_source_path} to {_target_path}')
        shutil.copyfile(_source_path, _target_path)
    logging.info(f'Copied {i + 1} images.')
    print('Done copying.')


def create_yolo_annotation_txt_files(annotations: pd.DataFrame, target_directories: dict):
    """
    Takes a pandas dataframe (from a coco json) with the annotations and turns them into the corresponding txt files.
    ToDo: Make this more generalizable, using list of categories and boxes. Should include the possibility to receive
          empty bbox and category lists, only fname.
    :param annotations:
    :param target_directories:
    :return:
    """
    for category, _target_directory in target_directories['labels'].items():
        _annotations_set = annotations.loc[annotations['set'] == category, :]
        for img in _annotations_set['file_name'].unique():
            _fname_noext = img.split('.')[0]
            _fname_out = os.path.join(_target_directory, _fname_noext + '.txt')
            _file_out = []
            _img_annotations = _annotations_set.loc[_annotations_set['file_name'] == img, :]
            for i, label_line in _img_annotations.iterrows():
                _bbox = label_line['bbox']
                _file_out.append(create_yolo_annotation_line(label_line, _bbox) + '\n')
            with open(_fname_out, 'w') as f:
                f.writelines(_file_out)
    print('Done writing annotation files.')


def create_yolo_annotation_line(category_id_no: int, bbox: List[float]):
    """
    Takes a cateogry id and yolo-formatted bbox coordinates and returns a string to be used in the annotation file.
    :param category_id_no:
    :param bbox: [x_center_normalised, y_center_normalised, box_width_normalised, box_height_normalised]
    :return:
    """
    logging.debug(category_id_no)
    logging.debug(bbox)

    category_id = str(category_id_no)
    _bbox_annotation = category_id
    for boxval in bbox:
        _bbox_annotation = ' '.join([_bbox_annotation, str(boxval)])
    return _bbox_annotation


def create_fallback_yolo_materials_dict(yolo_root_dir) -> dict:
    """
    Creates a unidirectional materials dict: {i: str}
    :param yolo_root_dir:
    :return:
    """
    materials_dict = {}
    unique_material_ids = get_material_ids_from_yolo_ds(yolo_root_dir)
    for i in unique_material_ids:
        materials_dict[int(i)] = "unspecified_" + str(i)
    return materials_dict


def create_materials_dict(materials: Set[str], flip=False) -> dict:
    """
    Takes a materials set and returns a dictionary with an index for each unique material: {material: index}
    :param materials:
    :param flip: Flip the dict from {i: material} format to {material: i} format.
    :return:
    """
    mats_dict = {i: v for i, v in enumerate(materials)}
    if flip:
        mats_dict = {v: k for k, v in mats_dict.items()}
    return mats_dict


def create_yolo_directories(target_directory: str) -> dict:
    """
    Creates the target directory, with subfolders according to yolo requirements. Also creates a "..._testing" folder in
    the parent directory.
    :param target_directory: str
    :return: dictionary with target directory paths
    """
    path_img_train = os.path.join(target_directory, 'images/train')
    path_img_val = os.path.join(target_directory, 'images/valid')
    path_img_test = os.path.join(target_directory, 'images/test')

    path_labels_train = os.path.join(target_directory, 'labels/train')
    path_labels_val = os.path.join(target_directory, 'labels/valid')
    path_labels_test = os.path.join(target_directory, 'labels/test')
    try:
        os.mkdir(target_directory)
        os.makedirs(path_img_train)
        os.makedirs(path_img_val)
        os.makedirs(path_img_test)
        os.makedirs(path_labels_train)
        os.makedirs(path_labels_val)
        os.makedirs(path_labels_test)
        print('Created directories.')
    except FileExistsError:
        raise FileExistsError('One or more target directories already exist.')
    else:
        directories = {'images': {'train': path_img_train,
                                  'val': path_img_val,
                                  'test': path_img_test},
                       'labels': {'train': path_labels_train,
                                  'val': path_labels_val,
                                  'test': path_labels_test}}
        return directories


def encode_img_for_labelme(img_fpath):
    """
    Encodes an image into a string using io.BytesIO and base64 encoding as in labelme:
    https://github.com/wkentaro/labelme.
    :param img_fpath:
    :return:
    """
    image_pil = Image.open(img_fpath)
    with io.BytesIO() as f:
        image_pil.save(f, format="PNG")
        f.seek(0)
        img_data = f.read()
    encoded_img = base64.b64encode(img_data).decode("utf-8")
    logging.debug(f"Encoded img has type {type(encoded_img)}")
    return encoded_img


def get_all_fpaths_by_extension(root_fdir: str, ext: str) -> List[str]:
    """
    Recursively extracts all file paths to files ending with the given extension down the folder hierarchy (i.e. it
    includes subfolders).
    :param root_fdir: str. Root directory from where to start searching
    :param ext: extension. e.g. ".txt" or "WAV"
    :return:
    """
    file_paths = [str(path) for path in Path(root_fdir).rglob('*' + ext)]
    return file_paths


def get_annotation_from_line(line: str):
    """
    Extract a list with the bbox coordinates from a yolo line.
    Yolo annotation structure: "class renter_rel_x center_rel_y rel_width rel_height confidence"
    Note that confidence is optional. It might be there or not, depending on whether it is a ground truth or inference
    box.
    Example: "0 0.7222 0.234 0.12 0.17" (without confidence)
    Example: "0 0.7222 0.234 0.12 0.17 0.8104" (with confidence)
    :param line:
    :return:
    """
    pattern = re.compile(r'(^\d+) (\d\.\d+) (\d\.\d+) (\d\.\d+) (\d\.\d+)( \d\.\d+)?')
    try:
        matches = list(pattern.findall(line)[0])
    except IndexError:
        print(f'No annotations found in line {line}')
    else:
        # Remove last element if empty (the conficence value):
        if not matches[5]:
            matches = matches[:-1]

        matches = [float(elem) for elem in matches]
        matches[0] = int(matches[0])
        return matches


def get_bboxes_from_labelme_json(fpath_json: str) -> List[BBox]:
    """
    Assumes that the json is in labelme_format.
    :param fpath_json:
    :return:
    """
    json_content = load_json(fpath_json)
    img_name = json_content['imagePath']
    img_width = json_content["imageWidth"]
    img_height = json_content["imageHeight"]
    _json_dir = os.path.split(fpath_json)[0]
    img_path = os.path.join(_json_dir, img_name)
    bboxes = []
    if json_content["shapes"]:  # If there ARE boxes in the json:
        for annotation in json_content['shapes']:
            if annotation['shape_type'] == 'rectangle':
                point_0, point_1 = np.array(annotation['points'][0]), np.array(annotation['points'][1])
                # Correct for possibly wrong order of points (because labelme creates them in "click order")
                if np.all(point_0 > point_1):  # i.e. if first point is bottom-right, not top-left
                    point_0, point_1 = point_1, point_0
                box_coords = [list(point_0), list(point_1)]
                bbox = BBox(bbox=box_coords,
                            material=annotation["label"],
                            bbox_format="labelme",
                            img_width=img_width,
                            img_height=img_height,
                            img_fpath=img_path)
                logging.debug(type(bbox))
                bboxes.append(bbox)
    return bboxes


def get_materials_from_labelme_jsons(json_fdir) -> Set[str]:
    """Returns a set of all the materials found in the json files in the target dir."""
    json_files = get_paths_to_json_files(json_fdir)
    materials = []
    for json_path in json_files:
        json_data = load_json(json_path)
        file = json_data['imagePath']
        for bbox in json_data['shapes']:
            material = bbox['label'].lower()
            logging.info(f"{file}: {material}")
            materials.append(material)
    return set(materials)


def get_material_ids_from_yolo_ds(yolo_root_fdir) -> set:
    """
    Recursively extracts the material ids from txt files in a yolo-structured folder.
    :param yolo_root_fdir:
    :return:
    """
    fpaths = get_all_fpaths_by_extension(yolo_root_fdir, ".txt")
    id_set = set()
    for fpath in fpaths:
        with open(fpath, 'r') as f:
            lines = f.readlines()
        for line in lines:
            id_set.add(line.split(" ")[0])
    return id_set


def get_bg_img(fpath_annotations_json: str, img_dir: str):
    # ToDo: Make this take a json path or a pd.df?
    """Takes a COCO style json and checks for images which are not part of the json dataset."""
    annotation_data = load_json(fpath_annotations_json)
    img_info = pd.DataFrame({'id': [img['id'] for img in annotation_data['images']],
                             'img_name': [img['file_name'] for img in annotation_data['images']]})
    img_files = [file for file in os.listdir(img_dir) if not file.startswith('.')]
    assert set(img_info['img_name']) == set(img_files)
    bg_imgs = []
    for img in img_files:
        if img not in img_info['img_name'].values:
            bg_imgs.append(img)
    return bg_imgs


def get_max_dim(img_dir: str):
    """
    Returns the largest dimension (in pixels) found in all images in the provided image folder. Note that this might be
    x or y dimension, and that the corresponding image is not necessarily the largest image (it might theoretically be
    very narrow along the other dimension).
    :param img_dir:
    :return:
    """
    max_dim = 0
    _img_files = list_image_names(img_dir)
    for img_name in _img_files:
        _img = Image.open(os.path.join(img_dir, img_name))
        _dims = _img.size
        if max(_dims) > max_dim:
            max_dim = max(_dims)
    return max_dim


def get_max_annotation_count(fdir_annotations) -> int:
    """
    Returns the maximum number of annotations per image found among all the annotations files.
    :param fdir_annotations: Path to directory containing yolo-style annotation txt files.
    :return: int. Maximum number of annotations found per image.
    """
    max_n_annot = 0
    filepaths = sorted(os.listdir(fdir_annotations))
    filepaths = [path for path in filepaths if path.endswith(".txt")]
    # filepaths = sorted(glob.glob(fdir_annotations, "*.txt"))
    for path in filepaths:
        with open(path, "r") as f:
            lines = f.readlines()
        if len(lines) > max_n_annot:
            max_n_annot = len(lines)
    return max_n_annot


def get_annotations_paths(ds_root_dir, ext='.txt') -> List[str]:
    """
    Returns a list of the paths to all annotation files in the dataset (assumes a yolo-structured dataset).
    :param ds_root_dir: Base dir of a yolo dataset.
    :param ext: file extension to look for (e.g. ".txt")
    :return: list of paths
    """
    fpath_lab_dir = os.path.join(ds_root_dir, "labels")
    if not os.path.exists(fpath_lab_dir):
        raise FileNotFoundError("Dataset dir does not contain a 'labels' directory.")

    lab_fpaths = []
    lab_dirs = ["test", "train", "valid"]
    for fdir in lab_dirs:
        current_lab_dir = os.path.join(fpath_lab_dir, fdir)
        print(current_lab_dir)
        file_pattern = f"{current_lab_dir}/*{ext}"
        current_lab_fpaths = glob.glob(file_pattern)
        lab_fpaths.extend(current_lab_fpaths)
    return sorted(lab_fpaths)


def get_box_location(box: BBox, n_vcuts: int, n_hcuts: int) -> Tuple[int, int]:
    """
    Takes a labelme-formatted box and returns which quadrant the box is located in.
    :param box:
    :param n_vcuts:
    :param n_hcuts:
    :param img_dims_wh:
    :return:
    """
    if not box.format_is_labelme():
        box.to_labelme()
    vcuts, hcuts = get_cut_locations(n_vcuts, n_hcuts, box.img_dims_wh)
    assert not box_is_sliced(box, vcuts, hcuts)

    vcuts = [0] + vcuts + [box.img_dims_wh[0]]
    hcuts = [0] + hcuts + [box.img_dims_wh[1]]
    logging.info(f"Vertical cuts: {vcuts}")
    logging.info(f"Horizontal cuts: {hcuts}")

    col, row = None, None
    box_center = box.box_center_xy
    for v, vcut in enumerate(vcuts[:-1]):
        for h, hcut in enumerate(hcuts[:-1]):
            if point_within_limits(box_center, vcut, vcuts[v + 1], hcut, hcuts[h + 1]):
                col, row = v, h
    return row, col


def get_cut_locations(n_vertical_cuts, n_horz_cuts, img_dims_wh: Tuple[int, int]) -> Tuple[List[int], List[int]]:
    """
    Returns two lists, with the vertical and horizontal cut locations based on the number of cuts specified.
    :param n_vertical_cuts: int. Number of vertical cuts.
    :param n_horz_cuts: int. Number of horizontal cuts
    :param img_dims_wh: tuple. Image dimensions (width, height) in pixels.
    :return: Tuple([vertical cut locations], [horizontal cut locations])
    """
    img_width, img_height = img_dims_wh
    vertical_cut_locations = [int((img_width / (n_vertical_cuts + 1)) * (i + 1)) for i in range(n_vertical_cuts)]
    horizontal_cut_locations = [int((img_height / (n_horz_cuts + 1)) * (i + 1)) for i in range(n_horz_cuts)]
    return vertical_cut_locations, horizontal_cut_locations


def get_fname_only(fpath) -> str:
    """
    Strips off the file extension.
    :param fpath:
    :return:
    """
    fname = os.path.split(fpath)[-1]
    fname = fname.split('.')[0]
    return fname


def get_paths_to_json_files(fdir: str) -> List[str]:
    """
    Not recursive.
    Returns a list of paths (List[str]) to the json files found in the directory provided. The directory may have other
    file types than jsons files - these will be ignored and only the json files listed.
    :param fdir:
    :return:
    """
    json_fpaths = [os.path.join(fdir, fname) for fname in sorted(os.listdir(fdir)) if fname.endswith('.json')]
    return json_fpaths


def get_paths_to_json_files_r(fdir: str) -> List[str]:
    """
    Recursively outputs the paths to all json files in the provided directory (and possible subdirectories).
    :param fdir: string. Path to dir.
    :return: List of path strings to each file
    """
    pass  # ToDo


def get_img_paths(ds_root_dir: str, ext: str = '.tif') -> List[str]:
    """
    Returns a list of the paths to all image files in the dataset (assumes a yolo-structured dataset).
    :param ds_root_dir: Base dir of a yolo dataset.
    :param ext: file extension to look for (e.g. ".txt")
    :return: list of paths
    """
    fpath_img_dir = os.path.join(ds_root_dir, "images")
    if not os.path.exists(fpath_img_dir):
        raise FileNotFoundError("Dataset dir does not contain an 'images' directory.")

    img_fpaths = []
    img_dirs = ["test", "train", "valid"]
    for fdir in img_dirs:
        current_img_dir = os.path.join(fpath_img_dir, fdir)
        file_pattern = f"{current_img_dir}/*{ext}"
        current_lab_fpaths = glob.glob(file_pattern)
        img_fpaths.extend(current_lab_fpaths)
    return sorted(img_fpaths)


def img_arr_to_b64(img_arr):
    # UNUSED. PRIMED FOR DELETION.
    """
    copied from: https://github.com/wkentaro/labelme/blob/main/labelme/utils/image.py
    :param img_arr:
    :return:
    """
    img_pil = Image.fromarray(img_arr)
    f = io.BytesIO()
    img_pil.save(f, format="PNG")
    img_bin = f.getvalue()
    img_b64 = base64.encodebytes(img_bin)
    return img_b64


def list_image_names(img_dir: str) -> List[str]:
    """Returns a (sorted) list of filenames of images in a folder that can be opened by PIL.Image.open(). Note that
    they might be of various filetypes. Ignores files that can not be opened by PIL.Image.open()."""
    _files = sorted(os.listdir(img_dir))
    images = []
    for _fname_img in _files:
        try:
            _ = Image.open(os.path.join(img_dir, _fname_img))
        except UnidentifiedImageError:
            logging.info(f'{_fname_img} is not a readable image.')
        else:
            images.append(_fname_img)
    return images


def list_json_names(fdir: str) -> List[str]:
    """
    Returns an ordered list of all the json filenames in dfir.
    :param fdir:
    :return:
    """
    json_fnames = [file for file in sorted(os.listdir(fdir)) if file.endswith('.json')]
    assert len(json_fnames) == len(set(json_fnames))  # Make sure fnames are unique.
    return json_fnames


def load_coco_ds(fpath_coco_json: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Takes path to the root directory of a COCO-style data set, then extracts info from the annotations.json file in the
    <annotations> subfolder     and returns two pandas data frames, one with info on images, one with the annotations.
    :param coco_root_dir: str
    :return: (pd.DataFrame, pd.DataFrame)
    """
    json_data = load_json(fpath_coco_json)
    images = pd.DataFrame(json_data['images'])
    annotations = pd.DataFrame(json_data['annotations'])
    return images, annotations


def load_json(json_fpath: str) -> dict:
    """Returns json data as a dict."""
    with open(json_fpath, 'r') as f:
        data = json.load(f)
    logging.debug(f'Loaded json object (type): {type(data)}')
    return data


def load_labelme_annotation_file(fpath_json) -> LabelmeAnnotation:
    """
    Load the json file containing labelme annotations.
    Assumes that img files and corresponding JSON files are in the same directory!
    :param fpath_json:
    :return:
    """
    json_data = load_json(fpath_json)
    _loaded_bboxes = get_bboxes_from_labelme_json(fpath_json)
    logging.debug(f"First element of loaded boxes: {type(_loaded_bboxes[:1])}")
    _fpath_head = os.path.split(fpath_json)[0]
    _full_img_path = os.path.join(_fpath_head, json_data["imagePath"])
    logging.debug(_full_img_path)
    annotations = LabelmeAnnotation(abs_img_fpath=_full_img_path, annotations=_loaded_bboxes)
    return annotations


def load_yolo_annotations(fpath_annotations_txt: str, img_fpath: str, materials_dict=None) -> List[BBox]:
    """
    Loads annotations from a yolo annotation txt file
    :param fpath_annotations_txt:
    :param img_fpath:
    :param materials_dict: {index: material_str}, example: {0: "plastic"}
    :return:
    """
    # Initiate bboxes and deal with possibly missing materials dict.
    bboxes = []
    if materials_dict is None:
        materials_dict = {0: "unspecified"}
    # Open image and get dimensions
    img_dims_wh = (0, 0)
    try:
        img = Image.open(img_fpath)
    except FileNotFoundError:
        print(f"No file found at location {img_fpath}")
    except UnidentifiedImageError:
        print(f"Could not open file as an image: {img_fpath}")
    else:
        img_dims_wh = img.size
    # Load the annotations (i.e. BBoxes)
    confidence = None
    try:
        with open(fpath_annotations_txt, 'r') as f:
            annotations_raw = f.readlines()
    except FileNotFoundError:
        print(f"No annotation file found at: f{fpath_annotations_txt}")
    else:
        if annotations_raw:  # if there are any lines in the file
            for line in annotations_raw:
                logging.debug(type(line))
                logging.debug(line)
                current_box = get_annotation_from_line(line)
                material_index = int(current_box[0])
                current_bbox_coords = [float(num) for num in current_box[1:5]]  # inclusive:exclusive indexing
                assert len(current_bbox_coords) == 4
                if len(current_box) == 6:
                    confidence = current_box[5]
                # Look up material and provide fallback material ("unlisted material") if key is non-existent:
                current_box_mat = materials_dict.get(material_index, "unspecified")
                bboxes.append(BBox(current_bbox_coords, current_box_mat, "yolo",
                                   img_width=img_dims_wh[0], img_height=img_dims_wh[1], img_fpath=img_fpath,
                                   confidence=confidence))
    logging.info(f"Successfully loaded annotations file {fpath_annotations_txt}")
    return bboxes


def merge_img_info_into_labels(images: pd.DataFrame, labels: pd.DataFrame):
    """
    Used in converting coco ds to yolo. Not for converting labelme to yolo.
    :param images:
    :param labels:
    :return:
    """
    assert images.shape[0] == len(images['file_name'].unique())
    logging.info('Images data frame has one image per row.')
    for i, line in images.iterrows():
        _img_id = line["id"]
        _current_fname = line['file_name']
        _current_width = line['width']
        _current_height = line['height']

        labels.loc[labels['image_id'] == _img_id, 'file_name'] = _current_fname
        labels.loc[labels['image_id'] == _img_id, 'img_width'] = _current_width
        labels.loc[labels['image_id'] == _img_id, 'img_height'] = _current_height
    return labels


def point_within_limits(point_xy: Tuple[int, int], xmin: int, xmax: int, ymin: int, ymax: int) -> bool:
    """
    Checks whether a point lies within (or on) limits.
    Inclusive. If points lies ON the limit, is is still considered within.
    :param point_xy:
    :param xmin:
    :param xmax:
    :param ymin:
    :param ymax:
    :return:
    """
    ptx, pty = point_xy
    if xmin <= ptx <= xmax and ymin <= pty <= ymax:
        return True
    return False


def save_groundtruth_visualisations_INCOMPLETE(ds_base_dir, materials_dict=None, color="green"):
    """

    :param ds_base_dir:
    :param materials_dict:
    :param color:
    :return:
    """
    if materials_dict is None:
        materials_dict = {0: "unspecified"}

    fpaths_labels = get_annotations_paths(ds_base_dir)
    fpaths_imgs = get_img_paths(ds_base_dir)
    for labels_path, img_path in zip(fpaths_labels, fpaths_imgs):
        base_name = os.path.split(img_path)[-1].split('.')[0]
        assert base_name == os.path.split(labels_path)[-1].split('.')[0]

        labels = load_yolo_annotations(labels_path, img_path, )
        # ToDo: finish this


def save_readable_json(fpath_json, fpath_output: str = None) -> None:
    """Takes an existing json and saves it as a neatly formatted json."""
    if fpath_output is None:
        tstamp = format(datetime.datetime.now(), '%Y_%m_%d-%H%M')
        fpath_output = '/home/findux/Desktop/readable_json_' + tstamp + '.json'
    json_data = load_json(fpath_json)
    with open(fpath_output, 'w') as f:
        json.dump(json_data, f, indent=4)


def make_json_readable(fpath_json, overwrite=True) -> None:
    """Overwrites an already existing json with a neatly formatted version of itself, or (if overwrite is set to false,
    creates a new file with a timestamp in the file name in the same location)"""
    json_data = load_json(fpath_json)
    file_out = fpath_json
    if not overwrite:
        tstamp = format(datetime.datetime.now(), '%Y_%m_%d-%H%M')
        file_out = fpath_json + tstamp + '.json'
    with open(file_out, 'w') as f:
        json.dump(json_data, f, indent=4)


def save_to_json(obj, out_path) -> None:
    """saves an object as a json file"""
    with open(out_path, "w") as f:
        json.dump(obj, f, indent=4)


def show_planned_cuts(fpath_img: str, vcut_locations: List[int], hcut_locations: List[int], fpath_annot: str = None):
    if fpath_annot is not None:
        visualize_single_img_annotations_yolo(fpath_img, fpath_annot)
    else:
        plt.imshow(Image.open(fpath_img))
    for vcut in vcut_locations:
        plt.axvline(x=vcut, color='white')
    for hcut in hcut_locations:
        plt.axhline(y=hcut, color='white')


def visualize_coco_annotations(coco_json_fpath: str):
    """
    NOTE: Only covers the images in one folder!
    Shows the images of a coco data set and the corresponding bounding boxes.
    Takes as input the link to the image directory, and a merged pd.DataFrame that includes the img file names.
    :param img_directory: string to image directory (required for loading the actual image for displaying.
    :param annotations_df: Merged annotations df (with filenames)
    :return:
    """
    json_data = load_json(coco_json_fpath)
    images = json_data["images"]
    annotations = json_data["annotations"]

    for img_entry in images:
        img_path = img_entry["file_name"]
        img_name = os.path.split(img_path)[-1]
        img_id = img_entry["id"]
        img = plt.imread(img_path)

        fig, ax = plt.subplots()
        ax.imshow(img)

        annotation_count = 0
        for annotation in annotations:
            if annotation["image_id"] == img_id:
                bbox = annotation["bbox"]
                logging.debug(f"Bbox: {bbox}")
                rect = patches.Rectangle(bbox[:2], bbox[2], bbox[3], color='red', fill=None)  # Rectangle(xy, width, height, ...)
                ax.add_patch(rect)
                annotation_count += 1

        print_text = f'{img_name}  |  Img. ID: {img_id}  |  Annotations: {annotation_count}'
        plt.text(0, -30, print_text)
        fig.canvas.manager.full_screen_toggle()
        plt.show()


def update_all_labelme_materials(fpath_dir: str, old_material: str, new_material: str, backup_dir=None) -> None:
    """
    Updates all old materials in all labelme json files in the current directory to new material.
    WARNING: All json files in the directory must be labelme_json_files.
    :param fpath_dir:
    :param old_material:
    :param new_material:
    :param backup_dir:
    :return:
    """
    json_files = [fname for fname in sorted(os.listdir(fpath_dir)) if fname.endswith(".json")]
    json_fpaths = [os.path.join(fpath_dir, fname) for fname in json_files]
    for json_fpath in json_fpaths:
        print(f"Processing file {os.path.split(json_fpath)[1]}")
        update_material_in_labelme_file(json_fpath, old_material, new_material, backup_dir)


def update_material_in_labelme_file(json_fpath: str, old_mat: str, new_mat: str, backup_dir=None) -> None:
    """
    Updates the annotations in a given json file and replaces the old material with the new one.
    """
    img_annotations = load_labelme_annotation_file(json_fpath)

    # Check if file will be changed and back it up if a backup dir has been provided.
    if backup_dir is not None:
        for bbox in img_annotations.shapes:
            if bbox.material == old_mat:
                if not os.path.isdir(backup_dir):
                    os.mkdir(backup_dir)
                shutil.copyfile(json_fpath, os.path.join(backup_dir, os.path.split(json_fpath)[1]))
                break  # One occurrence is enough to trigger making a backup.

    # Overwrite material in relevant boxes:
    img_path = img_annotations.full_img_path
    for i, bbox in enumerate(img_annotations.shapes):
        if bbox.material == old_mat:
            print(f"Updating material {bbox.material} to {new_mat} for box {i} in img {img_path}")
            bbox.material = new_mat
            # (bc. lists are mutable, there's no need for img_annotations.shapes[i].material = new_mat)
    img_annotations.to_json(os.path.split(json_fpath)[0])


def visualize_single_img_annotations_coco(img_name: str, img_dir: str, annotations_df: pd.DataFrame, prefix_text: str = ""):
    """Shows the annotation boxes"""
    _img_annotations = annotations_df
    _img_annotations["basename"] = [os.path.split(line["file_name"])[0] for i, line in _img_annotations.iterrows()]
    _img_annotations = annotations_df.loc[annotations_df['basename'] == img_name, :]
    logging.debug(_img_annotations)
    _annotation_count = _img_annotations.shape[0]
    _current_id = _img_annotations['image_id'].unique()
    try:
        _img = Image.open(os.path.join(img_dir, img_name))
    except FileNotFoundError:
        print(f'Image {img_name} not found in {img_dir}. Did you use uppercase where necessary?')
    else:
        _fig, _ax = plt.subplots()
        _ax.imshow(_img)
        for _, _line in _img_annotations.iterrows():
            _bbox = _line['bbox']
            _rect = patches.Rectangle(_bbox[:2], _bbox[2], _bbox[3], color='red', fill=None)
            _ax.add_patch(_rect)

        print_text = prefix_text + f'  |  {img_name}  |  Img-ID: {_current_id}  |  Annotations: {_annotation_count}'
        plt.text(0, -30, print_text)
        _fig.canvas.manager.full_screen_toggle()
        plt.show()


def visualize_yolo_predictions_and_ground_truths(fpath_img, fpath_gt_annotations, fpath_pred_annotations,
                                                 materials_dict=None, save_location=None, additional_text=""):
    """
    Displays a comparison of ground truths and predictions.
    :param fpath_img:
    :param fpath_gt_annotations:
    :param fpath_pred_annotations:
    :param materials_dict: {i: material_str}
    :param save_location: a directory
    :param additional_text:
    :return:
    """
    if materials_dict is None:
        materials_dict = {0: "unspecified"}
    # Read Image
    try:
        img = Image.open(fpath_img)
    except (FileNotFoundError, UnidentifiedImageError):
        print(f"Cannot open image at: {fpath_img}")
    else:
        img_name = os.path.split(fpath_img)[-1]
        img_width, img_height = img.size

        fig, ax = plt.subplots()
        ax.imshow(img)

        predictions = load_yolo_annotations(fpath_pred_annotations, fpath_img, materials_dict)
        for bbox in predictions:
            assert bbox.bbox_format == "yolo"
            coco_box = bbox_conversions.yolo_to_coco(bbox.bbox, img_width, img_height)
            box_patch = patches.Rectangle(coco_box[:2], coco_box[2], coco_box[3], color="red", fill=None, linewidth=1.5)
            confidence = bbox.confidence
            plt.text(coco_box[0], coco_box[1], s=confidence, c='white', va='bottom', size=6)
            ax.add_patch(box_patch)

        ground_truths = load_yolo_annotations(fpath_gt_annotations, fpath_img, materials_dict)
        for bbox in ground_truths:
            assert bbox.bbox_format == "yolo"
            coco_box = bbox_conversions.yolo_to_coco(bbox.bbox, img_width, img_height)
            box_patch = patches.Rectangle(coco_box[:2], coco_box[2], coco_box[3], color="lime", fill=None)
            ax.add_patch(box_patch)

        print_text = f'{img_name} |  ' + additional_text
        plt.text(0, -30, print_text)
        fig.canvas.manager.full_screen_toggle()
        if save_location:
            save_as = save_location + img_name.split(".")[0] + "_comparison.png"
            plt.savefig(save_as, bbox_inches='tight', dpi=300)
        plt.show()


def visualize_single_img_annotations_yolo(fpath_img: str, color="red", materials_dict=None):
    """
    ToDo: Implement color palette per class
    :param fpath_img:
    :param color:
    :param materials_dict: {i: material}
    :return:
    """
    if materials_dict is None:
        materials_dict = {0: "trash"}

    img_base_name = os.path.split(fpath_img)[-1].split('.')[0]
    fpath_annotations = os.path.join(os.path.split(fpath_img)[0], img_base_name + ".txt")
    logging.debug(f"Showing {os.path.split(fpath_img)[-1]} with annotations from {os.path.split(fpath_annotations)[-1]}")
    try:
        img = Image.open(fpath_img)
    except (FileNotFoundError, UnidentifiedImageError):
        print(f"Cannot open image at: {fpath_img}")
    else:
        img_name = os.path.split(fpath_img)[-1]
        img_width, img_height = img.size
        bboxes = load_yolo_annotations(fpath_annotations, fpath_img, materials_dict)
        annotation_count = len(bboxes)
        fig, ax = plt.subplots()
        ax.imshow(img)

        for bbox in bboxes:
            assert bbox.bbox_format == "yolo"
            coco_box = bbox_conversions.yolo_to_coco(bbox.bbox, img_width, img_height)
            box_patch = patches.Rectangle(coco_box[:2], coco_box[2], coco_box[3], color=color, fill=None)
            ax.add_patch(box_patch)

        print_text = f'{img_name} |  Annotations: {annotation_count}'
        plt.text(0, -30, print_text)
        fig.canvas.manager.full_screen_toggle()


def visualize_all_yolo_annotations(fdir, materials_dict = None):
    if materials_dict is None:
        materials_dict = create_fallback_yolo_materials_dict(fdir)
    img_paths = [os.path.join(fdir, img) for img in sorted(os.listdir(fdir)) if img.lower().endswith(YOLO_IMG_FORMATS)]
    for fpath in img_paths:
        print(fpath)
        visualize_single_img_annotations_yolo(fpath, materials_dict=materials_dict)
        plt.show()


if __name__ == '__main__':

    loglvl = logging.DEBUG
    logformat = "[%(levelname)s]\t%(funcName)15s: %(message)s"
    logging.basicConfig(format=logformat)
    logger = logging.getLogger()
    logger.setLevel(loglvl)
    logging.getLogger('matplotlib.font_manager').disabled = True
    # logger = logging.getLogger(__name__)
    # logger.setLevel(loglvl)
    # # logging.disable()

    fdir = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_06_no_duplicates/"
    all_corresponding = all_imgs_have_yolo_annotation(fdir)
    print(f"All are corresponding: {all_corresponding}")

    fpath_img = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_06_no_duplicates/Paradise_Bay_DJI_0461_0-1.tif"
    fdir = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_06_no_duplicates/all_materials/"
    print(all_x_have_y(fdir, "txt", "tif"))
    print(all_x_have_y(fdir, "tif", "txt"))
    # visualize_all_yolo_annotations(fdir, materials_dict={0: "trash"})

    # fdir = "/media/findux/DATA/Documents/Malta_II/datasets/dataset_06_no_duplicates/all_materials/"
    # update_all_labelme_materials(fdir, "plastic", "trash")
