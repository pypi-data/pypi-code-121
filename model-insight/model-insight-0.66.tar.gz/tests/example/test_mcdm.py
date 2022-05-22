import numpy as np
import mcdm_functions as mcfunc
criteria_weights = np.array([2,4,6,7,9])
temp = mcfunc.Normalize_Weights(criteria_weights,'divide_by_max')
print(temp)