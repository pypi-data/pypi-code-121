from wizzi_utils.coreset import coreset_tools as cot
from wizzi_utils.misc import misc_tools as mt
import numpy as np


def select_coreset_test():
    mt.get_function_name(ack=True, tabs=0)
    A = np.array([[1, 1], [2, 1], [3, 7], [4, 4], [5, 1]])
    SP = np.ones(shape=A.shape[0]) / A.shape[0]  # uniform probability
    C, CW = cot.select_coreset(A=A, SP=SP, c_size=2, with_reps=True)
    print(mt.to_str(var=A, title='\tA'))
    print(mt.to_str(var=C, title='\tC'))
    print(mt.to_str(var=CW, title='\tCW'))
    return


def select_coreset_frequency_test():
    mt.get_function_name(ack=True, tabs=0)
    A = np.array([[1, 1], [2, 1], [3, 7], [4, 4], [5, 1]])
    SP = np.ones(shape=A.shape[0]) / A.shape[0]  # uniform probability
    C, CW = cot.select_coreset_frequency(P=A, SP=SP, c_size=4)
    print(mt.to_str(var=A, title='\tA'))
    print(mt.to_str(var=C, title='\tC'))
    print(mt.to_str(var=CW, title='\tCW'))
    return


def test_all():
    print('{}{}:'.format('-' * 5, mt.get_base_file_and_function_name()))
    select_coreset_test()
    select_coreset_frequency_test()
    print('{}'.format('-' * 20))
    return
