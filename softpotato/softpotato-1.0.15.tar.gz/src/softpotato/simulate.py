import numpy as np
from scipy.sparse import diags

'''
    Pending:
    - Add C mechanism
    - Calculate concentration of P on the EC and C mechanisms

    Errors:
    - Denormalization of concentrations is wrong
'''

F = 96485 # C/mol, Faraday constant    
R = 8.315 # J/mol K, Gas constant
T = 298 # K, Temperature
FRT = F/(R*T)

class E:
    '''
        Defines an E species
    '''
    def __init__(self, n=1, DO=1e-5, DR=1e-5, cOb=0, cRb=1e-6, E0=0, ks=1e8, 
                 alpha=0.5):
        self.n = n
        self.DO = DO
        self.DR = DR
        self.DOR = DO/DR
        self.cOb = cOb
        self.cRb = cRb
        self.E0 = E0
        self.ks = ks
        self.alpha = alpha


class C:
    '''
        Defines a C species  
    '''
    def __init__(self, DP=1e-5, cPb=0, kc=1e-2):
        self.DP = DP
        self.cPb = cPb
        self.kc = kc
        #self.Kc = 0


class TGrid:
    '''
        Defines the grid in time
    '''
    def __init__(self, twf, Ewf):
        self.t = twf
        self.E = Ewf
        self.nT = np.size(self.t) # number of time elements
        self.dT = 1/self.nT # adimensional step time
        self.T = twf/twf[-1] # adimensional time

        
class XGrid:
    '''
        Defines the grid in space
    '''
    def __init__(self, species, tgrid, Ageo=1):
        self.lamb = 0.45 # For the algorithm to be stable, lamb = dT/dX^2 < 0.5
        self.Xmax = 6*np.sqrt(tgrid.nT*self.lamb) # Infinite distance
        self.dX = np.sqrt(tgrid.dT/self.lamb) # distance increment
        self.nX = int(self.Xmax/self.dX) # number of distance elements
        self.X = np.linspace(0, self.Xmax, self.nX) # Discretisation of distance
        self.Ageo = Ageo

        for x in species:
            if isinstance(x, E):
                ## Discretisation of variables and initialisation
                if x.cRb == 0: # In case only O present in solution
                    x.CR = np.zeros([tgrid.nT, self.nX])
                    x.CO = np.ones([tgrid.nT, self.nX])
                else:
                    x.CR = np.ones([tgrid.nT, self.nX])
                    x.CO = np.ones([tgrid.nT, self.nX])*x.cOb/x.cRb

                x.eps = (tgrid.E-x.E0)*x.n*FRT # adimensional potential waveform
                x.delta = np.sqrt(x.DR*tgrid.t[-1]) # cm, diffusion layer thickness
                x.Ke = x.ks*x.delta/x.DR # Normalised standard rate constant
                # Construct matrix:
                Cb = np.ones(self.nX-1) # Cbefore
                Cp = -2*np.ones(self.nX) # Cpresent
                Ca = np.ones(self.nX-1) # Cafter
                x.A = diags([Cb,Cp,Ca], [-1,0,1]).toarray()/(self.dX**2) 
                x.A[0,:] = np.zeros(self.nX)
                x.A[0,0] = 1 # Initial condition
            elif isinstance(x, C):
                x.CP = np.zeros([tgrid.nT, self.nX])


