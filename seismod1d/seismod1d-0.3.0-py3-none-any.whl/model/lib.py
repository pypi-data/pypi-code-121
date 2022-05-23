import numpy as np
from scipy.interpolate import interp1d


def insert_model_top(depth_min, depth, vp, vs, rhob, delta, epsilon, gamma):

    if len(np.array([depth_min])) == 0:
        return depth, vp, vs, rhob, delta, epsilon, gamma

    # double first layer (values defined as down-to)
    depth = np.insert(depth, 0, depth_min)
    if len(vp) > 0:
        vp = np.insert(vp, 0, vp[0])
    if len(vs) > 0:
        vs = np.insert(vs, 0, vs[0])
    if len(rhob) > 0:
        rhob = np.insert(rhob, 0, rhob[0])
    if len(delta) > 0:
        delta = np.insert(delta, 0, delta[0])
    if len(epsilon) > 0:
        epsilon = np.insert(epsilon, 0, epsilon[0])
    if len(gamma) > 0:
        gamma = np.insert(gamma, 0, gamma[0])

    return depth, vp, vs, rhob, delta, epsilon, gamma

def merge_layers(depth, vp, vs, rhob, delta=[], epsilon=[], gamma=[]):
    
    # loop through layers and merge if identical
    
    # input size
    nlayers = len(depth)
    

    # put input arrays togother in 2D array    
    M = np.vstack((vp, vs, rhob)).transpose()
    try:
        N = np.vstack((delta, epsilon, gamma)).transpose()
        M = np.hstack((M,N))
    except:
        pass
        
    # indices of layers that are redudant
    idelete = np.array([]).astype(int)        
            
    # loop
    for ii in np.arange(1,nlayers-1):
        
        top_layer = M[ii,:]
        bot_layer = M[ii+1,:]
        
        if np.array_equal(top_layer,bot_layer):
            idelete = np.append(idelete,ii)
    
    # remove redundant layers
    depth = np.delete(depth,idelete)
    vp = np.delete(vp,idelete)
    vs = np.delete(vs,idelete)
    rhob = np.delete(rhob,idelete)
    try: 
        delta = np.delete(delta,idelete)
        epsilon = np.delete(epsilon,idelete)
        gamma = np.delete(gamma,idelete)        
    except:
        pass
    
    return depth, vp, vs, rhob, delta, epsilon, gamma    

def remove_nan(depth, vp, vs, rhob, delta=[], epsilon=[], gamma=[]):

    # get input size
    nn = len(depth)

    # multiply together arrays to find all NaN-values
    vv = depth * vp * vs * rhob

    # include anisotropy
    if len(delta) == nn:
        vv = vv * delta
    if len(epsilon) == nn:
        vv = vv * epsilon
    if len(gamma) == nn:
        vv = vv * gamma

    # find nan's
    kk = np.where(np.isnan(vv) == False)

    # remove part with nan's
    depth = depth[kk]
    vp = vp[kk]
    vs = vs[kk]
    rhob = rhob[kk]

    # include anisotropy
    if len(delta) == nn:
        delta = delta[kk]
    if len(epsilon) == nn:
        epsilon = epsilon[kk]
    if len(gamma) == nn:
        gamma = gamma[kk]

    # return model without nan's
    return depth, vp, vs, rhob, delta, epsilon, gamma


def resample(x_old, y_old, x_new, kind="linear"):

    # reasmple single array
    ff = interp1d(x_old, y_old, kind=kind)
    return ff(x_new)


def depth_resample(
    dz, depth, vp, vs, rhob, delta=[], epsilon=[], gamma=[], kind="linear"
):

    # Resample model to uniform sampling (assume no nan-values)

    # output depth
    depth_new = np.arange(depth[0], depth[-1], dz)

    # resample all model arrays
    vp = resample(depth, vp, depth_new, kind=kind)
    vs = resample(depth, vs, depth_new, kind=kind)
    rhob = resample(depth, rhob, depth_new, kind=kind)
    if len(delta) == len(depth):
        delta = resample(depth, delta, depth_new, kind=kind)
    if len(epsilon) == len(depth):
        epsilon = resample(depth, epsilon, depth_new, kind=kind)
    if len(gamma) == len(depth):
        gamma = resample(depth, gamma, depth_new, kind=kind)

    # return resampled model
    return depth_new, vp, vs, rhob, delta, epsilon, gamma


def depth_centre_to_layer(z_in, z_base=np.nan):

    # adjust depth from instantaneous (centered) to layer (down-to) values

    # make new depth column
    z_out = 0.5 * (z_in[1:] + z_in[:-1])

    # add base of last layer
    if np.isnan(z_base):
        z_base = z_out[-1] + np.diff(z_out)[-1]
    z_out = np.append(z_out, z_base)

    return z_out
