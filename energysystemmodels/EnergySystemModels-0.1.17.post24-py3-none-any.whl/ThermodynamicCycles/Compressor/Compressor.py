from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI
import pandas as pd 

class Object:
    def __init__(self):
        self.Timestamp=None

        #Input and Output Connector
        self.Inlet=FluidPort() 
        self.Outlet=FluidPort()

        #Input Data
        self.eta_is=0.75
        self.HP_bar=None
        self.Tcond_degC=None
        self.HP=None #self.HP_bar*100000
        self.Tdischarge_target=None #°C
        

        #Initial Values
        self.Inlet.fluid="air"
        self.Inlet.P=101325
        self.F_kgs=0.1
        self.Inlet.F_kgs=self.F_kgs

        self.F_Sm3s=None
        self.F_Sm3h=None
        
        #Output Data
        self.df=[]
        self.HeatLossesRatio=0
        self.S3is=0
        self.T3is=0
        self.H3is=0
        self.H3ref=0
        self.T3ref=0
        self.S3ref=0
        self.To=0
        self.Qcomp=None
        self.Qlosses=0
        self.Ti_degC=0
        
    def calculate (self):


        if self.Tcond_degC is not None:
            self.HP = PropsSI('P','T',self.Tcond_degC+273.15,'Q',1,self.Inlet.fluid)
            print("test HP calculation",self.HP)

        if self.HP_bar is not None:
            self.HP=self.HP_bar*100000
        if self.HP is not None:
            self.HP_bar=self.HP/100000
        
        #Inlet temperature calculation
        self.Ti_degC=PropsSI('T','P',self.Inlet.P,'H',self.Inlet.h,self.Inlet.fluid)-273.15
        
        self.S3is = PropsSI('S','P',self.Inlet.P,'H',self.Inlet.h,self.Inlet.fluid)
        self.T3is=PropsSI('T','P',self.HP,'S',self.S3is,self.Inlet.fluid)
        self.H3is = PropsSI('H','P',self.HP,'S',self.S3is,self.Inlet.fluid)
        
        self.H3ref = (self.H3is-self.Inlet.h)/self.eta_is+self.Inlet.h
        self.T3ref=PropsSI('T','P',self.HP,'H',self.H3ref,self.Inlet.fluid)
        self.S3ref=PropsSI('S','P',self.HP,'H',self.H3ref,self.Inlet.fluid)
        
               
        if self.Tdischarge_target<=(self.T3ref-273.15):
            self.To=self.Tdischarge_target+273.15
            print("Le compresseur est refroidi")

        if self.Tdischarge_target>(self.T3ref-273.15):  
            self.Tdischarge_target=self.T3ref-273.15    # Passer un compresseur adiabatique
            self.To=self.T3ref
            print("Le compresseur n'est pas refroidi")
        
        self.Ho=PropsSI('H','P',self.HP,'T',self.To,self.Inlet.fluid)
        self.So=PropsSI('S','P',self.HP,'T',self.To,self.Inlet.fluid)
        
        #mass flow rate or Energy Power Calculation

        if self.Qcomp is not None:
            self.F_kgs=self.Qcomp/(self.H3ref-self.Inlet.h)
        else: # self.Inlet.F_kgs is not None:
            self.F_kgs=self.Inlet.F_kgs
            self.Qcomp=self.F_kgs*(self.H3ref-self.Inlet.h)
        
        

        self.Qlosses=self.F_kgs*(self.H3ref-self.Ho)

        self.HeatLossesRatio=self.Qlosses/self.Qcomp

        self.F_Sm3s=self.F_kgs/PropsSI("D", "P", 100000*1.01325, "T", (15+273.15), self.Inlet.fluid)
        self.F_Sm3h=self.F_Sm3s*3600

        self.eta_WhSm3=self.Qcomp/self.F_Sm3h
        
        # outlet connector calculation
        self.Outlet.fluid=self.Inlet.fluid
        self.Outlet.h=self.Ho
        self.Outlet.F_kgs=self.F_kgs
        self.Outlet.P=self.HP

        # Results
        self.df = pd.DataFrame({'Compressor': [self.Timestamp,self.Inlet.fluid,self.F_kgs,self.Qcomp/1000, self.Qlosses/1000, self.HeatLossesRatio,self.T3is-273.15,self.eta_WhSm3,self.T3is-273.15,self.H3is/1000,self.S3is/1000,self.T3ref-273.15,self.H3ref/1000,self.S3ref/1000,self.To-273.15,self.Ho/1000,self.So/1000,self.Outlet.P/100000,], },
                      index = ['Timestamp','comp_fluid','comp_F_kgs','Qcomp(KW)', 'Qlosses(KW)', 'HeatLossesRatio','Tis(°C)','eta_WhSm3',"T3is(°C)","H3is(kJ/kg)","S3is (J/kg-K)","T3ref(°C)","H3ref(kJ/kg)", "S3ref(J/kg-K)",
        "To(°C)", "Ho(kJ/kg)", "So(J/kg-K)","self.Outlet.P (bar)"])

      
       
        
        