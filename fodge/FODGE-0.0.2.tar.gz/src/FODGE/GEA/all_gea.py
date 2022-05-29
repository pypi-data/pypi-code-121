"""
Implantation of 5 state-of-the-art static embedding algorithms: Node2Vec, Graph Factorization, HOPE, GAE and GCN.
- The implementations of GF and HOPE were taken from GEM toolkit (https://github.com/palash1992/GEM)
- Node2vec is implemented using node2vec public package (https://github.com/eliorc/node2vec)
- The implementation of GCN was taken from their public github repository (https://github.com/tkipf/pygcn)
- The implementation of GAE was taken from their public github repository (https://github.com/tkipf/gae)
"""
from __future__ import division
from __future__ import print_function
import sys
from time import time
from node2vec import Node2Vec
from torch import optim
from scipy.sparse import identity
from scipy.sparse.linalg import inv
from scipy.sparse.linalg import svds
from sklearn.metrics import accuracy_score
from GEA.gae_pytorch.gae.model import GCNModelVAE
from GEA.gae_pytorch.gae.optimizer import loss_function
from GEA.gae_pytorch.gae.utils import load_data, mask_test_edges, preprocess_graph, get_roc_score, create_false_edges
from GEA.gcn.models import *
from GEA.gcn.utils import *



class GAE:
    def __init__(self, params, method_name, graph):
        self._d = params["hidden1"]
        self._method_name = method_name
        self._graph = graph
        self.create_adj_features()
        self._params = params
        self.embedding_matrix, self.embedding_dict = self.train()

    def create_adj_features(self):
        self._adj = nx.to_scipy_sparse_matrix(self._graph)
        self._features = torch.tensor(np.identity(self._graph.number_of_nodes())).type('torch.FloatTensor')

    def train(self):
        adj, features = self._adj, self._features
        n_nodes, feat_dim = features.shape

        nodes = list(self._graph.nodes())
        if len(nodes) > 100:
            hidden1 = self._params['hidden1']
        else:
            hidden1 = 100

        # Store original adjacency matrix (without diagonal entries) for later
        adj_orig = adj
        adj_orig = adj_orig - sp.dia_matrix((adj_orig.diagonal()[np.newaxis, :], [0]), shape=adj_orig.shape)
        adj_orig.eliminate_zeros()

        # adj_train, train_edges, val_edges, val_edges_false, test_edges, test_edges_false = mask_test_edges(adj)
        adj_train, train_edges, train_edges_false = create_false_edges(adj)
        adj = adj_train

        # Some preprocessing
        adj_norm = preprocess_graph(adj)
        adj_label = adj_train + sp.eye(adj_train.shape[0])
        # adj_label = sparse_to_tuple(adj_label)
        adj_label = torch.FloatTensor(adj_label.toarray())

        pos_weight = float(adj.shape[0] * adj.shape[0] - adj.sum()) / adj.sum()
        norm = adj.shape[0] * adj.shape[0] / float((adj.shape[0] * adj.shape[0] - adj.sum()) * 2)

        model = GCNModelVAE(feat_dim, hidden1, self._params['hidden2'], self._params['dropout'])
        optimizer = optim.Adam(model.parameters(), lr=self._params['lr'])

        hidden_emb = None
        for epoch in range(self._params['epochs']):
            t = time()
            model.train()
            optimizer.zero_grad()
            recovered, mu, logvar, z = model(features, adj_norm)
            loss = loss_function(preds=recovered, labels=adj_label,
                                 mu=mu, logvar=logvar, n_nodes=n_nodes,
                                 norm=norm, pos_weight=pos_weight)
            loss.backward()
            cur_loss = loss.item()
            optimizer.step()

            hidden_emb = mu.data.numpy()
            # roc_curr, ap_curr = get_roc_score(hidden_emb, adj_orig, val_edges, val_edges_false)
            roc_curr, ap_curr = get_roc_score(hidden_emb, adj_orig, train_edges, train_edges_false)

        embedding_matrix = z.detach().numpy()
        embedding_dict = {nodes[i]: embedding_matrix[i, :] for i in range(self._graph.number_of_nodes())}

        return embedding_matrix, embedding_dict


def train_(epoch, num_of_epochs, model, optimizer, loss, features, labels, adj, idx_train, idx_val, multilabel=False):
    """
    Train function for GCN.
    """
    t = time()
    optimizer.zero_grad()
    h, output = model(features, adj)
    if not multilabel:
        loss_train = loss(output[idx_train], labels[idx_train])
        acc_train = accuracy(output[idx_train], labels[idx_train])
    else:
        loss_train = 0
        acc_train = 0
        for j in range(labels.shape[0]):
            loss_train += loss(output[j, :], labels[j, :])
        loss_train /= labels.shape[0]
        output = output.detach().numpy()
        labels = labels.detach().numpy()
        for i in range(output.shape[0]):
            for j in range(output.shape[1]):
                if output[i, j] > 0.5:
                    output[i, j] = 1
                else:
                    output[i, j] = 0
            acc_train += accuracy_score(labels[i], output[i])
        acc_train /= output.shape[0]
    loss_train.backward()
    optimizer.step()

    print('Epoch: {:04d}'.format(epoch + 1),
          'loss_train: {:.4f}'.format(loss_train.item()),
          'acc_train: {:.4f}'.format(acc_train.item()), 'time: {:.4f}s'.format(time() - t))

    if epoch == num_of_epochs - 1:
        return h  # layer before last layer
        # return x  # layer before softmax


