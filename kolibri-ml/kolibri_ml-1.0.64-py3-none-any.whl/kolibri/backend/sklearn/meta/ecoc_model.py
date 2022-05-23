from copy import copy, deepcopy

import kdmt.distances
import numpy as np
from scipy.spatial.distance import hamming
from sklearn.base import BaseEstimator
from copy import deepcopy
from itertools import combinations
from kdmt.objects import class_from_module_path
from kolibri.backend.models import get_classification_model
from  kdmt.distances import euclidean_distance
from kolibri.backend.sklearn.meta.ecoc.code_matrix import get_code_matrix
from kdmt import distances
from kolibri.utils.matrix import  get_data_subset, get_subset_feature_from_matrix, create_col_from_partition, get_data_from_col
from kolibri.utils.common import estimate_weight
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from kdmt.dict import get_keys_for_value
from kdmt.matrix import has_duplicate_col, get_closet_vector

from kolibri.logger import get_logger

logger = get_logger(__name__)




def y_euclidean_distance(x, y, weights=None):
    """
    a different euclidean distance
    :param x: a sample
    :param y: another sample
    :param weights: the weights for each feature
    :return: distance
    """
    assert len(x) == len(y)
    if weights is None:
        weights = np.ones(len(x))
    distance = np.sqrt(np.sum(np.abs(y) * np.power(x - y, 2) * weights))
    return distance


class EcocEstimator(BaseEstimator):
    """
    ECOC meta classifier
    ref: http://www.cs.cmu.edu/~aberger/pdf/ecoc.pdf

    Parameters:
        base_estimator: string
            classfier name. This classfier name comes from kolibri model_type database. These are mainly sklearn models
        code_size:  specifies the code size. ie the number of base classifiers that will be created.
        decoder: str
            indicates the type of decoder, get a decoder object immediately when initialization.
            For more details, check Decoding.Decoder.get_decoder.

    Attributes:
        estimator_type: str, {'decision_function','predict_proba'}
            which type the estimator belongs to.
            'decision_function' - predict value range (-∞,+∞)
            'predict_proba' - predict value range [0,1]
        classes_: set
            the set of labels.
        estimators_: 1-d array
            trained classifers.

    Methods:
        fit(data, y): Fit the model_type according to the given training data.
        predict(data): Predict class labels for samples in data.
        predict_proba(data): Predict class labels for samples in data.
        predict_top_n(data): Predict class labels for samples in data.
    """

    @staticmethod
    def softmax(x):
        """Compute softmax values for each sets of scores in x."""
        e_x = 1/np.exp(x)
        return (e_x / e_x.sum(axis=0)) # only difference

    def __init__(self, base_estimator="LogisticRegression", code_matrix='centroid', distance="euclidean",random_state=42):


        self.params={"base_estimator":base_estimator, "code_matrix":code_matrix, "distance": distance}
        self.base_estimator = self._load_model_from_parameters(get_classification_model(base_estimator))
        self.code_matrix_fn = get_code_matrix(code_matrix)
        self.error_code = None
        self.estimators = []
        self.random_state = random_state
        self.distance=distances.euclidean_distance



    def get_params(self, deep=True):
        return self.params

    def _load_model_from_parameters(self, model_params):
        model_params=deepcopy(model_params)
        model=class_from_module_path(model_params["class"])
        default_params={p:model_params["parameters"][p]["value"] for p in model_params["parameters"]}
        for param, param_val in default_params.items():
            if isinstance(param_val, list):
                for i, p in enumerate(param_val):
                    if isinstance(p, dict):
                        default_params[param][i]=self._load_model_from_parameters(p)
            elif isinstance(param, dict):
                default_params[param] = self._load_model_from_parameters(param_val)

        return model(**default_params)

    def fit(self, X, y, sample_weight=None):
        if y is None:
            raise Exception('y should be initialized')
        self.classes_ = np.unique(y)
        print('creating code matrix')
        self.code_matrix, classes_index=self.code_matrix_fn(y, X)
        print('done')


        Y = np.array([self.code_matrix[classes_index[y[i]]] for i in range(X.shape[0])], dtype=np.double)

        print('fitting estimators')
        for i in range(Y.shape[1]):
            estimator = copy(self.base_estimator)
            self.estimators.append(estimator.fit(X, Y[:,i]))


    # def predict(self, data):
    #
    #     Y = np.array([self._predict(self.estimators[i], data) for i in range(len(self.estimators))]).T
    #
    #     pred = self.decode(Y, self.code_matrix).argmin(axis=1)
    #
    #     return [self.classes_[p] for p in pred]

    def decode(self, Y, M):
        return np.array([[self.distance(y, m) for m in M] for y in Y])


    def predict_proba(self, X):
        """
        Extended ECOC model_type intefrace, implementation is based on
        http://www.cs.cmu.edu/~aberger/pdf/ecoc.pdf
        :param X: classification input (can be a sparse matrix)
        :return: numpy array of classification results
        """
        if not hasattr(X, 'shape'):
            raise Exception('data must be a numpy object')

        predicted = []

        for i in range(len(self.estimators)):
            predicted.append(self.estimators[i].predict(X))

        predicted = np.array(predicted).T
        pred = self.decode(predicted, self.code_matrix)
        scores=EcocEstimator.softmax(pred.T).T


        return scores

    def predict_top_n(self, X, n=5):
        """
        Predict top N most relevant classes for each record
        :param X: classification input (can be a sparse matrix)
        :param n: how much top results should be given
        :return: numpy matrix of top predictions
        """
        result = self.predict_proba(X)
        sorted_probas = copy(result)
        sorted_probas.sort(axis=1)
        sorted_probas = sorted_probas[:, -n:][:, ::-1]
        class_mapper = np.vectorize(lambda x: self.idx2class[x])

        classes = class_mapper(result.argsort(axis=1)[:, -n:][:, ::-1])

        sorted_probas = [[float(j) for j in i] for i in sorted_probas.tolist()]
        classes = [[j for j in i] for i in classes.tolist()]

        return list(map(lambda x: dict(zip(x[0], x[1])), zip(classes, sorted_probas)))


