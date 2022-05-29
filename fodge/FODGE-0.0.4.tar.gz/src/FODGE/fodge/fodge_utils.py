"""
Utils file of FODGE
"""

from GEA.all_gea import *
import time as my_time
from scipy.linalg import orthogonal_procrustes
import numpy as np
import networkx as nx


def user_print(item, user_wish):
    """
    a function to show the user the state of the code. If you want a live update of the current state of the code and
    some details: set user wish to True else False
    """
    if user_wish is True:
        print(item, sep=' ', end='', flush=True)
        my_time.sleep(3)
        print(" ", end='\r')


def get_initial_proj_nodes_by_k_core(G, number):
    """
    Function to decide which nodes would be in the initial embedding by k-core score.
    :param G: Our graph
    :param number: Controls number of nodes in the initial projection
    :return: A list of the nodes that are in the initial projection
    """
    G.remove_edges_from(G.selfloop_edges())
    core_dict = nx.core_number(G)
    sorted_core_dict = {k: v for k, v in sorted(core_dict.items(), key=lambda item: item[1], reverse=True)}
    keys = list(sorted_core_dict.keys())
    chosen_nodes = keys[:number]
    return chosen_nodes


def jaccard_similarity(list1, list2):
    """
    Calculate Jaccard Similarity between two sets
    """
    intersection = len(list(set(list1).intersection((set(list2)))))
    union = len(list1) + len(list2) - intersection
    return float(intersection) / union


def from_dict_to_matrix(my_dict, d):
    """
    Convert a dictionary of embeddings (key is the vertex id and value is its embedding of dimension d) to a matrix
    of size nxd where n is number of nodes and d is the embedding dimension.
    """
    values = list(my_dict.values())
    for i in range(len(values)):
        v = values[i]
        t = v.copy()
        t = np.reshape(t, (d, 1))
        values[i] = t
    matrix = np.concatenate(tuple(values), axis=1)
    return matrix


def dict_of_core(core_nodes, dict_proj):
    """
    Create the dict of embeddings of the core nodes only
    """
    new_dict = {core_nodes[i]: dict_proj[core_nodes[i]] for i in range(len(core_nodes))}
    return new_dict


def find_rotation_matrix(p, q):
    """
    Find a rotation matrix using orthogonal procrustes
    """
    assert p.shape == q.shape
    n, dim = p.shape

    center_p = p - p.mean(axis=0)
    center_q = q - q.mean(axis=0)

    C = np.dot(np.transpose(center_p), center_q) / n
    V, S, W = np.linalg.svd(C)
    d = (np.linalg.det(V) * np.linalg.det(W)) < 0.0

    if d:
        S[-1] = -S[-1]
        V[:, -1] = -V[:, -1]

    R = np.dot(V, W)

    varP = np.var(p, axis=0).sum()
    c = 1 / varP * np.sum(S)

    t = q.mean(axis=0) - p.mean(axis=0).dot(c * R)

    return c, R, t


def rotation(dict_core_i_1, dict_core_i):
    """
    Perform the rotation of the new core based on it and the previous one
    """
    keys_i = set(dict_core_i.keys())
    keys_i_1 = set(dict_core_i_1.keys())
    nodes = list(keys_i.intersection(keys_i_1))
    print("common core is: ", len(nodes))
    Q_t_1 = np.array([dict_core_i[node] for node in nodes])
    Q_t = np.array([dict_core_i_1[node] for node in nodes])
    R_t, _ = orthogonal_procrustes(Q_t, Q_t_1)
    Q_t = np.array([dict_core_i_1[node] for node in dict_core_i_1])
    R_tQ_t = np.dot(Q_t, R_t)
    new_dict = {node: vec for node, vec in zip(dict_core_i_1, R_tQ_t)}
    return new_dict


def add_weights(G, weights):
    """
    Given a graph and a list of weights, add the weights to each edge of the graph (the order of the list of weights
    must be corresponding to the list of edges in the given graph)/
    :param G: The given graph
    :param weights: A list of weights (floats).
    :return: The graph where attribute of "weight" for each edge is added.
    """
    edges = list(G.edges())
    for i in range(len(edges)):
        e = edges[i]
        # G[e[0]][e[1]] = {"weight": weights[i]}
        G[e[0]][e[1]] = {"weight": 1}
    return G


