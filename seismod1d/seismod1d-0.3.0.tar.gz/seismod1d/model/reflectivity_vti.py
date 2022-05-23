import numpy as np


# turn off some warnings


# Alexey Stovas and Bjorn Ursin
# "Reflection and transmission responses of layered transversely isotropic viscoelastic media"
# Geophysical Prospecting, 2003, 51, 447–477


def conv_vti_thoms2cij(rho, vp, vs, delT=None, epsT=None, gamT=None):
    if delT is None:
        delT = np.zeros(np.shape(rho))
    if epsT is None:
        epsT = np.zeros(np.shape(rho))
    if gamT is None:
        gamT = np.zeros(np.shape(rho))

    c33 = rho * vp ** 2
    c44 = rho * vs ** 2
    c11 = c33 * (2 * epsT + 1)
    c66 = c44 * (2 * gamT + 1)
    c13 = np.sqrt(2 * c33 * (c33 - c44) * delT + (c33 - c44) ** 2) - c44

    return c11, c13, c33, c44, c66


def conv_vti_cij2_thoms(rho, c11, c13, c33, c44, c66):
    vp = np.sqrt(c33 / rho)  # vertical P-wave velocity (m/s)
    vs = np.sqrt(c44 / rho)  # vertical S-wave velocity (m/s)
    delT = ((c13 + c44) ** 2 - (c33 - c44) ** 2) / (2 * c33 * (c33 - c44))
    epsT = (c11 - c33) / (2 * c33)
    gamT = (c66 - c44) / (2 * c44)

    return vp, vs, delT, epsT, gamT


def get_greek_param_vti(rho, c11, c13, c33, c44):

    alpha0sq = c33 / rho
    beta0sq = c44 / rho
    sigma0 = 1 - (c44 / c33)

    del0 = (c13 - c33 + 2 * c44) / c33
    eta0 = (c11 * c33 - (c13 + 2 * c44) ** 2) / (2 * c33 ** 2)

    return alpha0sq, beta0sq, sigma0, del0, eta0


def get_phase_vel(th, vp0, vs0, delT, epsT):

    # if input angle is 2D, convert elastic arrays to 2D
    if th.ndim == 2:

        # convert input 1D arrays to 2D
        nn = len(vp0)
        nangles = th.shape[1]
        vp0 = np.tile(vp0.reshape((nn, 1)), (1, nangles))
        vs0 = np.tile(vs0.reshape((nn, 1)), (1, nangles))
        delT = np.tile(delT.reshape((nn, 1)), (1, nangles))
        epsT = np.tile(epsT.reshape((nn, 1)), (1, nangles))

    f = 1 - (vs0 / vp0) ** 2
    temp = (
        1
        + (4 / f)
        * np.sin(th) ** 2
        * (2 * delT * np.cos(th) ** 2 - epsT * np.cos(2 * th))
        + 4 * (epsT / f) ** 2 * np.sin(th) ** 4
    )
    temp = 1 + epsT * np.sin(th) ** 2 - (f / 2) + (f / 2) * np.sqrt(temp)
    vp_ph = vp0 * np.sqrt(temp)

    return vp_ph


