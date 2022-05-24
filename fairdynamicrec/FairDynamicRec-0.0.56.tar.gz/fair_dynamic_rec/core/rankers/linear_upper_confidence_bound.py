import numpy as np
from .linear_submodular_bandit import LSB

class LinUCB(LSB):
    def __init__(self, config, dataObj, parameters=None):
        super(LinUCB, self).__init__(config, dataObj, parameters)
        self.dim = self.dataObj.feature_data['train_item_latent_features'].shape[1]

        # parameters
        self.ill_matrix_counter = 0
        self.theta = np.ones((self.dataObj.n_users, self.dim))  # d-dimensional
        self.b = np.zeros((self.dataObj.n_users, self.dim))  # d
        self.M = np.zeros((self.dataObj.n_users, self.dim, self.dim))  # d by d
        self.MInv = np.zeros((self.dataObj.n_users, self.dim, self.dim))  # for fast matrix inverse computation, d by d
        for i in range(self.dataObj.n_users):
            self.M[i] = np.eye(self.dim)
            self.MInv[i] = np.eye(self.dim)
        # for ill inverse
        self.b_tmp = np.zeros((self.dataObj.n_users, self.dim))
        self.MInv_tmp = np.zeros((self.dataObj.n_users, self.dim, self.dim))

        # self.gamma = float(parameters.get("gamma",{}).get("value",0))
        # self.window = int(parameters.get('window',{}).get('value',0))
        # self.click_history = np.zeros((self.dataObj.n_users, self.dim))
        #
        # self.shuffle_K = int(parameters.get('shuffle_K',{}).get('value',0))
        # self.epsilon = float(parameters.get('epsilon', {}).get('value', 0))
        # self.ears_gamma = float(parameters.get('ears_gamma', {}).get('value', 0))

    def get_ranking(self, batch_users, round=None):
        """
        :param x: features
        :param k: number of positions
        :return: ranking: the ranked item id.
        """
        # assert x.shape[0] >= k
        rankings = np.zeros((len(batch_users), self.config.list_size), dtype=int)
        self.batch_features = np.zeros((len(batch_users), self.config.list_size, self.dim))
        tie_breaker = self.prng.rand(len(self.dataObj.feature_data['train_item_latent_features']))
        for i in range(len(batch_users)):
            user = batch_users[i]
            x = self.dataObj.feature_data['train_item_latent_features']
            if self.processing_type == 'item_weight':
                x = self.item_coef[user].reshape(self.dataObj.n_items, 1) * x

            if self.processing_type == 'recommended_discountfactor':
                cb = self.alpha * (1 - (self.exp_recommended[user] / (round + 1))) * np.sqrt(np.multiply(np.dot(x, self.MInv[user]), x).sum(axis=1))
            elif self.processing_type == 'examined_discountfactor':
                cb = self.alpha * (1 - (self.exp_examined[user] / (round + 1))) * np.sqrt(np.multiply(np.dot(x, self.MInv[user]), x).sum(axis=1))
            else:
                cb = self.alpha * np.sqrt(np.multiply(np.dot(x, self.MInv[user]), x).sum(axis=1))
            score = np.dot(x, self.theta[user])
            ucb = score + cb
            rankings[i] = np.lexsort((tie_breaker, -ucb))[:self.config.list_size]
            if self.processing_type == 'EARS':
                rankings[i] = np.asarray(self.shuffling_topK(rankings[i], np.sort(-ucb)[:self.config.list_size], self.config.list_size))
            self.batch_features[i] = self.dataObj.feature_data['train_item_latent_features'][rankings[i]]
        return rankings