import numpy as np

class Sweep:
    """

    Returns t and E for a sweep potential waveform.
    All the parameters are given a default value.

    ----------
    Parameters:
    Eini:   V, initial potential [-0.5 V]
    Efin:   V, final potential [0.5 V]
    sr:     V/s, scan rate [0.1 V/s]
    dE:     V, potential increment [0.01 V]
    ns:     number of sweeps [2]

    ----------
    Returns:
    self.t: s, time numpy array
    self.E: V, potential numpy array

    ----------
    Examples:
    > import softpotato as sp
    > cv = sp.technique.Sweep(sr=0.001) # Changing only the scan rate
    print(cv.E)
    print(cv.t)

    """

    def __init__(self, Eini=-0.5, Efin=0.5, sr=0.1, dE=0.01, ns=2):
        self.Eini = Eini
        self.Efin = Efin
        self.sr = sr
        self.dE = dE
        self.ns = ns

        Ewin = abs(self.Efin-self.Eini)
        tsw = Ewin/self.sr # total time for one sweep
        nt = int(Ewin/self.dE)

        self.E = np.array([])
        self.t = np.linspace(0, tsw*self.ns, nt*self.ns)

        for n in range(1, self.ns+1):
            if (n%2 == 1):
                self.E = np.append(self.E, np.linspace(self.Eini, self.Efin, nt))
            else:
                self.E = np.append(self.E, np.linspace(self.Efin, self.Eini, nt))

class Sweep2:
    """ 

    Returns t and E for a sweep potential waveform.
    All the parameters are given a default value.

    ----------
    Parameters:
    Eini:   V, initial potential [-0.5 V]
    Efin:   V, final potential [0.5 V]
    sr:     V/s, scan rate [0.1 V/s]
    dE:     V, potential increment [0.01 V]
    ns:     number of sweeps [2]

    ----------
    Returns:
    self.t: s, time numpy array
    self.E: V, potential numpy array

    ----------
    Examples:
    > import softpotato as sp
    > cv = sp.technique.Sweep(sr=0.001) # Changing only the scan rate
    print(cv.E)
    print(cv.t)

    """

    def __init__(self, Eini=0, Eupp=0.5, Elow=-0.5, sr=0.1, dE=0.01, ns=2): # Modified class to include upper and lower vertex potentials
        self.Eini = Eini
        self.Eupp = Eupp # Changed the Efin to upper vertex potential
        self.Elow = Elow # Added a lower vertex potential
        self.sr = sr
        self.dE = dE
        self.ns = ns

        Ewin = abs(self.Eupp-self.Elow) # Adapted Ewin to accomodate upper and lower vertex potentials
        tsw = Ewin/self.sr # total time for one sweep
        nt = int(Ewin/self.dE)
        ntupper = int(((Eupp - Eini)/Ewin)*nt) # Added ntupper and ntlower parameters to allow for asymmetric waveforms
        ntlower = int(((Eini - Elow)/Ewin)*nt)

        self.E = np.array([])
        self.t = np.linspace(0, tsw*self.ns, nt*self.ns)

        if Eini == Eupp or Eini == Elow: # Accomodates for situations in which initial potential is same as uppoer or lower vertex
            segments = 2
        else:
            segments = 3
            
        for n in range(1, self.ns+1):
            if (segments == 3) and (abs(dE) == dE):
                self.E = np.append(self.E, np.linspace(self.Eini, self.Eupp, ntupper))
                self.E = np.append(self.E, np.linspace(self.Eupp, self.Elow, nt))
                self.E = np.append(self.E, np.linspace(self.Elow, self.Eini, ntlower))
            elif (segments == 3) and (abs(dE) != dE): # When absolute of dE is not equal to dE it means the scan is negative
                self.E = np.append(self.E, np.linspace(self.Eini, self.Elow, ntlower))
                self.E = np.append(self.E, np.linspace(self.Elow, self.Eupp, nt))
                self.E = np.append(self.E, np.linspace(self.Eupp, self.Eini, ntupper))
            elif (segments == 2) and (Eini == Eupp):
                self.E = np.append(self.E, np.linspace(self.Eini, self.Elow, nt))
                self.E = np.append(self.E, np.linspace(self.Elow, self.Eupp, nt))
            elif (segments == 2) and  (Eini == Elow):
                self.E = np.append(self.E, np.linspace(self.Eini, self.Eupp, nt))
                self.E = np.append(self.E, np.linspace(self.Eupp, self.Elow, nt))



class Step:
    """ 
    ----------
    Description:
    Returns t and E for a step potential waveform.
    All the parameters are given a default value.

    ----------
    Paramters:
    Es:     V, potential step
    ttot:   s, total time of the step
    dt:     s, time increment

    ----------
    Returns:
    self.t: s, time numpy array
    self.E: V, potential numpy array

    ----------
    Examples:
    > import softpotato as sp
    > ca = sp.technique.Step(Es=0.1) # Changing only the step potential
    > print(ca.t)
    > print(ca.E)
    """

    def __init__(self, Es=0.5, ttot=1, dt=0.01):
        
        self.Es = Es
        self.ttot = ttot
        self.dt = dt
        self.nt = int(self.ttot/self.dt)

        self.E = np.ones([self.nt])*self.Es
        self.t = np.linspace(dt, self.ttot + dt, self.nt)



class Custom:
    """ 
    
    Returns t and E for a customised potential waveform.
    
    Parameters
    ----------
    wf:     list containing the waveform object
    
    Returns
    -------
    t:      s, time array
    E:      V, potential array
    
    Examples
    --------
    >>> import softpotato as sp
    >>> wf1 = sp.step(Estep, tini, ttot, dt)
    >>> wf2 = sp.sweep(Eini, Efin, sr, dE, ns)
    >>> wf = sp.Construct_wf([wf1, wf2])
    
    Returns t and E calculated with the parameters given
    """

    def __init__(self, wf):
        n = len(wf)
        t = np.array([0])
        E = np.array([0])

        for i in range(n):
            t = np.concatenate([t,wf[i].t+t[-1]])
            E = np.concatenate([E,wf[i].E])

        # Remove first data point to prevent repeating time
        self.t = t[1:]
        self.E = E[1:]
        

if __name__ == '__main__':
    cv = Sweep2()
    print(cv.E)
    print(cv.t)
