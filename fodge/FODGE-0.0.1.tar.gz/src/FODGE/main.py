"""
Main function to run FODGE.
In the terminal run
    python main.py -h
This will print a message with explanations on all relevant parameters you should insert and how to write the command
to run this file
"""

import argparse
from evaluation_tasks.temporal_link_prediction import *
from evaluation_tasks.calculate_non_edges import *
from evaluation_tasks.linear_regression_link_prediction import *


parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--name', default='facebook_friendships', type=str, help='Name of the dataset (str)')
parser.add_argument('--datasets_path', default='datasets', type=str, help='Path to where the dataset file is (str)')
parser.add_argument('--save_path', default='embeddings', type=str,
                    help='Path to where to save the calculated embedding (str)')
parser.add_argument('--initial_method', default='node2vec', type=str,
                    help='Initial GEA to embed the first snapshot with. Options are node2vec, HOPE, GAE, GF. If the'
                         'graph has tags, GCN option can also be used (str)')
parser.add_argument('--dim', default=128, type=int, help='Embedding dimension (int)')
parser.add_argument('--epsilon', default=0.01, type=float,
                    help='Relative weight given to first and second neighbors in the local update rule (float)')
parser.add_argument('--alpha', default=0.2, type=float,
                    help='The weight given to the recent embedding when calculating the current one (float)')
parser.add_argument('--beta', default=0.3, type=float, help='The rate of the exponential decay of the weights (float)')
parser.add_argument('--number', default=1000, type=int,
                    help='How many vertices in the cumulative initial snapshot (choose a number where a 5-core exists)'
                         '(int)')
parser.add_argument('--file_tags', default=None, type=str,
                    help='If GCN GEA is used, then one should provide the path of the file of tags (str)')
parser.add_argument('--link_prediction_1', default="False", type=str,
                    help='True if you want to perform temporal link prediction task (type 1 with neural network), else '
                         'False')
parser.add_argument('--link_prediction_2', default="False", type=str,
                    help='True if you want to perform temporal link prediction task (type 2 with linear regression),'
                         'else False')
parser.add_argument('--test_ratio', default=0.2, type=float, help='Test ratio for temporal link prediction tasks '
                                                                  '(relevant to both) both)')
parser.add_argument('--val_ratio', default=0.3, type=float, help='Val ratio for temporal link prediction task '
                                                                 '(relevant only to type 2- with linear regression)')
parser.add_argument('--non_edges_file', default='non_edges_facebook_friendships.csv', type=str,
                    help='Name of non edges csv file as explained in the readme. If you do not have any, insert None '
                         '(str) and it will be created during the running (can take a while). relevant only to type 1- 
                         'with linear regression')


args = parser.parse_args()

func = data_loader

if args.link_prediction_1 == "False" and args.link_prediction_2 == "False":
    # Only embed the temporal network
    DE = FODGE(args.name, args.datasets_path, args.save_path, func=func, initial_method=args.initial_method, dim=args.dim,
               epsilon=args.epsilon, alpha_exist=args.alpha, beta=args.beta, number=args.number,
               file_tags=args.file_tags)
elif args.link_prediction_1 == "True":
    # Perform first temporal link prediction
    if args.non_edges_file == "None":  # create non_edges_file if the user does not give one
        non_edges_file = create_non_edges_file(args.name, args.datasets_path, func)
        path_non_edges_file = os.path.join("evaluation_tasks", non_edges_file)
    else:
        path_non_edges_file = os.path.join("evaluation_tasks", args.non_edges_file)
    LP = TemporalLinkPrediction1(args.name, args.datasets_path, args.save_path, func=func,
                                 initial_method=args.initial_method, dim=args.dim, epsilon=args.epsilon,
                                 alpha_exist=args.alpha, beta=args.beta, number=args.number, test_ratio=args.test_ratio,
                                 non_edges_file=path_non_edges_file, file_tags=args.file_tags)
elif args.link_prediction_2 == "True":
    LP = TemporalLinkPrediction2(args.name, args.save_path, args.datasets_path, func=func,
                                 initial_method=args.initial_method, dim=args.dim, epsilon=args.epsilon,
                                 alpha_exist=args.alpha, beta=args.beta, number=args.number, test_ratio=args.test_ratio,
                                 val_ratio=args.val_ratio, file_tags=args.file_tags)