def divide_snapshot_nodes(previous_nodes, next_nodes):
    """
    For each snapshot divide the nodes into three groups: new- nodes that weren't in the previous snapshot,
    exist- nodes that are in both sequential snapshots, disappear- nodes that were in the previous snapshot but in the
    next they disappeared.
    :param previous_nodes: Node from snapshot t-1 (list)
    :param next_nodes: Nodes from snapshot t (list)
    :return: 3 lists of nodes as explained above
    """
    set_previous = set(previous_nodes)
    set_next = set(next_nodes)
    new = list(set_next - set_previous)
    exist = list(set_next.intersection(set_previous))
    disappear = list(set_previous - set(exist))
    return new, exist, disappear


def calculate_first_snapshot_embedding(user_wish, g_list_, nodes_list_, initial_method, params, file_tags=None):
    """
    Function to calculate the embedding of the first snapshot with state-of-the-art embedding method.
    :param user_wish: True if the user wants useful things to be printed, else False.
    :param g_list_: The list of graphs- graph for each time stamp.
    :param nodes_list_: List of lists of nodes- each time stamp has its own list of nodes
    :param initial_method: State-of-the-srt embedding method to embed the graph with.
    :param params: Parameters dict corresponding to the initial embedding used
    :return: The graph representing the first snapshot, initial dict of embeddings and initial set of nodes that are
             currently in the embedding.
    """
    # start with the first snapshot
    first_snapshot = g_list_[0]
    n = len(nodes_list_[0])
    e = first_snapshot.number_of_edges()
    user_print("number of nodes in first snapshot is: " + str(n), user_wish)
    user_print("number of edges in first snapshot is: " + str(e), user_wish)

    first_snapshot_nodes = nodes_list_[0]
    set_G_nodes = set(first_snapshot_nodes)

    # calculate the first snapshot embedding with a state-of-the-art algorithm
    user_print("calculate the projection of the first graph with {}...".format(initial_method), user_wish)
    _, dict_projections, _ = final(first_snapshot, initial_method, params, file_tags=file_tags)

    return first_snapshot, dict_projections, set_G_nodes


def initial_function(initial_method, g_list, nodes_list, params, file_tags=None):
    """
    Initial function to calculate the initial embedding, i.e. the embedding of the first snapshot.
    :param initial_method: embedding algorithm to embed the graph with
    :param g_list: The list of graph snapshots
    :param nodes_list: List of nodes for each time stamp
    :param file_tags: File of tags for each vertex if GEA used is GCN, else False
    :param params: Parameters for the embedding method
    :return: Initial embedding dictionary
    """
    user_wish = True

    # calculate fist snapshot embedding
    first_snapshot, dict_projections, set_proj_nodes = calculate_first_snapshot_embedding(user_wish, g_list,
                                                                                          nodes_list,
                                                                                          initial_method, params,
                                                                                          file_tags=file_tags)
    return dict_projections


def create_two_embedding_dicts(dict_snapshots, dict_projections):
    """
    First initialization of the two wanted embedding dictionaries. They are first embed with the nodes of the first
    snapshot and their embeddings.
    :param dict_snapshots: Dict where keys are times and values are a list of edges for each time stamp.
    :param dict_projections: Dict embeddings- currently keys are the nodes of the first snapshot and the values are
                             their embeddings in the first time stamp.
    :return: - full_dict_embeddings - A dictionary of all nodes embedding from all snapshots. If a node shows up in more
               than one snapshot so its final embedding in this dictionary is its embedding in the last time stamp the
               node has been shown,
             - dict_all_embeddings: A dictionary of dictionary. The keys are times and the value for each key is the
               embedding dictionary for the specific time.
             - times- the list of time stamps.
    """
    times = list(dict_snapshots.keys())

    dict_all_embeddings = {}
    dict_all_embeddings.update({times[0]: dict_projections.copy()})

    full_dict_embeddings = dict_projections.copy()

    return times, dict_all_embeddings, full_dict_embeddings


def create_dict_neighbors(H):
    """
    Given our undirected graph, Create a dictionary where value==node and key==set of its neighbours.
    """
    G = H.to_undirected()
    G_nodes = list(G.nodes())
    neighbors_dict = {}
    for i in range(len(G_nodes)):
        node = G_nodes[i]
        neighbors_dict.update({node: set(G[node])})
    return neighbors_dict