class EcocOneEstimator(EcocEstimator):
    """
    ECOC-ONE:Optimal node embedded ECOC
    """

    #def __init__(self, distance_measure=euclidean_distance, base_estimator=svm.SVC, iter_num=10, **param):
    #def __init__(self, distance_measure=euclidean_distance, base_estimator=KNeighborsClassifier, iter_num=10, **param):
    #def __init__(self, distance_measure=euclidean_distance, base_estimator=LogisticRegression, iter_num=10, **param):
    #def __init__(self, distance_measure=euclidean_distance, base_estimator=tree.DecisionTreeClassifier, iter_num=10, **param):
    #def __init__(self, distance_measure=euclidean_distance, base_estimator=GaussianNB, iter_num=10, **param):
#    def __init__(self, base_estimator="LogisticRegression", code_matrix='rand', distance="euclidean",random_state=42):

    def __init__(self, distance=euclidean_distance, base_estimator="mlp", iter_num=10, **param):
        super().__init__(base_estimator)
        self.train_data = None
        self.validate_data = None
        self.train_label = None
        self.validation_y = None
#        self.estimator = base_estimator
        self.matrix = None
        self.index = None
        self.predictors = None
        self.predictor_weights = None
        self.predicted_vector = []
        self.iter_num = iter_num
        self.param = param
        self.distance_measure = distance


    def create_matrix2(self, data, labels, estimator, **param):
        unique_labels=np.unique(labels)
        index = {l: i for i, l in enumerate(np.unique(labels))}
        matrix = None
        predictors = []
        predictor_weights = []
        class_1_variety_result=[]
        labels_to_divide = [np.unique(labels)]

        while len(labels_to_divide) > 0:
            label_set = labels_to_divide.pop(0)
            label_count = len(label_set)
            groups = combinations(range(label_count), np.int(np.ceil(label_count / 2)))
            score_result = 0
            est_result = None
            for group in groups:
                code=[-1 if c not in group else 1 for c in unique_labels]

                y = np.array([code[index[labels[i]]] for i in range(data.shape[0])], dtype=np.int)

                train_data, validate_data, train_label, validate_label = train_test_split(data, y,test_size=0.25, random_state=42)

                est = estimator(**param).fit(train_data, train_label)

                score = est.score(validate_data, validate_label)
                if score >= score_result:
                    score_result = score
                    est_result = est
                    class_1_variety_result = group

            new_col = np.ones((len(index), 1))
            new_col=[-1 if i not in class_1_variety_result else i for i in  new_col]
            if matrix is None:
                matrix = copy(new_col)
            else:
                matrix = np.hstack((matrix, new_col))
            predictors.append(est_result)
            predictor_weights.append(estimate_weight(1 - score_result))
            if len(class_1_variety_result) > 1:
                labels_to_divide.append(class_1_variety_result)
            if len(class_2_variety_result) > 1:
                labels_to_divide.append(class_2_variety_result)
        return matrix, index, predictors, predictor_weights


    def create_matrix(self, train_data, train_label, validate_data, validate_label, estimator, **param):
        index = {l: i for i, l in enumerate(np.unique(train_label))}
        matrix = None
        predictors = []
        predictor_weights = []
        class_1_variety_result=[]
        class_2_variety_result=[]
        labels_to_divide = [np.unique(train_label)]
        while len(labels_to_divide) > 0:
            label_set = labels_to_divide.pop(0)
            label_count = len(label_set)
            groups = combinations(range(label_count), np.int(np.ceil(label_count / 2)))
            score_result = 0
            est_result = None
            i=0
            for group in groups:
                if i >10:
                    break
                print(i)
                i+=1
                class_1_variety = np.array([label_set[i] for i in group])
                class_2_variety = np.array([l for l in label_set if l not in class_1_variety])
                class_1_data, class_1_label = get_data_subset(train_data, train_label, class_1_variety)
                class_2_data, class_2_label = get_data_subset(train_data, train_label, class_2_variety)
                class_1_cla = np.ones(len(class_1_data))
                class_2_cla = -np.ones(len(class_2_data))
                train_d = np.vstack((class_1_data, class_2_data))
                train_c = np.hstack((class_1_cla, class_2_cla))
                est = estimator.fit(train_d, train_c)
                class_1_data, class_1_label = get_data_subset(validate_data, validate_label, class_1_variety)
                class_2_data, class_2_label = get_data_subset(validate_data, validate_label, class_2_variety)
                class_1_cla = np.ones(len(class_1_data))
                class_2_cla = -np.ones(len(class_2_data))
                validation_d = np.array([])
                validation_c = np.array([])
                try:
                    validation_d = np.vstack((class_1_data, class_2_data))
                    validation_c = np.hstack((class_1_cla, class_2_cla))
                except Exception:
                    if len(class_1_data) > 0:
                        validation_d = class_1_data
                        validation_c = class_1_cla
                    elif len(class_2_data) > 0:
                        validation_d = class_2_data
                        validation_c = class_2_cla
                if validation_d.shape[0] > 0 and validation_d.shape[1] > 0:
                    score = est.score(validation_d, validation_c)
                else:
                    score = 0.8
                if score >= score_result:
                    score_result = score
                    est_result = est
                    class_1_variety_result = class_1_variety
                    class_2_variety_result = class_2_variety
            new_col = np.zeros((len(index), 1))
            for i in class_1_variety_result:
                new_col[index[i]] = 1
            for i in class_2_variety_result:
                new_col[index[i]] = -1
            if matrix is None:
                matrix = copy(new_col)
            else:
                matrix = np.hstack((matrix, new_col))
            predictors.append(est_result)
            predictor_weights.append(estimate_weight(1 - score_result))
            if len(class_1_variety_result) > 1:
                labels_to_divide.append(class_1_variety_result)
            if len(class_2_variety_result) > 1:
                labels_to_divide.append(class_2_variety_result)
        return matrix, index, predictors, predictor_weights

    def fit(self, data, label):
        self.train_data, self.validate_data, self.train_label, self.validation_y = train_test_split(data, label,
                                                                                                    test_size=0.25)
        self.matrix, self.index, self.predictors, self.predictor_weights = \
            self.create_matrix(self.train_data.toarray(), self.train_label, self.validate_data.toarray(), self.validation_y, self.base_estimator,
                               **self.param)
        feature_subset = get_subset_feature_from_matrix(self.matrix, self.index)
        for i in range(self.iter_num):
            y_pred = self.predict(self.validate_data)
            y_true = self.validation_y
            conf_mat = confusion_matrix(y_true, y_pred, self.index)
            while True:
                max_index = np.argmax(conf_mat)
                max_index_y = np.floor(max_index / conf_mat.shape[1])
                max_index_x = max_index % conf_mat.shape[1]
                label_y = get_keys_for_value(self.index, max_index_y)[0]
                label_x = get_keys_for_value(self.index, max_index_x)[0]
                score_result = 0
                col_result = None
                est_result = None
                est_weight_result = None
                feature_subset_m = None
                feature_subset_n = None
                for m in range(len(feature_subset) - 1):
                    for n in range(m + 1, len(feature_subset)):
                        if ((label_y in feature_subset[m] and label_x in feature_subset[n])
                            or (label_y in feature_subset[n] and label_x in feature_subset[m])) \
                                and (set(feature_subset[m]).intersection(set(feature_subset[n])) == set()):
                            col = create_col_from_partition(feature_subset[m], feature_subset[n], self.index)
                            if not has_duplicate_col(col, self.matrix):
                                train_data, train_cla = has_duplicate_col(self.train_data, self.train_label, col,
                                                                             self.index)
                                est = self.base_estimator(**self.param).fit(train_data, train_cla)
                                validation_data, validation_cla = get_data_from_col(self.validate_data,
                                                                                       self.validation_y, col,
                                                                                       self.index)
                                if validation_data is None:
                                    score = 0.8
                                else:
                                    score = est.score(validation_data, validation_cla)
                                if score >= score_result:
                                    score_result = score
                                    col_result = col
                                    est_result = est
                                    est_weight_result = estimate_weight(1 - score_result)
                                    feature_subset_m = m
                                    feature_subset_n = n
                if col_result is None:
                    conf_mat[np.int(max_index_y), np.int(max_index_x)] = 0
                    if np.sum(conf_mat) == 0:
                        break
                else:
                    break
            try:
                self.matrix = np.hstack((self.matrix, col_result))
                self.predictors.append(est_result)
                self.predictor_weights.append(est_weight_result)
                feature_subset.append(feature_subset[feature_subset_m] + feature_subset[feature_subset_n])
            except (TypeError, ValueError):
                pass

    def predict(self, data):
        res = []
        if len(self.predictors) == 0:
            logger.debug('The Model has not been fitted!')
        if len(data.shape) == 1:
            data = np.reshape(data, [1, -1])




        for X in data:
            predict_res = [estimator.predict(X)[0] for estimator in self.predictors]

            if self.predicted_vector == []:
                self.predicted_vector = deepcopy(predict_res)
            else:
                ###print(np.array(self.predicted_vector).shape)
                ###print(np.array(predict_res).shape)
                self.predicted_vector = np.row_stack((self.predicted_vector, predict_res))

            value = get_closet_vector(predict_res, self.matrix, y_euclidean_distance, np.array(self.predictor_weights))
            res.append(get_keys_for_value(self.index, value)[0])
        ###print('end')
        self.predicted_vector=[]
        # vector = []
        # for i in range(self.matrix.shape[1]):
        #     vector.append(list(self.predicted_vector[:, i]))
        # self.predicted_vector = copy.deepcopy(vector)

        return np.array(res)


