from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI
import pandas as pd 

class Object :
    def __init__(self):
        self.Inlet=FluidPort() 
        self.Outlet=FluidPort()
        #self.Ho = 0
        self.To=0
        self.So =0
        #self.LP = 2.7*100000
        #self.Outlet.P=self.LP
        self.Qdet=0
         #Output Data
        self.df=[]

    def calculate(self):
        self.Outlet.fluid=self.Inlet.fluid
        #print(self.Inlet.h)
        self.Outlet.h = self.Inlet.h
        #print("Ho=",self.Outlet.h)
        self.To=PropsSI('T','P',self.Outlet.P,'H',self.Outlet.h,self.Inlet.fluid)
        #print("self.To °C=",self.To-273.15)
        #print("valv self.Outlet.P=",self.Outlet.P)
        self.So =PropsSI('S','P',self.Outlet.P,'H',self.Outlet.h,self.Inlet.fluid)
        
        
        self.Outlet.F_kgs=self.Inlet.F_kgs
        #self.Outlet.P=self.LP
        #pour calculate une detente avec travail exterieur :(=0)
        self.Qdet=self.Inlet.F_kgs*(self.Outlet.h-self.Inlet.h)

        self.df = pd.DataFrame({'Expansion_Valve': [self.Inlet.fluid,self.Outlet.F_kgs,self.To-273.15, self.Outlet.h/1000, self.So/1000,], },
                      index = ['fluid','Outlet.F_kgs', "To(°C)", "Ho (kJ/kg)", "So(kJ/kg-K)", ])


       