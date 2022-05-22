from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI
import pandas as pd 

class Object :
    def __init__(self):
        self.Inlet=FluidPort() 
        self.Outlet=FluidPort()
        self.Tsl=0
        self.Hsl = 0
        self.Ssl = 0
        self.subcooling=2
        self.Qcond=0
        #Output Data
        self.df=[]
        
    def calculate (self):
        self.Tsl=PropsSI('T','P',self.Inlet.P,'Q',0,self.Inlet.fluid)
       
        self.Hsl =PropsSI('H','P',self.Inlet.P,'Q',0,self.Inlet.fluid)
        #print("H5=",self.Hsl )
        #print("self.Inlet.P=",self.Inlet.P )
        #print("self.Inlet.fluid=",self.Inlet.fluid )
        
        self.Ssl =PropsSI('S','P',self.Inlet.P,'Q',0,self.Inlet.fluid)
        
        self.To=self.Tsl-self.subcooling
        self.Ho = PropsSI('H','P',self.Inlet.P,'T',self.To,self.Inlet.fluid)
        self.So = PropsSI('S','P',self.Inlet.P,'T',self.To,self.Inlet.fluid)
        self.Outlet.fluid=self.Inlet.fluid
        self.Outlet.h=self.Ho
        self.Outlet.F_kgs=self.Inlet.F_kgs
        self.Outlet.P=self.Inlet.P
        
        self.Qcond=self.Inlet.F_kgs*(self.Inlet.h-self.Outlet.h)


        self.df = pd.DataFrame({'Condenser': [self.Inlet.fluid,self.Outlet.F_kgs,self.Tsl-273.15,self.Hsl/1000,self.Ssl/1000,self.To-273.15,self.Ho/1000,self.So/1000,self.Qcond/1000,], },
                      index = ['fluid','Outlet.F_kgs',"Tsl(°C)",    "Hsl(kJ/kg)",      "Ssl(kJ/kg-K)",       "To(°C)",      "Ho(kJ/kg)",       "So(kJ/kg-K)",     "Qcond(kW)", ])

      