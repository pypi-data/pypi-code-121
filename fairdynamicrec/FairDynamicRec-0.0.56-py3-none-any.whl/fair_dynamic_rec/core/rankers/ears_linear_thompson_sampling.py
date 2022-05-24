import numpy as np
from .abstract_ranker import AbstractRanker
from itertools import chain, combinations
from fair_dynamic_rec.core.util.online_logistic_regression import OnlineLogisticRegression
from scipy import special
from scipy.special import binom, expit
# from scipy.optimize import minimize
from tqdm import tqdm
from joblib import Parallel, delayed

# Linear Thompson Sampling strategy for fully personalized contextual bandits, as in [Chapelle and Li, 2011]
class EARSLinearTS(AbstractRanker):
    def __init__(self, config, dataObj, parameters=None):#, user_features, n_playlists, bias=0.0, cascade_model=True, l2_reg=1, shuffle_K=0, epsilon=.0):
        super(EARSLinearTS, self).__init__(config, dataObj)

        l2_reg = float(parameters["l2_reg"]["value"])
        bias = float(parameters["bias"]["value"])

        # self.user_features = user_features
        n_dim = self.dataObj.feature_data['train_user_latent_features'].shape[1]#user_features.shape[1]
        self.n_playlists = dataObj.n_items#n_playlists
        self.models = [OnlineLogisticRegression(l2_reg, 1, n_dim, bias, 15) for i in range(dataObj.n_items)]
        self.m = np.zeros((dataObj.n_items, n_dim))
        self.m[:, -1] = bias
        self.q = np.ones((dataObj.n_items, n_dim))
        self.n_dim = n_dim
        # self.cascade_model = cascade_model
        self.shuffle_K = int(parameters["shuffle_K"]["value"])
        self.epsilon = float(parameters["epsilon"]["value"])

    def get_ranking(self, batch_users, round=None):
        user_features = np.take(self.dataObj.feature_data['train_user_latent_features'], batch_users, axis=0)
        n_users = len(batch_users)
        recos = np.zeros((n_users, self.config.list_size), dtype=np.int64)
        P_clicks = np.zeros((n_users, self.config.list_size), dtype=np.float64)
        step = 1
        u = 0
        while u < n_users:
            u_next = min(n_users, u+step)
            p_features_sampled =(np.random.normal(self.m, 1/np.sqrt(self.q), size= (u_next-u, self.n_playlists, self.n_dim)))
            step_p = p_features_sampled.dot(user_features[u:u_next].T)
            for i in range(u_next - u):
                # Extract recommendation scores for this user
                u_scores = expit(step_p[i,:,i])
                # Argsort according to negative scores to get top-K
                u_recos = np.argsort(-u_scores)[:self.config.list_size]
                recos[u+i] = u_recos
                # Extract and store scores
                P_clicks[u+i] = u_scores[u_recos]

            u += step

        # Reshuffle top-12 if specified
        if self.shuffle_K > 1:
            for u in range(n_users):
                np.random.shuffle(recos[u,:self.shuffle_K])

        # Personalised reshuffling
        if self.shuffle_K == -1:
            # For every user
            gamma = 0.9
            E_c = Parallel(n_jobs=-1)(delayed(AbstractRanker.powerset_expectation_negation_partial)(P_clicks[u], gamma, 1) for u in range(n_users))
            # print(f'Expected clicks without shuffling top-K:', np.mean(E_c), np.var(E_c))
            K = 6
            E_c = Parallel(n_jobs=-1)(delayed(AbstractRanker.powerset_expectation_negation_partial)(P_clicks[u], gamma, K) for u in range(n_users))
            # print(f'Expected clicks after shuffling Top-{K}:', np.mean(E_c), np.var(E_c))

            K_s = Parallel(n_jobs=-1)(delayed(AbstractRanker.compute_user_K_prime)(P_clicks[u], gamma, epsilon=self.epsilon) for u in range(n_users))

            for u, K in enumerate(K_s):
                np.random.shuffle(recos[u,:K])

        return recos

    def update(self, batch_users, rankings, clicks, round=None, user_round=None):#, user_ids, recos , rewards, l_init=3):
        # rewards = 2 * rewards - 1
        # batch_size = len(user_ids)
        modified_playlists = {}
        for i in range(len(batch_users)):
            user = batch_users[i]
            _clicks = self.__collect_feedback(clicks, i)
        # for i in range(batch_size):
            total_stream = len(_clicks.nonzero()[0])
            # nb_display = 0
            for p, r in zip(rankings[i], _clicks):
                # nb_display +=1
                if p not in modified_playlists:
                    modified_playlists[p] = {"X" : [], "Y" : []}
                modified_playlists[p]["X"].append(self.dataObj.feature_data['train_user_latent_features'][batch_users[i]])
                modified_playlists[p]["Y"].append(r)
                if r == 1:
                    break
        for p,v in modified_playlists.items():
            X = np.array(v["X"])
            Y = np.array(v["Y"])
            self.models[p].fit(X,Y)
            self.m[p] = self.models[p].m
            self.q[p] = self.models[p].q
        return

    def __collect_feedback(self, clicks, batch_user_id):
        """
        :param y:
        :return: the last observed position.
        """
        # With  Cascade assumption, only the first click counts.
        if self.config.feedback_model == 'cascade':
            if np.sum(clicks[batch_user_id]) == 0:
                return clicks[batch_user_id]#, self.batch_features[batch_user_id]
            first_click = np.where(clicks[batch_user_id])[0][0]
            return clicks[batch_user_id][:first_click + 1]#, self.batch_features[batch_user_id][:first_click + 1]
        elif self.config.feedback_model == 'dcm':
            if np.sum(clicks[batch_user_id]) == 0:
                return clicks[batch_user_id]#, self.batch_features[batch_user_id]
            last_click = np.where(clicks[batch_user_id])[0][-1]
            return clicks[batch_user_id][:last_click + 1]#, self.batch_features[batch_user_id][:last_click + 1]
        # all items are observed
        else:
            return clicks[batch_user_id]#, self.batch_features[batch_user_id]

# def powerset_expectation_negation_partial(R, gamma, K):
#     ''' Expected number of clicks over all possible permutations of R by counting powersets. '''
#
#     N = len(R)
#     R_neg = (1 - R).tolist()
#
#     result = 0
#     for subset in powerset(R_neg[:K], K):
#         k = len(subset)
#         prod = np.multiply.reduce(subset)
#         discount = gamma ** k
#         if k != N:
#             discount *= (1 - gamma)
#         result += prod / special.binom(K, k) * discount
#
#     for i in range(K, N):
#         discount = gamma ** (i + 1)
#         if i != (N - 1):
#             discount *= (1 - gamma)
#         result += np.multiply.reduce(R_neg[:i + 1]) * discount
#
#     return 1 - result
# ## Utilities
# def powerset(iterable, maxsize):
#     ''' From https://stackoverflow.com/questions/1482308/how-to-get-all-subsets-of-a-set-powerset '''
#     s = list(iterable)
#     return chain.from_iterable(combinations(s, r) for r in range(maxsize+1))
# def compute_user_K_prime(R, gamma = 0.9, max_K = 12, epsilon = 0.02):
#     ''' Compute the value of K' for a user, up to which we can shuffle with max epsilon loss in clicks '''
#     E_c = np.array([powerset_expectation_negation_partial(R, gamma, K) for K in range(1, max_K + 1)])
#     E_c /= E_c[0]
#     return np.searchsorted(-E_c, -(1.0 - epsilon))