def create_dicts_of_connections(set_proj_nodes, set_no_proj_nodes, neighbors_dict):
    """
    a function that creates 3 dictionaries:
    1. dict_node_node (explained below)
    2. dict_node_enode (explained below)
    2. dict_enode_enode (explained below)
    """
    # value == (node that isn't in the embedding), key == (set of its neighbours that are also not in the embedding)
    dict_node_node = {}
    # value == (node that isn't in the embedding), key == (set of neighbours thar are in the embedding)
    dict_node_enode = {}
    # key==(node that is in the projection and has neighbors in it), value==(set of neighbors that are in projection)
    dict_enode_enode = {}
    # nodes that are not in the projection
    list_no_proj = list(set_no_proj_nodes)
    list_proj = list(set_proj_nodes)
    # not_connected_to_embed = []
    for i in range(len(list_no_proj)):
        node = list_no_proj[i]
        # neighbors of the node that aren't in the projection
        set1 = neighbors_dict[node].intersection(set_no_proj_nodes)
        dict_node_node.update({node: set1})
        # neighbors of the node that are in the projection
        set2 = neighbors_dict[node].intersection(set_proj_nodes)
        if len(set2) > 0:
            dict_node_enode.update({node: set2})
    for i in range(len(list_proj)):
        node = list_proj[i]
        # neighbors of the node that are in the projection
        set1 = neighbors_dict[node].intersection(set_proj_nodes)
        if len(set1) > 0:
            dict_enode_enode.update({node: set1})
    return dict_node_node, dict_node_enode, dict_enode_enode


def create_mapping(dict_times):
    """
    If times are not integers, transform them into integers.
    :param dict_times: Dict where keys are times.
    :return: A mapping which is a dictionary maps from current names of time stamps to integers (by their index)
    """
    keys = list(dict_times.keys())
    mapping = {}
    for i in range(len(keys)):
        mapping.update({keys[i]: i})
    return mapping


def create_new_cc(nodes_list, G, to_undirected=False):
    """
    If there are new nodes in the current snapshots that do not connect with nodes that were in the previous snapshot
    it means they create a new connected component. This function returns the sub graph that is built by these nodes
    and their connections with each other.
    :param nodes_list: A list of nodes in the new sub graph
    :param G: The given graph in the current snapshot
    :param to_undirected: If the graph is directed it needs to first be undirected.
    :return: The sub graph
    """
    if to_undirected is True:
        H = G.to_undirected()
        sub_G = nx.subgraph(H, nodes_list)
    else:
        sub_G = nx.subgraph(G, nodes_list)
    return sub_G


def create_new_connected_component(dict_projections, dict_cc, dict_nodes_cc, g_list_, set_no_proj, initial_method,
                                   params, i, file_tags=None):
    """
    If needed, create new connect component and update wanted dicts.
    :param dict_projections: Embedding dict
    :param dict_cc: Dict where keys are the number of the connected component and values are list of nodes that are in
                    this cc.
    :param dict_nodes_cc: Dict where keys are nodes and values is the number representing the cc they are in.
    :param g_list_: List of graphs for each time stamp.
    :param set_no_proj: Set of nodes that are currently not in the embedding because they create together a new cc.
    :param initial_method: State-of-the-art method to embed them with.
    :param params: Dict of parameters corresponding to the initial method.
    :param i: Index of the time stamp
    :param file_tags: If GCN GEA is used, one needs to provide file of tags
    :return: Updated dict_cc, dict_nodes_cc, and embedding dictionary.
    """
    new_cc = create_new_cc(list(set_no_proj), g_list_[i + 1], to_undirected=True)
    dict_cc, dict_nodes_cc = add_new_cc(new_cc, dict_nodes_cc, dict_cc)
    if new_cc.number_of_nodes() < params["dimension"] and initial_method == "HOPE":
        dim = params["dimension"]
        initial_method = "node2vec"
        params = {"dimension": dim, "walk_length": 80, "num_walks": 16, "workers": 2}
    _, dict_proj_new_cc, _ = final(new_cc, initial_method, params, file_tags=file_tags)
    z = {**dict_projections, **dict_proj_new_cc}.copy()
    return dict_cc, dict_nodes_cc, z


def create_dicts_cc(first_snapshot):
    """
    Function to create two important dictionaries:
    - dict_cc : keys are the different numbers representing the different connected components in the graph , while
    each value is a list of the nodes that are in the corresponding connected component.
    - dict_nodes_cc: keys are the nodes and each value is the connected component the node is related to.
    :param first_snapshot: The first snapshot graph
    :return: the two dictionaries
    """
    list_cc = sorted(nx.connected_components(first_snapshot), key=len, reverse=True)
    number_cc = len(list_cc)
    dict_cc = {i: list(c) for i, c in zip(list(range(number_cc)), list_cc)}
    dict_nodes_cc = {}
    for j in range(len(list_cc)):
        dict_nodes_cc.update({i: j for i in list_cc[j]})
    return dict_cc, dict_nodes_cc


