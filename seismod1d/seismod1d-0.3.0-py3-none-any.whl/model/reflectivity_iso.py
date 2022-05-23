import numpy as np

def zoeppritz_rpp(vp1, vs1, rho1, vp2, vs2, rho2, theta1=0):
    """
    Exact Zoeppritz from expression.

    This is useful because we can pass arrays to it, which we can't do to
    scattering_matrix().

    Dvorkin et al. (2014). Seismic Reflections of Rock Properties. Cambridge.

    Returns the complex reflectivity.

    Args:
        vp1 (ndarray): The upper P-wave velocity; float or 1D array length m.
        vs1 (ndarray): The upper S-wave velocity; float or 1D array length m.
        rho1 (ndarray): The upper layer's density; float or 1D array length m.
        vp2 (ndarray): The lower P-wave velocity; float or 1D array length m.
        vs2 (ndarray): The lower S-wave velocity; float or 1D array length m.
        rho2 (ndarray): The lower layer's density; float or 1D array length m.
        theta1 (ndarray): The incidence angle; float or 1D array length n.

    Returns:
        ndarray. The exact Zoeppritz solution for P-P reflectivity at the
            interface. Will be a float (for float inputs and one angle), a
            1 x n array (for float inputs and an array of angles), a 1 x m
            array (for float inputs and one angle), or an n x m array (for
            array inputs and an array of angles).
    """
    theta1 = np.radians(theta1).astype(complex)

    # turn off some warnings
    # np.seterr(divide='ignore', invalid='ignore')

    # convert input 1D arrays to 2D
    nn = len(vp1)
    nangles = theta1.shape[1]
    vp1 = np.tile(vp1.reshape((nn, 1)), (1, nangles))
    vs1 = np.tile(vs1.reshape((nn, 1)), (1, nangles)) + 1e-12
    rho1 = np.tile(rho1.reshape((nn, 1)), (1, nangles))
    vp2 = np.tile(vp2.reshape((nn, 1)), (1, nangles))
    vs2 = np.tile(vs2.reshape((nn, 1)), (1, nangles)) + 1e-12
    rho2 = np.tile(rho2.reshape((nn, 1)), (1, nangles))

    p = np.sin(theta1) / vp1  # Ray parameter
    theta2 = np.arcsin(p * vp2)
    phi1 = np.arcsin(p * vs1)  # Reflected S
    phi2 = np.arcsin(p * vs2)  # Transmitted S

    a = rho2 * (1 - 2 * np.sin(phi2) ** 2.0) - rho1 * (1 - 2 * np.sin(phi1) ** 2.0)
    b = rho2 * (1 - 2 * np.sin(phi2) ** 2.0) + 2 * rho1 * np.sin(phi1) ** 2.0
    c = rho1 * (1 - 2 * np.sin(phi1) ** 2.0) + 2 * rho2 * np.sin(phi2) ** 2.0
    d = 2 * (rho2 * vs2 ** 2 - rho1 * vs1 ** 2)

    E = (b * np.cos(theta1) / vp1) + (c * np.cos(theta2) / vp2)
    F = (b * np.cos(phi1) / vs1) + (c * np.cos(phi2) / vs2)
    G = a - d * np.cos(theta1) / vp1 * np.cos(phi2) / vs2
    H = a - d * np.cos(theta2) / vp2 * np.cos(phi1) / vs1

    D = E * F + G * H * p ** 2

    rpp = (1 / D) * (
        F * (b * (np.cos(theta1) / vp1) - c * (np.cos(theta2) / vp2))
        - H * p ** 2 * (a + d * (np.cos(theta1) / vp1) * (np.cos(phi2) / vs2))
    )

    return np.squeeze(rpp)

        
def get_zoeppritz_rpp(vp, vs, rho, reflection_angles, apply_tr_loss = False):
    
    # get all 
    ref = get_zoeppritz(vp, vs, rho, reflection_angles)
        
    # reflection coefficients        
    RC = ref["r_DPP"]
    
    # apply transmission loss    
    if apply_tr_loss:
        
        rd = ref["r_DPP"]
        td = ref["t_DPP"]
        tu = ref["t_UPP"]
        
        td = np.cumprod(td, axis=0)
        tu = np.cumprod(tu, axis=0)
        
        rd[1:,:] = rd[1:,:]*td[:-1,:]*tu[:-1,:]        
        
        RC = rd        
           
    
    return RC

