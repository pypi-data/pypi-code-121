import numpy as np
from .linear_submodular_bandit import LSB
from fair_dynamic_rec.core.util.utils import compute_user_K_prime

class EARSLSB(LSB):
    def __init__(self, config, dataObj, parameters=None):
        super(EARSLSB, self).__init__(config, dataObj, parameters)
        self.shuffle_K = int(parameters['shuffle_K']['value'])
        self.epsilon = float(parameters['epsilon']['value'])
        self.gamma = float(parameters['gamma']['value'])

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
                cb = self.alpha * np.sqrt(np.multiply(np.dot(gain_in_topic_coverage, self.MInv[user]), gain_in_topic_coverage).sum(axis=1))
                score = np.dot(gain_in_topic_coverage, self.theta[user])
                ucb = score + cb + 1e-6 * tie_breaker

                winner = np.argmax(ucb)
                while winner in ranking:
                    ucb[winner] = -np.inf
                    winner = np.argmax(ucb)

                ranking.append(winner)
                self.batch_features[i][j] = gain_in_topic_coverage[winner]
                scores.append(ucb[winner])

                coverage = self.ranking_coverage(self.dataObj.feature_data['train_item_topical_features'][ranking])
            rankings[i] = np.asarray(self.shuffling_topK(ranking, scores, self.config.list_size))
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