"""
Utils file for first temporal link prediction task
"""

import random
import numpy as np
import sys
import csv
import networkx as nx


def nodes_test_in_train(nodes_list, index):
    """
    Given list of nodes for each time stamp and an index separating between train and test examples, return the nodes
    in the test set that are also in the training set.
    :param nodes_list: List of lists of nodes for each time stamp.
    :param index: Index indicating the time stamp that afterwards it's the test set, and beforehand it's the train set.
    :return: A list of nodes in the test set that are also in the train set
    """
    nodes_train = []
    nodes_test = []

    for i in range(len(nodes_list)):
        if i < index:
            for j in nodes_list[i]:
                nodes_train.append(j)
        else:
            for j in nodes_list[i]:
                nodes_test.append(j)

    nodes_train = set(dict.fromkeys(nodes_train))
    nodes_test = set(dict.fromkeys(nodes_test))
    nodes = nodes_train.intersection(nodes_test)

    return nodes


def create_full_lists_missing_edges(index, non_edges_file, nodes, start_index, dict_snapshots, dict_embeddings):
    """
    Create lists of missing edges for both train and test.
    :param index: Index of pivot time- until pivot time (including) it is train set, afterwards it is test set.
    :param nodes: List of nodes of the graph
    :param non_edges_file: Csv file containing list of non edges (explained in the initialization of the class).
    :param start_index: Index of the cumulative initial snapshot
    :param dict_embeddings: Dict of embeddings, key is a vertex id and value is its numpy array embedding
    :param dict_snapshots: Dict of snapshots, key is a time and value is a list of edges occurring at this time
    :return: List of missing edges for both train and test sets.
    """
    missing_edges_train = calculate_list_of_false_edges(index, "train", nodes, start_index, dict_snapshots,
                                                        dict_embeddings, non_edges_file=non_edges_file)
    missing_edges_test = calculate_list_of_false_edges(index, "test", nodes, start_index, dict_snapshots,
                                                       dict_embeddings, non_edges_file=non_edges_file)
    return missing_edges_train, missing_edges_test


def choose_false_edges(non_edges, K):
    """
    From the list of non-edges choose K false edges.
    :param non_edges: List of non edges (train or test, depends on the input).
    :param K: Number of non-edges to choose randomly.
    :return List of K non-edges.
    """
    indexes = random.sample(range(0, len(non_edges)), K)
    false_edges = []
    for i in indexes:
        false_edges.append(non_edges[i])
    return false_edges


def create_data_for_link_prediction(K_train, K_test, missing_edges_train, missing_edges_test):
    """
    Create false train and test edges for link prediction task.
    :param K_train: Number of true/false edges to choose from the train set, is equal to the total number of edges
                    in the train set (for all time stamps).
    :param K_test: Number of true/false edges to choose from the test set, is equal to the total number of edges
                   in the test set (for all time stamps).
    :param missing_edges_train: List of missing edges in the train set
    :param missing_edges_test: List of missing edges in the test set
    :param non_edges_file: Csv file containing list of non edges (explained in the initialization of the class).
    :return: List of K non-edges chosen randomly from the whole lists of non edges, both for train and test.
    """
    false_edges_train = choose_false_edges(missing_edges_train, K_train)
    false_edges_test = choose_false_edges(missing_edges_test + missing_edges_train, K_test)
    return false_edges_train, false_edges_test


def remove_true_false_edges(dict_snapshots, dict_weights, index):
    """
    Remove chosen true edges from the graph so the embedding could be calculated without them.
    :param dict_snapshots: Dict where keys are times and values are a list of edges for each time stamp.
    :param dict_weights: Dict where keys are times and values are list of weights for each edge in the time stamp, order
                         corresponds to the order of edges in dict_snapshots.
    :param index: Index of pivot time- until pivot time (including) it is train set, afterwards it is test set.
    :return: Updated dict_snapshots and dict_weights.
    """
    times = list(dict_snapshots.keys())
    mapping = {i: times[i] for i in range(len(times))}
    keys = list(mapping.keys())
    for key in keys:
        if key < index:
            continue
        else:
            del dict_snapshots[mapping[key]]
            del dict_weights[mapping[key]]
    return dict_snapshots, dict_weights


