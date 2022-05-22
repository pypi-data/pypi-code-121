import numpy as np




def split_validation(trainval_list, *, VALIDATION_SIZE=0.2, SEED=1):
	"""
	separate a train list into a train list and a validation list
	:param train_list: list 
	:param VALIDATION_SIZE: the size of the validation set (0.2 means 80 20 training validation respectively)
	:param SEED: seed for numpy
	:return: 2 lists, the first is the validation list, and the 2nd is the train list
	"""
	
	middle = int(len(trainval_list) * VALIDATION_SIZE // 1)
	np.random.seed(SEED)
	np.random.shuffle(trainval_list)

	val_list   = trainval_list[:middle]
	train_list = trainval_list[middle:]

	return val_list, train_list