class DC_ECOC(EcocEstimator):
    """
    DC ECOC
    code by sunmengxin
    """

    def create_matrix(self, data, label, dc_option = 'F1'):    # 这里我默认设置使用的dc_option是F1
        labels_to_divide = [np.unique(label)]
        index = {l: i for i, l in enumerate(np.unique(label))}
        # if dc_option == 'F1':
        #     matrix = [[-1,0,1,0],[-1,0,-1,1],[1,-1,0,0],[-1,0,-1,-1],[1,1,0,0]]
        #     return matrix,index
        # elif dc_option == 'F2':
        #     matrix = [[-1,0,-1,-1],[-1,0,-1,1],[-1,0,1,0],[1,1,0,0],[1,-1,0,0]]
        #     return matrix,index
        # elif dc_option == 'F3':
        #     matrix = [[1,1,0,0],[-1,0,-1,1],[-1,0,1,0],[-1,0,-1,-1],[1,-1,0,0]]
        #     return matrix,index

        matrix = None
        while len(labels_to_divide) > 0:
            label_set = labels_to_divide.pop(0)

            # get correspoding label and data from whole data and label
            datas, labels = MT.get_data_subset(data, label, label_set)

            # DC search
            class_1, class_2 = Greedy_Search.greedy_search(datas, labels, dc_option=dc_option)
            new_col = np.zeros((len(index), 1))
            for i in class_1:
                new_col[index[i]] = 1
            for i in class_2:
                new_col[index[i]] = -1
            if matrix is None:
                matrix = copy.copy(new_col)
            else:
                matrix = np.hstack((matrix, new_col))
            if len(class_1) > 1:
                labels_to_divide.append(class_1)
            if len(class_2) > 1:
                labels_to_divide.append(class_2)
        return matrix, index

    def fit(self, data, label, **estimator_param):
        """
        a method to train base estimator based on given data and label
        :param data: data used to train base estimator
        :param label: label corresponding to the data
        :param estimator_param: some param used by base estimator
        :return: None
        """
        self.train_data = data
        self.train_label = label
        self.predictors = []
        if 'dc_option' in estimator_param:
            self.matrix, self.index = self.create_matrix(data, label, estimator_param['dc_option'])
            estimator_param.pop('dc_option')
        else:
            self.matrix, self.index = self.create_matrix(data, label, dc_option='F1')
        for i in range(self.matrix.shape[1]):
            dat, cla = MT.get_data_from_col(data, label, self.matrix[:, i], self.index)
            estimator = self.base_estimator(**estimator_param).fit(dat, cla)
            self.predictors.append(estimator)