class Simulate:
    '''
    '''
    def __init__(self, species, mech, tgrid, xgrid):
        self.species = species
        self.mech = mech
        self.tgrid = tgrid
        self.xgrid = xgrid

        self.join(species)

    def sim(self):
        nE = self.nE[0]
        nC = self.nC[0]
        sE = self.species[nE]
        sC = self.species[nC]
        for k in range(1, self.tgrid.nT):
            # Boundary condition, Butler-Volmer:
            CR1kb = sE.CR[k-1,1]
            CO1kb = sE.CO[k-1,1]
            sE.CR[k,0] = (CR1kb + self.xgrid.dX*sE.Ke*np.exp(-sE.alpha*sE.eps[k]
                         )*(CO1kb + CR1kb/sE.DOR))/(1 + self.xgrid.dX*sE.Ke*(
                         np.exp((1-sE.alpha)*sE.eps[k])+np.exp(
                         -sE.alpha*sE.eps[k])/sE.DOR))
            sE.CO[k,0] = CO1kb + (CR1kb - sE.CR[k,0])/sE.DOR
            # Runge-Kutta 4:
            sE.CR[k,1:-1] = self.RK4(sE.CR[k-1,:], 'E', sE)[1:-1]
            if self.mech == 'E':
                sE.CO[k,1:-1] = self.RK4(sE.CO[k-1,:], 'E', sE)[1:-1]
            elif self.mech == 'EC':
                sE.CO[k,1:-1] = self.RK4(sE.CO[k-1,:], 'EC', sE, sC)[1:-1]
                sC.CP[k,0] = sC.CP[k-1,1]
                sC.CP[k,1:-1] = self.RK4(sC.CP[k-1,:], 'ECP', sE, sC)[1:-1]
                
        for s in self.species:
            if isinstance(s, E):
                # Denormalising:
                if s.cRb:
                    I = -s.CR[:,2] + 4*s.CR[:,1] - 3*s.CR[:,0]
                    D = s.DR
                    c = s.cRb
                else: # In case only O present in solution
                    I = s.CO[:,2] - 4*s.CO[:,1] + 3*s.CO[:,0]
                    D = s.DO
                    c = s.cOb
                self.i = s.n*F*self.xgrid.Ageo*D*c*I/(2*self.xgrid.dX*s.delta)

                #self.cR = s.CR*s.cRb
                #self.cO = s.CO*s.cOb
                self.x = self.xgrid.X*s.delta
            elif isinstance(s, C):
                self.cP = s.CP#*s.cPb

        s.CR = 0 # Empty matrix to free memory
        s.CO = 0
        s.CP = 0

    def join(self, species):
        ns = len(species)
        self.nE = []
        self.nC = []
        for s in range(ns):
            if isinstance(species[s], E):
                self.nE.append(s)
            elif isinstance(species[s], C):
                self.nC.append(s)
        # User may only want to simulate an E mechanism:
        if not self.nC:
            self.nC.append(0)
        if not self.nE:
            self.nE.append(0)

        if self.mech == 'EC' or self.mech == 'C':
            species[self.nC[0]].Kc = species[self.nC[0]].kc* \
                                     species[self.nE[0]].delta/ \
                                     species[self.nE[0]].DR

    def fun(self, y, mech, species, params):
        rate = 0
        if mech == 'EC':
            rate = - self.tgrid.dT*params.Kc*y
        elif mech == 'ECP': # To obtain concentration profile of P
            rate = self.tgrid.dT*params.Kc*y
        return np.dot(species.A, y) + rate

    def RK4(self, y, mech, species, params=0):
        dT = self.tgrid.dT
        k1 = self.fun(y, mech, species, params)
        k2 = self.fun(y+dT*k1/2, mech, species, params)
        k3 = self.fun(y+dT*k2/2, mech, species, params)
        k4 = self.fun(y+dT*k3, mech, species, params)
        return y + (dT/6)*(k1 + 2*k2 + 2*k3 + k4)



if __name__ == '__main__':
    from calculate import *
    from technique import *
    from plotting import *

    # CV
    wf = Sweep(Eini=0.5, Efin=-0.5, sr=0.01)
    twf = wf.t
    Ewf = wf.E
    e = E(cRb=0, cOb=1e-6)
    tgrid = TGrid(twf, Ewf)
    xgrid = XGrid([e], tgrid)
    simE = Simulate([e], 'E', tgrid, xgrid)
    simE.sim()
    e = E(cRb=0, cOb=1e-6)
    c = C(kc=1e-1)
    xgrid = XGrid([e,c], tgrid)
    simEC = Simulate([e,c], 'EC', tgrid, xgrid)
    simEC.sim()
    plot(Ewf, [simE.i, simEC.i], xlab='$E$ / V', ylab='$i$ / A', 
         legend=['E', 'EC'], fig=1, show=0)

    # CA
    wf = Step(Es=-0.4, dt=0.01)
    twf = wf.t
    Ewf = wf.E
    tgrid = TGrid(twf, Ewf)
    e = E(cRb=0, cOb=1e-6)
    xgrid = XGrid([e], tgrid)
    simE = Simulate([e], 'E', tgrid, xgrid)
    simE.sim()
    e = E(cRb=0, cOb=1e-6)
    c = C(kc=1e-1)
    xgrid = XGrid([e,c], tgrid)
    simEC = Simulate([e,c], 'EC', tgrid, xgrid)
    simEC.sim()

    # Cottrell
    macro = Macro()
    i_cott = macro.Cottrell(twf)

    legend = ['E', 'EC', 'Cottrell']
    mark = ['-o', 'o', '--']
    plot(1/np.sqrt(twf[1:]), [simE.i[1:], simEC.i[1:], i_cott[1:]], 
         xlab='$t^{-1/2}$ / s$^{-1/2}$', ylab='$i$ / A', 
         legend=legend, mark=mark, fig=2, show=0)
    plot(twf[1:], [simE.i[1:]/i_cott[1:], simEC.i[1:]/i_cott[1:]],
         xlab='$t$ / s', ylab='$i$ / $i_{cott}$',
         legend=legend, mark=mark, fig=3, show=1)
