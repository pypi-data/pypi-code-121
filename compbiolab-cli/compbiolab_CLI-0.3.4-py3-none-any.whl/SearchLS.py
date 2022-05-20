from typing import Callable
import numpy as np
from scipy.spatial import distance
from .LSVector import LSVector
from .SearchLSOutput import SearchLSOutput
from .load_files import latent_space_list, load_family


class SearchLS:
    ls_name: str
    ls_data: np.ndarray
    metric: Callable
    p_norm: int
    result: SearchLSOutput

    def __init__(self, ls: LSVector, metric: Callable, p_norm: int):
        """

        Parameters
        ----------
        ls : LSVector
            Latent space
        metric : function
            Distance function
        p_norm : int
            The p-norm to apply for Minkowski
        """
        self.ls_name = ls.ls_name
        self.ls_data = ls.ls_data
        self.metric = metric
        self.p_norm = p_norm
        self.result = self.do_search()

    def do_search(self) -> SearchLSOutput:
        """ Find closest protein family

        Returns
        -------
        SearchLSOutput
        """
        closest_family: str = "none"
        min_dist: float = float("inf")
        i: int
        for i in range(len(latent_space_list)):
            if self.metric == distance.minkowski:
                distance_result: np.double = self.metric(self.ls_data, load_family(latent_space_list[i]), self.p_norm)
            else:
                distance_result = self.metric(self.ls_data, load_family(latent_space_list[i]))

            if distance_result < min_dist:
                min_dist = distance_result
                closest_family = latent_space_list[i]
        return SearchLSOutput(self.ls_name, self.metric.__name__, closest_family[:-4], str(min_dist))