def list_first_second_neigh(node, dict_neighbours):
    """
    Find the list of first and second nodes
    :param node: A node in the graph
    :param dict_neighbours: dict where keys is a node and value is a set of its node
    :return: Set of first and second neighbours
    """
    neigh = dict_neighbours[node].copy()
    for n in list(neigh):
        set1 = dict_neighbours[n].copy()
        neigh = neigh.union(set1)
    return neigh


def check_changed_existing(nodes_exist, dict_neighbors_old, dict_neighbors_new, dict_projections, second=False):
    """
    A function to check which nodes out of the nodes that are common to the current and previous snapshot have changed
    their neighbours. If they have, their embedding should be recalculated as new ones, but their current embeddings
    should be preserved for later use. In addition, they are deleted from the embedding dictionary (for now).
    :param nodes_exist: Common nodes between current and precious snapshots.
    :param dict_neighbors_old: Dictionary of neighbours of previous snapshots
    :param dict_neighbors_new: Dictionary of neighbours of current snapshots
    :param dict_projections: Dictionary of embeddings
    :param second: True if considering both first and second order neighbors, else False
    :return: A list of all changed nodes, a dictionary of the embeddings of all changed nodes, the update embedding
    dictionary of all nodes.
    """
    changed_exist = []
    changed_exist_proj_dict = {}
    for node in nodes_exist:
        if dict_projections.get(node) is not None:
            # changed existing nodes are nodes that their first neighbours are changed (don't check second order neighbors)
            if second is False:
                if dict_neighbors_old[node] == dict_neighbors_new[node]:
                    continue
                else:
                    changed_exist.append(node)
                    changed_exist_proj_dict.update({node: dict_projections[node]})
                    del dict_projections[node]
            # changed existing nodes are nodes that their first or second neighbours are changed
            else:
                first_second_neighbors_old = list_first_second_neigh(node, dict_neighbors_old)
                first_second_neighbors_new = list_first_second_neigh(node, dict_neighbors_new)
                if first_second_neighbors_old == first_second_neighbors_new:
                    continue
                else:
                    changed_exist.append(node)
                    changed_exist_proj_dict.update({node: dict_projections[node]})
                    del dict_projections[node]
    return changed_exist, changed_exist_proj_dict, dict_projections


def add_new_cc(graph, dict_nodes_cc, dict_cc):
    """
    If a new connected component is added in the current snapshot, update dict_cc and dict_nodes_cc.
    :param graph: The new sub graph that is added, it has its own connected components.
    :param dict_nodes_cc: Explained earlier
    :param dict_cc: Explained earlier
    :return: Two updated dicts
    """
    list_cc = sorted(nx.connected_components(graph), key=len, reverse=True)
    number_cc_new = len(list_cc)
    last_cc = sorted(list(dict_cc.keys()), reverse=False)[-1] + 1
    dict_cc.update({last_cc + j: list(list_cc[j]) for j in range(number_cc_new)})
    for k in range(len(list_cc)):
        dict_nodes_cc.update({i: last_cc + k for i in list_cc[k] if dict_nodes_cc.get(i) is None})
    return dict_cc, dict_nodes_cc


def update_full_dict_projections(nodes, full_dict_projections, t_dict_proj):
    """
    Full dict embeddings is a dictionary where keys are nodes and values are their embedding in the latest time stamp
    they have shown up, i.e. if a node is in oth time stamps t and k where t < k, then its embedding here is of
    time k (the bigger one).
    :param nodes: Nodes of current snapshot
    :param full_dict_projections: The current full_dict_projections
    :param t_dict_proj: embedding dict of time t
    :return: Updated full_dict_projections
    """
    for node in nodes:
        a = t_dict_proj[node]
        if full_dict_projections.get(node) is None:
            full_dict_projections.update({node: a})
        else:
            full_dict_projections[node] = a
    return full_dict_projections


