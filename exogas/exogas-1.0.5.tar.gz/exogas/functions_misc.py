### miscelaneous functions
import numpy as np
from exogas.constants import *


def M_to_L(Mstar): # stellar mass to stellar L MS

    if hasattr(Mstar,"__len__"):
        L=np.zeros(Mstar.shape[0])
        L[Mstar<0.43]=0.23*Mstar[Mstar<0.43]**2.3
        mask2= ((Mstar>=0.43))# & (M<2)).
        L[mask2]=Mstar[mask2]**4.
        mask3= (Mstar>=2.) & (Mstar<20.)
        L[mask3]=1.4*Mstar[mask3]**3.5
        L[Mstar>55.]=3.2e4*Mstar[Mstar>55.]
        
        
    else:
        L=0.0
        if Mstar<0.45:
            L=0.23*Mstar**2.3
        elif Mstar<2.:
            L=Mstar**4.
        elif Mstar<20.:
            L=1.4*Mstar**3.5
        else:
            L=3.2e4*Mstar

    return L


def power_law_dist(xmin, xmax,alpha, N):

    if alpha==-1.0: raise ValueError('power law index cannot take a value of -1')
    u=np.random.uniform(0.0, 1.0,N)
    beta=1.0+alpha
    return ( (xmax**beta-xmin**beta)*u +xmin**beta  )**(1./beta)
    

def tau_vis(r, alpha, cs, Mstar):
    # r in au
    # cs in m/s
    # Mstar in Msun
    
    Omega=np.sqrt(G*Mstar*Msun/((r*au_m)**3.0)) # s
    return (r*au_m)**2.0*Omega/(alpha*cs**2.)/year_s #/3.0

def radial_grid_powerlaw(rmin, rmax, Nr, alpha):

    u=np.linspace(rmin**alpha, rmax**alpha, Nr+1) # Nr+1
    rhalfs=u**(1./alpha) # Nr+1
    hs=rhalfs[1:]-rhalfs[:-1] # Nr
    rs=0.5*(rhalfs[1:] + rhalfs[:-1])
    return rs, rhalfs, hs



def N_optim_radial_grid(rmin, rmax, rb, res):

    Nr=10
    f=0
    while True:
        rs, rhalfs, hs = radial_grid_powerlaw(rmin, rmax, Nr, 0.5)  #0.5)
        for i in range(1,Nr):
            if rs[i]>rb:
                dr=rs[i]-rs[i-1]
                break
        if hs[i-1]/rs[i-1]<res:
            break
        else:
            Nr=int(Nr*1.2)
    return Nr


def tau_CO_matrix(Sigma_CO, Sigma_C1, log10tau_interp, fion=0.): # interpolate calculations based on photon counting

    tau=np.ones(Sigma_CO.shape[0])*130. # unshielded
    # to avoid nans we use a floor value for sigmas of 1e-50
    Sigma_COp=Sigma_CO*1. 
    Sigma_C1p=Sigma_C1*1.*(1.-fion)
    Sigma_COp[Sigma_COp<1.0e-50]=1.0e-50
    Sigma_C1p[Sigma_C1p<1.0e-50]=1.0e-50

  
    tau=10**(log10tau_interp(np.log10(Sigma_C1p),np.log10(Sigma_COp), grid=False)) # yr, it must be called with C1 first because of column and raws definition. Tested with jupyter notebook and also here https://github.com/scipy/scipy/issues/3164
    return tau # yr


def f_alpha_R(T):
    # CII, ionized carbon, z=6 and N=5 (remaining electrons)
    # from Badnell+2006 2006ApJS..167..334B
    A=2.5e-9
    B=0.7849
    C=0.1597
    T0=6.67e-3
    T1=1.943e6
    T2=4.955e4
    Bp=B+C*np.exp( -T2/T)
    return A*( np.sqrt(T/T0) * (1.+(T/T0)**0.5)**(1.-Bp) * (1.+(T/T1)**0.5)**(1.+Bp))**(-1.) # units of cm3 s-1



############## COLLISIONS

def f_Dbl(Mstar=1.0, Lstar=1.0, rho=2700.0):

    return 0.8*(Lstar/Mstar)*(2700.0/rho)


