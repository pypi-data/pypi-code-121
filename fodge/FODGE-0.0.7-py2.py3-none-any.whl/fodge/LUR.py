"""
Local update rule
"""

import heapq
from .fodge_utils import *


def lur_embed(current_node, proj_nodes, dict_proj, dim, dict_enode_enode, G, epsilon):
    """
    Calculate the current node embedding according to the formuala mentioned in the pdf file
    :param current_node: Calculated embedding node
    :param proj_nodes: Nodes that are currently in the embedding
    :param dict_proj: Dictionary of nodes and their embeddings
    :param dim: Embedding Dimension
    :param dict_enode_enode: key==(node that is in the projection and has neighbors in it), value==(set of neighbors
    that are in projection)
    :param G: The graph (networkx)
    :param epsilon: The weight that is given to the second order neighbours.
    :return: The node's final embedding
    """
    proj = []
    weights_first_neigh = []
    mean_two_order_proj = []
    # get a list of the projections of the neighbors in the projection
    proj_nodes1 = list(proj_nodes)
    # the number of first order neighbors
    k1 = len(proj_nodes)
    k2 = 0
    # to calculate the mean projection of the second order neighbors
    for k in range(len(proj_nodes1)):
        if dict_enode_enode.get(proj_nodes1[k]) is not None:
            two_order_neighs = dict_enode_enode.get(proj_nodes1[k]).copy()
            if current_node in two_order_neighs:
                two_order_neighs.remove(current_node)
            if len(two_order_neighs) == 0:
                two_order_neighs = None
        else:
            two_order_neighs = None
        # if the neighbors in the projection also have neighbors in the projection calculate the average projection
        if two_order_neighs is not None:
            two_order_neighs = list(two_order_neighs)
            k2 += len(two_order_neighs)
            two_order_projs = []
            weights_two_neigh = []
            for i in range(len(two_order_neighs)):
                two_order_proj = dict_proj[two_order_neighs[i]]
                weights_two_neigh.append(G[proj_nodes1[k]][two_order_neighs[i]]["weight"])
                two_order_projs.append(two_order_proj)
            two_order_projs = np.array(two_order_projs)
            weights_two_neigh = np.array(weights_two_neigh)
            two_order_projs = np.average(two_order_projs, axis=0, weights=weights_two_neigh)
        # else, the mean projection in 0
        else:
            two_order_projs = np.zeros(dim)
        mean_two_order_proj.append(two_order_projs)
        # list of embeddings of each first order neighbour
        proj.append(dict_proj[proj_nodes1[k]])
        weights_first_neigh.append(G[current_node][proj_nodes1[k]]["weight"])
    # for every neighbor we have the average projection of its neighbors, so now do average on all of them
    mean_two_order_proj = np.array(mean_two_order_proj)
    mean_two_order_proj = np.mean(mean_two_order_proj, axis=0)
    proj = np.array(proj)
    weights_first_neigh = np.array(weights_first_neigh)
    # find the mean proj of first order neighbours
    proj = np.average(proj, axis=0, weights=weights_first_neigh)
    # the final projection of the node
    final_proj = proj + epsilon * (k2 / k1) * (proj - mean_two_order_proj)
    return final_proj


