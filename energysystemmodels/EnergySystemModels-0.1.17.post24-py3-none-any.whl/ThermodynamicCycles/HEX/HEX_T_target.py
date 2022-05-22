from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI

class HEX_T_target:
    def __init__(self):
        #self.IsenEff=0.7
        self.Inlet=FluidPort() 
        self.F_kgs=0.1
        self.Inlet.F_kgs=self.F_kgs
        self.Outlet=FluidPort()
       # self.Sis=0
        self.T=0
        #self.His=0
        #self.LP=1*100000
        self.H=0
        self.T_target=0
        self.P_drop=0
        self.S=0
        # self.Tdischarge_target=80
        # self.T3ref2=0
        
        self.Qhex=0
        # self.Qlosses=0
        
    def calculate (self):
        self.F_kgs=self.Inlet.F_kgs
        self.Outlet.P=self.Inlet.P-self.P_drop
        
        
        self.T=self.T_target+273.15
        self.H = PropsSI('H','P',self.Outlet.P,'T',self.T,self.Inlet.fluid)
        self.S = PropsSI('S','P',self.Outlet.P,'H',self.H,self.Inlet.fluid)
        
        
        
              
        
        
        
        self.Outlet.h=self.H
        self.Outlet.F_kgs=self.F_kgs
        self.Outlet.fluid=self.Inlet.fluid
        
        self.Qhex=self.Inlet.F_kgs*(self.H-self.Inlet.h)
        
   
        
        