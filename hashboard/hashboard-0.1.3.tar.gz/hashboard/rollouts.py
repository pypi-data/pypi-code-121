import numpy as np
from .history import eg48_mean, phase_to_subsidy
from .timeline import Timeline

def get_new_difficulty_bits(zero_bits, timespan):
    '''
    Compute the new value of 32 + log2(difficulty)
    '''

    blocks_per_epoch = 2016
    seconds_in_epoch = blocks_per_epoch * 600.0

    # Only 2015 of the 2016 blocks actually contribute to the difficulty
    # calculation -- see https://www.bitrawr.com/difficulty-estimator --
    # so we apply this adjustment factor:
    adjustment_factor = blocks_per_epoch / (blocks_per_epoch - 1.0)

    adjustment = np.log(seconds_in_epoch * adjustment_factor / timespan) / np.log(2)
    adjustment = np.maximum(-2.0, np.minimum(adjustment, 2.0))
    difficulty_bits = np.maximum(zero_bits + adjustment, 32.0)

    return difficulty_bits


def extract_design_matrix(desc, df):

    matrices = []

    for t in desc:

        df2 = df[list(t[1])]
        df2 = {'curr': df2.iloc[1:], 'prev': df2.iloc[:-1]}[t[0]]
        if t[2] == 'ewma':
            matrix = [(df2 if (alpha >= 1.0) else df2.ewm(alpha=alpha).mean()) for alpha in t[3]]
            matrix = [m.values for m in matrix]
        elif t[2] == 'fourier':
            matrix = df2.values * (2.0 * np.pi)
            matrix = [matrix * freq for freq in t[3]]
            matrix = [f(m) for m in matrix for f in [np.cos, np.sin]]
        else:
            raise ValueError("Unknown transformation: %s" % t[2])

        matrix = [m[:, np.newaxis, :] for m in matrix]
        matrix = np.concatenate(matrix, axis=1)

        matrices.append(matrix)

    return matrices


def update_design_matrix(desc, prev_matrices, prev_dict, curr_dict):

    matrices = []

    for (idx, t) in enumerate(desc):

        d = {'curr': curr_dict, 'prev': prev_dict}[t[0]]
        matrix = np.concatenate([d[a].reshape((-1, 1, 1)) for a in t[1]], axis=2)
        alphas = t[3].reshape((1, -1, 1))
        matrix = matrix * alphas

        if t[2] == 'ewma':
            matrix += prev_matrices[idx] * (1.0 - alphas)
        elif t[2] == 'fourier':
            matrix *= (2.0 * np.pi)
            matrix = np.concatenate([np.cos(matrix), np.sin(matrix)], axis=1)
        else:
            raise ValueError("Unknown transformation: %s" % t[2])

        matrices.append(matrix)

    return matrices