def get_layer_qd(p, alpha0sq, beta0sq, sigma0, del0, eta0):  # , opt)

    # ensure all input is treated as complex numbers
    p = p.astype(complex)
    alpha0sq = alpha0sq.astype(complex)
    beta0sq = beta0sq.astype(complex)
    sigma0 = sigma0.astype(complex)
    del0 = del0.astype(complex)
    eta0 = del0.astype(complex)

    # if input slowness is 2D, convert elastic arrays to 2D
    if p.ndim == 2:

        # convert input 1D arrays to 2D
        nn = len(alpha0sq)
        nslow = p.shape[1]
        alpha0sq, beta0sq, sigma0, del0, eta0
        alpha0sq = np.tile(alpha0sq.reshape((nn, 1)), (1, nslow))
        beta0sq = np.tile(beta0sq.reshape((nn, 1)), (1, nslow))
        sigma0 = np.tile(sigma0.reshape((nn, 1)), (1, nslow))
        del0 = np.tile(del0.reshape((nn, 1)), (1, nslow))
        eta0 = np.tile(eta0.reshape((nn, 1)), (1, nslow))

    # q parameters
    R1 = 2 * (1 - p ** 2 * beta0sq) * (del0 + 2 * p ** 2 * alpha0sq * eta0) ** 2
    R2 = (
        sigma0
        + 2 * p ** 2 * beta0sq * del0
        - 2 * p ** 2 * alpha0sq * (1 - 2 * p ** 2 * beta0sq) * eta0
    )
    R = R1 * (R2 + np.sqrt(R2 ** 2 + 2 * p ** 2 * beta0sq * R1)) ** -1

    # % if isequal(opt.type,'weak')
    # %     R=0;
    # % end

    Sa = 2 * del0 + 2 * p ** 2 * alpha0sq * eta0 + R
    Sb = 2 * (1 - p ** 2 * beta0sq) * (alpha0sq / beta0sq) * eta0 - R

    # % if isequal(opt.type,'iso')
    # %     Sa=0; Sb=0;
    # % end

    qa0sq = (1 / alpha0sq) - p ** 2
    qb0sq = (1 / beta0sq) - p ** 2

    tempa = qa0sq - p ** 2 * Sa
    tempb = qb0sq - p ** 2 * Sb
    qa = np.sqrt(tempa)
    qb = np.sqrt(tempb)

    # % qa=-qa;%real(qa)+1i*imag(qa);
    # % qb=-qb;

    # d parameters
    d2 = np.sqrt((sigma0 + del0) / (sigma0 + Sa))
    d3 = 2 * beta0sq * (sigma0 + 0.5 * (Sa + del0)) / (sigma0 + del0)
    d4 = np.sqrt(
        (sigma0 - p ** 2 * beta0sq * (sigma0 + Sb))
        / ((1 - p ** 2 * beta0sq * (1 + Sb)) * (sigma0 + del0))
    )
    d5 = (sigma0 - 2 * p ** 2 * beta0sq * (sigma0 + 0.5 * (Sb + del0))) / (
        sigma0 + del0
    )
    d1 = (p ** 2 * d3 + d5) ** -0.5

    return d1, d2, d3, d4, d5, qa, qb


