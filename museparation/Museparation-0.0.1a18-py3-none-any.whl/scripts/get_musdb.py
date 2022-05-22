import os
import glob
import numpy as np

from ..util.load_dataset import load_set_xy
from ..util.split_validation import split_validation

def get_musdb(root_path):
	#Not yet implemented
	pass

def get_musdbhq(root_path):
	"""
	Script to load musdbhq 
	:param root_path: the root directory of MUSDB18HQ (containing train and test directories)
	:return: A dictionary {"train", "val", "test"} containing lists of dictionaries {"bass", "drums", "mixture", "other", "vocals"} containing the absolute path to respective track
	"""
	subsets = dict()
	instruments = ["bass", "drums", "mixture", "other", "vocals"]

	for subset in ["train", "test"]:
		subsets[subset] = load_set_xy(os.path.join(root_path, subset), instruments=instruments)

	subsets["val"], subsets["train"] = split_validation(subsets["train"])
	return subsets


