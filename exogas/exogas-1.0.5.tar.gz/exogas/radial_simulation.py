import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from scipy import interpolate
import sys, os
from tqdm import tqdm

from exogas.constants import *
from exogas.functions_misc import *

class radial_simulation:
    """
    A class used to simulate the evolution of gas in debris discs considering CO gas release, viscous evolution, diffusion, CO photodissociation and carbon capture by dust. 

    ...

    Attributes
    ----------
    Mstar : float
        Stellar mass in units of solar masses
    Lstar : float
        Stellar luminosity in units of solar luminosity
    rmin : float
        minimum radius in the simulation grid
    rmax0 : float
        minimum maximum radius in the simulation grid in au. The actual maximum radius is calculated based on the viscosity, belt radius and length of the simulation 
    resolution: float
        ratio between the width and radius of radial bins (it is constant along the grid)
    rbelt : float
        center of the planetesimal belt, in au 
    width : float
        FWHM of the belt. The belt has a Gaussian profile.
    fir: float
        fractional luminosity of the disc at the end of the simulation.
    fco: float
        fraction of CO in planetesimals.
    alpha: float
        alpha viscosity parameter.
    fion: float
        fraction of carbon atoms that are ionised (uniform across the disc).
    mu0: float
        initial mean molecular weight.
    mus: 1d numpy array
        mean molecular weights as a function of radius.
    Sigma_floor: float
        floor value of the surface density in Mearth/au**2 at the start of the simulation at rc.
    rc: float
        cut-off radius of the initial surface density in au.
    ts_out: numpy array 
        epochs that we want to obtain.
    dt0: float
        maximum timestep in yr.
    Tb: float
        temperature at the belt center in K.
    cs_b: float
        sounds speed at the belt center in m/s.
    tvis: float
        viscous timescale at the belt center in yr. 
    grid: sub-class
        class containing the radial grid parameters.
    Ts: 1d numpy array
        Temperature array in K
    cs: 1d numpy array
        sounds speeds in m/s.
    Omegas: 1d numpy array
        Keplerian frequencies in 1/yr.
    Omegas_s: 1d numpy array
        Keplerian frequencies in 1/s.
    nus: 1d numpy array
        viscosity in units of m**2/s.
    nus_au2_yr: 1d numpy array
        viscosity in units of au**2/yr.
    dt: float
        timestep used to evolve the system.
    Nt: int
        total number of steps.
    ts_sim: 1d numpy array
        array of Nt simulated epochs.
    MdotCO: float
        CO input rate in units of Mearth/yr.
    fir: 1d numpy array
        array of fractional luminosities as a function of time.
    ts_sim: 1d numpy array
        array of Nt simulated epochs.
    log10tau_interp: function
        function that returns the CO photodissociation timescale.
    diffusion: boolean
        whether or not include radial diffusion.
    photodissociation: boolean
        whether or not to include CO photodissociation.
    carbon_capture: boolean
        whether or not to include carbon capture.
    pcapture: float
        probability that a dust grain will capture a carbon grain after a collision
    co_reformation: boolean, optional
        whether or not to include CO reformation
    preform: float, optional
        probability of CO reforming from captured carbon 
    Sigma0: 2d numpy array (2, Nr)
        Initial surface density
    ts: 1d numpy array
        array of exact output epochs (differ by dt with respect ts_out)
    Sigma_g: Nd numpy array (2, Nr, Nt2)
        array containing the surface density of CO and C as a function of radius and time
    mixed: boolean, optional
             whether CO and carbon are vertically mixed or not.

    Methods
    -------
    Sigma_next(Sigma_prev, MdotCO, fir)
        evolves the surface density by one timestep and returns the evolved surface density array (2xNr)

    Sigma_dot_vis(Sigmas)
        returns dSigma/dt and the radial velocity of the gas due to viscous evolution.

    Diffusion(Sigmas)
        returns dSigma/dt due to diffusion

    Sig_dot_p_Gauss(MdotCO)
        returns dSigma/dt due to CO release from planetesimals

    viscous_evolution()
        evolves the system and computes Sigma_g from t=0 to t=tf 

    R_c_capture(fir)
        returns  the rate at which one carbon atom is captured by dust grains

    """

    def __init__(self, Mstar=None, Lstar=None, rmin=None, resolution=None, rmax0=None, rbelt=None, width=None, fir=None, fco=None, alpha=None, fion=None, mu0=None, Sigma_floor=None, rc=None,  ts_out=None, dt0=None, verbose=True, viscous=True, diffusion=True, photodissociation=True, carbon_capture=False, pcapture=None, MdotCO=None, tcoll=None, co_reformation=False,  preform=None, mixed=False):
        """
        Parameters
        ----------
        Mstar : float, optional
             Stellar mass in units of solar masses
        Lstar : float, optional
             Stellar luminosity in units of solar luminosity
        rmin : float, optional
             minimum radius in the simulation grid
        rmax0 : float, optional
             minimum maximum radius in the simulation grid in au. The actual maximum radius is calculated based on the viscosity, belt radius and length of the simulation 
        resolution: float, optional
             ratio between the width and radius of the radial bin centered at the belt (the resolution increases with radius).
        rbelt : float, optional
             center of the planetesimal belt, in au 
        width : float, optional
             FWHM of the belt. The belt has a Gaussian profile.
        fir: float, optional
             fractional luminosity of the disc0 (value at the end of the simulation if fir decays with time).
        fco: float, optional
             fraction of CO in planetesimals.
        alpha: float, optional
             alpha viscosity parameter.
        fion: float, optional
             fraction of carbon atoms that are ionised (uniform across the disc).
        mu0: float, optional
             initial mean molecular weight.
        Sigma_floor: float
             floor value of the surface density in Mearth/au**2 at the start of the simulation at rc.
        rc: float, optional
             cut-off radius of the initial surface density in au.
        tf: float, optional
             simulation final time in yr.
        dt0: float, optional
             maximum timestep in yr.
        verbose: boolean, optional
             whether to print or not some values.
        diffusion: boolean, optional
             whether or not include radial diffusion.
        photodissociation: boolean, optional
             whether or not to include CO photodissociation.
        carbon_capture: boolean, optional
             whether or not to include carbon capture.
        pcapture: float, optional
             probability that a dust grain will capture a carbon grain after a collision
        co_reformation: boolean, optional
             whether or not to include CO reformation
        preform: float, optional
             probability of CO reforming from captured carbon    
        MdotCO: float, optional
             CO input rate in units of Mearth/yr. This is taken as constant if tcoll<0, or the value at t=tf if tcoll>0.
        tcoll: float, optional
             collisional timescale at t=0 in yr.
        mixed: boolean, optional
             whether CO and carbon are vertically mixed or not.
        Raises
        ------
        ValueError
            If the photodissociation timescale tables are not found in the working directory
        """
        
        ################################
        ### default parameters
        ################################

        # system
        default_Mstar=2.0 # Msun
        default_rmin=1.0  # au
        default_resolution=0.1
        default_rmax0=3.0e3 # au
        
        ## belt parameters
        default_rbelt=100.0 # au 
        default_width=default_rbelt*0.5  # au, FWHM
        default_sig_belt=default_width/(2.0*np.sqrt(2.*np.log(2.)))
        default_fir=1.0e-3 # fractional luminosity
        default_tcoll=-1.
        
        ## gas parameters
        default_fco=0.1
        default_alpha=1.0e-3
        default_fion=0.0
        default_mu0=14.0
        default_Sigma_floor=1.0e-50 # Mearth/au2
        default_rc=50. # au

        ##  simulation parameters
        default_tf=1.0e7 # yr
        default_dt0=60. # yr (maximum dt)
        default_Ntout=11
        default_ts_out=np.linspace(0., default_tf, default_Ntout)

        default_pcapture=1.
        default_preform=1.
        
        ### system
        self.Mstar=Mstar if Mstar is not None else default_Mstar
        self.Lstar=Lstar if Lstar is not None else M_to_L(self.Mstar)
        self.rmin=rmin if rmin is not None and rmin>0. else default_rmin
        
        if rmax0 is not None and rmax0>self.rmin:
            self.rmax0=rmax0 
        else:
            if default_rmax0> self.rmin:
                self.rmax0=default_rmax0
            else:
                raise ValueError('rmin>rmax')
    
        self.resolution=resolution if resolution is not None else default_resolution
        
        #### belt
        self.rbelt=rbelt if rbelt is not None else default_rbelt
        self.width=width if width is not None else self.rbelt*0.5
        self.sig_belt=self.width/(2.0*np.sqrt(2.*np.log(2.)))
        self.fir=fir if fir is not None else default_fir

        if self.resolution>self.width/self.rbelt/5.:
            print('Changing resolution to resolve belt width with 5 bins')
            self.resolution=self.width/self.rbelt/5.

        try: 
            if tcoll>0.:
                self.tcoll=tcoll
            else: self.tcoll=default_tcoll
        except:
            self.tcoll=default_tcoll
        #### gas parameters
        self.fco=fco if fco is not None else default_fco
        self.alpha=alpha if alpha is not None else default_alpha
        self.fion=fion if fion is not None else default_fion
        self.mu0=mu0 if mu0 is not None else default_mu0
        self.Sigma_floor=Sigma_floor if Sigma_floor is not None else default_Sigma_floor
        self.rc=rc if rc is not None else default_rc

        ### output epochs
        if isinstance(ts_out, np.ndarray):
            if (ts_out >= 0.).all() and np.all(ts_out[1:] >= ts_out[:-1]) and ts_out[-1]<2.0e10:
                self.ts_out=ts_out
            else:
                sys.exit('ts_out contains some negative epochs or it is not monotonically increasing or tf is longer than the age of the universe')
        else:
            self.ts_out=default_ts_out
        self.Nt2=self.ts_out.shape[0]
        self.tf=self.ts_out[-1]
        self.dt0=dt0 if dt0 is not None else default_dt0
        
        ################################
        #### calculate basic properties of the simulation
        ################################


        #### switches
        self.viscous=viscous
        self.diffusion=diffusion
        self.photodissociation=photodissociation
        self.carbon_capture=carbon_capture
        if self.carbon_capture:
            self.pcapture=pcapture if (pcapture is not None and (pcapture<=1. and pcapture>=0.)) else default_pcapture
        self.co_reformation=co_reformation
        if self.co_reformation:
            self.preform=preform if (preform is not None and (preform<=1. and preform>=0.)) else default_preform
        self.mixed=mixed
        
        #### temperature and viscosity at the belt center
        self.Tb=278.3*(self.Lstar**0.25)*self.rbelt**(-0.5) # K # Temperature at belt
        self.cs_b=np.sqrt(kb*self.Tb/(self.mu0*mp)) # m/s sounds speed at belt
        self.tvis=tau_vis(self.rbelt, self.alpha, self.cs_b, self.Mstar)

        #### spatial grid
        if self.tcoll>0.:
            rmax=max(self.rmax0, 3.0 * self.rbelt*(1.0+self.tf/self.tvis))# when Mdot becomes very small, the maximum radius is very important as it sets the evolution timescale.
        else:
            rmax=self.rmax0
        Nr=N_optim_radial_grid(self.rmin, rmax, self.rbelt, self.resolution)
        self.grid = radial_grid(rmin=self.rmin, rmax=rmax, Nr=Nr, p=0.5) 
        for ir in range(Nr):
            if self.grid.rs[ir]>self.rbelt:
                self.ibelt=ir
                break
        
        #### temporal grid
        self.Ts=278.3*(self.Lstar**0.25)*self.grid.rs**(-0.5) # K
        self.cs=np.sqrt(kb*self.Ts/(self.mu0*mp))
        self.Omegas=2.0*np.pi*np.sqrt(self.Mstar/(self.grid.rs**3.0)) # 1/yr
        self.Omegas_s=self.Omegas/year_s
        self.mus=np.ones(self.grid.Nr)*self.mu0
        self.nus=self.alpha*kb*self.Ts/(self.mus*mp)/(self.Omegas_s) # m2/s 1.0e13*np.ones(Nr) #
        self.nus_au2_yr=self.nus*year_s/(au_m**2.0)

        
        if self.photodissociation and self.viscous:
            self.dt=min(0.02*self.grid.hs[0]**2./self.nus_au2_yr[0], self.dt0) # yr
        elif self.viscous:
            self.dt=0.02*self.grid.hs[0]**2./self.nus_au2_yr[0]
        else:
            self.dt=self.dt0
            

        if self.ts_out[0]==0.:
            i_epoch=1
        else: i_epoch=0
        if ts_out[i_epoch]<=self.dt:
            #sys.exit('1st output epoch >0 and shorter than simulation timestep = %1.1e yr'%(self.dt))
            print('1st or 2nd output epoch is shorter than default simulation timestep of %1.1e yr'%(self.dt))
            print('lowering the timestep to %1.1e yr'%ts_out[i_epoch])
            self.dt=ts_out[i_epoch]

        self.Nt=int(self.tf/self.dt)+1
        self.ts_sim=np.linspace(0.0, self.tf, self.Nt)
        
        #### CO input rate
        if MdotCO==None: # calculate Mdot CO based on fir
            if self.tcoll<0.:
                print('fixed CO input rate based on constant fractional luminosity')
                MdotCO_fixed= self.fco* 1.2e-3 * self.rbelt**1.5 / self.width  * self.fir**2. * self.Lstar * self.Mstar**(-0.5) # Mearth/ yr
                self.MdotCO=MdotCO_fixed*np.ones(self.Nt)
                self.fir=self.fir*np.ones(self.Nt)
            else:
                print('varying CO input rate based on final fractional luminosity and tcoll given by the user')
                MdotCO_final= self.fco* 1.2e-3 * self.rbelt**1.5 / self.width  * self.fir**2. * self.Lstar * self.Mstar**(-0.5) # Mearth/ yr
                self.MdotCO=MdotCO_final*(1.+self.tf/self.tcoll)**2./(1.+self.ts_sim/self.tcoll)**2.
                self.fir=self.fir*(1.+self.tf/self.tcoll)/(1.+self.ts_sim/self.tcoll)

        elif MdotCO>0.: 
            if self.tcoll<0.:
                print('fixed CO input rate based on Mdot given by the user')
                self.MdotCO=np.ones(self.Nt)*MdotCO
                self.fir=self.fir*np.ones(self.Nt)

            else:
                print('varying CO input rate based on final Mdot and tcoll given by the user')
                self.MdotCO=MdotCO*(1.+self.tf/self.tcoll)**2./(1.+self.ts_sim/self.tcoll)**2.
                self.fir=self.fir*(1.+self.tf/self.tcoll)/(1.+self.ts_sim/self.tcoll)

        else:
            raise ValueError('input MdotCO must be a float greater than zero')


        ##########################################
        ### Grid of CO photodissociation timescales calculated using photon counting (a la Cataldi et al. 2020)
        ##########################################

        dir_path = os.path.dirname(os.path.realpath(__file__))+'/photodissociation/'
        SCO_grid=np.loadtxt(dir_path+'Sigma_CO_Mearth_au2.txt')
        SC1_grid=np.loadtxt(dir_path+'Sigma_C1_Mearth_au2.txt')
        if self.mixed:
            tauCO_grid=np.loadtxt(dir_path+'tau_CO_yr_mixed.txt')
        else:
            tauCO_grid=np.loadtxt(dir_path+'tau_CO_yr_layered.txt')

        self.log10tau_interp=interpolate.RectBivariateSpline( np.log10(SC1_grid),np.log10(SCO_grid), np.log10(tauCO_grid)) # x and y must be swaped, i.e. (y,x) https://github.com/scipy/scipy/issues/3164
                
       
        
        self.verbose=verbose                           
        if self.verbose:
            print('Rmin = %1.1f au'%(self.grid.rmin))
            print('Rmax = %1.1f au'%(self.grid.rmax))
            print('Nr = %i'%(self.grid.Nr))
            print('Nt simulation=%i'%self.Nt)
            print('simulation timestep = %1.1f yr'%self.dt)
            print('viscous timescale to cross one radial bin = %1.1f yr'%(self.grid.hs[0]**2./self.nus_au2_yr[0]))
            print('tvis = %1.1e yr'%self.tvis)
            print('Mdot CO at t=0 is %1.1e Mearth/yr'%(self.MdotCO[0]))
            print('Mdot CO at t=tf is %1.1e Mearth/yr'%(self.MdotCO[-1]))

        #### initial condition
        self.Sigma0=np.zeros((2, Nr))
        self.Sigma0[:,:]=self.Sigma_floor*(self.grid.rs/self.rc)**(-1.)*np.exp(-(self.grid.rs/self.rc))


    ##############################################
    ################ METHODS ###################
    ##############################################


    #### function to advance one step
    def Sigma_next(self, Sigma_prev, MdotCO, fir):
    
        ###########################################
        ################ viscous evolution
        ###########################################
        if self.viscous:
            Sdot_vis, Sigma_vr_halfs=self.Sigma_dot_vis(Sigma_prev)
            Snext= Sigma_prev + self.dt*Sdot_vis # viscous evolution

        else:
            Snext=Sigma_prev*1.
        ###########################################
        ############### inner boundary condition
        ###########################################

        #if np.all(Snext[:,2])>0.0:
        #    Snext[:,0]=np.minimum(Snext[:,1]*(nus_au2_yr[1]/nus_au2_yr[0]), Snext[:,1]*(rs[0]/rs[1])**(np.log(Snext[:,2]/Snext[:,1])/np.log(rs[2]/rs[1])))
        #else: 
        Snext[:,0]=Snext[:,1]*(self.nus_au2_yr[1]/self.nus_au2_yr[0]) # constant Mdot
    
        ###########################################
        ############# Outer boundary condition (power law or constant mass)
        ###########################################

        if np.all(Snext[:,-3])>0.0: # minimum between power law and constant Mdot
            Snext[:,-1]=np.minimum(Snext[:,-2]*(self.nus_au2_yr[-2]/self.nus_au2_yr[-1]), Snext[:,-2]*(self.grid.rs[-1]/self.grid.rs[-2])**(np.log(Snext[:,-2]/Snext[:,-3])/np.log(self.grid.rs[-2]/self.grid.rs[-3])))
        else: 
            Snext[:,-1]=Snext[:,-2]*(self.nus_au2_yr[-2]/self.nus_au2_yr[-1])

        ###########################################
        ################ diffusion evolution (this has to come after photodissociation and input rate, otherwise we get weird strong wiggles that diverge resulting in nans)
        ###########################################
        if self.diffusion:
            Snext=Snext+self.dt*self.Diffusion(Snext)

        ###########################################
        ############### CO mas input rate
        ###########################################
        Snext[0,:]=Snext[0,:]+self.dt*self.Sig_dot_p_Gauss(MdotCO)
        Snext[1,:]=Snext[1,:]*1.
            
        ###########################################
        ############## photodissociation
        ###########################################
        if self.photodissociation:
            
            # if self.mixed:
            #     tphCO=tau_CO_photon_counting(Sigma_prev[0,:], Sigma_prev[1,:], self.log10tau_interp, fion=self.fion)
            # else:
            #     tphCO=tau_CO_carbon_layer(Sigma_prev[0,:], Sigma_prev[1,:], self.log10tau_interp, fion=self.fion)
            tphCO=tau_CO_matrix(Sigma_prev[0,:], Sigma_prev[1,:], self.log10tau_interp, fion=self.fion)
            Sdot_ph=Sigma_prev[0,:]/tphCO
            Snext[0,:]=Snext[0,:]-self.dt*Sdot_ph
            Snext[1,:]=Snext[1,:]+self.dt*Sdot_ph*muc1co
            #Snext2[0,Snext2[0,:]<0.0]=0.0


        ###########################################
        ############## carbon capture
        ###########################################

        if self.carbon_capture:
            Snext[1,:]=Snext[1,:]-self.dt*Snext[1,:]*self.R_c_capture(fir)*self.pcapture

            if self.co_reformation:
                Snext[0,:]=Snext[0,:]+self.dt*Snext[1,:]*self.R_c_capture(fir)*self.pcapture*self.preform*28./12.

    
        Snext[Snext[:,:]<0.0]=0.0
        
        return Snext


    def Sigma_dot_vis(self, Sigmas):
  
        ########## CALCULATE VR*Sigma=F1
        
        Sigma_tot=Sigmas[0,:]+Sigmas[1,:]*(1.+4./3.) # CO+C+O
        eps=np.ones((2,self.grid.Nr))*0.5
        mask_m=Sigma_tot>0.0
        eps[0,mask_m]=Sigmas[0,mask_m]/Sigma_tot[mask_m]
        eps[1,mask_m]=Sigmas[1,mask_m]/Sigma_tot[mask_m]
    

        G1s=Sigma_tot*self.nus_au2_yr*np.sqrt(self.grid.rs) # Nr
        Sigma_vr_halfs=-3.0*(G1s[1:]-G1s[:-1])/(self.grid.rs[1:]-self.grid.rs[:-1])/np.sqrt(self.grid.rhalfs[1:-1]) # Nr-1
        
        ############## CALCULATE dSIGMA/dT
        eps_halfs=np.zeros((2,self.grid.Nr-1))
        eps_halfs[:,:]=np.where(Sigma_vr_halfs[:]>0.0, eps[:,:-1], eps[:,1:])
    
        G2s=self.grid.rhalfs[1:-1]*Sigma_vr_halfs  # Nr-1
        G3s=G2s*eps_halfs    #  2x(Nr-1)
        Sdot=np.zeros((2,self.grid.Nr))
        Sdot[:,1:-1]=-(G3s[:,1:]-G3s[:,:-1])*2./(self.grid.rhalfs[2:-1]**2.-self.grid.rhalfs[1:-2]**2.) # Nr-2

        return Sdot, Sigma_vr_halfs


    def Diffusion(self,Sigmas):

        Sigma_tot=Sigmas[0,:]+Sigmas[1,:]*(28./12.) # CO+C+O
        eps=np.ones((2,self.grid.Nr))*0.5
        mask_m=Sigma_tot>0.
        eps[0,mask_m]=Sigmas[0,mask_m]/Sigma_tot[mask_m]
        eps[1,mask_m]=Sigmas[1,mask_m]/Sigma_tot[mask_m]

        # # geometric average
        eps_half=np.sqrt(eps[:,1:]*eps[:,:-1]) # Nr-1 at cell boundaries
        eps_dot=(eps_half[:,1:]-eps_half[:,:-1])/(self.grid.hs[1:-1]) # Nr-2 at cell centers

        F=self.grid.rs[1:-1]*self.nus_au2_yr[1:-1]*Sigma_tot[1:-1]*eps_dot # Nr-2
        
        Sdot_diff=np.zeros((2,self.grid.Nr))    
        Sdot_diff[:,1:-2]= (F[:,1:]-F[:,:-1])/(self.grid.rs[2:-1]-self.grid.rs[1:-2])/(self.grid.rs[1:-2]) # Nr-3
    
        return Sdot_diff

    def Sig_dot_p_Gauss(self, MdotCO):
        
        mask_belt=((self.grid.rs<self.rbelt+self.width) & (self.grid.rs>self.rbelt-self.width))
        Sdot_comets=np.zeros(self.grid.Nr)
        Sdot_comets[mask_belt]=np.exp( -0.5* 2* (self.grid.rs[mask_belt]-self.rbelt)**2.0 / (self.sig_belt**2.) ) # factor 2 inside exponential is to make Mdot prop to Sigma**2
        #Sdot_comets[mask_belt]=np.exp( - (self.grid.rs[mask_belt]-self.rbelt)**2.0 / (2.*self.sig_belt**2.) ) # factor 2 inside exponential is to make Mdot prop to Sigma**2 

        Sdot_comets[mask_belt]=MdotCO*Sdot_comets[mask_belt]/(2.*np.pi*np.sum(Sdot_comets[mask_belt]*self.grid.rs[mask_belt]*self.grid.hs[mask_belt]))

        return Sdot_comets

    def viscous_evolution(self):
        ### function to evolve the disc until self.tf


        self.ts=np.zeros(self.Nt2)
        self.Sigma_g=np.zeros((2,self.grid.Nr,self.Nt2))
    
        if self.ts_out[0]==0.:
            self.Sigma_g[:,:,0]=self.Sigma0
            self.ts[0]=0.
            j=1
        else:  j=0
    
            
        Sigma_temp=self.Sigma0*1.0

        for i in tqdm(range(1,self.Nt)):
            mask_m=np.sum(Sigma_temp, axis=0)>0.0
            self.mus[mask_m]=(Sigma_temp[0,mask_m]+Sigma_temp[1,mask_m]*(1.+16./12.))/(Sigma_temp[0,mask_m]/28.+Sigma_temp[1,mask_m]/6.) # Sigma+Oxigen/(N)
    
            Sigma_temp=self.Sigma_next(Sigma_temp, self.MdotCO[i], self.fir[i])
            
            if self.ts_sim[i]>=self.ts_out[j]:
                self.Sigma_g[:,:,j]=Sigma_temp*1.
                self.ts[j]=self.ts_sim[i]
                j+=1
        print('simulation finished')
        # return Sigma_g, ts2


    def R_c_capture(self, fir):

        return self.Omegas * self.grid.rs * fir / (self.sig_belt *np.sqrt(np.pi*2.)) * np.exp(-0.5 * (self.grid.rs-self.rbelt)**2./ (self.sig_belt**2.)) # 1/yr

    def plot_panels(self, ts_plot=None, cmap='magma', rmax_mtot=None):

        vmin=0.1
        vmax=0.8
        # font size and style
        font= {'family':'Times New Roman', 'size': 10}
        rc('font', **font)

        if ts_plot is None:
            ts_plot=np.logspace(3, int(np.log10(self.tf)), int(np.log10(self.tf))-3+1)

        ### critical surface densities
        sigma_C1c=2*(1./sigma_c1)*m_c1/Mearth*au_cm**2.0 # mearth/au2
        sigma_COc=2*(1./sigma_co)*m_co/Mearth*au_cm**2.0 # mearth/au2


        fig=plt.figure(figsize=(12,3))

        ax1=fig.add_subplot(131)
        ax2=fig.add_subplot(132)
        ax3=fig.add_subplot(133)

        if rmax_mtot==None: rmax_mtot=self.grid.rmax 
        mask_mtot=self.grid.rs<=rmax_mtot
        MCOs=np.sum(self.Sigma_g[0,mask_mtot,:].T*self.grid.hs[mask_mtot]*self.grid.rs[mask_mtot]*2.0*np.pi, axis=1)
        MC1s=np.sum(self.Sigma_g[1,mask_mtot,:].T*self.grid.hs[mask_mtot]*self.grid.rs[mask_mtot]*2.0*np.pi, axis=1)

        #### plottingg surface densities
        for i, ti in enumerate(ts_plot):
            it=0
            ### find epoch in time grid
            for k in range(len(self.ts)):
                if self.ts[k]>=ti:
                    it=k
                    break

            cmap=plt.get_cmap(cmap)
            x=vmin+(vmax-vmin)*i*1./(len(ts_plot)-1)
            colori=cmap(x)

            time_str=sci_notation(ts_plot[i]/1.0e6, sig_fig=0)+' Myr'

            ax1.plot(self.grid.rs, self.Sigma_g[0,:,it], color=colori, label=time_str)
            ax2.plot(self.grid.rs, self.Sigma_g[1,:,it]*(1.0-self.fion), color=colori)

        ### draw critical surface densities
        ax1.axhline(sigma_COc, color='grey', ls='dashed')
        ax2.axhline(sigma_C1c, color='grey', ls='dashed')

        # maximum and minimum surface densities to plot
        ymax=max( np.max(self.Sigma_g[0,:,:]), np.max(self.Sigma_g[1,:,:]), sigma_C1c)*2.0
        ymin=min( self.Sigma_g[0,self.ibelt,it], sigma_COc)/100.0

        for axi in [ax1, ax2]:
            axi.set_xlim(1.0, 3.0e3)
            axi.set_ylim(ymin, ymax)
            axi.set_xscale('log')
            axi.set_yscale('log')
            axi.set_xlabel('Radius [au]')
        ax1.legend(frameon=True, loc=3)
        ax1.set_ylabel(r'CO Surface density [$M_{\oplus}$ au$^{-2}$]')
        ax2.set_ylabel(r'CI Surface density [$M_{\oplus}$ au$^{-2}$]')

        #### plotting masses

        ax3.plot(self.ts/1.0e6, MCOs, color='C0', label='CO')
        ax3.plot(self.ts/1.0e6, MC1s*(1.0-self.fion), color='C1', label='CI')

        MCO_st=self.MdotCO*130.0 # solution in quasy steady state if CO is unshielded. Note that self.dotCO is larger than self.ts because it does not skip any epochs. Its corresponding time array is self.ts_sim
        MC1_st=self.MdotCO*m_c1/m_co * (2.*self.rbelt / (3.*self.nus_au2_yr[0]*(1./self.grid.rs[0])))*(1.+2.*(rmax_mtot/self.rbelt)**0.5-1.0) # From integrating Metzeger equations
        ax3.plot(self.ts_sim/1.0e6, MCO_st, color='C0', ls='dashed')
        ax3.plot(self.ts_sim/1.0e6, MC1_st, color='C1', ls='dashed')
        ax3.set_ylabel(r'Gas mass [$M_{\oplus}$]')
        ax3.set_xlabel(r'Time [Myr]')
        ax3.set_xscale('log')
        ax3.set_yscale('log')
        ax3.set_xlim(ts_plot[0]/1.0e6, ts_plot[-1]/1.0e6)
        ax3.set_ylim(1.0e-8, 1.0e6)
        ax3.legend(frameon=True, loc=2)
        fig.tight_layout()

        return fig



    
            
class radial_grid:
    """
    A class used to represent the radial grid of a simulation


    Attributes
    ----------
    rmin : float
        minimum radius in au
    rmax : float
        maximum radius
    Nr : int
        number of radial bins
    p : float
        power law index to define radial grid spacing.
    rhalfs : 1d numpy array
        array containing the Nr+1 edges of the radial bins
    hs : 1d numpy array
        array containing the Nr widths of the radial bins
    rs : 1d numpy array
        array containing the Nr centers of the radial bins

    """
    
    default_rmin=1.0   # au
    default_rmax=3.0e3 # au
    default_Nr=100
    default_p=0.5
    
    def __init__(self, rmin=None, rmax=None, Nr=None, p=None):
        self.rmin=rmin if rmin is not None else default_rmin
        self.rmax=rmax if rmax is not None else default_rmax
        self.Nr=Nr if Nr is not None else default_Nr
        self.p=p if p is not None else default_p


        u=np.linspace(self.rmin**p, self.rmax**p, self.Nr+1) # Nr+1
        self.rhalfs=u**(1./p) # Nr+1
        self.hs=self.rhalfs[1:]-self.rhalfs[:-1] # Nr
        self.rs=0.5*(self.rhalfs[1:] + self.rhalfs[:-1])



    
