"""
Main file to run the second temporal link prediction task (linear regression)
"""

import __init__
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from fodge.load_data import *
import pandas as pd
from fodge.run_fodge import FODGE
from GEA.all_gea import *


class TemporalLinkPrediction2:
    """
    Class to run dynamic link prediction task.
    """

    def __init__(self, name, save_path, graph_path, func=data_loader, initial_method="node2vec", dim=128, epsilon=0.01,
                 alpha_exist=0., beta=0.99, number=0, test_ratio=0.2, val_ratio=0.2, file_tags=None):
        """
        Init function to initialize this class.
        :param name: Name of the dataset (string).
        :param graph_path: Path to where the dataset file is.
        :param save_path: Path to where to save the calculated embedding
        :param func: Loader function to load the dataset as a dictionary of snapshots. In order to create your own
                     load function, one should define it in the file load_data.py. (Name of the function)
        :param initial_method: Initial state-of-the-art algorithm to embed the first snapshot with. Options are
                               "node2vec", "HOPE", "GAE", "GF" and "GCN".
        :param dim: Embedding dimension (int)
        :param epsilon: The weight that is given to the second order neighbours.
        :param alpha_exist: Weight that is given to the previous changed existing nodes embeddings when they are
        recalculated (float between 0 and 1).
        :param beta: Rate of exponential decay of the edges weights through time
        :param number: How many vertices in the cumulative initial snapshot (choose a number where a 5-core exists)
        :param test_ratio: Test ratio for temporal link prediction task (float)
        :param val_ratio: Val ratio for temporal link prediction task (float)
        :param file_tags: If GCN GEA is used, then one should profile a file of tags
        """
        initial_t = time()
        # initialize the FODGE class
        self.DE = FODGE(name, graph_path, save_path, func=func, initial_method=initial_method, dim=dim, epsilon=epsilon,
                        alpha_exist=alpha_exist, beta=beta, number=number, file_tags=file_tags, mission="lp2")
        self.start_index = self.DE.index
        self.graph_lp = self.DE.create_weighted_graph_for_all_times()
        print("number of nodes: ", self.graph_lp.number_of_nodes())
        self.dict_snapshots = self.DE.dict_snapshots.copy()

        # calculate the embedding using FODGE
        self.full_dict_embeddings, self.dict_all_embeddings, self.total_time = self.DE.calculate_embedding()
        self.DE.full_dict_embeddings, self.DE.dict_all_embeddings = self.full_dict_embeddings, self.dict_all_embeddings
        self.DE.save_embedding(save_path, mission="lp2")

        t = time() - initial_t
        print(f"FODGE is done after {t} seconds. Starting temporal link prediction task")

        print("dict is ready")
        measure_list = ["Avg", "Had", "L1", "L2"]
        node2idx = dict(zip(list(self.graph_lp.nodes()), np.arange(self.graph_lp.number_of_nodes())))
        link_prediction_all_time(name, node2idx, self.DE.dict_snapshots, self.dict_all_embeddings,
                                 measure_list, test_ratio, val_ratio, 1-test_ratio-val_ratio)


def get_neg_edge_samples(pos_edges, edge_num, all_edge_dict, node_num, add_label=True):
    """
    Generate negative links (edges) in a graph
    :param pos_edges: ids of positive edges (numpy array)
    :param edge_num: Number of edges to choose
    :param all_edge_dict: Dict of all edges
    :param node_num: Number of nodes in the whole temporal network
    :param add_label: True for adding True/False to positive/negative edges, else False.
    """
    neg_edge_dict = dict()
    neg_edge_list = []
    cnt = 0
    while cnt < edge_num:
        from_id = np.random.choice(node_num)
        to_id = np.random.choice(node_num)
        if from_id == to_id:
            continue
        if (from_id, to_id) in all_edge_dict or (to_id, from_id) in all_edge_dict:
            continue
        if (from_id, to_id) in neg_edge_dict or (to_id, from_id) in neg_edge_dict:
            continue
        if add_label:
            neg_edge_list.append([from_id, to_id, 0])
        else:
            neg_edge_list.append([from_id, to_id])
        cnt += 1
    neg_edges = np.array(neg_edge_list)
    all_edges = np.vstack([pos_edges, neg_edges])
    return all_edges


