import numpy as np
from nexoclom.modelcode.state import state

# RK coefficients
c = np.array([0, 0.2, 0.3, 0.8, 8./9., 1., 1.])
b = np.array([35./384., 0., 500./1113., 125./192., -2187./6784.,
              11./84., 0.])
bs = np.array([5179./57600., 0., 7571./16695., 393./640., -92097./339200.,
               187./2100., 1./40.])
bd = b - bs

a = np.zeros((7,7))
a[1,0] = 0.2
a[2,:2] = [3./40., 9./40.]
a[3,:3] = [44./45., -56./15., 32./9.]
a[4,:4] = [19372./6561., -25360./2187., 64448./6561., -212./729.]
a[5,:5] = [9017./3168., -355./33., 46732./5247., 49./176., -5103./18656.]
a[6,:] = b


def rk5(output, X0, h):
    """Perform a single rk5 step."""
    x = np.zeros((X0.shape[0], X0.shape[1], 7))
    x[:,:,0] = X0
    x[:,7,0] = np.log(x[:,7,0])
    accel = np.zeros((X0.shape[0], 3, 7))
    ioniz = np.zeros((X0.shape[0], 7))
    
    for n in range(6):
        accel[:,:,n], ioniz[:,n] = state(x[:,:,n], output)
        x[:,0,n+1] = -h*c[n+1]
        for i in np.arange(n+1):
            x[:,1:4,n+1] += h[:,np.newaxis]*a[n+1,i]*x[:,4:7,i]
            x[:,4:7,n+1] += h[:,np.newaxis]*a[n+1,i]*accel[:,:,i]
            x[:,7,n+1] -= h*a[n+1,i]*ioniz[:,i]
        x[:,:,n+1] += x[:,:,0]

    if output.inputs.options.step_size == 0:
        delta = np.zeros_like(X0)
        for i in range(6):
            delta[:,1:4] += bd[i]*x[:,4:7,i]
            delta[:,4:7] += bd[i]*accel[:,:,i]
            delta[:,7] += bd[i]*ioniz[:,i]
        delta = np.abs(h[:,np.newaxis]*delta)
    else:
        delta = None

    # Put frac back the way it should be
    result = x[:,:,6]
    result[:,7] = np.exp(result[:,7])
    
    assert np.all(np.isclose(result[:,0], x[:,0,0] - h))
    
    return result, delta
