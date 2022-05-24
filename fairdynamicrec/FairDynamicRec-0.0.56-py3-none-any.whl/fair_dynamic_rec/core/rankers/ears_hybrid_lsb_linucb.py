import numpy as np
from .hybrid_lsb_linucb import HybridLSBLinUCB
from fair_dynamic_rec.core.util.utils import compute_user_K_prime

class EARSHybridLSBLinUCB(HybridLSBLinUCB):
    def __init__(self, config, dataObj, parameters=None):
        super(EARSHybridLSBLinUCB, self).__init__(config, dataObj, parameters)
        self.shuffle_K = int(parameters['shuffle_K']['value'])
        self.epsilon = float(parameters['epsilon']['value'])
        self.gamma = float(parameters['gamma']['value'])

    def get_ranking(self, batch_users, round=None):
        """
        :param x: n * (n_topic + n_feature) np array
        :param k: number of positions
        :return: ranking: the ranked item id.
        """
        # assert x.shape[0] >= k
        rankings = np.zeros((len(batch_users), self.config.list_size), dtype=int)
        self.batch_features = np.zeros((len(batch_users), self.config.list_size, self.topic_dim + self.latent_dim))
        tie_breaker = self.prng.rand(len(self.dataObj.feature_data['train_item_latent_features']))

        # self.delta_t = np.zeros((k, x.shape[1]))
        # delta = x

        # z = delta[:, :self.n_z]  # topic
        # x = delta[:, self.n_z:]  # feature

        # tie_breaker = self.prng.rand(len(delta))
        for i in range(len(batch_users)):
            scores = []
            user = batch_users[i]
            # for CB
            BA_X = np.matmul(self.B[user].T, self.A_x_inv[user])  # B.T  A_x^-1
            ABA = np.matmul(self.A_z_inv[user], BA_X)  # A_z^-1 B.T A_X^-1
            ABABA = np.matmul(BA_X.T, ABA)

            # score and cb for the relevance
            score_x = np.dot(self.dataObj.feature_data['train_item_latent_features'], self.theta[user])
            XAX = np.multiply(np.dot(self.dataObj.feature_data['train_item_latent_features'], self.A_x_inv[user]), self.dataObj.feature_data['train_item_latent_features']).sum(axis=1)  # x^T A_X^-1 X^T
            cb_x = np.multiply(np.dot(self.dataObj.feature_data['train_item_latent_features'], ABABA), self.dataObj.feature_data['train_item_latent_features']).sum(axis=1) + XAX
            ucb_x = score_x + 1e-6 * tie_breaker
            ABAX = np.dot(ABA, self.dataObj.feature_data['train_item_latent_features'].T).T
            # score and cb for the topic
            # delta_t = []
            batch_features = []
            coverage = np.zeros(self.topic_dim)
            ranking = []
            # ranking_set = set()
            for j in range(self.config.list_size):
                # Line 8 - 11 of Nips 11
                z_t = self.conditional_coverage(x=self.dataObj.feature_data['train_item_topical_features'], coverage=coverage)
                ZAZ = np.multiply(np.dot(z_t, self.A_z_inv[user]), z_t).sum(axis=1)  # Z^T A_Z^-1 Z^T
                # cb_z = ZAZ - 2 * np.multiply(np.dot(z_t, ABA), x).sum(axis=1)
                cb_z = ZAZ - 2 * np.multiply(z_t, ABAX).sum(axis=1)

                # if (self.mitigation is None):
                cb = self.alpha * np.sqrt(cb_z + cb_x)
                # else:
                #     cb = self.alpha * (1 - (self.n_recommended / (t + 1))) * np.sqrt(cb_z + cb_x)
                score_z = np.dot(z_t, self.beta[i])
                ucb = ucb_x + score_z + cb
                # ucb = ucb_x + (1-user_avg_popularity)*score_z + cb

                # if(self.mitigation is not None):
                #     # tmp_n_recommended = self.n_recommended.copy()
                #     # tmp_n_recommended[np.where(tmp_n_recommended == 0)] = 1
                #     # ucb = (1-pow(self.n_recommended/(t+1),2)) * ucb
                #     ucb = (1 - (self.n_recommended / (t + 1))) * ucb

                winner = np.argmax(ucb)
                while winner in ranking:
                    ucb[winner] = -np.inf
                    winner = np.argmax(ucb)

                ranking.append(winner)
                # ranking_set.add(winner)
                batch_features.append(z_t[winner])

                scores.append(ucb[winner])

                coverage = self.ranking_coverage(self.dataObj.feature_data['train_item_topical_features'][ranking])

            rankings[i] = np.asarray(self.shuffling_topK(ranking, scores, self.config.list_size))
            self.batch_features[i][:, :self.topic_dim] = np.asarray(batch_features)
            self.batch_features[i][:, self.topic_dim:] = self.dataObj.feature_data['train_item_latent_features'][rankings[i]]
        return rankings

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
            K_s = compute_user_K_prime(scores, self.gamma, K, epsilon=self.epsilon)

            np.random.shuffle(ranking[:K_s])
        return ranking