def generate_edge_sample(node2idx, t, dict_snapshots, test_ratio, val_ratio, train_ratio):
    """
    Generate edge samples for train, val and test for a specific time
    :param node2idx: Dict where keys are names of nodes and values are their corresponding ids.
    :param t: Current time
    :param dict_snapshots: Dict where keys are times and each value is a list of edges occurring in this time.
    :param test_ratio: Test ratio for temporal link prediction task (float)
    :param val_ratio: Val ratio for temporal link prediction task (float)
    :param train_ratio: Train ratio for temporal link prediction task (float)
    """
    all_edge_dict = {}
    edge_list = []
    edges = dict_snapshots[t]
    g = nx.Graph()
    g.add_edges_from(edges)
    n = g.number_of_nodes()
    for e in edges:
        from_id, to_id = node2idx[e[0]], node2idx[e[1]]
        all_edge_dict.update({(to_id, from_id): 1})
        all_edge_dict.update({(from_id, to_id): 1})
        edge_list.append([from_id, to_id, 1])
        edge_list.append([to_id, from_id, 1])
    all_edges = np.array(edge_list)
    del edge_list
    edge_num = all_edges.shape[0]

    np.random.shuffle(all_edges)
    test_num = int(np.floor(edge_num * test_ratio))
    val_num = int(np.floor(edge_num * val_ratio))
    train_num = int(np.floor((edge_num - test_num - val_num) * train_ratio))

    val_edges = all_edges[: val_num]
    test_edges = all_edges[val_num: val_num + test_num]
    train_edges = all_edges[val_num + test_num: val_num + test_num + train_num]
    del all_edges

    train_edges = get_neg_edge_samples(train_edges, train_num, all_edge_dict, len(node2idx))
    test_edges = get_neg_edge_samples(test_edges, test_num, all_edge_dict, len(node2idx))
    val_edges = get_neg_edge_samples(val_edges, val_num, all_edge_dict, len(node2idx))

    df_train = pd.DataFrame(train_edges, columns=['from_id', 'to_id', 'label'])
    df_test = pd.DataFrame(test_edges, columns=['from_id', 'to_id', 'label'])
    df_val = pd.DataFrame(val_edges, columns=['from_id', 'to_id', 'label'])

    return df_train, df_val, df_test


def generate_edge_samples_all_times(node2idx, dict_snapshots, test_ratio, val_ratio, train_ratio):
    """
    Generate edge samples for train, val and test for a specific time for all times
    :param node2idx: Dict where keys are names of nodes and values are their corresponding ids.
    :param dict_snapshots: Dict where keys are times and each value is a list of edges occurring in this time.
    :param test_ratio: Test ratio for temporal link prediction task (float)
    :param val_ratio: Val ratio for temporal link prediction task (float)
    :param train_ratio: Train ratio for temporal link prediction task (float)
    """
    times = list(dict_snapshots.keys())
    list_dataframes = {}
    for t in times:
        i, j, k = generate_edge_sample(node2idx, t, dict_snapshots, test_ratio, val_ratio, train_ratio)
        list_dataframes.update({t: (i, j, k)})
    return list_dataframes


def get_edge_feature(node2idx, measure_list, edge_arr, embedding_arr, dict_all_embeddings, curr_t):
    """
    For all the edges in the given array, compute its value with the embeddings of the corresponding nodes according
    to the measures.
    :param node2idx: Dict where keys are names of nodes and values are their corresponding ids.
    :param measure_list: List of measures. One of 'L1', 'L2', 'Had', 'Avg'
    :param embedding_arr: Dict of embeddings of the nodes
    :param edge_arr: Relevant edges (numpy array)
    :param dict_all_embeddings: Dict of the embeddings at any given time. Keys are times and values are dicts of the
                                embeddings of all the nodes that appear specifically at this time.
    :param curr_t: Current time
    """
    idx2node = {i: n for n, i in node2idx.items()}
    feature_dict = dict()
    times = list(dict_all_embeddings.keys())
    time2index = {times[j]: j for j in range(len(times))}
    for measure in measure_list:
        assert measure in ['Avg', 'Had', 'L1', 'L2']
        feature_dict[measure] = []
    for i, edge in enumerate(edge_arr):
        from_id, to_id = idx2node[edge[0]], idx2node[edge[1]]
        if embedding_arr.get(from_id) is None or embedding_arr.get(to_id) is None:
            for t in times:
                if time2index[t] <= time2index[curr_t]:
                    continue
                else:
                    if len(set([from_id]).intersection(set(dict_all_embeddings[t]))) == 1 and \
                            len(set([to_id]).intersection(set(dict_all_embeddings[t]))) == 1:
                        new_embed = dict_all_embeddings[t].copy()
                        break
        else:
            new_embed = embedding_arr.copy()
        for measure in measure_list:
            if measure == 'Avg':
                feature_dict[measure].append((new_embed[from_id] + new_embed[to_id]) / 2)
            elif measure == 'Had':
                feature_dict[measure].append(new_embed[from_id] * new_embed[to_id])
            elif measure == 'L1':
                feature_dict[measure].append(np.abs(new_embed[from_id] - new_embed[to_id]))
            elif measure == 'L2':
                feature_dict[measure].append((new_embed[from_id] - new_embed[to_id]) ** 2)
    for measure in measure_list:
        feature_dict[measure] = np.array(feature_dict[measure])
    return feature_dict