def update_dicts_cc(node, dict_node_enode, dict_cc, dict_nodes_cc):
    """
    For a new node added to the embedding, dicts of connected components should be updated.
    :param node: Current node
    :param dict_node_enode: Dict where value == (node that isn't in the embedding), key == (set of neighbours thar are
                            in the embedding)
    :param dict_cc: Dict where keys are the number of the connected component and values are list of nodes that are in
                    this cc.
    :param dict_nodes_cc: Dict where keys are nodes and values is the number representing the cc they are in.
    :return: Updated dict_cc, dict_nodes_cc and list_cc which is the list of cc that needs to be united together.
    """
    list_cc = []
    neighbors = dict_node_enode[node]
    values = [dict_nodes_cc[n] for n in neighbors]
    values = list(dict.fromkeys(values))
    values.sort()
    # the node does not connect between two connected components

    if dict_nodes_cc.get(node) is None:
        dict_nodes_cc.update({node: values[0]})
        dict_cc[values[0]].append(node)
    else:
        current_cc = dict_nodes_cc[node]
        if current_cc != values[0]:
            dict_nodes_cc.update({node: values[0]})
            dict_cc[values[0]].append(node)
            my_set = set(dict_cc[current_cc])
            my_set2 = my_set - set([node])
            if len(my_set2) == 0:
                del dict_cc[current_cc]
            else:
                dict_cc[current_cc] = list(my_set2)

    if len(values) > 1:
        for i in values:
            list_cc.append(i)
    # the node connects between two connected components, it will be in the earliest cc

    return list_cc, dict_nodes_cc, dict_cc


def find_removal_edges(g1, g2):
    """
    Given a graph in snapshot t and another graph in snapshot t+1, find the removal edges, i.e. the ones that in G_t but
    not in G_(t+1).
    :param g1: Graph in snapshot t
    :param g2: Graph in snapshot t+1
    :return: List of removal edges
    """
    edges_1 = set(g1.edges())
    new_edges_1 = []
    for e in edges_1:
        new_edges_1.append(e if int(e[0]) < int(e[1]) else (e[1], e[0]))
    edges_2 = set(g2.edges())
    new_edges_2 = []
    for e in edges_2:
        new_edges_2.append(e if int(e[0]) < int(e[1]) else (e[1], e[0]))
    return list(set(new_edges_1) - set(new_edges_2))


def find_changed_nodes(removal_edges, g):
    """
    Find the nodes that are changed, i.e the nodes that are common to both consecutive snapshots and their neighbors are
    changed.
    :param removal_edges: List of removal edges
    :param g: The previous snapshot
    :return: List of changed existing nodes.
    """
    nodes = set(g.nodes())
    nodes_list = []
    for e in removal_edges:
        nodes_list.append(e[0])
        nodes_list.append(e[1])
    nodes_list = set(nodes_list).intersection(nodes)
    return nodes_list


def calculate_union_embedding(g, dict_projections, changed_nodes, nodes, nodes_previous, initial_method, params):
    """
    Calculate the embeddings of the united connected components
    """
    _, dict_enode_proj, _ = final(g, initial_method, params)
    non_changed_nodes = set(nodes) - changed_nodes
    dict_projections.update({n: dict_enode_proj[n] for n in non_changed_nodes})
    changed_previous = changed_nodes.intersection(set(nodes_previous))
    if len(changed_previous) > 0:
        for l in changed_nodes:
            del dict_projections[l]
    dict_changed_proj = {c: dict_enode_proj[c] for c in changed_nodes}
    # del dict_projections[l] for l in changed_nodes if l in nodes_previous
    return dict_projections, non_changed_nodes, dict_changed_proj


def create_dict_cc_nodes_cc(dict_projections):
    """
    Create dictionary of connected components.
    :param dict_projections: Dict of nodes and their embeddings
    :return: dict cc: key - the number of the cc , value - list of nodes in this cc
             dict_nodes_cc: key - the graph's node , value - the number of cc the node is in
    """
    keys = list(dict_projections.keys())
    dict_cc = {0: keys}
    dict_nodes_cc = {m: 0 for m in keys}
    return dict_cc, dict_nodes_cc


def changes_existing_nodes(nodes_exist, alpha, dict_proj, dict_proj_changed_exist):
    """
    For nodes that are in both sequential snapshots, update their embedding by their current embedding and new
    calculated embedding. Do it only for those that their neighbours are changed.
    :param nodes_exist: Nodes that exist in both sequential snapshots and their neighbours are changed
    :param alpha: Parameter representing the importance that is given to the old embedding
    :param dict_proj: Dictionary of embeddings of the nodes
    :param dict_proj_changed_exist: Dict of previous embedding of the changed existing nodes.
    :return: An updated embedding dictionary
    """
    for node in nodes_exist:
        if dict_proj.get(node) is not None:
            new_proj = dict_proj[node]
            old_proj = dict_proj_changed_exist[node]
            final_proj = alpha * old_proj + (1 - alpha) * new_proj
            dict_proj[node] = final_proj
    return dict_proj