def one_iteration(dict_enode_proj, dict_node_enode, dict_node_node, dict_enode_enode, dict_cc, dict_nodes_cc,
                  set_n_e, current_node, dim, G, epsilon):
    """
    A function that does one iteration over a given batch
    """
    condition = 1

    # check cc
    list_cc, dict_nodes_cc, dict_cc = update_dicts_cc(current_node, dict_node_enode, dict_cc, dict_nodes_cc)

    # get the neighbors in projection of node i
    embd_neigh = dict_node_enode[current_node]
    # the final projection of the node
    final_proj = lur_embed(current_node, embd_neigh, dict_enode_proj, dim, dict_enode_enode, G, epsilon)
    # add the node and its projection to the dict of projections
    dict_enode_proj.update({current_node: final_proj})
    # add our node to the dict of proj to proj and delete it from node_enode because now it's in the projection
    dict_enode_enode.update({current_node: embd_neigh})
    dict_node_enode.pop(current_node)
    # get the non embd neighbors of the node
    relevant_n_e = dict_node_node[current_node]
    # delete because now it is in the projection
    dict_node_node.pop(current_node)
    embd_neigh = list(embd_neigh)
    for i in range(len(embd_neigh)):
        f = dict_enode_enode.get(embd_neigh[i])
        if f is not None:
            dict_enode_enode[embd_neigh[i]].update([current_node])
        else:
            dict_enode_enode.update({embd_neigh[i]: set([current_node])})
    # check if num of non embd neighbors of our node bigger then zero
    if len(relevant_n_e) > 0:
        # loop of non embd neighbors
        relevant_n_e1 = list(relevant_n_e)
        for j in range(len(relevant_n_e)):
            tmp_append_n_n = dict_node_node.get(relevant_n_e1[j])
            if tmp_append_n_n is not None:
                # if relevant_n_e1[j] in dict_node_node:
                tmp_append_n_n = tmp_append_n_n - set([current_node])
                dict_node_node[relevant_n_e1[j]] = tmp_append_n_n
            tmp_append = dict_node_enode.get(relevant_n_e1[j])
            if tmp_append is not None:
                # add our node to the set cause now our node is in embd
                tmp_append.update(set([current_node]))
                dict_node_enode[relevant_n_e1[j]] = tmp_append
            else:
                dict_node_enode.update({relevant_n_e1[j]: set([current_node])})
    set_n_e.remove(current_node)

    return condition, dict_enode_proj, dict_node_enode, dict_node_node, dict_enode_enode, set_n_e, list_cc, dict_cc, \
           dict_nodes_cc


def one_iteration_for_connected_cc(dict_enode_proj, dict_node_enode, dict_node_node, dict_enode_enode, set_n_e,
                                   current_node, dim, G, epsilon):
    """
    A function that does one iteration over a given batch for a specific new connected component (for merging)
    """
    condition = 1
    # get the neighbors in projection of node i
    embd_neigh = dict_node_enode[current_node]
    # the final projection of the node
    final_proj = lur_embed(current_node, embd_neigh, dict_enode_proj, dim, dict_enode_enode, G, epsilon)
    # add the node and its projection to the dict of projections
    dict_enode_proj.update({current_node: final_proj})
    # add our node to the dict of proj to proj and delete it from node_enode because now it's in the projection
    dict_enode_enode.update({current_node: embd_neigh})
    dict_node_enode.pop(current_node)
    # get the non embd neighbors of the node
    relevant_n_e = dict_node_node[current_node]
    # delete because now it is in the projection
    dict_node_node.pop(current_node)
    embd_neigh = list(embd_neigh)
    for i in range(len(embd_neigh)):
        f = dict_enode_enode.get(embd_neigh[i])
        if f is not None:
            dict_enode_enode[embd_neigh[i]].update([current_node])
        else:
            dict_enode_enode.update({embd_neigh[i]: set([current_node])})
    # check if num of non embd neighbors of our node bigger then zero
    if len(relevant_n_e) > 0:
        # loop of non embd neighbors
        relevant_n_e1 = list(relevant_n_e)
        for j in range(len(relevant_n_e)):
            tmp_append_n_n = dict_node_node.get(relevant_n_e1[j])
            if tmp_append_n_n is not None:
                # if relevant_n_e1[j] in dict_node_node:
                tmp_append_n_n = tmp_append_n_n - set([current_node])
                dict_node_node[relevant_n_e1[j]] = tmp_append_n_n
            tmp_append = dict_node_enode.get(relevant_n_e1[j])
            if tmp_append is not None:
                # add our node to the set cause now our node is in embd
                tmp_append.update(set([current_node]))
                dict_node_enode[relevant_n_e1[j]] = tmp_append
            else:
                dict_node_enode.update({relevant_n_e1[j]: set([current_node])})
    set_n_e.remove(current_node)
    return condition, dict_enode_proj, dict_node_enode, dict_node_node, dict_enode_enode, set_n_e


