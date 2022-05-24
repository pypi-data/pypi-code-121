import numpy as np
from .abstract_ranker import AbstractRanker
import math
from fair_dynamic_rec.core.util.utils import compute_user_K_prime

class LSB(AbstractRanker):
    def __init__(self, config, dataObj, parameters=None):
        super(LSB, self).__init__(config, dataObj)
        self.n_samples = np.zeros(dataObj.n_users)
        self.n_clicks = np.zeros(dataObj.n_users)
        self.dim = self.dataObj.feature_data['train_item_topical_features'].shape[1]
        self.prng = np.random.RandomState(seed=config.seed)
        self.alpha = float(parameters["alpha"]["value"])

        self.sigma = float(parameters["sigma"]["value"])
        # self.t = 1
        # self.seed = seed
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
        self.batch_features = None

        # parameters for feature_weight
        self.gamma = float(parameters.get("gamma",{}).get("value",0))
        self.processing_type = parameters.get("processing_type",{}).get("value",'')
        self.window = int(parameters.get('window',{}).get('value',0))
        self.click_history = np.zeros((self.dataObj.n_users, self.dim))

        # parameters for EARS
        self.shuffle_K = int(parameters.get('shuffle_K',{}).get('value',0))
        self.epsilon = float(parameters.get('epsilon',{}).get('value',0))
        self.ears_gamma = float(parameters.get('ears_gamma',{}).get('value',0))

        # parameters for item_weight
        self.item_coef = np.ones((self.dataObj.n_users, self.dataObj.n_items))

        # parameters for discount factor
        self.exp_recommended = np.zeros((self.dataObj.n_users, self.dataObj.n_items))
        self.exp_examined = np.zeros((self.dataObj.n_users, self.dataObj.n_items))

    def get_ranking(self, batch_users, round=None):
        """
        :param x: features
        :param k: number of positions
        :return: ranking: the ranked item id.
        delta: the conditional topic coverage of each item. Eq. (3) of NIPS 11 paper.
        """
        # assert x.shape[0] >= k
        rankings = np.zeros((len(batch_users), self.config.list_size), dtype=int)
        self.batch_features = np.zeros((len(batch_users), self.config.list_size, self.dim))
        tie_breaker = self.prng.rand(len(self.dataObj.feature_data['train_item_topical_features']))
        for i in range(len(batch_users)):
            user = batch_users[i]
            coverage = np.zeros(self.dim)
            ranking = []
            scores = []
            for j in range(self.config.list_size):
                # Line 8 - 11 of Nips 11
                gain_in_topic_coverage = self.conditional_coverage(x=self.dataObj.feature_data['train_item_topical_features'], coverage=coverage)
                x = gain_in_topic_coverage
                if self.processing_type == 'item_weight':
                    x = self.item_coef[user].reshape(self.dataObj.n_items, 1) * gain_in_topic_coverage

                if self.processing_type == 'recommended_discountfactor':
                    cb = self.alpha * (1 - (self.exp_recommended[user] / (round + 1))) * np.sqrt(np.multiply(np.dot(x, self.MInv[user]), x).sum(axis=1))
                elif self.processing_type == 'examined_discountfactor':
                    cb = self.alpha * (1 - (self.exp_examined[user] / (round + 1))) * np.sqrt(np.multiply(np.dot(x, self.MInv[user]), x).sum(axis=1))
                else:
                    cb = self.alpha * np.sqrt(np.multiply(np.dot(x, self.MInv[user]), x).sum(axis=1))
                score = np.dot(x, self.theta[user])
                ucb = score + cb + 1e-6 * tie_breaker

                winner = np.argmax(ucb)
                while winner in ranking:
                    ucb[winner] = -np.inf
                    winner = np.argmax(ucb)

                ranking.append(winner)
                self.batch_features[i][j] = gain_in_topic_coverage[winner]
                scores.append(ucb[winner])

                coverage = self.ranking_coverage(self.dataObj.feature_data['train_item_topical_features'][ranking])

            if self.processing_type == 'EARS':
                rankings[i] = np.asarray(self.shuffling_topK(ranking, scores, self.config.list_size))
            else:
                rankings[i] = np.asarray(ranking)
        return rankings

    def update(self, batch_users, rankings, clicks, round=None, user_round=None):
        for i in range(len(batch_users)):
            user = batch_users[i]
            _clicks, _batch_features = self.__collect_feedback(clicks, i)

            discount_coef = [1 / (math.log(1 + j)) for j in range(1, len(rankings[0]) + 1)]
            discount_coef_reward = [math.log(1+j) for j in range(1, len(_clicks) + 1)]
            discount_coef_penalization = [self.gamma * 1 / (math.log(1+j)) for j in range(1, len(_clicks) + 1)]

            if self.processing_type == 'recommended_discountfactor':
                self.exp_recommended[user][np.array(rankings[0])] += discount_coef
            elif self.processing_type == 'examined_discountfactor':
                if len(clicks) == 0:
                    self.exp_examined[user][np.array(rankings[0])] += discount_coef
                else:
                    self.exp_examined[user][np.array(rankings[0][:len(clicks)])] += discount_coef[:len(clicks)]

            if self.processing_type == 'item_weight':
                _batch_features = self.update_item_weight(rankings[0], _batch_features, _clicks, discount_coef_penalization, discount_coef_reward, user, user_round)

            """
            This is for computing self.theta (Line 3-5 of Alogirthm 1 of NIPS 11)
            For fast matrix inverse, we use Woodbury matrix identity (https://en.wikipedia.org/wiki/Woodbury_matrix_identity)

            Return: self.theta is updated.
            """
            # for the inverse of M, feature matrix
            # x * m^-1 * x^T
            xmx = np.dot(_batch_features, np.dot(self.MInv[user], _batch_features.T))
            # (1/sigma I + xmx)^-1
            try:
                tmp_inv = np.linalg.inv(1 / self.sigma * np.eye(len(_batch_features)) + xmx)
            except np.linalg.LinAlgError:
                # for the ill matrix. if the matrix is not invertible, we ignore this update
                self.ill_matrix_counter += 1
                return
            # m^-1*x^T
            MInv_xT = self.MInv[user].dot(_batch_features.T)
            # MInv_xT*tmp_inv*MInv_xT^T
            self.MInv_tmp[user] = np.dot(np.dot(MInv_xT, tmp_inv), MInv_xT.T)
            # MInv - the new part
            self.MInv[user] -= self.MInv_tmp[user]

            self.M[user] += self.sigma * _batch_features.T.dot(_batch_features)

            # for b: feedback
            if self.processing_type == 'feature_weight':
                self.update_feature_weight(_batch_features, _clicks, discount_coef_penalization, discount_coef_reward, user, user_round)
            else:
                self.b[user] += np.dot(_clicks, _batch_features)


            # self.b_tmp[user] = np.dot(_clicks, _batch_features)
            # self.b[user] += self.b_tmp[user]

            # for parameter theta
            self.theta[user] = np.dot(self.MInv[user], self.b[user])
            # self.theta[self.theta < 0] = 0

            self.n_samples[user] += len(_clicks)
            self.n_clicks[user] += sum(_clicks)

    def __collect_feedback(self, clicks, batch_user_id):
        """
        :param y:
        :return: the last observed position.
        """
        # With  Cascade assumption, only the first click counts.
        if self.config.feedback_model == 'cascade':
            if np.sum(clicks[batch_user_id]) == 0:
                return clicks[batch_user_id], self.batch_features[batch_user_id]
            first_click = np.where(clicks[batch_user_id])[0][0]
            return clicks[batch_user_id][:first_click + 1], self.batch_features[batch_user_id][:first_click + 1]
        elif self.config.feedback_model == 'dcm':
            if np.sum(clicks[batch_user_id]) == 0:
                return clicks[batch_user_id], self.batch_features[batch_user_id]
            last_click = np.where(clicks[batch_user_id])[0][-1]
            return clicks[batch_user_id][:last_click + 1], self.batch_features[batch_user_id][:last_click + 1]
        # all items are observed
        else:
            return clicks[batch_user_id], self.batch_features[batch_user_id]

    def shuffling_topK(self, ranking, scores, K):
        # Reshuffle top-12 if specified
        if self.shuffle_K > 1:
            np.random.shuffle(ranking[:self.shuffle_K])

        # Personalised reshuffling
        if self.shuffle_K == -1:
            # For every user
            # gamma = 0.9
            # E_c = Parallel(n_jobs=-1)(delayed(AbstractRanker.powerset_expectation_negation_partial)(scores, gamma, 1))
            # print(f'Expected clicks without shuffling top-K:', np.mean(E_c), np.var(E_c))
            # K = 6
            # E_c = Parallel(n_jobs=-1)(delayed(AbstractRanker.powerset_expectation_negation_partial)(scores, gamma, K))
            # print(f'Expected clicks after shuffling Top-{K}:', np.mean(E_c), np.var(E_c))

            # K_s = Parallel(n_jobs=-1)(delayed(compute_user_K_prime)(scores, self.gamma, K, epsilon=self.epsilon))
            K_s = compute_user_K_prime(scores, self.ears_gamma, K, epsilon=self.epsilon)

            np.random.shuffle(ranking[:K_s])
        return ranking

    def update_feature_weight(self, _batch_features, _clicks, discount_coef_penalization, discount_coef_reward, user, user_round):
        clicked_items_index = np.where(_clicks == 1)[0]
        _x = _batch_features
        if len(clicked_items_index) == 0:
            _x = -np.multiply(np.array(discount_coef_penalization).reshape(len(_clicks), 1), _x)
        else:
            previous_clicked_item_index = 0
            for clicked_item_index in clicked_items_index:
                current_clicked_item_index = clicked_item_index
                _x[current_clicked_item_index, :] = discount_coef_reward[current_clicked_item_index] * _x[current_clicked_item_index, :]
                _x[previous_clicked_item_index: current_clicked_item_index, :] = -np.multiply(np.array(discount_coef_penalization[previous_clicked_item_index: current_clicked_item_index]).reshape(current_clicked_item_index - previous_clicked_item_index, 1), _x[previous_clicked_item_index: current_clicked_item_index,:])
                previous_clicked_item_index = current_clicked_item_index + 1
        self.click_history[user] += _x.sum(axis=0)
        if user_round[user] % self.window == 0:
            self.b[user] += self.click_history[user] / self.window
            self.click_history[user] = np.zeros(self.dim)
        else:
            self.b[user] = np.dot(_clicks, _batch_features)
    def update_item_weight(self, rankings, _batch_features, _clicks, discount_coef_penalization, discount_coef_reward, user, user_round):
        clicked_items_index = np.where(_clicks == 1)[0]

        _x = _batch_features
        if len(clicked_items_index) == 0:
            self.item_coef[user][rankings] += -np.array(discount_coef_penalization)
            _x = self.item_coef[user][rankings][:len(_clicks)].reshape(len(_clicks),1) * _x
            # _x = -np.multiply(np.array(discount_coef_penalization).reshape(len(_clicks), 1), _batch_features)
        else:
            previous_clicked_item_index = 0
            for clicked_item_index in clicked_items_index:
                current_clicked_item_index = clicked_item_index
                self.item_coef[user][rankings[current_clicked_item_index]] += discount_coef_reward[current_clicked_item_index]
                _x[current_clicked_item_index,:] = self.item_coef[user][rankings[current_clicked_item_index]] * _x[current_clicked_item_index,:]
                # _x[current_clicked_item_index, :] = discount_coef_reward[current_clicked_item_index] * _batch_features[current_clicked_item_index, :]
                if current_clicked_item_index != previous_clicked_item_index:
                    self.item_coef[user][rankings[previous_clicked_item_index:current_clicked_item_index]] += -np.array(discount_coef_penalization[previous_clicked_item_index:current_clicked_item_index])
                    _x[previous_clicked_item_index:current_clicked_item_index,:] = self.item_coef[user][rankings[previous_clicked_item_index:current_clicked_item_index]].reshape(current_clicked_item_index - previous_clicked_item_index, 1) * _x[previous_clicked_item_index: current_clicked_item_index,:]
                # _x[previous_clicked_item_index: current_clicked_item_index, :] = -np.multiply(np.array(discount_coef_penalization[previous_clicked_item_index: current_clicked_item_index]).reshape(current_clicked_item_index - previous_clicked_item_index, 1), _batch_features[previous_clicked_item_index: current_clicked_item_index,:])
                previous_clicked_item_index = current_clicked_item_index + 1
        # self.click_history[user] += _x.sum(axis=0)
        if user_round[user] % self.window == 0:
            return _x
            # self.b[user] += self.click_history[user] / self.window
            # self.click_history[user] = np.zeros(self.dim)
        else:
            return _batch_features