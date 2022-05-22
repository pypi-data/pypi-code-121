import os
import glob
import numpy as np



def load_set_xy(path, instruments):
	"""
	Loads the set in 0th axis configuration (a lot of directories, each with tracks with the instrument names)
	:param path: Path to the set (train set / test set, not the full dataset)
	:param instrument: List of instruments that will be loaded (the name of the track files must be exact)
	:return: List of dictionaries, each with key-instrument names and value-path to the track
	"""
	tracks = glob.glob(os.path.join(path, "*"))
	samples = list()

	for track_folder in sorted(tracks):
		track = dict()
		for stem in instruments:
			audio_path = os.path.join(track_folder, stem + ".wav")
			track[stem] = audio_path
		samples.append(track)
	
	return samples


def load_set_yx(path, instruments):
	"""
	Loads the set in 1st axis configuration (instrument length of directories, filled with a lot of tracks)
	:param path: Path to the set (train set / test set, not the full dataset)
	:param instrument: List of instruments that will be loaded (the name of the directories must be exact)
	:return: dictionary of Lists, each with key-instrument names and value-list of paths to the track
	"""
	samples = dict()

	for track in instruments:
		samples[track] = sorted(glob.glob(os.pash.join(path, track, "*")))
	
	return samples
	
	
def yx_to_xy(yx_set, shuffle = True):
	"""
	converts the return of load_set_yx to be the same configuration as the return of load_set_xy (minimum length will be used)
	:param yx_set: Return value of load_set_yx
	:param shuffle: shuffles the configuration
	:return: Return value of load_set_xy
	"""
	subsets = list()
	min_length = min([len(i) for i in yx_set])


	if shuffle:
		for key in yx_set:
			yx_set[key] = np.shuffle(yx_set[key])


	for i in min_length:
		sample = {key : yx_set[key][i] for key in yx_set}
		subsets.append(sample)
	
	return subsets

