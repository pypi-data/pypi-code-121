import soundfile

def write_wav(path, audio, sr):
	soundfile.write(path, audio.T, sr, "PCM_16")
