"""
Main file of FODGE
"""

from fodge.LUR import *
from fodge.fodge_utils import *
import time
from fodge.load_data import *
import sys


class FODGE:
    """
    Class to run one of our suggested dynamic embedding methods.
    """

    def __init__(self, name, graph_path, save_path, func=data_loader, initial_method="node2vec", dim=128, epsilon=0.01,
                 alpha_exist=0., beta=0.99, number=0, mission=None, file_tags=None):
        """
        Init function to initialize the class.
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
        :param mission: None if it is not for a specific mission, "lp" for Temporal Link Prediction task and "nc" for
                        node classification task.
        :param file_tags: If GCN GEA is used, then one should profile a file of tags
        """
        self.name = name
        # create dict of snapshots containing the edges to each time and corresponding dict of weights
        self.dict_snapshots, self.dict_weights = self.load_graph(func, (name, graph_path))

        if file_tags is not None:
            self.graph = self.create_weighted_graph_for_all_times()
            nodes = list(self.graph.nodes())
            self.nc_nodes = []
            self.nodes_no_nc = list(set(nodes) - set(self.nc_nodes))

        self.initial_method = initial_method
        self.file_tags = file_tags
        self.number = number
        self.beta = beta
        self.epsilon = epsilon
        self.dim = dim
        self.alpha_exist = alpha_exist
        self.params_dict = self.define_params_for_initial_method()

        self.g_list, self.nodes_list, T, self.index = self.create_cumulative_graphs(number)

        if self.index > 0:
            self.change_dict_snapshots(T)

        print("The temporal network after creating the cumulative initial snapshot:")
        keys = list(self.dict_snapshots.keys())
        for i in range(len(keys)):
            print(i, keys[i])

        print("Ready to embed the {} temporal network with FODGE".format(name))

        if mission is None:
            # calculate the graph embedding and return a dictionary of nodes as keys and embedding vectors as values,
            self.full_dict_embeddings, self.dict_all_embeddings, self.total_time = self.calculate_embedding()
            self.save_embedding(save_path)

    @staticmethod
    def load_graph(func, t):
        """
        Function to load the graph as a dictionary of snapshots
        """
        dict_snapshots, dict_weights = func(*t)
        return dict_snapshots, dict_weights

    def define_params_for_initial_method(self):
        """
        According to the initial state-of-the-art embedding method, create the dictionary of parameters.
        :return: Parameters dictionary
        """
        if self.initial_method == "node2vec":
            params_dict = {"dimension": self.dim, "walk_length": 80, "num_walks": 16, "workers": 2}
        elif self.initial_method == "GF":
            params_dict = {"dimension": self.dim, "eta": 0.1, "regularization": 0.1, "max_iter": 1000,
                           "print_step": 100}
        elif self.initial_method == "HOPE":
            params_dict = {"dimension": self.dim, "beta": 0.1}
        elif self.initial_method == "GAE":
            params_dict = {"model": "gcn_vae", "seed": 42, "epochs": 70, "hidden1": 256, "hidden2": self.dim, "lr": 0.1,
                           "dropout": 0.2, "dataset_str": self.name, "dimension": self.dim}
        elif self.initial_method == "GCN":
            params_dict = {"dimension": self.dim, "epochs": 100, "lr": 0.03, "weight_decay": 0, "dropout": 0.2,
                           "nc_nodes": self.nc_nodes}
        else:
            sys.exit("Chosen GEA is not valid. Please choose one of the following: node2vec, HOPE, GF, GEA. If you have"
                     "tags to your data, you can also choose GCN")
        return params_dict

    def change_weights(self, t1, t2, H):
        """
        Change weights between consecutive snapshots according to exponential decay rate
        """
        edges1 = set(self.dict_snapshots[t1])
        edges2 = set(self.dict_snapshots[t2])
        common_edges = edges1.intersection(edges2)
        new_edges = list(edges2 - common_edges)
        old_edges = list(edges1 - common_edges)
        for e in list(common_edges):
            H[e[0]][e[1]]["weight"] = 1
            H[e[1]][e[0]]["weight"] = 1
        for n in new_edges:
            H[n[0]][n[1]]["weight"] = 1
            H[n[1]][n[0]]["weight"] = 1
        for o in old_edges:
            w = H[o[0]][o[1]]["weight"]
            H[o[0]][o[1]]["weight"] = self.beta * w
            H[o[1]][o[0]]["weight"] = self.beta * w
        return H

    def create_cumulative_graphs(self, number):
        """
        Create the temporal network gamma=[G1,G2,...,GT]
        """
        index = 0
        T = None
        g_list = []
        nodes_list = []
        times = list(self.dict_snapshots.keys())
        for i in range(len(times)):
            if i == 0:
                G = nx.DiGraph()
                G.add_edges_from(self.dict_snapshots[times[0]])
                weights = self.dict_weights[times[i]]
                G = add_weights(G, weights)
                H = G.to_undirected()
                g_list.append(H.copy())
                nodes = list(H.copy().nodes())
                nodes_list.append(nodes)
            else:
                H.add_edges_from(self.dict_snapshots[times[i]])
                H.to_undirected()
                H = self.change_weights(times[i - 1], times[i], H)
                H_copy = H.copy()
                g_list.append(H_copy)
                nodes_list.append(list(H_copy.nodes()))
                if H_copy.number_of_nodes() < number:
                    index = i
                    T = H_copy.copy()
            print(i, g_list[i].number_of_nodes(), g_list[i].number_of_edges())
        if number != 0:
            g_list = g_list[index:]
            nodes_list = nodes_list[index:]

        return g_list, nodes_list, T, index

    def change_dict_snapshots(self, H):
        """
        If the first snapshot is a union of a few graphs, delete these times and put the only the first time with all
        the edges of the union graph.
        """
        edges = list(H.edges())
        times_to_delete = list(self.dict_snapshots.keys())[:self.index]
        for t in times_to_delete:
            del self.dict_snapshots[t]
        self.dict_snapshots[list(self.dict_snapshots.keys())[0]] = edges

    def create_graph_for_all_times(self):
        """
        Create a "static" graph with all nodes and edges from all snapshots.
        """
        edges = []
        times = list(self.dict_snapshots.keys())
        for t in times:
            for edge in self.dict_snapshots[t]:
                edges.append(edge)
        G = nx.DiGraph()
        G.add_edges_from(edges)
        H = G.to_undirected()
        return H

    def create_weighted_graph_for_all_times(self):
        """
        Create a "static" graph with all nodes and edges from all snapshots. (weighted)
        """
        edges = []
        weights = {}
        times = list(self.dict_snapshots.keys())
        for t in times:
            for edge in self.dict_snapshots[t]:
                if weights.get(edge) is None:
                    weights.update({edge: 1})
                    weights.update({(edge[1], edge[0]): 1})
                else:
                    weights[edge] += 1
                    weights[(edge[1], edge[0])] += 1
                edges.append(edge)
        G = nx.DiGraph()
        G.add_edges_from(edges)
        H = G.to_undirected()
        edges = list(H.edges())
        for e in edges:
            H[e[0]][e[1]]["weight"] = weights[e]
            H[e[1]][e[0]]["weight"] = weights[e]
        return H

    def calculate_embedding(self):
        """
        Function to calculate the embedding of the given graph and return:
        - full_dict_embeddings - A dictionary of all nodes embedding from all snapshots. If a node shows up in more
          than one snapshot so its final embedding in this dictionary is its embedding in the last time stamp the node
          has been shown,
        - dict_all_embeddings: A dictionary of dictionary. The keys are times and the value for each key is the
          embedding dictionary for the specific time.
        - total_time: Running time in seconds for the whole embedding calculation of our suggested method.
        """
        full_dict_embeddings, dict_all_embeddings, total_time = \
            main_fodge(self.initial_method, self.dict_snapshots, self.g_list, self.nodes_list, self.dim,
                       self.params_dict, epsilon=self.epsilon, alpha_exist=self.alpha_exist, file_tags=self.file_tags)
        return full_dict_embeddings, dict_all_embeddings, total_time

    def save_embedding(self, path, mission=None):
        """
        Save the calculated embedding in a .npy file.
        1) full_dict_embeddings: Dict of the embeddings of all the nodes at the final time.
        2) dict_all_embeddings: Dict of the embeddings at any given time. Keys are times and values are dicts of the
        embeddings of all the nodes that appear specifically at this time.
        :param path: Path to where to save the embedding
        :param mission: lp for temporal link prediction task, else None
        :return:
        """
        m = mission if mission is not None else ""
        curr_time = datetime.now().strftime("%Y%m%d_%H%M")
        file_name = self.name + " " + m + " + " + self.initial_method + " +n=" + str(self.number) + " + a=" + str(
            self.alpha_exist) + " + b=" + str(self.beta) + " + e=" + str(self.epsilon) + " " + str(curr_time)
        np.save(os.path.join(path, '{}.npy'.format(file_name)), self.full_dict_embeddings)
        np.save(os.path.join(path, '{}_all_embeddings.npy'.format(file_name)), self.dict_all_embeddings)


