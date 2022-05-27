import sys
import numpy as np
import pickle
from nexoclom import math as mathMB


def calculation_step(filename):
    with open(filename, 'rb') as file:
        X0, ind, params, lowalt, dOmega = pickle.load(file)
        nvelbins = params['nvelbins']
        nazbins = params['nazbins']
        naltbins = params['naltbins']
    
    fraction_observed = np.zeros(len(ind))
    for index in range(len(ind)):
        sub = X0.loc[ind[index]]
    
        # Speed, az/alt phase space distribution in cell
        speed = mathMB.Histogram(sub.speed, bins=nvelbins, weights=sub.weight,
                                 range=[0, sub.speed.max()])
    
        angdist = mathMB.Histogram2d(sub.azimuth, sub.altitude, weights=sub.weight,
                                     bins=(nazbins, naltbins),
                                     range=[[0, 2*np.pi], [0, np.pi/2]])
    
        # Convolve with gaussian to smooth things out
        ang = mathMB.smooth2d(angdist.histogram, 3, wrap=True)
    
        az_max = np.zeros((2, nazbins))
        alt_max = np.zeros((2, naltbins))
        for i in range(nazbins):
            row = mathMB.smooth(ang[i,:], 7, wrap=True)
            az_max[:,i] = [np.where(row == row.max())[0].mean(), row.max()]
        for i in range(naltbins):
            row = mathMB.smooth(ang[:,i], 7, wrap=True)
            alt_max[:,i] = [np.where(row == row.max())[0][0], row.max()]
    
        # Ignore high altitudes (bad statistics)
        top = np.mean([az_max[1,:].max(), alt_max[1, lowalt].max()])
        ang /= top
        integral = np.sum(ang * dOmega)
        fraction_observed[index] = integral.value/(2*np.pi)
        
    savefile = filename.replace('data', 'fraction')
    with open(savefile, 'wb') as file:
        pickle.dump(fraction_observed, file)

if __name__ == '__main__':
    calculation_step(sys.argv[1])
