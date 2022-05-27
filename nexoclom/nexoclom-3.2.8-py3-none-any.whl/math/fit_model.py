import numpy as np
from scipy.optimize import minimize_scalar
import statsmodels.regression.linear_model as lm
from astropy.visualization import PercentileInterval


class InputError(Exception):
    """Raised when a required parameter is not included."""
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

def fit_model(data, model, sigma, fit_method='chisq', masking=None,
              mask_only=False, **kwargs):
    def chisq(x):
        return np.sum((data[mask] - x*model[mask])**2 /
                      sigma[mask]**2)/(sum(mask)-1)
    
    def difference(x):
        return np.sum(np.abs(data[mask] - x*model[mask]))
    
    mask = np.array([True for _ in data])
    sigmalimit = None
    if masking is not None:
        for masktype in masking.split(';'):
            masktype = masktype.strip().lower()
            if masktype.startswith('middle'):
                perinterval = float(masktype[6:])
                # Estimate model strength (source rate) by fitting middle %
                interval = PercentileInterval(perinterval)
                lim = interval.get_limits(data)
                mask = (mask &
                        (data >= lim[0]) &
                        (data <= lim[1]))
            elif (masktype.startswith('minalt')) and ('altitude' in kwargs):
                minalt = float(masktype[6:])
                mask = mask & (kwargs['altitude'] >= minalt)
            elif masktype.startswith('minalt'):
                raise InputError('nexoclom.math.fit_model', 'Altitude not supplied.')
            elif masktype.startswith('minsnr'):
                minSNR = float(masktype[6:])
                snr = data/sigma
                mask = mask & (snr > minSNR)
            elif masktype.startswith('siglimit'):
                sigmalimit = masktype
            else:
                raise InputError('nexoclom.math.fit_model',
                                 f'masking = {masktype} not defined.')
    else:
        pass
    
    if mask_only:
        return None, None, mask
    else:
        available_fitfunctions = ['chisq', 'difference', 'wls']
        if np.any(mask) == False:
            # No data points are included - just do a simple fit for show
            mask_ = mask.copy()
            mask[:] = True
            model_strength = minimize_scalar(difference)
            mask = mask_
            return model_strength.x, model_strength.fun, mask
        elif fit_method.lower() in available_fitfunctions:
            if fit_method == 'wls':
                # Weighted least squares fit
                wls_model = lm.WLS(model[mask], data[mask], 1./sigma[mask]**2)
                result = wls_model.fit()
                
                if sigmalimit is not None:
                    siglimit = float(sigmalimit[8:])
                    diff = (data - model/result.params[0])/sigma
                    mask = mask & (diff < siglimit*sigma)
                    wls_model = lm.WLS(model[mask], data[mask], 1./sigma[mask]**2)
                    result = wls_model.fit()
                else:
                    pass
                return 1./result.params[0], result.rsquared, mask
            else:
                model_strength = minimize_scalar(eval(fit_method.lower()))
                
                if sigmalimit is not None:
                    siglimit = float(sigmalimit[8:])
                    diff = (data - model_strength.x*model)/sigma
                    mask = mask & (diff < siglimit*sigma)
                    model_strength = minimize_scalar(eval(fit_method.lower()))
                else:
                    pass
                return model_strength.x, model_strength.fun, mask
        else:
            raise InputError('nexoclom.math.fit_model',
                             f'fit_method = {fit_method} not defined.')
