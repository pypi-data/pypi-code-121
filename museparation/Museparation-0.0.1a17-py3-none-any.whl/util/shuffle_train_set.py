import numpy as np



def shuffle_train_set(train_set, it):
	"""
	Shuffles the train dataset
	:param train_set: A list containing dictionaries [{"bass": bass_path, ...}, {}, {}, ...]
	:param it: integer, used as seed (everytime the dataset needs to be reshuffled, it should be changed)
	:return: The same shape as the input, mixture removed, shuffled
	"""
	np.random.seed(it)
	length = len(train_set)
	
	bass   = np.arange(length)
	drums  = np.arange(length)
	other  = np.arange(length)
	vocals = np.arange(length)

	np.shuffle(bass)
	np.shuffle(drums)
	np.shuffle(other)
	np.shuffle(vocals)

	return [{"bass" : bass[i], "drums" : drums[i], "other" : other[i], "vocals" : vocals[i]} for i in length]