def main_fodge(initial_method, dict_snapshots, g_list, nodes_list, dim, params, epsilon=0.01, alpha_exist=0.,
               file_tags=None):
    """
    Main function to run the our suggested dynamic embedding method - FODGE. The inputs variables were already explained
    in the initialization function. This function returns 2 embedding dicts and running time in seconds as explained in
    the "save_embedding" method of the previous class.
    """
    total_time = 0
    t = time.time()

    # start with the initial cumulative snapshot embedding
    dict_projections = initial_function(initial_method, g_list, nodes_list, params, file_tags=file_tags)
    print("number of nodes in projection: ", len(dict_projections))

    # create dictionaries of connected components
    dict_cc, dict_nodes_cc = create_dict_cc_nodes_cc(dict_projections)

    # calculate neighbours dict for each snapshot
    list_neighbours_dict = []
    for i in range(len(g_list)):
        list_neighbours_dict.append(create_dict_neighbors(g_list[i]))

    counter = 1

    # First initialization of the wanted embedding dictionaries and total running time
    times, dict_all_embeddings, full_dict_embeddings = create_two_embedding_dicts(dict_snapshots, dict_projections)

    set_proj_nodes = set(nodes_list[0])

    highest_k_core_all = [get_initial_proj_nodes_by_k_core(g_list[i], 100) for i in range(len(g_list))]

    for i in range(len(g_list) - 1):
        print("Snapshot number", counter)
        # save the dict of embeddings
        if i > 0:
            dict_projections = z.copy()

        j_s = jaccard_similarity(highest_k_core_all[i], highest_k_core_all[i + 1])
        print("js is: ", j_s)

        # perform rotation if needed
        if j_s < 0.9:
            sub_g = g_list[i + 1].subgraph(highest_k_core_all[i + 1])
            print("number of nodes", sub_g.number_of_nodes(), "number of edges", sub_g.number_of_edges())
            print("project core")
            _, dict_proj_core_i_1, _ = final(sub_g, initial_method, params, file_tags=file_tags)
            dict_proj_core_i = dict_of_core(highest_k_core_all[i], dict_projections)

            new_dict_proj_core = rotation(dict_proj_core_i_1, dict_proj_core_i)

            for h in highest_k_core_all[i + 1]:
                dict_projections.update({h: new_dict_proj_core[h]})
                full_dict_embeddings.update({h: new_dict_proj_core[h]})

        # separate nodes of each snapshot to new, exist and disappear (according to the next snapshot)
        new, exist, disappear = divide_snapshot_nodes(nodes_list[i], nodes_list[i + 1])

        # neighbours dictionary for each snapshot
        neighbors_dict = list_neighbours_dict[i + 1]

        # existing nodes that their connections are changes need to be treated as new ones
        changed_exist, changed_exist_proj_dict, dict_projections = check_changed_existing(exist,
                                                                                          list_neighbours_dict[i],
                                                                                          neighbors_dict,
                                                                                          dict_projections)

        set_nodes_no_proj = set(new).union(set(changed_exist))
        set_proj_nodes = set_proj_nodes - set(disappear) - set(changed_exist)
        list_proj_nodes = list(set_proj_nodes)

        # each time update the embedding dict according to the current time stamp
        new_dict = {l: dict_projections[l] for l in list_proj_nodes}
        dict_projections = new_dict.copy()

        # create dicts of connections
        dict_node_node, dict_node_enode, dict_enode_enode = create_dicts_of_connections \
            (set_proj_nodes, set_nodes_no_proj, neighbors_dict)

        # calculate each new node embedding
        dict_projections, dict_nodes_cc, dict_cc, set_no_proj = \
            final_function_lur(dict_projections, dict_node_enode, dict_node_node, dict_enode_enode, dict_cc,
                               dict_nodes_cc, set_nodes_no_proj, 1, dim, g_list[i + 1], epsilon)

        # update which nodes are in the embedding now
        set_proj_nodes = set(nodes_list[i + 1])

        # only for the existing nodes (i.e. nodes that are in sequential numbers) update their embedding according
        # to their last and new embedding (only if neighbours were changed)
        dict_projections = changes_existing_nodes(changed_exist, alpha_exist, dict_projections,
                                                  changed_exist_proj_dict)

        # if there are nodes that are not in the final embedding it means there is a new connected component that
        # needs to be embed from scratch with state-of-the-art embedding algorithm
        if len(set_no_proj) > 1:
            dict_cc, dict_nodes_cc, z = create_new_connected_component(dict_projections, dict_cc, dict_nodes_cc,
                                                                       g_list, set_no_proj, initial_method, params,
                                                                       i, file_tags=file_tags)
        else:
            z = dict_projections.copy()

        # to calculate running time
        elapsed_time = time.time() - t
        total_time += elapsed_time

        counter += 1

        # update wanted dictionaries
        dict_all_embeddings.update({times[counter-1]: z.copy()})
        full_dict_embeddings = update_full_dict_projections(list(z.keys()), full_dict_embeddings, z)

        # print useful information
        print("running time: ", elapsed_time)
        print("The number of nodes that aren't in the final projection:", len(set_no_proj))
        print("The number of nodes that are in the final projection:", len(z), "\n")

    return full_dict_embeddings, dict_all_embeddings, total_time