def get_zoeppritz(vp, vs, rho, reflection_angles):
    
        
    # Amundsen et. al
    
    # turn off some warnings
    np.seterr(divide="ignore", invalid="ignore", under="ignore")    
    
    # get number of input layers
    nlayers = len(vp)    
    
    # if input angles is 1D array, make 2D array (one row per interface)
    if reflection_angles.ndim == 1:

        # make 2D array with N rows (same incidence angle for all layers)
        reflection_angles = np.tile(reflection_angles, (nlayers, 1))    
        
    # add small number to vs to ensure non-zero values
    vs[vs==0] = vs[vs==0] + 1e-12
    
    # convert input 1D model arrays to 2D        
    nangles = reflection_angles.shape[1]
    vp = np.tile(vp.reshape((nlayers, 1)), (1, nangles))
    vs = np.tile(vs.reshape((nlayers, 1)), (1, nangles))
    rho = np.tile(rho.reshape((nlayers, 1)), (1, nangles))
    
    # split model into upper and lower layer values
    vp1 = vp[:-1,:]
    vs1 = vs[:-1,:]
    rho1 = rho[:-1,:]
    vp2 = vp[1:,:]
    vs2 = vs[1:,:]
    rho2 = rho[1:,:]

    # convert reflection angles from degree to radian (ignore last row)
    #th_rad = (np.pi/180)*reflection_angles[:-1,:]   
    th_rad = np.radians(reflection_angles[:-1,:]).astype(complex)
    
    # get slowness
    p = np.sin(th_rad)/vp1#.astype(complex)
        
    mu1 = rho1 * vs1**2
    mu2 = rho2 * vs2**2
    
    qp1 = np.sqrt(vp1**-2 - p**2)
    qs1 = np.sqrt(vs1**-2 - p**2)
    qp2 = np.sqrt(vp2**-2 - p**2)
    qs2 = np.sqrt(vs2**-2 - p**2)
    
    dmu = mu1 - mu2
    drho = rho1 - rho2

    d1 = 2*p**2*dmu*(qp1 - qp2) + (rho1*qp2 + rho2*qp1)
    d2 = 2*p**2*dmu*(qs1 - qs2) + (rho1*qs2 + rho2*qs1)
    d3 = p*(2*dmu*(qp1*qs2 + p**2)-drho)
    d4 = p*(2*dmu*(qp2*qs1 + p**2)-drho)

    c1 = 2*p**2*dmu*(qp1 + qp2) - (rho1*qp2 - rho2*qp1)
    c2 = -2*p**2*dmu*(qs1 + qs2) - (rho1*qs2 - rho2*qs1)
    c3 = -p*(2*dmu*(qp1*qs2-p**2)+drho)
    c4 = -p*(2*dmu*(qp2*qs1-p**2)+drho)

    A2 = 4*p**2*rho2*vs2**4*qs2
    B = 1 - 2*p**2*vs2**2
    A1 = B**2
    C1 = 2*p*rho1*vs2**2
    C2 = 2*p*rho2*vs2**2

    # Solid/solid interface
    det = (d1*d2 + d4*d3)
    r_DPP = (c1*d2 - c3*d4)/det
    r_DPS = -(vp1/vs1)*(c3*d1 + c1*d3)/det
    r_DSP = (vs1/vp1)*(c4*d2 - c2*d4)/det
    r_DSS = -(c2*d1 + c4*d3)/det    
    
    t_DPP = (vp1/vp2)*(2*rho1*qp1*d2)/det
    t_DPS = (vp1/vs2)*(2*rho1*qp1*d4)/det # changed polarity of t_DPS formula in Amundsen's to fit Crewes 
    t_DSP = (vs1/vp2)*(2*rho1*qs1*d3)/det
    t_DSS = (vs1/vs2)*(2*rho1*qs1*d1)/det
    
    t_UPP = (vp2/vp1)*(2*rho2*qp2*d2)/det    
    
    # turn back on all warnings
    np.seterr(all="warn")    
    

    # make output dict
    out = {"r_DPP": r_DPP, "r_DPS": r_DPS, "r_DSP": r_DSP, "r_DSS": r_DSS, 
           "t_DPP": t_DPP, "t_DPS": t_DPS, "t_DSP": t_DSP, "t_DSS": t_DSS, 
           "t_UPP": t_UPP}
    
    # add NaN base layer (for consistent sizes)
    vv = np.nan * np.ones((1, nangles))
    for key in out:            
        out[key] = np.concatenate([out[key], vv])          
            
    return out
    
        