class Rollouts(object):

    def __init__(self, laststate, n_rollouts, models):

        self.laststate = laststate
        self.current_price = float(laststate['features']['price'])
        self.n_rollouts = n_rollouts
        self.gamma_params = np.array([48] * n_rollouts)
        self.models = models

        # Ensure all features and design matrices have shape (n_rollouts, ...)
        zero_array = np.array([0.0] * n_rollouts)

        f = self.laststate['features']
        for k in f:
            if 'height' not in k:
                f[k] = f[k] + zero_array

        self.timeline = [f]

        for f in self.laststate['design_matrices'].values():
            for k in range(len(f)):
                z = zero_array.reshape((-1,) + (1,) * (len(f[k].shape) - 1))
                f[k] = f[k] + z

    def __getitem__(self, key):
        '''
        Return an array of shape (n_phases,) or (n_phases, n_rollouts)
        according to the specified key. Possible keys are:

        -- end_height : block height at the end of the phase;
        -- end_time : Unix time at the end of the phase;
        -- log_hashrate : natural logarithm of hashes per second;
        -- log_price : natural logarithm of BTC/USD exchange rate;
        -- log_reward : natural logarithm of total reward per block (in BTC);
        -- zero_bits : 32 + log2(difficulty).

        The first of these is 1-dimensional; all others are 2-dimensional.
        '''

        return np.stack([t[key] for t in self.timeline], axis=0)

    def run_model(self, modelname, currstate):

        dm = update_design_matrix(self.models[modelname]['predictors'],
                                  self.laststate['design_matrices'][modelname],
                                  self.laststate['features'],
                                  currstate['features'])
        currstate['design_matrices'][modelname] = dm
        X = np.concatenate([m.reshape((len(m), -1)) for m in dm], axis=1)
        sqrt_cov = self.models[modelname]['sqrt_cov']
        epsilon = np.dot(np.random.randn(self.n_rollouts, len(sqrt_cov)), sqrt_cov)
        Y = self.models[modelname]['model'].predict(X) + epsilon

        for (i, label) in enumerate(self.models[modelname]['responses']):
            currstate['features'][label] = Y[:, i]

    def iterate(self):

        phase = self.laststate['phase'] + 1
        height = phase * 48

        lastdict = self.laststate['features']

        zero_bits = lastdict['zero_bits']
        start_time = lastdict['end_time']
        last_retarget = lastdict['last_retarget']

        if (height % 2016) == 0:
            # difficulty adjustment
            zero_bits = get_new_difficulty_bits(zero_bits, start_time - last_retarget)
            last_retarget = start_time

        subsidy_btc = phase_to_subsidy(phase)

        if (height % 210000) == 0:
            # halving
            print("Block subsidy reduced to %.8f BTC at height %d." % (subsidy_btc, height))

        # The exact distribution of ilhr - log(hashrate). This is unbiased
        # (mean zero) but asymmetrically distributed.
        epsilon = eg48_mean - np.log(np.random.gamma(self.gamma_params, 1))

        currdict = {'start_height': height,
                    'end_height': height + 48,
                    'zero_bits': zero_bits,
                    'start_time': start_time,
                    'last_retarget': last_retarget,
                    'subsidy_btc': subsidy_btc,
                    'epsilon': epsilon}

        currstate = {'phase': phase, 'features': currdict, 'design_matrices': {}}

        self.run_model('fee', currstate)

        currdict['log_reward'] = np.log(np.exp(currdict['log_fees']) + subsidy_btc)

        self.run_model('hashrate', currstate)

        currdict['ilhr'] = currdict['log_hashrate'] + epsilon
        currdict['duration'] = np.exp(np.log(2) * currdict['zero_bits'] + eg48_mean - currdict['ilhr'])
        currdict['end_time'] = currdict['start_time'] + currdict['duration']

        self.laststate = currstate
        self.timeline.append(currdict)

    def resample_indices(self):

        et = self['end_time']
        ll = int(max(et[0])) // 86400
        ul = int(min(et[-1])) // 86400
        unix_times = np.array(range(ll, ul + 1)) * 86400

        as2 = lambda x : np.argsort(np.argsort(x, axis=0), axis=0)
        queries = unix_times.reshape((-1, 1)) + 0 * et[0]

        row_indices = as2(np.concatenate([queries, et], axis=0))[:len(queries)] - as2(queries)
        col_indices = np.array([list(range(len(et[0])))])

        return unix_times, row_indices, col_indices

    def to_timeline(self):

        unix_times, idxs, idxs2 = self.resample_indices()

        inv_cumsum = lambda x : np.concatenate([x[:1], np.diff(x, axis=0)], axis=0)

        # compute average block reward:
        block_reward = np.exp(self['log_reward'])
        c1 = inv_cumsum(np.cumsum(block_reward, axis=0)[idxs, idxs2])
        c2 = inv_cumsum(np.cumsum(block_reward / block_reward, axis=0)[idxs, idxs2])
        block_reward = c1 / (c2 + 1.0e-8)

        hashes_per_block = np.exp(np.log(2) * self['zero_bits'][idxs, idxs2])
        price = np.exp(self['log_price'][idxs, idxs2])

        return Timeline(unix_times, self.current_price, price, block_reward, hashes_per_block)
