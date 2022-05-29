import numpy as np
from wizzi_utils import misc_tools as mt


def find_centers(A: np.array, k: int = 1) -> np.array:
    """
    :requires: sklearn
    :param A: nx(d+1) data array. A=X|y
    :param k: how many centers
    :return: centers kxd
    see find_centers_test()

    if you get No module named 'sklearn.__check_build._check_build'
    pip uninstall scikit-learn
    pip uninstall sklearn
    pip install sklearn
    """
    try:
        # noinspection PyPackageRequirements
        from sklearn.cluster import KMeans
        k_means_obj = KMeans(n_clusters=k)
        k_means_obj.fit(A)
        centers = k_means_obj.cluster_centers_
    except (ModuleNotFoundError, ImportError) as e:
        centers = None
        mt.exception_error(e)
    return centers
