#!/usr/bin/env python3

import logging
import os
import random
import shutil


class NotEnoughFiles(Exception):
    def __init__(self):
        error_message = "Not enough files available to reduce by the requested amount."
        super().__init__(error_message)


def shrink_yolo_training_set(base_ds_location, reduce_n, seed=42) -> None:
    """
    Reduces a yolo dataset by the amount of specified number of images. Moves files into an "unused_training_data" folder.
    :param base_ds_location: Path to the location containing the images and labels folders
    :param reduce_n: Amount of images to remove from dataset.
    :param seed: Seed for random selection of files to remove from training set.
    :return: None
    """
    base_dir = base_ds_location
    backup_dir = os.path.join(base_dir, "unused_training_data")
    img_dir = os.path.join(base_dir, "images/train")
    annot_dir = os.path.join(base_dir, "labels/train")
    try:
        os.mkdir(backup_dir)
    except FileExistsError:
        print(f"Reusing already existing folder for unused files: {backup_dir}")
    img_paths = [os.path.join(img_dir, img) for img in sorted(os.listdir(img_dir))]
    annot_paths = [os.path.join(annot_dir, annotation) for annotation in sorted(os.listdir(annot_dir))]
    img_names = [os.path.split(img)[-1] for img in sorted(os.listdir(img_dir))]
    annot_names = [os.path.split(annotation)[-1] for annotation in sorted(os.listdir(annot_dir))]
    assert len(img_names) == len(annot_names)
    if len(img_names) < reduce_n:
        raise NotEnoughFiles

    for img, annotation in zip(img_names, annot_names):
        assert img.split('.')[-2] == annotation.split('.')[-2]  # Same fname (w/o ext.)

    # Create indexes of files to move:
    random.seed(seed)
    indices = random.sample(list(range(len(img_names))), reduce_n)
    for i in indices:
        img_source = img_paths[i]
        assert os.path.split(img_source)[-1] == img_names[i]
        img_target = os.path.join(backup_dir, img_names[i])
        annot_source = annot_paths[i]
        assert os.path.split(annot_source)[-1] == annot_names[i]
        annot_target = os.path.join(backup_dir, annot_names[i])

        logging.debug(f"Moving {img_source} to {img_target}")
        logging.debug(f"Moving {annot_source} to {annot_target}")
        shutil.move(img_source, img_target)
        shutil.move(annot_source, annot_target)


if __name__ == "__main__":

    ds_path = "/opt/nfs/shared/scratch/bioblu/dataset_01_subsets/dataset_200/"
    reducy_by = 38
    shrink_yolo_training_set(ds_path, reducy_by)