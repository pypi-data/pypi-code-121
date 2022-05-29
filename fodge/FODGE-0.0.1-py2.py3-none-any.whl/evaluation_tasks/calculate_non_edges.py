"""
File to generate non-edges csv file
"""

import __init__
import itertools as IT
import csv
import json
import random
import os
import networkx as nx
from datetime import datetime
from fodge.load_data import *


def create_graphs(dict_snapshots):
    """
    From dictionary of times and edges for each time, returen a list of static graphs for each snapshot, list of
    nodes of each graph and list of remaining nodes.
    """
    keys = list(dict_snapshots.keys())
    g_list = []
    for i in range(len(keys)):
        G = nx.DiGraph()
        G.add_edges_from(dict_snapshots[keys[i]])
        H = G.to_undirected()
        g_list.append(H.copy())
        print(i)
    return g_list


def load_graph(func, t):
    """
    Function to load the graph as a dictionary of snapshots
    :param func:
    :param t:
    :return:
    """
    dict_snapshots, dict_weights = func(*t)
    return dict_snapshots, dict_weights


def create_non_edges_file(name, path, func):
    print("First creating non edges file")
    dict_snapshots, dict_weights = load_graph(func, (name, path))
    print("Starting create graphs")
    g_list = create_graphs(dict_snapshots)
    my_list = []
    print("Starting find non edges for each time")
    for i in range(len(g_list)):
        g = g_list[i]
        e = g.number_of_edges()
        n = g.number_of_nodes()
        print(i, n, e)
        nodes = list(g.nodes())
        # could be very big so change 0.5 to smaller values if needed.
        indexes = random.sample(range(0, len(nodes)), int(len(nodes) * 0.5))
        new_nodes = []
        for j in indexes:
            new_nodes.append(nodes[j])
        missing = [pair for pair in IT.combinations(new_nodes, 2) if not g.has_edge(*pair)]
        print(i, len(missing))
        for pair in missing:
            my_list.append((i, pair[0], pair[1]))

    # indexes = random.sample(range(0, len(my_list)), int(len(my_list)))
    # new_list = []
    # for l in indexes:
    #   new_list.append(my_list[l])
    print("Almost done, writing the csv file!")
    csvfile = open('evaluation_tasks/non_edges_{}.csv'.format(name), 'w', newline='')
    obj = csv.writer(csvfile)
    obj.writerows(my_list)
    csvfile.close()
    print("Non edges file is ready!")


# name_ = "facebook_friendships"
# datasets_path = os.path.join("..", "datasets")
# func_ = data_loader
# create_non_edges_file(name_, datasets_path, func_)
