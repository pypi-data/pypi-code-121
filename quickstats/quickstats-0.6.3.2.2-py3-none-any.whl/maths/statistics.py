import numpy as np

def calculate_nll(obs:float, exp:float):
    import ROOT
    return np.log(ROOT.TMath.Poisson(obs, exp))

def calculate_chi2(data_obs, data_exp, error_obs=None, threshold:float=3, epsilon:float=1e-6):
    if np.any(data_obs < 0):
        raise RuntimeError("data observed has negative-value element(s)")
    if np.any(data_exp < 0):
        raise RuntimeError("data expected has negative-value element(s)")        
    if error_obs is None:
        error_obs = np.sqrt(data_obs)
    data_obs = np.array(data_obs, dtype=np.float64)
    data_exp = np.array(data_exp, dtype=np.float64)
    error_obs = np.array(error_obs, dtype=np.float64)
    if data_obs.shape != data_exp.shape:
        raise RuntimeError("data observed and data expected have different shapes")
    if data_obs.shape != error_obs.shape:
        raise RuntimeError("data observed and error observed have different shapes")
    if data_obs.ndim != 1:
        raise RuntimeError("only one dimensional data is supported")
    chi2, chi2_last, obs_aggregate, exp_aggregate, error2_aggregate = 0., 0., 0., 0., 0.
     = 0.
    nbin_chi2 = 0
    bin_last = 1
    n_bins = len(data_obs)
    for i in range(n_bins):
        obs_aggregate += data_obs[i]
        exp_aggregate += data_exp[i]
        error2_aggregate += error_obs[i] ** 2
        if (obs_aggregate / np.sqrt(error2_aggregate) < threshold) or \
           (abs(obs_aggregate) < epsilon):
            if i != (n_bins - 1):
                continue
            else:
                chi2 -= chi2_last
                obs_aggregate = np.sum(data_obs[bin_last:])
                exp_aggregate = np.sum(data_exp[bin_last:])
                error2_aggregate = np.sum(error_obs[bin_last:] ** 2)
                chi2 += ((obs_aggregate - exp_aggregate) / np.sqrt(error2_aggregate)) ** 2
                if nbin_chi2 == 0:
                    nbin_chi2 += 1
        else:
            chi2_last = ((obs_aggregate - exp_aggregate) / np.sqrt(error2_aggregate)) ** 2
            bin_last = i
            chi2 += chi2_last
            nbin_chi2 += 1
            obs_aggregate, exp_aggregate, error2_aggregate = 0., 0., 0.
    # calculate likelihood
    nll, nll_last, nll_sat, nll_sat_last = 0., 0., 0., 0.
    obs_aggregate, exp_aggregate = 0., 0.
    nbin_nll = 0
    bin_last = 0
    for i in range(n_bins):
        obs_aggregate += data_obs[i]
        exp_aggregate += data_exp[i]
        error2_aggregate += error_obs[i] ** 2
        if (obs_aggregate < 2):
            if i != (n_bins - 1):
                continue
            else:
                nll -= nll_last
                nll_sat -= nll_sat_last
                obs_aggregate = np.sum(data_obs[bin_last:])
                exp_aggregate = np.sum(data_exp[bin_last:])
                nll += -1 * self.calculate_nll(obs_aggregate, exp_aggregate)
                # saturated
                nll_sat += -1 * self.calculate_nll(obs_aggregate, obs_aggregate)
                if nbin_nll == 0:
                    nbin_nll += 1
        else:
            nll_last = -1 * self.calculate_nll(obs_aggregate, exp_aggregate)
            nll_sat_last = -1 * self.calculate_nll(obs_aggregate, obs_aggregate)
            nll += nll_last
            nll_sat += nll_sat_last
            bin_last = i
            nbin_nll += 1
            obs_aggregate, exp_aggregate = 0., 0.
    result = {
        'chi2': chi2,
        'nbin_chi2': nbin_chi2,
        'nll': nll,
        'nll_sat': nll_sat,
        'nbin_nll': nbin_nll
    }
    return result