def get_interface_rt_old(
    p,
    rho_1,
    qa_1,
    qb_1,
    d1_1,
    d2_1,
    d3_1,
    d4_1,
    d5_1,
    rho_2,
    qa_2,
    qb_2,
    d1_2,
    d2_2,
    d3_2,
    d4_2,
    d5_2,
):

    # make top and bottom arrays
    # qa_1, qb_1, d1_1, d2_1, d3_1, d4_1, d5_1 = qa[:-1,:], qb[:-1,:], d1[:-1,:], d2[:-1,:], d3[:-1,:], d4[:-1,:], d5[:-1,:]
    # qa_2, qb_2, d1_2, d2_2, d3_2, d4_2, d5_2 = qa[1:,:], qb[1:,:], d1[1:,:], d2[1:,:], d3[1:,:], d4[1:,:], d5[1:,:]

    # get density ratio, and convert to 2D matrix
    zeta = (rho_2 / rho_1) ** 0.5
    nslow = p.shape[1]
    zeta = np.tile(zeta.reshape((len(zeta), 1)), (1, nslow))

    # Final T and R Matrices
    temp = ((d2_1 * d4_1) ** 2 * qa_1 * qb_1 * (p ** 2 * d3_1 * zeta ** -1 + d5_2 * zeta) ** 2 \
        + (d2_2 * d4_2) ** 2 * qa_2 * qb_2 * (p ** 2 * d3_2 * zeta + d5_1 * zeta ** -1) ** 2 \
        + p ** 2 * (d2_1 * d2_2 * d4_1 * d4_2) ** 2 * qa_1 * qa_2 * qb_1 * qb_2 * (d3_1 * zeta ** -1 - d3_2 * zeta) ** 2 \
        + p ** 2 * (d5_1 * zeta ** -1 - d5_2 * zeta) ** 2)
        
    F = ((d2_2 * d4_1) ** 2 * qa_2 * qb_1 \
        + (d2_1 * d4_2) ** 2 * qa_1 * qb_2 \
        + (d1_1 * d1_2) ** 2 * temp)
        
    # reflection 

    # r_DPP
    temp = ((d2_1 * d4_1) ** 2 * qa_1 * qb_1 * (p ** 2 * d3_1 * zeta ** -1 + d5_2 * zeta) ** 2 \
        - (d2_2 * d4_2) ** 2 * qa_2 * qb_2 * (p ** 2 * d3_2 * zeta + d5_1 * zeta ** -1) ** 2 \
        + p ** 2 * (d2_1 * d2_2 * d4_1 * d4_2) ** 2 * qa_1 * qa_2 * qb_1 * qb_2 * (d3_1 * zeta ** -1 - d3_2 * zeta) ** 2 \
        - p ** 2 * (d5_1 * zeta ** -1 - d5_2 * zeta) ** 2)    
    r_DPP = (1 / F) * ((d2_2 * d4_1) ** 2 * qa_2 * qb_1 \
        - (d2_1 * d4_2) ** 2 * qa_1 * qb_2 \
        - (d1_1 * d1_2) ** 2 * temp)
    r_DPP = -r_DPP  # Don't know why I must change the polarity (??)
    
    # r_DSS
    temp = ((d2_1 * d4_1) ** 2 * qa_1 * qb_1 * (p ** 2 * d3_1 * zeta ** -1 + d5_2 * zeta) ** 2 \
        - (d2_2 * d4_2) ** 2 * qa_2 * qb_2 * (p ** 2 * d3_2 * zeta + d5_1 * zeta ** -1) ** 2 \
        + p ** 2 * (d2_1 * d2_2 * d4_1 * d4_2) ** 2 * qa_1 * qa_2 * qb_1 * qb_2 * (d3_1 * zeta ** -1 - d3_2 * zeta) ** 2 \
        - p ** 2 * (d5_1 * zeta ** -1 - d5_2 * zeta) ** 2)    
    r_DSS = (1 / F) * ((d2_2 * d4_1) ** 2 * qa_2 * qb_1 \
        - (d2_1 * d4_2) ** 2 * qa_1 * qb_2 \
        + (d1_1 * d1_2) ** 2 * temp)
    r_DSS = -r_DSS  # Don't know why I must change the polarity (??)    
    
    # r_DPS
    temp = (d2_2 * d4_2) ** 2 * qa_2 * qb_2 * (p ** 2 * d3_2 * zeta + d5_1 * zeta ** -1) * (d3_1 * zeta ** -1 - d3_2 * zeta) \
        + (p ** 2 * d3_1 * zeta ** -1 + d5_2 * zeta) * (d5_1 * zeta ** -1 - d5_2 * zeta)
    r_DPS = ((2 * p / F) * (d1_1 * d1_2) ** 2 * d2_1 * d4_1 * (qa_1 * qb_1) ** 0.5 * temp)
    r_DSP = r_DPS    
    
    
    

    # a = (d2_2 * d4_1) ** 2 * qa_2 * qb_1
    # b = (d2_1 * d4_2) ** 2 * qa_1 * qb_2
    # c = (d1_1 * d1_2) ** 2 * temp

    qa_1_sqroot = qa_1 ** 0.5
    qb_1_sqroot = qb_1 ** 0.5
    # qa_2_sqroot = qa_2 ** .5
    # qb_2_sqroot = qb_2 ** .5

    temp = (d2_2 * d4_2) ** 2 * qa_2 * qb_2 * (
        p ** 2 * d3_2 * zeta + d5_1 * zeta ** -1
    ) * (d3_1 * zeta ** -1 - d3_2 * zeta) + (
        p ** 2 * d3_1 * zeta ** -1 + d5_2 * zeta
    ) * (
        d5_1 * zeta ** -1 - d5_2 * zeta
    )
    r_DPS = (
        (2 * p / F)
        * (d1_1 * d1_2) ** 2
        * d2_1
        * d4_1
        * (qa_1_sqroot * qb_1_sqroot)
        * temp
    )
    r_DSP = r_DPS
    
    # t_DPP
    temp = d4_2 ** 2 * qb_2 * (p ** 2 * d3_2 * zeta + d5_1 * zeta ** -1) \
        + d4_1 ** 2 * qb_1 * (p ** 2 * d3_1 * zeta ** -1 + d5_2 * zeta)        
    t_DPP = (2 / F) * d1_1 * d1_2 * d2_1 * d2_2 * (qa_1 * qa_2) ** 0.5 * temp    

    out = {"r_DPP": r_DPP, "r_DPS": r_DPS, "r_DSP": r_DSP, "r_DSS": r_DSS, "t_DPP": t_DPP}
    return out