def final_function_lur(dict_enode_proj, dict_node_enode, dict_node_node, dict_enode_enode, dict_cc, dict_nodes_cc,
                       set_n_e, batch_precent, dim, G, epsilon):
    """
    the final function that iteratively divided the dictionary of nodes without embedding into number of batches
    determined by batch_precent. It does by building a heap every iteration so that we enter the nodes to the
    projection from the nodes which have the most neighbors in the embedding to the least. This way the projection
    gets more accurate.
    """
    condition = 1
    k = 0
    set_n_e2 = set_n_e.copy()
    while condition > 0:
        condition = 0
        k += 1
        batch_size = int(batch_precent * len(set_n_e2))
        # loop over node are not in the embedding
        if batch_size > len(set_n_e):
            num_times = len(set_n_e)
        else:
            num_times = batch_size
        list_n_e = list(set_n_e)
        heap = []
        for i in range(len(list_n_e)):
            my_node = list_n_e[i]
            a = dict_node_enode.get(my_node)
            if a is not None:
                num_neighbors = len(dict_node_enode[my_node])
            else:
                num_neighbors = 0
            heapq.heappush(heap, [-num_neighbors, my_node])
        for i in range(len(set_n_e))[:num_times]:
            # look on node number i in the loop
            current_node = heapq.heappop(heap)[1]
            if dict_node_enode.get(current_node) is not None:
                condition, dict_enode_proj, dict_node_enode, dict_node_node, dict_enode_enode, set_n_e, list_cc, \
                dict_cc, dict_nodes_cc = one_iteration(dict_enode_proj, dict_node_enode, dict_node_node,
                                                       dict_enode_enode, dict_cc, dict_nodes_cc, set_n_e, current_node,
                                                       dim, G, epsilon)
                # if list_cc > 0 then the node connects between several connected components and they should be
                # embed all over again considering the new connections
                if len(list_cc) > 0:
                    list_all_nodes = []
                    for j in range(len(list_cc) - 1):
                        for pw in dict_cc[list_cc[j + 1]]:
                            list_all_nodes.append(pw)
                    set_no_proj_nodes = set(list_all_nodes)
                    dict_enode_proj, set_no_e = final_function_lur_for_connected_cc(dict_enode_proj, dict_node_enode,
                                                                                     dict_node_node,
                                                                                     dict_enode_enode,
                                                                                     set_no_proj_nodes, batch_precent,
                                                                                     dim, G, epsilon)
                    for n in list_all_nodes:
                        dict_nodes_cc[n] = list_cc[0]
                    for j in range(len(list_cc) - 1):
                        for p in dict_cc[list_cc[j + 1]]:
                            dict_cc[list_cc[0]].append(p)
                        if dict_cc.get(list_cc[j + 1]) is not None:
                            del dict_cc[list_cc[j + 1]]
    return dict_enode_proj, dict_nodes_cc, dict_cc, set_n_e


def final_function_lur_for_connected_cc(dict_enode_proj, dict_node_enode, dict_node_node, dict_enode_enode, set_n_e,
                                        batch_precent, dim, G, epsilon):
    """
    the final function that iteratively divided the dictionary of nodes without embedding into number of batches
    determined by batch_precent. It does by building a heap every iteration so that we enter the nodes to the
    projection from the nodes which have the most neighbors in the embedding to the least. This way the projection
    gets more accurate.
    """
    condition = 1
    k = 0
    set_n_e2 = set_n_e.copy()
    while condition > 0:
        condition = 0
        k += 1
        batch_size = int(batch_precent * len(set_n_e2))
        # loop over node are not in the embedding
        if batch_size > len(set_n_e):
            num_times = len(set_n_e)
        else:
            num_times = batch_size
        list_n_e = list(set_n_e)
        heap = []
        for i in range(len(list_n_e)):
            my_node = list_n_e[i]
            a = dict_node_enode.get(my_node)
            if a is not None:
                num_neighbors = len(dict_node_enode[my_node])
            else:
                num_neighbors = 0
            heapq.heappush(heap, [-num_neighbors, my_node])
        for i in range(len(set_n_e))[:num_times]:
            # look on node number i in the loop
            current_node = heapq.heappop(heap)[1]
            if dict_node_enode.get(current_node) is not None:
                condition, dict_enode_proj, dict_node_enode, dict_node_node, dict_enode_enode, set_n_e = \
                    one_iteration_for_connected_cc(dict_enode_proj, dict_node_enode, dict_node_node, dict_enode_enode,
                                                   set_n_e, current_node, dim, G, epsilon)
    return dict_enode_proj, set_n_e