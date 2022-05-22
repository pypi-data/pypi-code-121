import os 

import h5py
import numpy as np
from torch.utils.data import Dataset
from sortedcontainers import SortedList
from tqdm import tqdm

from ..util.load_audio import load_audio

class WaveunetShuffleDataset(Dataset):
	"""

	"""

	def __init__(self, dataset, hdf_dir, filename, instruments, sr, channels, shapes, random_hops, audio_transform=None, in_memory=False):
		"""
		:param dataset: (list of dictionaries)
		"""
		super(WaveunetShuffleDataset, self).__init__()

		self.hdf_dataset = None
		self.hdf_dir = hdf_dir
		self.hdf_file = os.path.join(hdf_dir, filename + ".hdf5")

		self.random_hops = random_hops
		self.sr = sr
		self.channels = channels
		self.shapes = shapes
		self.audio_transform = audio_transform
		self.in_memory = in_memory
		self.instruments = instruments
		
		if not os.path.exists(self.hdf_file):
			if not os.path.exists(hdf_dir):
				os.makedirs(hdf_dir)

			with h5py.File(self.hdf_file, "w") as f:
				f.attrs["sr"] = sr
				f.attrs["channels"] = channels
				f.attrs["instruments"] = instruments
				
				print("Adding audio files to dataset...")
				for idx, track in enumerate(tqdm(dataset)):
					grp = f.create_group(str(idx))
					for stem in instruments:
						audio_data, _ = load_audio(track[stem], sr=self.sr, mono=(self.channels==1))
						grp.create_dataset(stem, shape=audio_data.shape, dtype=audio_data.dtype, data=audio_data)

					grp.attrs["target_length"] = audio_data.shape[1]

		with h5py.File(self.hdf_file, "r") as f:
			if f.attrs["sr"] != sr or \
				f.attrs["channels"] != channels or\
				list(f.attrs["instruments"]) != instruments:
				raise ValueError(
					"SR or channel or instruments not the same as the already existing hdf file")

		with h5py.File(self.hdf_file, "r") as f:
			lengths = [f[str(song_idx)].attrs["target_length"] for song_idx in range(len(f))]
			lengths = [(l // self.shapes["output_frames"]) + 1 for l in lengths]

		self.start_pos = SortedList(np.cumsum(lengths))
		self.length = self.start_pos[-1]

		self.inst_shuffle = {key : np.arange(self.length) for key in self.instruments}
		self.shuffle()


	def __getitem__(self, index):
		if self.hdf_dataset is None:
			driver = "core" if self.in_memory else None
			self.hdf_dataset = h5py.File(self.hdf_file, "r", driver=driver)
		
		targets = {}
		for stem in self.instruments:
			targets[stem] = self.getStem(stem, self.inst_shuffle[stem][index])

		if self.audio_transform is not None:
			targets = self.audio_transform(targets)

		mixture = np.sum(list(targets.values()), axis = 0)
		mixture = np.clip(mixture, -1, 1)

		for key in targets:
			targets[key] = targets[key][:, self.shapes["output_start_frame"]:self.shapes["output_end_frame"]]
		return mixture, targets


	
	def getStem(self, stem, index):
		audio_idx = self.start_pos.bisect_right(index)
		index = index - self.start_pos[audio_idx - 1]

		target_length = self.hdf_dataset[str(audio_idx)].attrs["target_length"]
		if self.random_hops:
			start_target_pos = np.random.randint(0, max(target_length - self.shapes["output_frames"] + 1, 1))
		else:
			start_target_pos = index * self.shapes["output_frames"]

		start_pos = start_target_pos - self.shapes["output_start_frame"]
		if start_pos < 0:
			pad_front = abs(start_pos)
			start_pos = 0
		else:
			pad_front = 0
		
		end_pos = start_target_pos - self.shapes["output_start_frame"] + self.shapes["input_frames"]
		if end_pos > target_length:
			pad_back = end_pos - target_length
			end_pos = target_length
		else:
			pad_back = 0


		target = self.hdf_dataset[str(audio_idx)][stem][:, start_pos:end_pos].astype(np.float32)
		if pad_front > 0 or pad_back > 0:
			target = np.pad(target, [(0, 0), (pad_front, pad_back)], mode="constant", constant_values=0.0)
		return target
		
	def shuffle(self):
			for key in self.inst_shuffle:
				np.random.shuffle(self.inst_shuffle[key])

	def __len__(self):
		return self.length
