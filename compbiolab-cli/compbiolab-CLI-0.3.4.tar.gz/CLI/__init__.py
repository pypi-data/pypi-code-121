import argparse
from typing import List

output_opt_parser: argparse.ArgumentParser = argparse.ArgumentParser(add_help=False)
output_opt_parser.add_argument("-out", help="Output filename", dest="output_file", type=str, default="")
output_opt_parser.add_argument("-of", help="Output format. Default: text", dest="output_format", type=str, choices=["text", "csv"], default="text")
output_opt_parser.add_argument("-om", help="Output mode. Default: a", dest="output_mode", type=str, choices=['a', 'w'], default='a')

metrics: List[str] = ['euclidean', 'minkowski', 'cityblock', 'sqeuclidean', 'cosine',
                      'correlation', 'hamming', 'jaccard', 'chebyshev', 'canberra',
                      'braycurtis', 'yule', 'dice', 'kulsinski', 'rogerstanimoto',
                      'russellrao', 'sokalmichener', 'sokalsneath']

dist_opt_parser: argparse.ArgumentParser = argparse.ArgumentParser(add_help=False)
dist_opt_parser.add_argument("-m", help="Distance metric. Default: euclidean", metavar="DISTANCE_METRIC", dest="distance_metric", type=str, choices=metrics, default="euclidean")
dist_opt_parser.add_argument("-p", help="Scalar, The p-norm to apply for Minkowski, weighted and unweighted. Default: 2", dest="p_norm", type=int, default=2)
