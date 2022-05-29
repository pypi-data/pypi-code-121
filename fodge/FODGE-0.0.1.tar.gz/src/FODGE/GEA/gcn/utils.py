import numpy as np
import scipy.sparse as sp
import torch
import scipy
import networkx as nx
from scipy import io


def encode_onehot(labels):
    classes = set(labels)
    classes_dict = {c: np.identity(len(classes))[i, :] for i, c in
                    enumerate(classes)}
    labels_onehot = np.array(list(map(classes_dict.get, labels)),
                             dtype=np.int32)
    return labels_onehot


def read_yelp_labels(file_tags):
    """
    Read labels of yelp dataset
    """
    X = np.loadtxt(file_tags)
    Y = np.int_(X)
    number_of_labels = Y.shape[1]
    for k in range(number_of_labels):
        if np.all((Y[:, k] == 0), axis=0):
            Y = np.delete(Y, k, 1)
    return Y
    

def read_flickr_labels(file_tags):
    features_struct = scipy.io.loadmat(file_tags)
    labels = scipy.sparse.csr_matrix(features_struct["group"])
    a = scipy.sparse.csr_matrix.toarray(labels)
    return a


def read_labels_nodes(file_tags):
    X = np.genfromtxt(file_tags, dtype=np.dtype(str))
    d_X = {"labels": X[:, -1], "nodes": X[:, 0]}
    return d_X


def new_load_data(G, sub_G, file_tags, num_of_nodes, nc_nodes, multilabel=False, features_file=None):
    nodes = list(sub_G.nodes())
    n2i = {nodes[i]: i for i in range(len(nodes))}
    common = list(set(nodes).intersection(set(nc_nodes)))
    train_nodes = list(set(nodes)-set(common))
    
    all_labels = {}
    with open(file_tags, 'r') as reader:
        for line in reader:
            parts = line.strip().split()
            n_id, l_id = str(parts[0]), str(parts[1])
            all_labels[n_id] = l_id
    reader.close()
    labels_d = {}
    for node in nodes:
        labels_d.update({node: all_labels[node]})
    labels = list(labels_d.values())
    labels = np.asarray(labels, dtype=np.dtype(str))
    labels = encode_onehot(labels)
        
    if features_file is None:
        features = sp.identity(num_of_nodes, dtype=np.float32)
    else:
        idx_features_labels = np.genfromtxt("../datasets/cora.content", dtype=np.dtype(str))
        features = sp.csr_matrix(idx_features_labels[:, 1:-1], dtype=np.float32)
    
    idx_map = {j: i for i, j in enumerate(nodes)}
    adj = sp.coo_matrix(nx.to_scipy_sparse_matrix(sub_G))

    # build symmetric adjacency matrix
    adj = adj + adj.T.multiply(adj.T > adj) - adj.multiply(adj.T > adj)

    features = normalize(features)
    adj = normalize(adj + sp.eye(adj.shape[0]))
    
    idx_train = [n2i[t] for t in train_nodes]
    idx_val = [n2i[t] for t in common]
    idx_test = [n2i[t] for t in common]

    features = torch.FloatTensor(np.array(features.todense()))
    if multilabel:
        labels = torch.FloatTensor(labels)
    else:
        labels = torch.LongTensor(np.where(labels)[1])
    
    adj = sparse_mx_to_torch_sparse_tensor(adj)

    idx_train = torch.LongTensor(idx_train)
    idx_val = torch.LongTensor(idx_val)
    idx_test = torch.LongTensor(idx_test)

    return adj, features, labels, idx_train, idx_val, idx_test


def normalize(mx):
    """Row-normalize sparse matrix"""
    rowsum = np.array(mx.sum(1))
    r_inv = np.power(rowsum, -1).flatten()
    r_inv[np.isinf(r_inv)] = 0.
    r_mat_inv = sp.diags(r_inv)
    mx = r_mat_inv.dot(mx)
    return mx


def accuracy(output, labels):
    preds = output.max(1)[1].type_as(labels)
    correct = preds.eq(labels).double()
    correct = correct.sum()
    return correct / len(labels)


def sparse_mx_to_torch_sparse_tensor(sparse_mx):
    """Convert a scipy sparse matrix to a torch sparse tensor."""
    sparse_mx = sparse_mx.tocoo().astype(np.float32)
    indices = torch.from_numpy(
        np.vstack((sparse_mx.row, sparse_mx.col)).astype(np.int64))
    values = torch.from_numpy(sparse_mx.data)
    shape = torch.Size(sparse_mx.shape)
    return torch.sparse.FloatTensor(indices, values, shape)
