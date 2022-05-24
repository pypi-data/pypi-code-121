import numpy as np
from .linear_upper_confidence_bound import LinUCB
from fair_dynamic_rec.core.util.utils import compute_user_K_prime

class EARSLinUCB(LinUCB):
    def __init__(self, config, dataObj, parameters=None):
        super(EARSLinUCB, self).__init__(config, dataObj, parameters)
        self.shuffle_K = int(parameters['shuffle_K']['value'])
        self.epsilon = float(parameters['epsilon']['value'])
        self.gamma = float(parameters['gamma']['value'])

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
            cb = self.alpha * np.sqrt(np.multiply(np.dot(self.dataObj.feature_data['train_item_latent_features'], self.MInv[user]), self.dataObj.feature_data['train_item_latent_features']).sum(axis=1))
            score = np.dot(self.dataObj.feature_data['train_item_latent_features'], self.theta[user])
            ucb = score + cb
            rankings[i] = np.lexsort((tie_breaker, -ucb))[:self.config.list_size]

            rankings[i] = np.asarray(self.shuffling_topK(rankings[i], np.sort(-ucb)[:self.config.list_size], self.config.list_size))

            self.batch_features[i] = self.dataObj.feature_data['train_item_latent_features'][rankings[i]]
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