def get_interface_rt(
    p,
    rho_1,
    qa_1,
    qb_1,
    d1_1,
    d2_1,
    d3_1,
    d4_1,
    d5_1,
    rho_2,
    qa_2,
    qb_2,
    d1_2,
    d2_2,
    d3_2,
    d4_2,
    d5_2,
):
    
    # get density ratio, and convert to 2D matrix
    zeta = (rho_2 / rho_1) ** 0.5
    nslow = p.shape[1]
    zeta = np.tile(zeta.reshape((len(zeta), 1)), (1, nslow))    

    
    # C matrix
    c11 = (d2_2/d2_1) * (qa_2/qa_1)**0.5 * (p**2 * d3_2 * zeta + d5_1 * zeta**-1)
    c12 = (d2_1 * d4_2)**-1 * (qa_1 * qb_2)**-0.5 * p * (d5_1 * zeta**-1 - d5_2*zeta)
    c21 = (d2_2 * d4_1) * (qa_2 * qb_1)**0.5 * p * (d3_1 * zeta**-1 - d3_2*zeta)
    c22 = (d4_1/d4_2) * (qb_1/qb_2)**0.5 * (p**2 * d3_1 * zeta**-1 + d5_2 * zeta)
    
    c11 = d1_1 * d1_2 * c11
    c12 = d1_1 * d1_2 * c12
    c21 = d1_1 * d1_2 * c21
    c22 = d1_1 * d1_2 * c22
    
    det_C = c11*c22 - c21*c12
    
    # D matrix
    d11 = (1/det_C) * c22
    d12 = (1/det_C) * -c21
    d21 = (1/det_C) * -c12
    d22 = (1/det_C) * c11
    
    # make R_D matrix
    temp = (det_C**2 + 1 + c11**2 + c12**2 + c21**2 + c22**2)**-1   
    r_DPP = temp * (det_C**2 - 1 + c11**2 + c12**2 - c21**2 - c22**2)
    r_DPP = -r_DPP # must change sign, don't know why
    r_DSS = temp * (det_C**2 - 1 - c11**2 - c12**2 + c21**2 + c22**2)    
    r_DPS = temp * 2 * (c11*c21 + c12*c22)
    r_DSP = temp * 2 * (c11*c21 + c12*c22)
    
    # make T_D matrix
    t_DPP = 2 * temp * (c11 + c22 * det_C)
    
    # return output
    out = {"r_DPP": r_DPP, "r_DPS": r_DPS, "r_DSP": r_DSP, "r_DSS": r_DSS, "t_DPP": t_DPP}
    return out


