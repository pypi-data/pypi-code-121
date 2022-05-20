from typing import List, Callable
from numpy import double
from scipy.spatial import distance
from .CompareLSOutput import CompareLSOutput
from .LSVector import LSVector


class CompareLS:
    vectors: List[LSVector]
    metric: Callable
    p_norm: int
    result: CompareLSOutput

    def __init__(self, vectors: List[LSVector], metric: Callable, p_norm: int):
        """

        Parameters
        ----------
        vectors : List[LSVector]
            Two latent spaces
        metric : function
            Distance function
        p_norm : int
            The p-norm to apply for Minkowski
        """
        self.vectors = vectors
        self.metric = metric
        self.p_norm = p_norm
        self.result = self.do_compare()

    def do_compare(self) -> CompareLSOutput:
        """ Compare latent spaces

        Returns
        -------
        CompareLSOutput
            Result of the comparison
        """
        # find distance between the vectors
        if self.metric == distance.minkowski:
            distance_result: double = self.metric(self.vectors[0].ls_data, self.vectors[1].ls_data, self.p_norm)
        else:
            distance_result = self.metric(self.vectors[0].ls_data, self.vectors[1].ls_data)

        # create CompareLSOutput object
        return CompareLSOutput(
            self.vectors[0].ls_name, self.vectors[1].ls_name, self.metric.__name__, str(distance_result))
