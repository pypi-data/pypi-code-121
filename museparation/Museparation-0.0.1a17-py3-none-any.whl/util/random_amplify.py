import numpy as np

def random_amplify(stem_dicc, minimum, maximum):
	for key in stem_dicc:
		stem_dicc[key] = stem_dicc[key] * np.random.uniform(minimum, maximum)
	return stem_dicc
