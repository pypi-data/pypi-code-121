import argparse
from typing import Callable, List
from .SearchLSOutput import SearchLSOutput
from .get_metric import get_distance_function
from .SearchLS import SearchLS
from .output_results import output_result
from .LSVector import LSVector


def ls_search(args: argparse.Namespace):
    """

    Parameters
    ----------
    args : argparse.Namespace
    """
    # get the arguments
    output_filename: str = args.output_file
    out_format: str = args.output_format
    out_mode: str = args.output_mode
    p_norm: int = args.p_norm  # The p-norm to apply for Minkowski - default is 2
    lat_spaces: List[str] = args.latent_space
    
    # set the distance metric
    distance_function: Callable = get_distance_function(args.distance_metric)
    
    # find the closest latent space
    lat_space: str
    for lat_space in lat_spaces:
        v: LSVector = LSVector(lat_space)
        res: SearchLSOutput = SearchLS(v, distance_function, p_norm).result
        output_result(res, output_filename, out_format, out_mode)