class StaticGraphEmbedding:
    def __init__(self, d, method_name, graph):
        """
        Initialize the Embedding class
        :param d: dimension of embedding
        """
        self._d = d
        self._method_name = method_name
        self._graph = graph

    @staticmethod
    def get_method_name(self):
        """
        Returns the name for the embedding method
        :param self:
        :return: The name of embedding
        """
        return self._method_name

    def learn_embedding(self):
        """
        Learning the graph embedding from the adjacency matrix.
        :param graph: the graph to embed in networkx DiGraph format
        :return:
        """
        pass

    @staticmethod
    def get_embedding(self):
        """
        Returns the learnt embedding
        :return: A numpy array of size #nodes * d
        """
        pass


class GCNModel(StaticGraphEmbedding):
    def __init__(self, params, method_name, all_graph, graph, file_tags, multilabel=False):
        super(GCNModel, self).__init__(params["dimension"], method_name, graph)
        # Training settings
        self._adj, self._features, self._labels, self._idx_train, self._idx_val, self._idx_test = \
            new_load_data(all_graph, graph, file_tags, len(graph.nodes()), params["nc_nodes"], multilabel=multilabel)
        self.multi = multilabel
        self._seed = 42
        self._epochs = params["epochs"]
        self._lr = params["lr"]
        self._weight_decay = params["weight_decay"]
        self._dropout = params["dropout"]
        if multilabel:
            self._loss = torch.nn.BCEWithLogitsLoss()
            nclass = int(self._labels.shape[1])
        else:
            self._loss = F.nll_loss
            nclass = graph.number_of_nodes()
        self._model = GCN(nfeat=self._features.shape[1], nhid=self._d, nclass=nclass, dropout=self._dropout,
                          multilabel=self.multi)
        self._optimizer = optim.Adam(self._model.parameters(), lr=self._lr, weight_decay=self._weight_decay)

    def learn_embedding(self):
        self._model.train()
        for epoch in range(self._epochs):
            output1 = train_(epoch, self._epochs, self._model, self._optimizer, self._loss, self._features,
                             self._labels, self._adj, self._idx_train, self._idx_val, self.multi)
        y = output1.detach().numpy()
        nodes = list(self._graph.nodes())
        self._dict_embedding = {nodes[i]: y[i, :] for i in range(len(nodes))}
        return self._dict_embedding


class GraphFactorization(StaticGraphEmbedding):
    """
    Graph Factorization factorizes the adjacency matrix with regularization.
    Args: hyper_dict (object): Hyper parameters.
    """

    def __init__(self, params, method_name, graph):
        super(GraphFactorization, self).__init__(params["dimension"], method_name, graph)
        """
        Initialize the GraphFactorization class
        Args: params:
            d: dimension of the embedding
            eta: learning rate of sgd
            regu: regularization coefficient of magnitude of weights
            max_iter: max iterations in sgd
            print_step: #iterations to log the prgoress (step%print_step)
        """
        self._eta = params["eta"]
        self._regu = params["regularization"]
        self._max_iter = params["max_iter"]
        self._print_step = params["print_step"]
        self._X = np.zeros(shape=(len(list(self._graph.nodes())), self._d))

    def get_f_value(self):
        """
        Get the value of f- the optimization function
        """
        nodes = list(self._graph.nodes())
        new_names = list(np.arange(0, len(nodes)))
        mapping = {}
        for i in new_names:
            mapping.update({nodes[i]: str(i)})
        H = nx.relabel.relabel_nodes(self._graph, mapping)
        f1 = 0
        for i, j, w in H.edges(data='weight', default=1):
            f1 += (w - np.dot(self._X[int(i), :], self._X[int(j), :])) ** 2
        f2 = self._regu * (np.linalg.norm(self._X) ** 2)
        return H, [f1, f2, f1 + f2]

    def learn_embedding(self):
        """
        Apply graph factorization embedding
        """
        t1 = time()
        node_num = len(list(self._graph.nodes()))
        self._X = 0.01 * np.random.randn(node_num, self._d)
        for iter_id in range(self._max_iter):
            my_f = self.get_f_value()
            count = 0
            if not iter_id % self._print_step:
                H, [f1, f2, f] = self.get_f_value()
                print('\t\tIter id: %d, Objective: %g, f1: %g, f2: %g' % (
                    iter_id,
                    f,
                    f1,
                    f2
                ))
            for i, j, w in H.edges(data='weight', default=1):
                if j <= i:
                    continue
                term1 = -(w - np.dot(self._X[int(i), :], self._X[int(j), :])) * self._X[int(j), :]
                term2 = self._regu * self._X[int(i), :]
                delPhi = term1 + term2
                self._X[int(i), :] -= self._eta * delPhi
            if count > 30:
                break
        t2 = time()
        projections = {}
        nodes = list(self._graph.nodes())
        new_nodes = list(H.nodes())
        for j in range(len(nodes)):
            projections.update({nodes[j]: self._X[int(new_nodes[j]), :]})
        # X is the embedding matrix and projections are the embedding dictionary
        return self._X, (t2 - t1), projections

    def get_embedding(self):
        return self._X


