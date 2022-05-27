import numpy as np
from nexoclom.modelcode.surface_temperature import surface_temperature


def rebound_direction(outputs, x):
    npackets = x.shape[0]

    # Choose the altitude -- f(alt) = cos(alt)
    sinalt = outputs.randgen.random(npackets)
    alt = np.arcsin(sinalt)

    # Choose the azimuth -- f(az) = 1/(azmax-azmin)
    az = 2*np.pi*outputs.randgen.random(npackets)

    # Find the velocity components in coordinate system centered on packet
    v_rad = np.sin(alt)                 # Radial component of velocity
    v_tan0 = np.cos(alt) * np.cos(az)   # Component along latitude (points E)
    v_tan1 = np.cos(alt) * np.sin(az)   # Component along longitude (points N)

    # Now rotate to proper surface point
    # v_ren = M # v_xyz => v_xyz = invert(M) # v_ren

    rad = x.copy()
    rad /= np.linalg.norm(rad, axis=1)[:,np.newaxis]
    east = np.array([x[:,1], -x[:,0], np.zeros(npackets)]).transpose()
    east /= np.linalg.norm(east, axis=1)[:,np.newaxis]
    north = np.array([-x[:,2]*x[:,0], -x[:,2]*x[:,1],
                      x[:,0]**2 + x[:,1]**2]).transpose()
    north /= np.linalg.norm(north, axis=1)[:,np.newaxis]
    
    direction = (v_tan0[:,np.newaxis]*north +
                 v_tan1[:,np.newaxis]*east +
                 v_rad[:,np.newaxis]*rad)
    assert np.all(np.isfinite(direction))
    
    return direction


def bouncepackets(outputs, Ximpcheck, r0, hitplanet):
    npackets = np.sum(hitplanet)
    # This will need to be rewritten for satellite impacts

    # Determine where packets hit surface
    Xtemp, rtemp = Ximpcheck[hitplanet,:], r0[hitplanet]
    a = np.sum(Xtemp[:,4:7]**2, axis=1)  # = vv02
    b = 2 * np.sum(Xtemp[:,1:4] * Xtemp[:,4:7], axis=1)
    c = np.sum(Xtemp[:,1:4]**2, axis=1) - 1.
    dd = b**2 - 4*a*c

    t0 = (-b - np.sqrt(b**2-4*a*c))/(2*a)
    t1 = (-b + np.sqrt(b**2-4*a*c))/(2*a)
    t = np.minimum(t0, t1) # t0 <= 0)*t0 + (t1 < 0)*t1

    # point where packet hit the surface
    Xtemp[:,1:4] = Xtemp[:,1:4] + Xtemp[:,4:7] * t[:,np.newaxis]
    assert np.all(np.isclose(np.linalg.norm(Xtemp[:,1:4], axis=1), 1.))

    # Determine impact velocity
    PE = 2*outputs.GM*(1./rtemp - 1)
    v_old2 = a + PE
    v_old2[v_old2 < 0] = 0.

    direction = rebound_direction(outputs, Xtemp[:,1:4])
    
    if outputs.inputs.surfaceinteraction.accomfactor == 0:
        v_new = np.sqrt(v_old2)
    else:
        lonhit = (np.arctan2(Xtemp[:,1], -Xtemp[:,2])+2*np.pi) % (2*np.pi)
        lathit = np.arcsin(Xtemp[:,3])
        
        surftemp = surface_temperature(outputs.inputs.geometry,
                                       lonhit, lathit)
        probability = outputs.randgen.random(npackets)
        v_emit = outputs.surfaceint.v_interp(surftemp, probability)
        v_emit /= outputs.inputs.geometry.planet.radius.value
        
        afactor = outputs.inputs.surfaceinteraction.accomfactor
        v_new = np.sqrt(v_emit**2 * afactor + v_old2 * (1-afactor))
        
    Xtemp[:,4:7] = direction * v_new[:,np.newaxis]

    # Adjust the fractional values
    if outputs.inputs.surfaceinteraction.sticktype == 'temperature dependent':
        lonhit = (np.arctan2(Xtemp[:,1], -Xtemp[:,2])+2*np.pi) % (2*np.pi)
        lathit = np.arcsin(Xtemp[:,3])
        stickcoef = outputs.surfaceint.stickcoef(lonhit, lathit)
        assert np.all(stickcoef <= 1) and np.all(stickcoef >= 0), (
            'Problem with the sticking coefficient')
        Xtemp[:,7] *= (1 - stickcoef)
    elif outputs.inputs.surfaceinteraction.sticktype == 'surface map':
        assert 0
    elif outputs.inputs.surfaceinteraction.stickcoef > 0:
        Xtemp[:,7] *= (1 - outputs.inputs.surfaceinteraction.stickcoef)
    elif outputs.inputs.surfaceinteraction.stickcoef == 0:
        pass
    else:
        assert 0, 'Should not be able to get here.'
        
    # Put new values back in
    Ximpcheck[hitplanet,:] = Xtemp
