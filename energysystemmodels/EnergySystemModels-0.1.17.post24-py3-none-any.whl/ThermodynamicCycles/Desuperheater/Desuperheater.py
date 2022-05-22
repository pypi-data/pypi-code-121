from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI
import pandas as pd 

class Object:
    def __init__(self):
        self.Inlet=FluidPort() 
        self.Outlet=FluidPort()
        self.Tsv=1
        self.Hsv = 1
        self.Ssv = 1
        self.Qdesurch=0
        #Output Data
        self.df=[]

    def calculate (self):
        #print("Inlet.P=",self.Inlet.P)
        #print("Outlet.P=",self.Outlet.P)

        self.Tsv=PropsSI('T','P',self.Inlet.P,'Q',1,self.Inlet.fluid)
        self.Hsv = PropsSI('H','P',self.Inlet.P,'Q',1,self.Inlet.fluid)
        self.Ssv = PropsSI('S','P',self.Inlet.P,'Q',1,self.Inlet.fluid)
        self.Outlet.fluid=self.Inlet.fluid
        self.Outlet.h=self.Hsv
        self.Outlet.F_kgs=self.Inlet.F_kgs
        self.Outlet.P=self.Inlet.P
        self.Qdesurch=self.Inlet.F_kgs*(self.Inlet.h-self.Hsv)


        self.df = pd.DataFrame({'Desuperheater': [self.Inlet.fluid,self.Outlet.F_kgs,self.Tsv-273.15, self.Hsv/1000,self.Ssv/1000, self.Qdesurch/1000,], },
                      index = ['fluid','Outlet.F_kgs', "Tsv(°C)", "Hsv(kJ/kg)",  "Ssv(kJ/kg-K)",     "Qdesurch(kW)",])

       