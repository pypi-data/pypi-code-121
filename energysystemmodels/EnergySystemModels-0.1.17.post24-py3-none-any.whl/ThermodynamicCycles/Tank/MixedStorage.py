from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI
import pandas as pd 
import math

class Object :
    def __init__(self):

        self.Timestamp=None

        self.Inlet=FluidPort() 
        self.Outlet=FluidPort()
        self.df=[]
        self.Qstr_J=None #Energie stockée
        self.cumul_Qstr_kWh=0

        self.V=1
        self.Tinit_degC=12
        self.rho=1000
        self.m=1000/3600
        self.t=3600
        self.Ti_degC=60
        self.T=None
        self.T_degC=None
        self.Cp=4181
        self.U=0 #coeffcient d'échange global
        self.S=3 # surface d'échange vers l'ambiance
        self.Tamb_degC=12 #Température ambiance
        self.const=None #constante de calcul (pour simplfier l'écriture)
        self.const_t=None # constante de calcul exp
    def calculate(self):
        self.m=self.Inlet.F_kgs
        self.Ti_degC=-273.15+PropsSI('T','P',self.Inlet.P,'H',self.Inlet.h,self.Inlet.fluid)
        

        self.const=(self.m*self.Cp*self.Ti_degC+self.U*self.S*self.Tamb_degC)/(self.m*self.Cp+self.U*self.S)
        #print("Ti_degC",self.const)
        self.const_t=(self.m*self.Cp+self.U*self.S)/(self.rho*self.V*self.Cp)

        self.T_degC=self.const+(self.Tinit_degC-self.const)*math.exp(-(self.const_t*self.t))
        self.T=self.T_degC+273.17

        #recalcul du CP
        self.Cp=PropsSI('CPMASS','P',self.Inlet.P,'T',self.T,self.Inlet.fluid)
        #print("Cp=",self.Cp)
        #calcul de l'énergie stockée
        self.Qstr_J=self.rho*self.V*self.Cp*(self.T_degC-self.Tinit_degC)
        self.Qstr_kWh=self.Qstr_J/(3600000)
        self.cumul_Qstr_kWh=self.Qstr_J/(3600000)+self.cumul_Qstr_kWh
        
        self.Qstr_kW=self.Qstr_kWh/(self.t/3600)
        #connecteur de sortie
        self.Outlet.fluid=self.Inlet.fluid
        self.Outlet.h=PropsSI('H','P',self.Inlet.P,'T',self.T,self.Inlet.fluid)
        self.Outlet.P=self.Inlet.P
        self.Outlet.F_kgs=self.Inlet.F_kgs

        

        self.df = pd.DataFrame({'MixedStorage': [self.Timestamp,self.Inlet.fluid,self.Ti_degC,self.Inlet.F_kgs,self.T_degC,self.Inlet.h,self.Outlet.h,self.Qstr_kWh,self.Qstr_kW,self.cumul_Qstr_kWh,], },
                      index = ['Timestamp','str_fluid','str_Ti_degC','str_Inlet.F_kgs','str_T_degC','str_Inlet.h','str_Outlet.h','Qstr_kWh','Qstr_kW',"cumul_Qstr_kWh",  ])

        #reinitialisation de la Température pour une n éme ittération 
        self.Tinit_degC=self.T_degC
       