def f_tc_simple(Mtot, r, dr, Dc=10.0, e=0.05, Qd=150.0, Mstar=1.0): # collisional timescale of largest planetesimal

    return 1.4e-3 * r**(13.0/3) * (dr/r) * Dc * Qd**(5./6.) *e**(-5.0/3.0) * Mstar**(-4.0/3.0)*Mtot**(-1.0) # in yr

def f_G(q,Xc):

    return (Xc**(5.-3*q)-1. ) + (6.*q-10.)*(3.*q-4.)**(-1.)*(Xc**(4.-3.*q) -1. ) + (3.*q-5.)*(3.*q-3.)**(-1.)*(Xc**(3.-3.*q)-1. )

def f_Xc(Qd, r, Mstar, e, I):

    return 1.3e-3*(Qd * r / (Mstar*(1.25*e**2. + I**2.)))**(1./3.)

def f_tc_Xc(Mtot, r, dr, rho=2700.0, Dc=10.0, e=0.05, I=0.05, Qd=150.0, Mstar=1.0, q=11./6.): # collisional timescale of largest planetesimal
    A=(3.8 * rho * r**2.5 * dr * Dc  )/(Mstar**0.5 * Mtot) # yr (error in Eq 9 Wyatt, Smith, Su, Rieke, Greaves et al. 2007, equation is in years)
    B= ( (12.*q - 20.)*( 1.+1.25*(e/I)**2.0 )**(-0.5) )/((18.-9.*q)*f_G(q, f_Xc(Qd, r, Mstar, e, I)))
    return A*B # yr
    

def Mtot_t(Mtot0, t, r, dr,  rho=2700.0, Dc=10.0, e=0.05, I=0.05, Qd=150.0, Mstar=1.0, q=11./6.):
    # t in years
    tc0=f_tc_Xc(Mtot0, r, dr, rho, Dc, e, I, Qd, Mstar, q=q)
    if hasattr(tc0, "__len__"):
        for i in range(len(tc0)):
            if tc0[i]<0.0:
                tc0[i]=f_tc_simple(Mtot0[i], r[i], dr[i],  Dc, e, Qd, Mstar[i])
    else:
        if tc0<0.0:
            tc0=f_tc_simple(Mtot0, r, dr,  Dc, e, Qd, Mstar)
        
    return Mtot0/(1.0+t/tc0) 

def Mtot_t_simple(Mtot0, t, r, dr,  rho=2700.0, Dc=10.0, e=0.05, I=0.05, Qd=150.0, Mstar=1.0, q=11./6.):
    # t in years
    tc0=f_tc_simple(Mtot0, r, dr,  Dc, e, Qd, Mstar)

    return Mtot0/(1.0+t/tc0) 

def Mtotdot_t(Mtot0, t, r, dr, rho=2700.0,  Dc=10.0, e=0.05, I=0.05, Qd=150.0, Mstar=1.0, q=11./6.):
    # t in years
    tc0=f_tc_Xc(Mtot0, r, dr, rho,  Dc, e, I, Qd, Mstar, q=q)

    if hasattr(tc0, "__len__"):
        for i in range(len(tc0)):
            if tc0[i]<0.0:
                tc0[i]=f_tc_simple(Mtot0[i], r[i], dr[i],  Dc, e, Qd, Mstar[i])
    else:
        if tc0<0.0:
            tc0=f_tc_simple(Mtot0, r, dr,  Dc, e, Qd, Mstar)
   
    return Mtot0/(1.0+t/tc0)**2. / tc0 # Mearth/yr



### MISCELLANEOUS

def sci_notation(number, sig_fig=2): # stolen from https://stackoverflow.com/questions/53553377/python-scientific-notation-with-superscript-exponent
    ret_string = "{0:.{1:d}e}".format(number, sig_fig)
    a,b = ret_string.split("e")
    b = int(b)         # removed leading "+" and strips leading zeros too.
    
    # check exponent
    if b==0: 
        c=''
    else: c="x$10^{%i}$"%b
    
    # check digit
    if a=='1':
        if c=='':
            return '1'
        else:
            return c[1:]
    else: 
        return a + c
