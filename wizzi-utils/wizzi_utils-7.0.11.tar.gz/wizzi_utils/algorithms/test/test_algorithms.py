from wizzi_utils.algorithms import algorithms as alg
from wizzi_utils.misc import misc_tools as mt
from wizzi_utils.pyplot import pyplot_tools as pyplt
import numpy as np

PLT_MAX_TIME = 2  # close plt after x seconds - minimum 2


def find_centers_test():
    """
    if you get No module named 'sklearn.__check_build._check_build'
    pip uninstall scikit-learn
    pip uninstall sklearn
    pip install sklearn
    :return:
    """
    mt.get_function_name(ack=True, tabs=0)
    A = np.array([[-1, -1], [-1, 1], [1, 1], [1, -1]])
    centers = alg.find_centers(A, k=1)
    if centers is not None:
        print('\tVisual test: square and it\'s center')

        pyplt.plot_2d_one_figure(
            datum=[
                {
                    'data': A,
                    'c': 'g',
                    'label': 'Data',
                    'marker': 'o',
                },
                {
                    'data': centers,
                    'c': 'r',
                    'label': '1Mean',
                    'marker': 'x',
                }
            ],
            fig_title='square and it\'s center',
            win_d={
                'title': 'find_centers_test()',
                'location': (0, 0),
                'resize': 1,
                'zoomed': False
            },
            max_time=PLT_MAX_TIME
        )
    return


def test_all():
    print('{}{}:'.format('-' * 5, mt.get_base_file_and_function_name()))
    find_centers_test()
    print('{}'.format('-' * 20))
    return
