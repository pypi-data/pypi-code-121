import h5py
import os
import numpy as np

from .load_audio import load_audio

def create_hdf(hdf_dir_path, filename, data, *, source=None, output=["bass", "drums", "other", "vocals"], sr=44100, mono=False):
	"""
	Create an hdf database for the particular use case
	:param hdf_dir_path: path to hdf directory
	:param filename: the name of the hdf file (xxxx.hdf5)
	:param data: (list of dictionaries) the data to be inserted
	:param source: the key for the source audio path (key refers to the key in data), None would mean the source will be computed as the sum of output
	:param output: a list of keys to be used as the output 
	:param sr: sample rate for the audio
	:param mono: True if data should be summed into mono
	:return: (String) path to the hdf5 file
	"""
	if(not os.path.exists(hdf_dir_path)):
		os.makedirs(hdf_dir_path)

	hdf_path = os.path.join(hdf_dir_path, filename + ".hdf5")
	with h5py.File(hdf_path, 'w') as f:
		#set f.attrs for sr, channels, and instruments maybe?

		for index, datum in enumerate(data):
			stem_audio = []
			for stem in output:
				audio_data, _ = load_audio(datum[stem], sr=sr, mono=mono)
				stem_audio.append(audio_data)
			
			if(source):
				mix_data, _ = load_audio(datum[source], sr=sr, mono=mono)
			else:
				min_length = min([i.shape[1] for i in stem_audio])
				stem_audio = [i[:, :min_length] for i in stem_audio]
				mix_data = np.sum(stem_audio, axis = 0)

			output_data = np.concatenate(stem_audio, axis=0)

			grp = f.create_group(str(index))
			grp.create_dataset("source", shape=mix_data.shape, dtype=mix_data.dtype, data=mix_data)
			grp.create_dataset("output", shape=output_data.shape, dtype=output_data.dtype, data=output_data)
	
	return hdf_path
