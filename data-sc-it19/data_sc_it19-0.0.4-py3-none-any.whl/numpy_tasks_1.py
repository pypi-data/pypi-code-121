# how to get index locations that satisfy given condition using np.where
# create an array
import numpy as np
##arr_rand = np.array([8, 8, 7, 7, 0, 4, 2, 5, 2])
##print("Array:", arr_rand)
##
### positions where  value > 5
##index_gt5 = np.where(arr_rand > 5, 'gt5', 'le5')
##print("positions > 5 ", index_gt5)

# csv file importing
##path = 'https://raw.githubusercontent.com/selva86/datasets/master/Auto.csv'
##data = np.genfromtxt(path, delimiter=',', skip_header=1, dtype="float")
##print(data[:3])
##
##with open("out.csv", 'w') as thefile:
##    np.savetxt(thefile, data, delimiter=",")

# vectorize() - make scalar function works on vectors

def func(x):
    if x % 2:
        return x ** 2
    else:
        return x / 2

func_vect = np.vectorize(func, otypes=[float])

print(func_vect([10, 11, 12, 18, 17]))