def get_tr_rc_vti(vp, vs, rho, delT, epsT, gamT, th_deg):
    
    # get transmission and reflection coefficients for layered vti media

    # turn off some warnings
    np.seterr(divide="ignore", invalid="ignore")

    # set anisotorpy to zero if empty
    if len(delT) == 0:
        delT = 0 * vp
    if len(epsT) == 0:
        epsT = 0 * vp
    if len(gamT) == 0:
        gamT = 0 * vp

    # add small number to vs to avoid division by zero
    vs = vs + 1e-12

    # if input angles are 1D array, make 2D array
    nlayers = len(vp)
    if th_deg.ndim == 1:
        th_deg = np.tile(th_deg, (nlayers, 1))

    # convert angles to radians and ensure complex type
    th_rad = (np.pi / 180) * th_deg

    # get phase velocity as function of angle
    vp_ph = get_phase_vel(th_rad, vp, vs, delT, epsT)

    # slowness
    pp = np.sin(th_rad) / vp_ph

    # get Thomsen parameters
    c11, c13, c33, c44, c66 = conv_vti_thoms2cij(
        rho, vp, vs, delT=delT, epsT=epsT, gamT=gamT
    )

    # get additional parameters
    alpha0sq, beta0sq, sigma0, del0, eta0 = get_greek_param_vti(rho, c11, c13, c33, c44)

    # get slowness dependent parameters    
    d1_1, d2_1, d3_1, d4_1, d5_1, qa_1, qb_1 = get_layer_qd(
        pp[:-1, :], alpha0sq[:-1], beta0sq[:-1], sigma0[:-1], del0[:-1], eta0[:-1]
    )
    d1_2, d2_2, d3_2, d4_2, d5_2, qa_2, qb_2 = get_layer_qd(
        pp[:-1, :], alpha0sq[1:], beta0sq[1:], sigma0[1:], del0[1:], eta0[1:]
    )

    # get interface reflection and transmission coefficients
    ref = get_interface_rt(
        pp[:-1, :],
        rho[:-1],
        qa_1,
        qb_1,
        d1_1,
        d2_1,
        d3_1,
        d4_1,
        d5_1,
        rho[1:],
        qa_2,
        qb_2,
        d1_2,
        d2_2,
        d3_2,
        d4_2,
        d5_2,
    )
    
    # add NaN base layer (for consistent sizes)    
    vv = np.nan * np.ones((1, th_deg.shape[1]))
    for key in ref:            
        ref[key] = np.concatenate([ref[key], vv])       
    
    # turn back on warnings
    np.seterr(all="warn")    
    
    # return reflection/transmission coefficients
    return ref


def get_rpp_vti(vp, vs, rho, delT, epsT, gamT, th_deg, apply_tr_loss=False):
    
    # get PP reflection coefficients for layered vti media
    
    
    # get all reflection and transmission coefficients
    ref = get_tr_rc_vti(vp, vs, rho, delT, epsT, gamT, th_deg)

    
    # select downgoing PP ref. coef
    RC = ref["r_DPP"]
    
    # apply transmission loss
    if apply_tr_loss:
        
        print('WARNING: Transmission loss is not yet implemented for VTI media.')
        
        #R = ref["r_DPP"] # reflection coefficient
        #T = ref["t_DPP"] # transmission coefficient
        

    # add bottom layer (not used)
    RC = np.concatenate([RC, np.nan * np.ones((1, RC.shape[1]))])

    # turn back on warnings
    np.seterr(all="warn")

    # return result
    return RC

