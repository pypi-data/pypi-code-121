import numpy as np
import librosa

def load_audio(audio_path, sr=44100, mono=False):
	"""
	"""
	data, sanity_sr = librosa.load(audio_path, sr=sr, mono=mono)

	if(len(data.shape) == 1):
		data = data[np.newaxis, :]

	return data, sanity_sr
