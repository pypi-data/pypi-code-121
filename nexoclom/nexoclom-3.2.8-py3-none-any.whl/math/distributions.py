import numpy as np
from nexoclom.atomicdata import atomicmass
import astropy.units as u
import astropy.constants as const


def sputdist(velocity, U, alpha, beta, species):
    mspecies = atomicmass(species)
    v_b = np.sqrt(2*U/mspecies)
    v_b = v_b.to(u.km/u.s)
    f_v = velocity**(2*beta+1) / (velocity**2 + v_b**2)**alpha
    f_v /= np.max(f_v)
    return f_v.value


def MaxwellianDist(velocity, temperature, species):
    vth2 = 2*temperature*const.k_B/atomicmass(species)
    vth2 = vth2.to(u.km**2/u.s**2)
    f_v = velocity**3 * np.exp(-velocity**2/vth2)
    f_v /= np.max(f_v)
    return f_v.value

class CumDist:
    """Cumulative distribution function"""
    
    def __init__(self, x, y=None):
        """
        :param x: If y is specified, x is the values at which the probability
            distribution function was sampled;
            otherwise it is randomly chosen values from a distribution function
            
        :param y: If given, the probability distribution function
        """
        ind = np.argsort(x)
        self.x = x[ind]
        if y is None:
            self.sum = np.linspace(0, 1, len(x))
        else:
            y_ = y[ind]
            s = y_.cumsum()
            s -= s.min()
            self.sum = s/s.max()

# class CumDist2d:
#     """See Numerical Recipes, Ch 14.8"""
#     def __init__(self, x, y, sourcemap=None):
#         # x, y are randomly chosen from 2D distribution
#         q1, q2, q3, q4 = tuple(np.zeros((len(x), len(y))) for _ in range(4))
#         npts = len(x) * len(y)
#         grid = np.indices((len(x), len(y)))
#         xgrid, ygrid = grid[0], grid[1]
#
#         # q1 = (x[xgrid] <= x[np.newaxis,:]) & (y[ygrid] <= y[:,np.newaxis])
#
#         xLT = x[xgrid] <= x[np.newaxis,:]
#         yLT = y[ygrid] <= y[:,np.newaxis]
#         xGT = x[xgrid] > x[np.newaxis,:]
#         yGT = y[ygrid] > y[:,np.newaxis]
#
#         func_q1 = lambda i, j: sum(xLT[:,i] & yLT[j,:])
#         from IPython import embed; embed()
#         import sys; sys.exit()
#
#         q1 = np.fromfunction(func_q1, (10, 10), dtype=int)
#
#         # print(q1pts[5, 5])
#         i, j = 5, 5
#         print(q1[i,j])
#         print(np.sum((x <= x[i]) & (y <= y[j])))
#
#
#
#         if sourcemap is None:
#             for i in range(len(x)):
#                 for j in range(len(y)):
#                     q1[i,j] = np.sum((x <= x[i]) & (y <= y[j]))/npts
#                     q2[i,j] = np.sum((x <= x[i]) & (y > y[j]))/npts
#                     q3[i,j] = np.sum((x > x[i]) & (y <= y[j]))/npts
#                     q4[i,j] = np.sum((x > x[i]) & (y > y[j]))/npts
#         else:
#             # func = interpolate.RectBivariateSpline(sourcemap['longitude'].value,
#             #                                        sourcemap['latitude'].value,
#             #                                        sourcemap['map'])
#             # z = func.ev(x, y)
#             x, y = sourcemap['longitude'].value, sourcemap['latitude'].value
#             z = sourcemap['map']
#             total = np.sum(z)
#             for i in range(len(x)):
#                 for j in range(len(y)):
#                     q1[i] = np.sum(z[(x <= x[i]) & (y <= y[i])])/total
#                     q2[i] = np.sum(z[(x <= x[i]) & (y > y[i])])/total
#                     q3[i] = np.sum(z[(x > x[i]) & (y <= y[i])])/total
#                     q4[i] = np.sum(z[(x > x[i]) & (y > y[i])])/total