def get_ruger_par(vp, vs, rho, delT, epsT, gamT, p):
                  
    # get elastic parameters
    c11, c13, c33, c44, c66 = conv_vti_thoms2cij(rho, vp, vs, delT=delT, epsT=epsT, gamT=gamT) 
    
    # rename elastic parameters according to convention in Rüger
    c55 = c44
    
    # make a parameters
    a11, a13, a33, a55, a66 = c11/rho, c13/rho, c33/rho, c55/rho, c66/rho
    
    # make K parameters
    K1 = (rho/c33) + (rho/c55) - ((c11/c55) + (c55/c33) - ((c13 + c55)**2/(c33*c55)) ) * p**2
    K2 = (c11/c33)*p**2 - (rho/c33)
    K3 = p**2 - (rho/c55)
    
    # make q parameters
    qa = (1/np.sqrt(2)) * np.sqrt(K1 - np.sqrt(K1**2 - 4*K2*K3))
    qb = (1/np.sqrt(2)) * np.sqrt(K1 + np.sqrt(K1**2 - 4*K2*K3))
    
    # make l and m parameters        
    temp = a11*p**2 + a55*qa**2 - 1 + a33*qa**2 + a55*p**2 - 1
    la = ((a33*qa**2 + a55*p**2 - 1)/temp)**0.5        
    lb = ((a11*p**2 + a55*qb**2 - 1)/temp)**0.5
    ma = ((a11*p**2 + a55*qa**2 - 1)/temp)**0.5    
    mb = ((a11*qb**2 + a55*p**2 - 1)/temp)**0.5
        
    # return layer parameters    
    return a11, a13, a33, a55, a66, qa, qb, la, lb, ma, mb    
    

def get_rpp_vti_ruger(vp, vs, rho, delT, epsT, gamT, th_deg, apply_tr_loss=False):
        
    # Rüger 
    
    # get size of input
    nlayer = len(vp)
    nth = th_deg.shape[1]
    
    # initiate output
    r_dpp = np.zeros(th_deg.shape)
        
    # convert angles to radians 
    th_rad = (np.pi / 180) * th_deg

    # get phase velocity as function of angle
    vp_ph = get_phase_vel(th_rad, vp, vs, delT, epsT).astype(complex)

    # slowness
    pp = np.sin(th_rad) / vp_ph 
    
    print(pp)
    

    for ii in np.arange(nlayer-1): # loop over layers   
        for jj in np.arange(nth):   
            
            # single value slowness
            p = pp[ii,jj]
    
            # get values for upper layer
            a11_1, a13_1, a33_1, a55_1, a66_1, qa_1, qb_1, la_1, lb_1, ma_1, mb_1 = get_ruger_par(
                vp[ii], vs[ii], rho[ii], delT[ii], epsT[ii], gamT[ii], pp[ii,jj])
            
            # get values for lower layer
            a11_2, a13_2, a33_2, a55_2, a66_2, qa_2, qb_2, la_2, lb_2, ma_2, mb_2 = get_ruger_par(
                vp[ii+1], vs[ii+1], rho[ii+1], delT[ii+1], epsT[ii+1], gamT[ii+1], pp[ii,jj])
                            
            # elements of M matrix
            m11 = la_1
            m12 = mb_1
            m13 = -la_2
            m14 = -mb_2
            m31 = ma_1
            m32 = -lb_1
            m33 = ma_2
            m34 = -lb_2
            m21 = p * la_1 * a13_1 + qa_1 * ma_1 * a33_1
            m22 = p * mb_1 * a13_1 - qb_1 * lb_1 * a33_1
            m23 = -(p * la_2 * a13_2 + qa_2 * ma_2 * a33_2)
            m24 = -(p * mb_2 * a13_2 - qb_2 * lb_2 * a33_2)
            m41 = a55_1 * (qa_1 * la_1 + p * ma_1)
            m42 = a55_1 * (qb_1 * mb_1 - p * lb_1)
            m43 = a55_2 * (qa_2 * la_2 + p * ma_2)
            m44 = a55_2 * (qb_2 * mb_2 - p * lb_2)    
            
            # make linear system
            M = np.array([[m11, m12, m13, m14], [m21, m22, m23, m24], [m31, m32, m33, m34], [m41, m42, m43, m44]]).astype(complex)
            b = np.array([-m11, -m21, m31, m41]).astype(complex)
            
            print(M)
            print(b)
            
            # solve linear system
            x = np.linalg.solve(M, b)
            print('x')
            print(x)
            
            # assign solution
            r_dpp[ii,jj] = x[0]
            
            
            
    return r_dpp
    
    
    
    
    
    
    
    
    
    






