class Self_Adaption_ECOC(EcocEstimator):
    """
    self adaption ECOC:many DC ecoc merge and form new ECOC by ternary conpution
    """

    def create_matrix(self, data, label, **param):
        labels_to_divide = [np.unique(label)]
        index = {l: i for i, l in enumerate(np.unique(label))}
        param['dc_option']=['F1','N2','F3']
        M = None
        if 'base_M' not in param:
            DCECOC = DC_ECOC()
            if 'dc_option' in param:
                for each in param['dc_option']:
                    m, index = DCECOC.create_matrix(data, label, dc_option=each)
                    if M is None:
                        M = copy.deepcopy(m)
                    else:
                        M = np.hstack((M, m))
            else:
                logging.warning('use default DC: F1')
                M = DCECOC.create_matrix(data, label, dc_option='F1')
        else:
            for each in param['base_M']:
                if M is None:
                    M = copy.deepcopy(each)
                else:
                    M = np.hstack((M, each))

        if M is None:
            logging.debug('ERROR:Matrix is None')
            raise ValueError('ERROR:Matrix is None')

        # M = MT.remove_reverse(M)
        # M = MT.remove_duplicate_column(M) #simplify the process
        M = MT.select_column(M, data, label, len(index))

        if 'ternary_option' not in param:
            param['ternary_option'] = '+'

        logging.info("merged matrix:\r\n" + str(M))
        GPM = None
        while (len(M[0]) != 0):
            if len(M[0]) == 1:
                if GPM is None:
                    GPM = copy.copy(np.hstack((M)))
                else:
                    GPM = np.hstack((GPM, M))
                M = np.delete(M, 0, axis=1)
                break

            elif len(M[0]) == 2 or len(M[0]) == 3:
                left_node, right_node, M = MT.get_2column(M)
                parent_node = MT.left_right_create_parent(left_node, right_node, param['ternary_option'], data, label)
                M = np.hstack((M, parent_node))

                GPM = MT.insert_2column(GPM, left_node, right_node)

            elif len(M[0]) >= 4:
                left_left_node, left_right_node, M = MT.get_2column(M)
                left_parent_node = MT.left_right_create_parent(left_left_node, left_right_node, param['ternary_option'],
                                                               data, label)
                GPM = MT.insert_2column(GPM, left_left_node, left_right_node)

                right_left_node, right_right_node, M = MT.get_2column(M)
                right_parent_node = MT.left_right_create_parent(right_left_node, right_right_node,
                                                                param['ternary_option'], data, label)
                GPM = MT.insert_2column(GPM, right_left_node, right_right_node)

                M = np.hstack((M, left_parent_node, right_parent_node))

            # M = MT.change_unfit_DC(M,data,label,dc_option='D2')
        logging.info('1.create matrix ' + str(len(GPM[0])) + '\n' + str(GPM))

        GPM = MT.remove_reverse(GPM)  # delete reverse column and row
        logging.info('2.remove reverse matrix ' + str(len(GPM[0])) + '\n' + str(GPM))

        GPM = MT.remove_duplicate_column(GPM)  # delete identical column
        logging.info('3.remove duplicate matrix ' + str(len(GPM[0])) + '\n' + str(GPM))

        # GPM,new_index = MT.remove_duplicate_row(GPM,index) # delete identical row  ------may need!!
        GPM = MT.remove_unfit(GPM)  # delete column that does not contain +1 and -1
        logging.info('4.remove unfit matrix ' + str(len(GPM[0])) + '\n' + str(GPM))

        return GPM, index

    def fit(self, data, label, **param):
        """
        a method to train base estimator based on given data and label
        :param data: data used to train base estimator
        :param label: label corresponding to the data
        :param estimator_param: some param used by matrix and base estimator
        :return: None
        """
        self.train_data = data
        self.train_label = label
        self.predictors = []
        self.matrix, self.index = self.create_matrix(data, label, **param)

        for i in range(self.matrix.shape[1]):
            dat, cla = MT.get_data_from_col(data, label, self.matrix[:, i], self.index)
            if 'estimator_param' in param:
                estimator = self.estimator(**param['estimator_param']).fit(dat, cla)
            else:
                estimator = self.estimator().fit(dat, cla)
            self.predictors.append(estimator)


