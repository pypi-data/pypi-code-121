import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import matplotlib
from scipy import interpolate
import sys,os
from tqdm import tqdm

from exogas.constants import *
from exogas.functions_misc import *


class vertical_simulation:

    def __init__(self, Mstar=None, Lstar=None, Nz=None, zmax_to_H=None, T=None, rbelt=None, width=None, MdotCO=None,  alphar=None, alphav=None, mu0=None,ts_out=None, dt0=None, verbose=True, viscous=True, diffusion=True, photodissociation=True, ionization=True, Ntheta=None, fir=None, fco=None, tcoll=None): #Ntout=None


        # fco=None, fir=None, fion=None, mu0=None, Sigma_floor=None, rc=None,  tf=None, dt0=None, verbose=True, dt_skip=10, diffusion=True, photodissociation=True, carbon_capture=False, pcapture=None, MdotCO=None, tcoll=None, co_reformation=False,  preform=None, mixed=True):
      
        
        ################################
        ### default parameters
        ################################

        # system
        default_Mstar=2.0 # Msun
        default_Nz=25
        default_zmax_to_H=5. # Zmax/H
        
        ## belt parameters
        default_rbelt=100.0 # au 
        default_width=default_rbelt*0.5  # au, FWHM
        default_sig_belt=default_width/(2.0*np.sqrt(2.*np.log(2.)))
        default_MdotCO=1.0e-7 # Mearth/yr
        default_fir=1.0e-3 # fractional luminosity
        default_tcoll=-1.
        
        
        ## gas parameters
        default_alphar=1.0e-3
        default_alphav=1.0e-3
        default_fco=0.1
        default_mu0=14.0
        
        ##  simulation parameters
        default_tf=1.0e6 # yr
        default_dt0=20. # yr (maximum dt)
        default_Ntout=11
        default_ts_out=np.linspace(0., default_tf, default_Ntout)

        default_Ntheta=10
        # default_pcapture=1.
        # default_preform=1.
        
        ### system
        self.Mstar=Mstar if Mstar is not None else default_Mstar
        self.Lstar=Lstar if Lstar is not None else M_to_L(self.Mstar)
        self.Nz=Nz if Nz is not None and Nz>0 else default_Nz
        self.zmax_to_H=zmax_to_H if zmax_to_H is not None and zmax_to_H>0 else default_zmax_to_H
        
    
        #### belt
        self.rbelt=rbelt if rbelt is not None else default_rbelt
        self.width=width if width is not None else self.rbelt*0.5
        self.sig_belt=self.width/(2.0*np.sqrt(2.*np.log(2.)))
        self.fir=fir if fir is not None else default_fir
        try: 
            if tcoll>0.:
                self.tcoll=tcoll
            else: self.tcoll=default_tcoll
        except:
            self.tcoll=default_tcoll


            
        #### gas parameters
        self.fco=fco if fco is not None else default_fco
        self.alphar=alphar if alphar is not None else default_alphar
        self.alphav=alphav if alphav is not None else default_alphav
        self.mu0=mu0 if mu0 is not None else default_mu0

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

        self.viscous=viscous
        self.diffusion=diffusion
        self.photodissociation=photodissociation
        self.ionization=ionization

        
        #### temperature and viscosity at the belt center
        if T==None or T<=0.0:
            self.Tb=278.3*(self.Lstar**0.25)*self.rbelt**(-0.5) # K # Temperature at belt
        else: self.Tb=T
        self.cs=np.sqrt(kb*self.Tb/(self.mu0*mp)) # m/s sounds speed at belt
        self.Omega=2.0*np.pi*np.sqrt(self.Mstar/(self.rbelt**3.0)) # 1/yr
        self.Omega_s=self.Omega/year_s
        self.H=self.cs/self.Omega_s/au_m # au
        self.nur=self.alphar*kb*self.Tb/(self.mu0*mp)/(self.Omega_s) # m2/s 1.0e13*np.ones(Nr) #
        self.nur_au2_yr=self.nur*year_s/(au_m**2.0)
        self.nuv=self.alphav*kb*self.Tb/(self.mu0*mp)/(self.Omega_s) # m2/s 1.0e13*np.ones(Nr) #
        self.nuv_au2_yr=self.nuv*year_s/(au_m**2.0)

        ## viscous timescales
        self.tvisr=self.rbelt**2./self.nur_au2_yr
        self.tvisv=self.H**2./self.nuv_au2_yr

        
        #### spatial grid
        self.zmax=self.zmax_to_H*self.H # au
        self.zs=np.linspace(0., self.zmax, self.Nz)
        self.dz=(self.zs[1]-self.zs[0])
        self.Ntheta=int(Ntheta) if Ntheta is not None and Ntheta>1 else default_Ntheta
        self.thetas=np.linspace(0., np.pi/2.-1.0e-3, self.Ntheta)
        
        #### temporal grid
        if (self.photodissociation or self.ionization):
            if self.diffusion:
                self.dt=min(0.1*self.tvisv, self.dt0) # yr
            else:
                self.dt=self.dt0
        elif self.diffusion:
            self.dt=0.1*self.tvisv
        elif self.viscous:
            self.dt=0.02*self.tvisr
        else:   
            self.dt=self.dt0

        if self.ts_out[0]==0.:
            i_epoch=1
        else: i_epoch=0

        if self.ts_out[i_epoch]<=self.dt:
            #sys.exit('1st output epoch >0 and shorter than simulation timestep = %1.1e yr'%(self.dt))
            print('1st or 2nd output epoch is shorter than default simulation timestep of %1.1e yr'%(self.dt))
            print('lowering the timestep to %1.1e yr'%ts_out[i_epoch])
            self.dt=self.ts_out[i_epoch]


        self.Nt=int(self.tf/self.dt)+1
        self.ts_sim=np.linspace(0.0, self.tf, self.Nt)
        
        # this is to calculate numerically a factor used to calculate the gas input rate
        Nr=10000
        rs=np.linspace(1.0e-11, self.rbelt+self.width*3, Nr)
        dr=rs[1]-rs[0]
        Sdot_comets=np.zeros(Nr)
        Sdot_comets=np.exp( -0.5* 2* (rs-self.rbelt)**2.0 / (self.sig_belt**2.) ) # factor 2 inside exponential is to make Mdot prop to Sigma**2
        #Sdot_comets[mask_belt]=np.exp( - (self.grid.rs[mask_belt]-self.rbelt)**2.0 / (2.*self.sig_belt**2.) ) # factor 2 inside exponential is to make Mdot prop to Sigma**2 
        Sdot_comets=Sdot_comets/(2.*np.pi*np.sum(Sdot_comets*rs*dr)) # normalized to 1
        for ir in range(Nr):
            if rs[ir]>self.rbelt:
                ibelt=ir
                break
        self.geometry_belt=Sdot_comets[ibelt] * np.exp(-0.5* (self.zs/self.H)**2.)/(np.sqrt(2.*np.pi)*self.H) 

        # # this is to calculate numerically a factor used to calculate the gas input rate
        # self.geometry_belt=1./(np.sqrt(2.*np.pi)*(self.sig_belt/np.sqrt(2.))*2.*np.pi*self.rbelt) * np.exp(-0.5* (self.zs/self.H)**2.)/(np.sqrt(2.*np.pi)*self.H)  # factor sqrt(2) dividing sig_belt is to make Mdot prop to Sigma**2 

        
        dir_path = os.path.dirname(os.path.realpath(__file__))+'/photodissociation/'

        table_selfshielding=np.loadtxt(dir_path+'self-shielding.dat')
        self.logfCO = interpolate.interp1d(np.log10(table_selfshielding[0,:]), np.log10(table_selfshielding[1,:]))
        self.minNCO=table_selfshielding[0,0]
        self.maxNCO=table_selfshielding[0,-1]
        

        
         #### CO input rate
        if MdotCO==None: # calculate Mdot CO based on fir
            if self.tcoll<0.:
                print('fixed CO input rate based on constant fractional luminosity')
                MdotCO_fixed= self.fco* 1.2e-3 * self.rbelt**1.5 / self.width  * self.fir**2. * self.Lstar * self.Mstar**(-0.5) # Mearth/ yr
                self.MdotCO=MdotCO_fixed*np.ones(self.Nt)
                self.fir=self.fir*np.ones(self.Nt) # needed if carbon capture is implemented and we need to keep track of fir vs t
            else:
                print('varying CO input rate based on final fractional luminosity and tcoll given by the user')
                MdotCO_final= self.fco* 1.2e-3 * self.rbelt**1.5 / self.width  * self.fir**2. * self.Lstar * self.Mstar**(-0.5) # Mearth/ yr
                self.MdotCO=MdotCO_final*(1.+self.tf/self.tcoll)**2./(1.+self.ts_sim/self.tcoll)**2.
                self.fir=self.fir*(1.+self.tf/self.tcoll)/(1.+self.ts_sim/self.tcoll)

        elif MdotCO>0.: 
            if self.tcoll<0.:
                print('fixed CO input rate based on Mdot given by the user')
                self.MdotCO=np.ones(self.Nt)*MdotCO
                self.fir=self.fir*np.ones(self.Nt)  # needed if carbon capture is implemented and we need to keep track of fir vs t

            else:
                print('varying CO input rate based on final Mdot and tcoll given by the user')
                self.MdotCO=MdotCO*(1.+self.tf/self.tcoll)**2./(1.+self.ts_sim/self.tcoll)**2.
                self.fir=self.fir*(1.+self.tf/self.tcoll)/(1.+self.ts_sim/self.tcoll)
        else:
            raise ValueError('input MdotCO must be a float greater than zero')


        ### expected surface density


        self.rho_dot=self.MdotCO[0]*self.geometry_belt
        self.rho_eq_unshielded = self.rho_dot * 130.
        
        # /(2.*np.pi*self.rbelt*np.sqrt(2.*np.pi)*self.sig_belt)
        # self.rho_eq_unshielded=self.Sigma_dot*130./(np.sqrt(2.*np.pi)*self.H)

        
        
        # self.Sigma_eq=self.MdotCO[0]*/(3.*np.pi*self.nur_au2_yr)
        # self.rho_eq_midplane=self.Sigma_eq/(np.sqrt(2.*np.pi)*self.H)
        # self.Sigma_dot=self.MdotCO[0]/(2.*np.pi*self.rbelt*np.sqrt(2.*np.pi)*self.sig_belt)
        # self.rho_eq_unshielded=self.Sigma_dot*130./(np.sqrt(2.*np.pi)*self.H)

        ######## initial condition
        self.rhos0=np.zeros((3, self.Nz)) 
        self.rhotot=np.zeros(self.Nz)
        self.rhotot= self.rho_eq_unshielded * np.exp( - 0.5* (self.zs/self.H)**2 )
        self.rhos0[1,:]=self.rhotot*1.0e-10
        self.rhos0[0,:]=self.rhotot*1.0e-10# -self.rhos0[1,:]*28./12

        self.verbose=verbose                           
        if self.verbose:
            print('Zmax = %1.1f au'%(self.zmax))
            print('Nz = %i'%(self.Nz))
            print('Nt simulation=%i'%self.Nt)
            print('simulation timestep = %1.1f yr'%self.dt)
            # print('vertical diffusion timescale to cross one vertical bin = %1.1e yr'%(self.dz**2./self.nuv_au2_yr))
            print('t_diffusion = %1.1e yr'%self.tvisv)
            print('t_vis = %1.1e yr'%self.tvisr)
            print('MdotCO at t=0 is %1.1e Mearth/yr'%(self.MdotCO[0]))
            print('MdotCO at t=%1.1e is %1.1e Mearth/yr'%(self.ts_sim[-1], self.MdotCO[-1]))
            print('SigmadotCO at t=%1.1e is %1.1e Mearth/yr/au2'%(self.ts_sim[-1], Sdot_comets[ibelt]*self.MdotCO[-1]))
            print('T = %1.1f K'%(self.Tb))
    ##############################################
    ################ METHODS ###################
    ##############################################



    def Diffusion(self, rho_temp):
        # assume 0 index is midplane and -1 index is at Zmax
    
        rhosp1=np.concatenate([rho_temp[:,1][:,None],rho_temp], axis=1) # copies 2nd cell (just above the midplane) and puts it just below the midplane to extend vertical grid

    
        rho_tot=rhosp1[0,:]+(rhosp1[1,:]+rhosp1[2,:])*(28./12.) # CO+CI+CII+O, N+1
        eps=np.ones((3,self.Nz+1))
        mask_m=rho_tot>0.

        eps[0,mask_m]=rhosp1[0,mask_m]/rho_tot[mask_m]
        eps[1,mask_m]=rhosp1[1,mask_m]/rho_tot[mask_m]
        eps[2,mask_m]=rhosp1[2,mask_m]/rho_tot[mask_m]
    
        eps_dot_half=(eps[:,1:]-eps[:,:-1])/(self.dz) # Nz at cell boundaries # first derivative
    
        rho_tot_half=(rho_tot[1:]+rho_tot[:-1])/2. # Nz at cell boundaries
    
        F_half=(self.nuv_au2_yr*rho_tot_half*eps_dot_half) # Nz at cell boundaries
        
        rhodot_diff=np.zeros((3,self.Nz))    
        rhodot_diff[:,:-1]= (F_half[:,1:]-F_half[:,:-1])/(self.dz) # Nz-1 # 2nd derivative
    
        return rhodot_diff

    def viscous_tau(self):

        return 2./3. * self.rbelt * np.sqrt(2.*np.pi)*(self.sig_belt/np.sqrt(2.)) / self.nur_au2_yr  # yr derived from steady-state condition from Metzger+2012. Factor 1/sqrt(2) comes from the fact that release rate is prop to sigma**2
    
    def Viscous_eovlution(self, rho_temp, t):

        return rho_temp/self.viscous_tau()

    def Gas_input(self, MdotCO):
        
        # Mdot in earth masses / yr
        return MdotCO*self.geometry_belt


    def Photodissociation_CO(self,rho_temp):
    

        if self.Ntheta>1:
            # integrate over 4pi assuming density is constant with z
            R_top    = np.trapz(np.sin(self.thetas)*self.shielding_CO(self.NCOs_top[:,None]/np.cos(self.thetas), self.NCIs_top[:,None]/np.cos(self.thetas)), self.thetas , axis=1)
            R_bottom = np.trapz(np.sin(self.thetas)*self.shielding_CO(self.NCOs_bottom[:,None]/np.cos(self.thetas), self.NCIs_bottom[:,None]/np.cos(self.thetas)), self.thetas , axis=1)
            return (R_top+R_bottom)*rho_temp[0,:]/260.
        else:

            return (self.shielding_CO(self.NCOs_top, self.NCIs_top)  + self.shielding_CO(self.NCOs_bottom, self.NCIs_bottom))*rho_temp[0,:]/260. # Mearth/yr

        
    def shielding_CO(self, NCO, NCI):

        # CI shielding
        kcI=np.exp(-NCI*sigma_c1)
        
        ## CO self-shielding
        if self.Ntheta>1:
            kco=np.ones((self.Nz, self.Ntheta)).flatten()
            NCOflat=NCO.flatten()
            mask1=(NCOflat>=self.minNCO) & (NCOflat<=self.maxNCO)
            kco[ mask1]=10.0**self.logfCO(np.log10(NCOflat[mask1]))
            mask2=( NCOflat<self.minNCO)
            kco[mask2]=1.0
            mask3=(NCOflat>self.maxNCO)
            kco[mask3]=0.0
            kco.reshape( (self.Nz, self.Ntheta)  )

            return kco.reshape( (self.Nz, self.Ntheta)  )*kcI 

        else:
            kco=np.ones(self.Nz)
            mask1=(NCO>=self.minNCO) & (NCO<=self.maxNCO)
            kco[ mask1]=10.0**self.logfCO(np.log10(NCO[mask1]))
            mask2=( NCO<self.minNCO)
            kco[mask2]=1.0
            mask3=(NCO>self.maxNCO)
            kco[mask3]=0.0

            return kco*kcI 

    def R_ion(self, rho_temp):
        t_ion=1.0040e2 # yr # calculated a priori (consistent with Rollins+2012)

        if self.Ntheta>1.:
            R_top= np.trapz(np.sin(self.thetas)* np.exp(- self.NCIs_top[:,None]*sigma_c1/np.cos(self.thetas)), self.thetas , axis=1)
            R_bottom=np.trapz(np.sin(self.thetas)* np.exp(- self.NCIs_bottom[:,None]*sigma_c1/np.cos(self.thetas)), self.thetas , axis=1)
        else:
            R_top    = np.exp(-self.NCIs_top*sigma_c1)
            R_bottom = np.exp(-self.NCIs_bottom*sigma_c1)

            
        return (R_top+R_bottom)/(2*t_ion)

    def R_recomb(self, rho_temp):
        # alpha in units of # units of cm3 s-1
        # alpha*ne. ne=ncII.
        
        return f_alpha_R(self.Tb) * (rho_temp[2,:]*Mearth/au_cm**3./(12.*mp))*year_s  # year-1, alpha * ncII

    def update_column_densities(self, rho_temp):

        NCO_tot=2*np.trapz(rho_temp[0,:], self.zs)*Mearth/au_cm**2./(28.*mp)
        NCI_tot=2*np.trapz(rho_temp[1,:], self.zs)*Mearth/au_cm**2./(12.*mp)
        # self.NCOs_top=np.cumsum(rho_temp[0,::-1])[::-1]*self.dz*Mearth/au_cm**2./(28.*mp)
        # self.NCIs_top=np.cumsum(rho_temp[1,::-1])[::-1]*self.dz*Mearth/au_cm**2./(12.*mp)
        # self.NCOs_bottom=NCO_tot-self.NCOs_top
        # self.NCIs_bottom=NCI_tot-self.NCIs_top

        ### modification to not include the column density contained in cell
        self.NCOs_top=np.roll( np.cumsum(rho_temp[0,::-1])[::-1]*self.dz*Mearth/au_cm**2./(28.*mp), -1) # roll by one to have column density on top
        self.NCIs_top=np.roll( np.cumsum(rho_temp[1,::-1])[::-1]*self.dz*Mearth/au_cm**2./(12.*mp), -1) # roll by one to have column density on top

        self.NCOs_top[-1]=0.
        self.NCIs_top[-1]=0.
        
        self.NCOs_bottom=NCO_tot-self.NCOs_top - rho_temp[0,:]*self.dz*Mearth/au_cm**2./(28.*mp)
        self.NCIs_bottom=NCI_tot-self.NCIs_top - rho_temp[1,:]*self.dz*Mearth/au_cm**2./(12.*mp)
        
    def vertical_evolution(self):
        ### function to evolve the disc until self.tf

    
        self.ts=np.zeros(self.Nt2)
        self.rhos=np.zeros((3, self.Nz,self.Nt2 ))
        if self.ts_out[0]==0.:
            self.rhos[:,:,0]=self.rhos0
            self.ts[0]=0.
            j=1
        else:  j=0

        rho_temp=self.rhos0*1.0
        self.update_column_densities(rho_temp)

        for i in tqdm(range(1,self.Nt)):


            ### update column densities
            self.update_column_densities(rho_temp)
            
            # time step
            rho_temp=self.Rho_next(rho_temp, self.MdotCO[i], self.ts_sim[i])
            if self.ts_sim[i]>=self.ts_out[j]:
                self.ts[j]=self.ts_sim[i]
                self.rhos[:,:,j]=rho_temp*1.
                j+=1
            
        print('simulation finished')




    def Rho_next(self, rho_temp, MdotCO,t):

        ###########################################
        ################ viscous evolution
        ###########################################
        if self.viscous:
            rho_next=rho_temp - self.dt*self.Viscous_eovlution(rho_temp,t)
        else:
            rho_next=rho_temp*1.
        ###########################################
        ############### CO mas input rate
        ###########################################
        rho_next[0,:]=rho_next[0,:] + self.dt*self.Gas_input(MdotCO)
        ###########################################
        ################ diffusion evolution 
        ###########################################
        if self.diffusion:
            rho_next=rho_next+self.dt*self.Diffusion(rho_next)
        ###########################################
        ############## photodissociation
        ###########################################
        if self.photodissociation:
            R_photodissociation=self.Photodissociation_CO(rho_temp)
            rho_next[0,:]=rho_next[0,:]-self.dt*R_photodissociation
            rho_next[1,:]=rho_next[1,:]+12./28.*self.dt*R_photodissociation

        ###########################################
        ############## photodissociation
        ###########################################
        if self.ionization:
            r_ionization=rho_temp[1,:]*self.R_ion(rho_temp)
            r_recomb=rho_temp[2,:]*self.R_recomb(rho_temp)
            rho_next[1,:]=rho_next[1,:]+self.dt*(r_recomb-r_ionization)
            rho_next[2,:]=rho_next[2,:]-self.dt*(r_recomb-r_ionization)

        return rho_next
        
    def plot_panels(self, ts_plot=None, cmap='magma'):

        # font size and style
        font= {'family':'Times New Roman', 'size': 10}
        rc('font', **font)

        cmap=plt.get_cmap('magma')
        vmin=0.1
        vmax=0.8
        Ntplot=len(ts_plot)
        major_ticks_x=np.arange(0., 10.0, 2.0)
        minor_ticks_x=np.arange(0., 10.0, 0.5)

        if ts_plot is None:
            ts_plot=np.logspace(3, int(np.log10(self.tf)), int(np.log10(self.tf))-3+1)

        fig=plt.figure(figsize=(8,5.))
        ax1=fig.add_subplot(231)
        ax2=fig.add_subplot(232)
        ax3=fig.add_subplot(233)
        ax4=fig.add_subplot(234)

        gs = fig.add_gridspec(2,3)
        ax5=fig.add_subplot(gs[1, 1:])


        for it, ti in enumerate(ts_plot):

            ## find right epoch
            for j in range(self.Nt2):
                if self.ts[j]>=ti:
                    break
            # plot the right epoch
            x=vmin+(vmax-vmin)*it/(Ntplot-1.)
            colori=cmap(x)
            time_str=sci_notation(ts_plot[it]/1.0e6, sig_fig=0)+' Myr'

            ax1.plot(self.zs/self.H, self.rhos[0,:,j], color=colori, label=time_str)
            ax2.plot(self.zs/self.H, self.rhos[1,:,j], color=colori)
            ax3.plot(self.zs/self.H, self.rhos[2,:,j], color=colori)

    
        ax1.plot(self.zs/self.H,self.rho_eq_unshielded, ls='--', color='grey')

        NCOs=np.cumsum(self.rhos[0,::-1,-1])[::-1]*self.dz*Mearth/au_cm**2/(28.*mp)
        NCIs=np.cumsum(self.rhos[1,::-1,-1])[::-1]*self.dz*Mearth/au_cm**2/(12.*mp)
        NCIIs=np.cumsum(self.rhos[2,::-1,-1])[::-1]*self.dz*Mearth/au_cm**2/(12.*mp)

        ax4.axhline(NCO_midplane/2., color='C0', ls=':')
        ax4.axhline(NCI_midplane/2., color='C1', ls=':')

        ax4.plot(self.zs[:]/self.H,NCOs, color='C0', label='CO')
        ax4.plot(self.zs[:]/self.H,NCIs, color='C1', label='CI')
        ax4.plot(self.zs[:]/self.H,NCIIs, color='C3', label='CII')


        Sigmas=2*np.sum(self.rhos[:,1:,:]*self.dz, axis=1)+self.rhos[:,0,:]*self.dz # N emisphere + midplane 

        ax5.plot(self.ts/1.0e6, Sigmas[0,:], color='C0', label='CO' )
        ax5.plot(self.ts/1.0e6, Sigmas[1,:], color='C1', label='CI')
        ax5.plot(self.ts/1.0e6, Sigmas[2,:], color='C3', label='CII')


        axs=[ax1,ax2,ax3, ax4]
        for i, axi in enumerate(axs):
            axi.set_xticks(major_ticks_x)                                                       
            axi.set_xticks(minor_ticks_x, minor=True)
            axi.set_xlim(0, self.zmax/self.H)
            if axi!=ax4: axi.set_ylim(0.,)
            axi.set_xlabel(r'$z/H$')

        ax1.set_ylabel(r'Gas density [$M_{\oplus}$ au$^{-3}$]')
        ax4.set_ylabel(r'Column density above z [cm$^{-2}$]')
        ax5.set_ylabel(r'Suface density [$M_{\oplus}$ au$^{-2}$]')
        ax5.set_xlabel('Time [Myr]')
        ax5.set_xlim(self.ts[0]/1.0e6, self.ts[-1]/1.0e6)

        for axi in axs[:-1]:
            axi.ticklabel_format(scilimits=(0,0))
        ax4.set_yscale('log')    
        ax5.set_xscale('log')    
        ax5.set_yscale('log')    
    
        locmaj = matplotlib.ticker.LogLocator(base=10,numticks=8) 
        locmin = matplotlib.ticker.LogLocator(base=10.0,subs=np.arange(2, 10) * .1,numticks=100) # subs=(0.2,0.4,0.6,0.8)
        ax4.yaxis.set_major_locator(locmaj)
        ax4.yaxis.set_minor_locator(locmin)
        locmaj = matplotlib.ticker.LogLocator(base=10,numticks=8) 
        locmin = matplotlib.ticker.LogLocator(base=10.0,subs=np.arange(2, 10) * .1,numticks=100) # subs=(0.2,0.4,0.6,0.8)
        ax5.yaxis.set_major_locator(locmaj)
        ax5.yaxis.set_minor_locator(locmin)


        ax1.set_title('CO')
        ax2.set_title('CI')
        ax3.set_title('CII')
        # ax4.set_title('Column densities')

        ax1.legend(loc=1, frameon=False, ncol=1, fontsize=8)
        ax4.legend(loc=3, frameon=False, ncol=1, fontsize=8)
        ax5.legend(loc=2, frameon=False, ncol=1, fontsize=8)
        ax5.yaxis.set_label_position("right")
        ax5.yaxis.tick_right()
        ax5.tick_params(which='both', left=True)

        plt.tight_layout()

        return fig

        