def for_lp_mission(name, graph, nodes_list, dict_snapshots, dict_weights, r, start_index):
    """
    Create initial data for the link prediction task- index pivot time, nodes common to train and test set,
    dict of edges for each snapshot without the chosen test positive edges, number of edges in train and test.
    :param name: Name of the dataset
    :param graph: Our graph
    :param nodes_list: List of all nodes in the graph (for all time stamps)
    :param dict_snapshots: Dict where keys are times and values are a list of edges for each time stamp.
    :param dict_weights: Weights of the edges at each time
    :param r: Wanted test ratio (r = K_test / (K_train + K_test)
    :param start_index: The index of the cumulative graph
    :return: Explained above.
    """
    # this is a function that finds the index that times before are train and times after is test, but it is better
    # determine ahead because it takes a long time to run it
    try:
        index = choose_test_index(name) - start_index
    except:
        pivot_time, index, mapping = get_pivot_time(graph, dict_snapshots, wanted_ratio=r, min_ratio=0.1)
    print("pay attention the index is !!!!!!!!", index)
    nodes = nodes_test_in_train(nodes_list, index)
    print("len nodes is ", len(nodes))
    K_train, K_test, true_edges_train, true_edges_test = train_test_edges(dict_snapshots, index, nodes)
    dict_snapshots, dict_weights = remove_true_false_edges(dict_snapshots, dict_weights, index)
    return index, nodes, dict_snapshots, true_edges_train, true_edges_test, K_train, K_test, dict_weights


def calculate_list_of_false_edges(index, type_, nodes, start_index, dict_snapshots, dict_projections,
                                  non_edges_file=None):
    """
    Get a list of non edges.
    :param index: Representing the time stamp that separates between nodes in train and nodes in test
    :param type_: "train" - for train nodes, "test"- for test nodes
    :param nodes: Set of nodes common to test and train set.
    :param non_edges_file: CSV file where each row is time,source,target. To create such file please see
    "calculate_non_edges.py" file.
    :param start_index: The index of the cumulative graph
    :param dict_snapshots: Dict where keys are times and values are a list of edges for each time stamp.
    :param dict_projections: Dict of embeddings, key is a vertex id and value is its numpy array embedding
    :return: A list of non-edges
    """
    l = len(dict_snapshots.keys()) + start_index
    mapping = {}
    for j in range(l):
        if j < start_index:
            mapping.update({j: 0})
        else:
            mapping.update({j: j - start_index})

    if non_edges_file is None:
        sys.exit("you have to create non_edges_file")
    else:
        non_edges = []
        print("Starting taking non_edges, may take a while (5-10 minutes), stay put!")
        csvfile = open(non_edges_file, 'r', newline='')
        obj = csv.reader(csvfile)
        for row in obj:
            if mapping.get(int(row[0])) is not None:
                if type_ == "train":
                    if mapping[int(row[0])] < index:
                        if dict_projections.get(row[1]) is not None and dict_projections.get(row[2]) is not None:
                            if len(set([row[1], row[2]]).intersection(nodes)) == 2:
                                non_edges.append((mapping[int(row[0])], (row[1], row[2])))
                else:
                    if mapping[int(row[0])] >= index:
                        if dict_projections.get(row[1]) is not None and dict_projections.get(row[2]) is not None:
                            if len(set([row[1], row[2]]).intersection(nodes)) == 2:
                                non_edges.append((mapping[int(row[0])], (row[1], row[2])))
    print("example for non edges: ", non_edges[0])
    return non_edges


def create_x_y(dict_proj, true_edges, false_edges, K, d):
    """
    Create X, Y for linear regression
    :param dict_proj: Dict of embeddings (vertex: embedding)
    :param true_edges: List of true edges
    :param false_edges: List of false edges
    :param K: Number of train/test edges
    :param d: Embedding dimension
    :return: X, Y for linear regression
    """
    nodes = list(dict_proj.keys())
    dict_edges = {n: [] for n in nodes}
    X = np.zeros(shape=(2 * K, 2 * d))
    Y = np.zeros(shape=(2 * K, 1))
    count = 0
    for m in true_edges:
        edge = m[1]
        embd1 = dict_proj[edge[0]]
        embd2 = dict_proj[edge[1]]
        con_embed = np.concatenate((embd1, embd2), axis=0)
        X[count, :] = con_embed
        Y[count, 0] = int(1)
        count += 1
        dict_edges[edge[0]].append(count)
        dict_edges[edge[1]].append(count)
    for m in false_edges:
        edge = m[1]
        embd1 = dict_proj[edge[0]]
        embd2 = dict_proj[edge[1]]
        con_embed = np.concatenate((embd1, embd2), axis=0)
        X[count, :] = con_embed
        Y[count, 0] = int(0)
        count += 1
        dict_edges[edge[0]].append(count)
        dict_edges[edge[1]].append(count)
    return X, Y, dict_edges


def create_mapping(dict_times):
    """
    If times are not integers transform each one of them to a unique integer of its own.
    """
    keys = list(dict_times.keys())
    mapping = {}
    for i in range(len(keys)):
        mapping.update({keys[i]: i})
    return mapping


