"""
Main file to run the second temporal link prediction task (neural network)
"""

import evaluation_tasks.__init__
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
from fodge.load_data import *
from fodge.run_fodge import FODGE
from keras.layers import Input, Dense, Activation
from keras.models import Model, Sequential
from GEA.all_gea import *
import keras
import tensorflow as tf
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from evaluation_tasks.scores_utils import *
from evaluation_tasks.tlp_utils import *


class TemporalLinkPrediction1:
    """
    Class to run dynamic link prediction task.
    """
    def __init__(self, name, graph_path, save_path, func=data_loader, initial_method="node2vec", dim=128,
                 epsilon=0.01, alpha_exist=0., beta=0.7, number=0, test_ratio=0.2, non_edges_file="non_edges_dblp.csv",
                 file_tags=None):
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
        :param non_edges_file: CSV file containing non edges. Can be created with the file 'calculate_non_edges.py'
        :param file_tags: If GCN GEA is used, then one should profile a file of tags
        """
        initial_t = time()
        # initialize the FODGE class
        self.DE = FODGE(name, graph_path, save_path, func=func, initial_method=initial_method, dim=dim, epsilon=epsilon,
                        alpha_exist=alpha_exist, beta=beta, number=number, file_tags=file_tags, mission="lp1")
        self.start_index = self.DE.index
        self.graph = self.DE.create_weighted_graph_for_all_times()
        self.dict_snapshots = self.DE.dict_snapshots.copy()

        # prepare data for temporal link prediction task, including finding the train and test edges changing the
        # dict of snapshots accordingly
        self.index, self.nodes, self.DE.dict_snapshots, self.true_edges_train, self.true_edges_test, self.K_train, \
            self.K_test, self.DE.dict_weights = for_lp_mission(name, self.graph, self.DE.nodes_list,
                                                               self.DE.dict_snapshots, self.DE.dict_weights, test_ratio,
                                                               self.start_index)
            
        self.graph_lp = self.DE.create_weighted_graph_for_all_times()

        print("Times in train are: ")
        print(list(self.DE.dict_snapshots.keys()))
        print("Number of edges in the train set: ", self.K_train, " | Number of edges in the test set: ", self.K_test)

        # test edges are deleted so we need to re-build it
        self.DE.g_list, self.DE.nodes_list, T, index = self.DE.create_cumulative_graphs(number)

        # calculate the embedding using FODGE
        self.full_dict_embeddings, self.dict_all_embeddings, self.total_time = self.DE.calculate_embedding()
        self.DE.full_dict_embeddings, self.DE.dict_all_embeddings = self.full_dict_embeddings, self.dict_all_embeddings
        self.DE.save_embedding(save_path, mission="lp1")

        t = time() - initial_t
        
        print(f"FODGE is done after {t} seconds. Starting temporal link prediction task")

        # perform temporal link prediction task
        self.params_dict = {"rounds": 1, "number_choose": 1}
        self.dict_initial = lp_mission(self.full_dict_embeddings, self.dict_snapshots, self.nodes, self.index,
                                       [test_ratio], self.params_dict["rounds"], self.params_dict["number_choose"],
                                       self.true_edges_train, self.true_edges_test, self.K_train, self.K_test,
                                       non_edges_file, self.start_index, self.DE.dim)
    

def create_keras_model(d):
    """
    Create the keras model of the task, d is the embedding dimension
    """
    model = Sequential()
    
    model.add(Dense(d, activation="relu", input_shape=(2*d, )))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))
    
    opti = keras.optimizers.Adam(learning_rate=0.01)

    model.compile(optimizer="Adam", loss="binary_crossentropy", metrics=[tf.keras.metrics.AUC()])
    model.summary()
    
    return model


def fit_and_predict(model, X_train, X_test, y):
    """
    Fitting of the model and predicting
    :param model: Keras model
    :param X_train: Training samples
    :param X_test: Test samples
    :param y: Labels
    :return: Predicted values
    """
    y_train = y.reshape((-1,1))
    model.fit(X_train, y_train, epochs=5)
    print("done fitting")
    y_pred = model.predict(X_test)
    print("done predicting")
    return y_pred

    
def evaluate_edge_classification(X_train, X_test, Y_train, Y_test, d):
    """
    Predictions of nodes' labels.
    :param X_train: The features' graph- norm (for train set)
    :param X_test: The features' graph- norm (for tset set)
    :param Y_train: The edges labels- 0 for true, 1 for false (for train set)
    :param Y_test: The edges labels- 0 for true, 1 for false (for test set)
    :return: Scores- F1-macro, F1-micro accuracy and auc
    """
    model = create_keras_model(d)
    my_prediction = fit_and_predict(model, X_train, X_test, Y_train)
    prediction = my_prediction.ravel()
    fpr_keras, tpr_keras, thresholds_keras = roc_curve(Y_test, prediction)
    auc_keras = auc(fpr_keras, tpr_keras)
    # print("auc score is ", auc_keras)
    score = model.evaluate(X_test, Y_test, verbose=1)
    print("Test Loss: ", score[0])
    print("Test AUC: ", score[1])

    for i in range(my_prediction.size):
        a = my_prediction[i][0]
        if a > 0.5:
            my_prediction[i][0] = 1
        else:
            my_prediction[i][0] = 0
    
    acc = accuracy_score(Y_test, my_prediction)
    micro = f1_score(Y_test, my_prediction, average='micro')
    macro = f1_score(Y_test, my_prediction, average='macro')
    return micro, macro, acc, score[1]
    

def exp_lp(X_train, X_test, Y_train, Y_test, test_ratio_arr, rounds, d):
    """
    The final node classification task as explained in our git.
    :param X_train: The features' graph- norm (for train set)
    :param X_test: The features' graph- norm (for tset set)
    :param Y_train: The edges labels- 0 for true, 1 for false (for train set)
    :param Y_test: The edges labels- 0 for true, 1 for false (for test set)
    :param test_ratio_arr: To determine how to split the data into train and test. This an array with multiple options
                           of how to split.
    :param rounds: How many times we're doing the mission. Scores will be the average.
    :param d: Embedding Dimension
    :return: Scores for all splits and all splits- F1-micro, F1-macro accuracy and auc
    """

    micro = [None] * rounds
    macro = [None] * rounds
    acc = [None] * rounds
    auc = [None] * rounds

    for round_id in range(rounds):
        micro_round = [None] * len(test_ratio_arr)
        macro_round = [None] * len(test_ratio_arr)
        acc_round = [None] * len(test_ratio_arr)
        auc_round = [None] * len(test_ratio_arr)

        for i, test_ratio in enumerate(test_ratio_arr):
            micro_round[i], macro_round[i], acc_round[i], auc_round[i] = evaluate_edge_classification\
                (X_train, X_test, Y_train, Y_test, d)

        micro[round_id] = micro_round
        macro[round_id] = macro_round
        acc[round_id] = acc_round
        auc[round_id] = auc_round

    micro = np.asarray(micro)
    macro = np.asarray(macro)
    acc = np.asarray(acc)
    auc = np.asarray(auc)

    return micro, macro, acc, auc


def lp_mission(full_dict_proj, dict_snapshots, nodes, index, ratio_arr, rounds, number_choose, true_edges_train,
               true_edges_test, K_train, K_test, non_edges_file, start_index, d):
    """
    Dynamic Link prediction Task where one wants the scores as a function of size of the initial embedding.
    Notice test ratio must be fixed. The variable that changes here is the size of the initial embedding. For more
    explanation, see our pdf file attached in out git.
    :param full_dict_proj: Dict embeddings for all nodes that appear in the graph, no matter in which time stamps.
                           If a node appear in more than one time stamp, its final embedding is its emedding it the
                           last time it has appeared.
    :param dict_snapshots: Dict where keys==times and values==list of edges for each time stamp.
    :param nodes: List of nodes that appear both in test and train
    :param index: Index of pivot time- until pivot time (including) it is train set, afterwards it is test set.
    :param ratio_arr: Wanted test ratio (r = K_test / (K_train + K_test)
    :param rounds: How many times we're doing the mission. Scores will be the average.
    :param number_choose: Number of times to choose false edges randomly.
    :param true_edges_train: List of true edges for train set.
    :param true_edges_test: List of true edges for test set.
    :param K_train: Number of true edges in the train set.
    :param K_test: Number of true edges in the test set.
    :param non_edges_file: Csv file containing non edges in each time. First column is the time stamp, second is
                               source node and third is target node.
    :param start_index: Index of the cumulative initial graph
    :param d: Embedding dimension
    :return: Scores of link prediction task for each dataset- Micro-F1, Macro-F1, Accuracy and AUC. They return as
            lists for each size of initial embedding for each method
    """
    dict_initial = {}
    for r in ratio_arr:
        all_micro = []
        all_macro = []
        all_acc = []
        all_auc = []
        for j in range(1):
            my_micro, my_macro, my_acc, my_auc = initialize_scores()
            missing_edges_train, missing_edges_test = create_full_lists_missing_edges(index, non_edges_file, nodes, start_index, dict_snapshots, full_dict_proj)
            for i in range(number_choose):
                false_edges_train, false_edges_test = create_data_for_link_prediction(K_train, K_test, missing_edges_train, missing_edges_test)
                print(K_test, " : ", K_train)
                X_train, Y_train, dict_edges_train = create_x_y(full_dict_proj, true_edges_train, false_edges_train, K_train, d)
                X_test, Y_test, dict_edges_test = create_x_y(full_dict_proj, true_edges_test, false_edges_test, K_test, d)
                micro, macro, acc, auc = exp_lp(X_train, X_test, Y_train, Y_test, [r], rounds, d)
                avg_micro, avg_macro, avg_acc, avg_auc = calculate_all_avg_scores_lp(micro, macro, acc, auc, rounds)
                my_micro = first_help_calculate_lp(my_micro, avg_micro)
                my_macro = first_help_calculate_lp(my_macro, avg_macro)
                my_acc = first_help_calculate_lp(my_acc, avg_acc)
                my_auc = first_help_calculate_lp(my_auc, avg_auc)
            my_micro = second_help_calculate_lp(my_micro, number_choose)
            my_macro = second_help_calculate_lp(my_macro, number_choose)
            my_acc = second_help_calculate_lp(my_acc, number_choose)
            my_auc = second_help_calculate_lp(my_auc, number_choose)
            all_micro.append(my_micro[0])
            all_macro.append(my_macro[0])
            all_acc.append(my_acc[0])
            all_auc.append(my_auc[0])
        dict_initial.update({r: [all_micro, all_macro, all_acc, all_auc]})
    return dict_initial