def train(node2idx, measure_list, train_edges, val_edges, embeddings, dict_all_embeddings, curr_t):
    """
    Train function!
    """
    print('Start training!')
    train_edges.columns = range(train_edges.shape[1])
    val_edges.columns = range(val_edges.shape[1])
    train_labels = train_edges.iloc[:, -1].values
    val_labels = val_edges.iloc[:, -1].values
    train_edges = train_edges.values
    val_edges = val_edges.values
    train_feature_dict = get_edge_feature(node2idx, measure_list, train_edges, embeddings, dict_all_embeddings, curr_t)
    val_feature_dict = get_edge_feature(node2idx, measure_list, val_edges, embeddings, dict_all_embeddings, curr_t)

    model_dict = dict()
    for measure in measure_list:
        if measure == 'sigmoid':
            continue
        models = []
        # for C in [0.01, 0.1, 1, 10]:
        for C in [0.01, 0.1, 1, 10]:
            model = LogisticRegression(C=C, solver='lbfgs', max_iter=1000, class_weight='balanced')
            model.fit(train_feature_dict[measure], train_labels)
            models.append(model)
        best_auc = 0
        model_idx = -1
        for i, model in enumerate(models):
            val_pred = model.predict_proba(val_feature_dict[measure])[:, 1]
            auc = roc_auc_score(val_labels, val_pred)
            if auc >= best_auc:
                best_auc = auc
                model_idx = i
        model_dict[measure] = models[model_idx]
    print('Finish training!')
    return model_dict


def test_function(node2idx, measure_list, test_edges, embeddings, model_dict, date, dict_all_embeddings):
    """
    Test function!
    """
    test_labels = test_edges.iloc[:, -1].values
    test_edges = test_edges.values
    test_feature_dict = get_edge_feature(node2idx, measure_list, test_edges, embeddings, dict_all_embeddings, date)
    auc_list = [date]
    for measure in measure_list:
        if measure == 'sigmoid':
            test_pred = test_feature_dict[measure]
        else:
            test_pred = model_dict[measure].predict_proba(test_feature_dict[measure])[:, 1]
        auc_list.append(roc_auc_score(test_labels, test_pred))
    return auc_list


def link_prediction_all_time(name, node2idx, dict_snapshots, dict_all_embeddings, measure_list, test_ratio, val_ratio,
                             train_ratio):
    """
    Final function to perform temporal link prediction task
    """
    dataframes = generate_edge_samples_all_times(node2idx, dict_snapshots, test_ratio, val_ratio, train_ratio)
    times = list(dataframes.keys())
    all_auc_list = []

    for t in times:
        train_edges, val_edges, test_edges = dataframes[t]
        print('Current date is: {}'.format(t))
        embeddings = dict_all_embeddings[t]
        model_dict = train(node2idx, measure_list, train_edges, val_edges, embeddings, dict_all_embeddings, t)
        auc_list = test_function(node2idx, measure_list, test_edges, embeddings, model_dict, t, dict_all_embeddings)
        all_auc_list.append(auc_list)
    # print('all auc list len: ', len(all_auc_list)
    column_names = ['date'] + measure_list
    df_output = pd.DataFrame(all_auc_list, columns=column_names)
    print(df_output)
    print('method = FODGE', ', average AUC of Had: ', df_output["Had"].mean())
    print('method = FODGE', ', average AUC of Avg: ', df_output.["Avg"].mean())
    print('method = FODGE', ', average AUC of L1: ', df_output.["L1"].mean())
    print('method = FODGE', ', average AUC of L2: ', df_output.["L2"].mean())

    # save the results in a csv file
    output_file_path = os.path.join("lp_results_{}.csv".format(name))
    df_output.to_csv(output_file_path, sep=',', index=False)
