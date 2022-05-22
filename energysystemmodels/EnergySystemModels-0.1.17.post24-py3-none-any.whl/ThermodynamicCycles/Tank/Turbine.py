from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI

class Object:
    def __init__(self):
        self.IsenEff=0.7
        self.Inlet=FluidPort() 
        self.F_kgs=0.1
        self.Inlet.F_kgs=self.F_kgs
        self.Outlet=FluidPort()
        self.Sis=0
        self.Tis=0
        self.His=0
        self.LP=1*100000
        self.H=0
        self.T=0
        self.S=0
        # self.Tdischarge_target=80
        # self.T3ref2=0
        
        self.Qturb=0
        # self.Qlosses=0
        
    def calculate (self):
        self.F_kgs=self.Inlet.F_kgs
        self.Sis = PropsSI('S','P',self.Inlet.P,'H',self.Inlet.h,self.Inlet.fluid)
        self.Tis=PropsSI('T','P',self.LP,'S',self.Sis,self.Inlet.fluid)
        self.His = PropsSI('H','P',self.LP,'S',self.Sis,self.Inlet.fluid)
        
        self.H = (self.His-self.Inlet.h)*self.IsenEff+self.Inlet.h
        self.T=PropsSI('T','P',self.LP,'H',self.H,self.Inlet.fluid)
        self.S=PropsSI('S','P',self.LP,'H',self.H,self.Inlet.fluid)
        
        # self.T3ref2=self.Tdischarge_target+273.15
        # self.H3ref2=PropsSI('H','P',self.HP,'T',self.T3ref2,self.Inlet.fluid)
        # self.S3ref2=PropsSI('S','P',self.HP,'T',self.T3ref2,self.Inlet.fluid)
        
        self.Outlet.fluid=self.Inlet.fluid
        self.Outlet.h=self.H
        self.Outlet.F_kgs=self.F_kgs
        self.Outlet.P=self.LP
        
        self.Qturb=-self.Inlet.F_kgs*(self.H-self.Inlet.h)
        
        # self.Qlosses=self.Inlet.F_kgs*(self.H3ref-self.H3ref2)
        
      #  print("Tis=",self.Tis-273.15,"His=",self.His,"Tref=",self.T-273.15,"H=",self.H)
       # print("Qturb=",self.Qturb)
        # print("Qlosses=",self.Qlosses)
        # print("self.Inlet.F_kgs=",self.Inlet.F_kgs)
        
        