class HOPE(StaticGraphEmbedding):
    def __init__(self, params, method_name, graph):
        super(HOPE, self).__init__(params["dimension"], method_name, graph)
        """
        Initialize the HOPE class
        Args:
            d: dimension of the embedding
            beta: higher order coefficient
        """
        self._beta = params["beta"]

    def learn_embedding(self):
        """
        Apply HOPE embedding
        """
        A = nx.to_scipy_sparse_matrix(self._graph, format='csc')
        I = identity(self._graph.number_of_nodes(), format='csc')
        M_g = I - - self._beta * A
        M_l = self._beta * A
        # A = nx.to_numpy_matrix(self._graph)
        # M_g = np.eye(len(self._graph.nodes())) - self._beta * A
        # M_l = self._beta * A
        # S = inv(M_g).dot(M_l)
        S = np.dot(inv(M_g), M_l)

        u, s, vt = svds(S, k=self._d // 2)
        X1 = np.dot(u, np.diag(np.sqrt(s)))
        X2 = np.dot(vt.T, np.diag(np.sqrt(s)))
        self._X = np.concatenate((X1, X2), axis=1)

        p_d_p_t = np.dot(u, np.dot(np.diag(s), vt))
        eig_err = np.linalg.norm(p_d_p_t - S)
        print('SVD error (low rank): %f' % eig_err)

        # create dictionary of nodes
        nodes = list(self._graph.nodes())
        projections = {}
        for i in range(len(nodes)):
            y = self._X[i]
            y = np.reshape(y, newshape=(1, self._d))
            projections.update({nodes[i]: y[0]})
        # X is the embedding matrix, S is the similarity, projections is the embedding dictionary
        return projections, S, self._X, X1, X2

    def get_embedding(self):
        return self._X


class NODE2VEC(StaticGraphEmbedding):
    """
    Nod2Vec Embedding using random walks
    """

    def __init__(self, params, method_name, graph):
        super(NODE2VEC, self).__init__(params["dimension"], method_name, graph)
        """
        parameters:
        "walk_length" - Length of each random walk
        "num_walks" - Number of random walks from each source nodes
        "workers" - How many times repeat this process
        """
        self._walk_length = params["walk_length"]
        self._num_walks = params["num_walks"]
        self._workers = params["workers"]

    def learn_embedding(self):
        """
        Apply Node2Vec embedding
        """
        node2vec = Node2Vec(self._graph, dimensions=self._d, walk_length=self._walk_length,
                            num_walks=self._num_walks, workers=self._workers)
        model = node2vec.fit()
        nodes = list(self._graph.nodes())
        self._my_dict = {}
        for node in nodes:
            self._my_dict.update({node: np.asarray(model.wv.get_vector(node))})
        self._X = np.zeros((len(nodes), self._d))
        for i in range(len(nodes)):
            self._X[i, :] = np.asarray(model.wv.get_vector(nodes[i]))
        # X is the embedding matrix and projections are the embedding dictionary
        return self._X, self._my_dict

    def get_embedding(self):
        return self._X, self._my_dict


def final(G, method_name, params, file_tags=None):
    """
    Final function to apply state-of-the-art embedding methods
    :param G: Graph to embed
    :param method_name: state-of-the-art embedding algorithm
    :param params: Parameters dictionary according to the embedding method
    :return:
    """
    if method_name == "HOPE":
        t = time()
        embedding = HOPE(params, method_name, G)
        projections, S, _, X1, X2 = embedding.learn_embedding()
        X = embedding.get_embedding()
        elapsed_time = time() - t
    elif method_name == "node2vec":
        t = time()
        embedding = NODE2VEC(params, method_name, G)
        embedding.learn_embedding()
        X, projections = embedding.get_embedding()
        elapsed_time = time() - t
    elif method_name == "GF":
        t = time()
        embedding = GraphFactorization(params, method_name, G)
        _, _, projections = embedding.learn_embedding()
        X = embedding.get_embedding()
        elapsed_time = time() - t
    elif method_name == "GAE":
        t = time()
        embedding = GAE(params, method_name, G)
        X, projections = embedding.embedding_matrix, embedding.embedding_dict
        elapsed_time = time() - t
    elif method_name == "GCN":
        t = time()
        embedding = GCNModel(params, method_name, G, G, file_tags=file_tags)
        projections = embedding.learn_embedding()
        elapsed_time = time() - t
        X = None
    else:
        sys.exit("Chosen GEA is not valid. Please choose one of the following: node2vec, HOPE, GF, GEA. If you have"
                 "tags to your data, you can also choose GCN")
    return X, projections, elapsed_time