class CSFT_ECOC(EcocEstimator):
    """
    change subtree of DC ECOC matrix
    """

    def create_matrix(self, data, label, **param):
        labels_to_divide = [np.unique(label)]
        index = {l: i for i, l in enumerate(np.unique(label))}

        TM = None
        DCECOC = DC_ECOC()
        if 'dc_option' in param:
            for each in param['dc_option']:
                m, index = DCECOC.create_matrix(data, label, dc_option=each)
                if M is None:
                    M = [m]
                else:
                    M = M.append(m)
        else:

            logging.debug('ERROR: undefine the type of DCECOC')
            return

        train_data, train_label, val_data, val_label = MT.split_traindata(data,
                                                                          label)  # split data into train and validation

        # select the most effective matrix
        res = np.zeros(1, len(M))
        for i in range(len(M)):
            m = M[i]
            res[i] = MT.res_matrix(m, index, train_data, train_label, val_data, val_label, self.estimator,
                                   self.distance_measure)
        best_M = M[res.index(max(res))]

        most_time = 10
        res = 1
        while (most_time and res < 0.8):

            sel_m = random.random(len(M))
            new_M, new_index = MT.change_subtree(best_M, M[sel_m])
            new_res = MT.res_matrix(new_M, new_index, train_data, train_label, val_data, val_label, self.estimator,
                                    self.distance_measure)
            if new_res > res:
                best_M = new_M
                res = new_res

            most_time = most_time + 1

        return M, index

    def fit(self, data, label, **estimator_param):
        """
        a method to train base estimator based on given data and label
        :param data: data used to train base estimator
        :param label: label corresponding to the data
        :param estimator_param: some param used by base estimator
        :return: None
        """
        self.predictors = []
        if 'dc_option' in estimator_param:
            self.matrix, self.index = self.create_matrix(data, label, dc_option=estimator_param['dc_option'])
            estimator_param.pop('dc_option')
        else:
            self.matrix, self.index = self.create_matrix(data, label)
        for i in range(self.matrix.shape[1]):
            dat, cla = MT.get_data_from_col(data, label, self.matrix[:, i], self.index)
            estimator = self.estimator(**estimator_param).fit(dat, cla)
            self.predictors.append(estimator)