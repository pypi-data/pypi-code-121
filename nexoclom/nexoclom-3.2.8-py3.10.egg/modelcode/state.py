"""Computes acceleration and ionization on a packet due to specified forces

Gravitational acceleration

Equations of motion:
    dvxdt = sum_objects (GM * (x-x_obj))/(r_obj)^3
    dvydt = sum_objects (GM * (y-y_obj))/(r_obj)^3
    dvzdt = sum_objects (GM * (z-z_obj))/(r_obj)^3
        -- r_obj = sqrt( (x-x_obj)^2 + (y-y_obj)^2 + (z-z_obj)^2 )
    dndt = instantaneous change in density

Current version: Assumes there is only a planet -- does not do moons yet
"""
import numpy as np


def state(x, output):
    # compute gravitational acceleration
    if output.inputs.forces.gravity:
        r3 = (np.linalg.norm(x[:,1:4], axis=1))**3
        agrav = output.GM * x[:,1:4]/r3[:,np.newaxis]
    else:
        agrav = np.zeros(x[:,1:4].shape)
        
    # compute radiation acceleration
    arad = np.zeros(x[:,1:4].shape)
    if output.inputs.forces.radpres:
        rho = np.linalg.norm(x[:,[1,3]], axis=1)
        out_of_shadow = (rho > 1) | (x[:,2] < 0)

        # radial velocity of each packet realtive to the Sun
        vv = x[:,5] + output.vrplanet

        # Compute radiation acceleration
        arad[:,1] = np.interp(vv, output.radpres.velocity,
                              output.radpres.accel) * out_of_shadow
    else:
        pass
    
    # Compute total acceleration
    accel = agrav + arad

    # Compute ionization rate
    if output.inputs.options.lifetime > 0:
        # Explicitly set lifetime
        ionizerate = np.ones(x[:,0].shape)/output.inputs.options.lifetime.value
    else:
        if output.loss_info.photo is not None:
            # Compute photoionization rate
            rho = np.linalg.norm(x[:,[1,3]], axis=1)
            out_of_shadow = (rho > 1) | (x[:,2] < 0)
            photorate = output.loss_info.photo * out_of_shadow
        else:
            photorate = np.zeros(x[:,0].shape)
         
        '''
        magcoord = xyz_to_magcoord(t, x, output.inputs, output.planet)

        if output.loss_info.eimp:
            # Compute electron impact rate
            assert 0, 'Electron impacts not set up yet'
        else:
            eimprate = 0.

        if output.loss_info.chX:
            # Compute charge exchange rate
            assert 0, 'Charge exchange not set up yet'
        else:
            chxrate = 0.
        '''

        ionizerate = photorate  # + eimprate + chxrate

    return accel, ionizerate