def get_graph_T(graph, dict_edges, min_time=-np.inf, max_time=np.inf, mapping=None):
    """
    Given 2 times, return the graph that has all nodes and edges that have been in the snapshots in between (including
    the maximum time).
    :param graph: The given graph
    :param dict_edges: Dict where keys==times and values==list of edges for each time stamp.
    :param min_time: Minimum time
    :param max_time: Maximum time
    :param mapping: If times are not integers, it is a mapping dictionary between the name of the times and indexes.
    :return: The new graph between the two times, and the new dict_times between these 2 times.
    """
    relevant_edges = []
    relevant_edges_no_time = []
    new_dict_edges = {}

    if len(graph.nodes()) == 0:
        return graph

    keys = list(dict_edges.keys())

    for key in keys:
        t = key
        if mapping is not None:
            t = mapping[t]
        if min_time < t <= max_time:
            for edge in dict_edges[key]:
                u = edge[0]
                v = edge[1]
                relevant_edges.append((u, v, t))
                relevant_edges_no_time.append((u, v))
                if new_dict_edges.get(t) is None:
                    new_dict_edges.update({t: [(u, v)]})
                else:
                    new_dict_edges[t].append((u, v))
        else:
            continue

    new_graph = nx.DiGraph()
    new_graph.add_edges_from(relevant_edges_no_time)

    return new_graph, new_dict_edges


def get_graph_times(dict_time_edge):
    """
    Get all time stamps.
    """
    keys = list(dict_time_edge.keys())
    # keys.sort()
    return keys


def get_pivot_time(graph, dict_edges, wanted_ratio=0.2, min_ratio=0.1):
    """
    Given a graph and dictionary of snapshots (keys are times and values are the graph's edges in that time), calculate
    the pivot time that gives a wanted ratio to the train and test edges.
    :param graph: Our graph
    :param dict_edges: Dict where keys==times and values==list of edges for each time stamp.
    :param wanted_ratio: Wanted test ratio (r = K_test / (K_train + K_test)
    :param min_ratio: If we can't find time for the wanted ratio, try for the minimum ratio.
    :return: The pivot time and its index.
    """
    times = get_graph_times(dict_edges)
    mapping = {}
    for i in range(len(times)):
        mapping.update({times[i]: i})

    if wanted_ratio == 0:
        return times[-1]

    time2dist_from_ratio = {}
    for time in times[int(len(times) / 3):]:
        if mapping is not None:
            time = mapping[time]
        train_graph, _ = get_graph_T(graph, dict_edges, max_time=time, mapping=mapping)
        num_edges_train = train_graph.number_of_edges()

        test_graph, _ = get_graph_T(graph, dict_edges, min_time=time, mapping=mapping)
        test_graph.remove_nodes_from(
            [node for node in list(test_graph.nodes()) if node not in list(train_graph.nodes())])
        num_edges_test = test_graph.number_of_edges()

        current_ratio = num_edges_test / (num_edges_test + num_edges_train)
        print(2)

        if current_ratio <= min_ratio:
            continue

        time2dist_from_ratio.update({time: np.abs(wanted_ratio - current_ratio)})

    pivot_time = min(time2dist_from_ratio, key=time2dist_from_ratio.get)

    if mapping is not None:
        for key, value in mapping.items():
            if value == pivot_time:
                true_time = key
    else:
        true_time = 0

    print(f"pivot time {pivot_time}, is close to the wanted ratio by {round(time2dist_from_ratio[pivot_time], 3)}")

    return true_time, pivot_time, mapping


def train_test_edges(dict_edges_by_time, index_pivot_time, nodes):
    """
    Function to return a list of false edges and true edges, each list has tuples in the form: (time, (source, target))
    :param dict_edges_by_time: Dict where keys==times and values==list of edges for each time stamp.
    :param index_pivot_time: Representing the time stamp that separates between nodes in train and nodes in test
    :param nodes: Nodes appear both in the train and test sets.
    """
    times = get_graph_times(dict_edges_by_time)
    train_times = times[:index_pivot_time]
    test_times = times[index_pivot_time:]

    train_dict_times = {}
    test_dict_times = {}

    for t in train_times:
        train_dict_times.update({t: dict_edges_by_time[t]})
    for t in test_times:
        test_dict_times.update({t: dict_edges_by_time[t]})

    l1 = 0
    train_edges = []
    keys = list(train_dict_times.keys())
    for j in range(len(keys)):
        key = keys[j]
        for i in train_dict_times[key]:
            if len(set([i[0], i[1]]).intersection(nodes)) == 2:
                l1 += 1
                train_edges.append((j, i))

    l2 = 0
    test_edges = []
    keys = list(test_dict_times.keys())
    for j in range(len(keys)):
        key = keys[j]
        for s in range(len(test_dict_times[key])):
            i = test_dict_times[key][s]
            if len(set([i[0], i[1]]).intersection(nodes)) == 2:
                l2 += 1
                test_edges.append((j + index_pivot_time, i))

    return l1, l2, train_edges, test_edges


def choose_test_index(name):
    if name == "facebook-wosn-wall":
        val = 42
    elif name == "facebook_friendships":
        val = 23
    elif name == "ia-enron-email-dynamic":
        val = 43
    elif name == "dblp":
        val = 24
    elif name == "wiki-talk-temporal":
        val = 72
    elif name == "fb-wosn-friends":
        val = 24
    elif name == "sx-mathoverflow":
        val = 60
    return val