from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI
import pandas as pd 

import numpy as np

class Object:
    def __init__(self):
        self.Inlet=FluidPort() 
        self.Ti_degC=None #Tevap
        self.LP_bar=None
        self.fluid = None
        self.Outlet=FluidPort()
        
        self.surchauff=2 #surchauffe
        self.Tsl=0
        self.Tsv=0
        self.Hsv=0
        self.Ssv=0
        self.To=0
        self.Ho=0
        self.So=0
        self.Qevap=0
        
        self.Qevap_i=[] #descritisation de la puissance de l'évaporateur
        self.Tfluid_i=[]
        
        
        #calcul côté eau
        # self.Tw_inlet=30 #°C donnéesd'entrée
        # self.Tw_outlet=20 #°C recalculée
        # self.m_water_flow=1000000000000000000 #m3/h donnée d'entée
        # self.h_water_outlet=0
        # self.h_water_inlet=0
        # self.Twater_i=[]
        
        #calcul de pincement
        #◙self.pinch=[]

        #output data
        self.df=[]
        
    def calculate (self):
        if self.fluid is None:
          self.fluid=self.Inlet.fluid
        else:
          self.Inlet.fluid=self.fluid
       # print("evaporateur P1",self.Inlet.P)

        # Pevap calculation
        if self.Ti_degC is not None:
          self.Inlet.P=PropsSI('P','T',self.Ti_degC+273.17,'Q',0,self.fluid)
        if self.LP_bar is not None:
          self.Inlet.P=1e5*self.LP_bar
        
        self.Tsv = PropsSI('T','P',self.Inlet.P,'Q',1,self.fluid)
        self.Tsl=PropsSI('T','P',self.Inlet.P,'Q',0,self.fluid)
        
       # print("evaporateur T1",self.Ti-273.15)
        self.Hsv=PropsSI('H','P',self.Inlet.P,'Q',1,self.fluid)
        self.Ssv=PropsSI('S','P',self.Inlet.P,'Q',1,self.fluid)

        self.To=self.Tsv+self.surchauff
        self.Ho = PropsSI('H','P',self.Inlet.P,'T',self.To,self.fluid)
        self.So = PropsSI('S','P',self.Inlet.P,'T',self.To,self.fluid)
        self.Outlet.fluid=self.fluid 
        self.Outlet.h=self.Ho
        self.Outlet.F_kgs=self.Inlet.F_kgs
        self.Outlet.P=self.Inlet.P
        
      #  Qevap avec surchauffe
        self.Qevap=-self.Inlet.F_kgs*(self.Inlet.h-self.Outlet.h)
        
      #  print("self.Inlet.h=",self.Inlet.h)
        
        #print("self.Qevap=",self.Qevap)
        if self.Qevap!=0:
            self.Qevap_i=np.arange(0,self.Qevap,(self.Qevap/20)) #descritisation de la puissance de l'évaporateur
        #print("self.Qevapi (kW)=",self.Qevap_i)
      
        
          #bilan sur l'eau
        
        # self.h_water_inlet=PropsSI('H','P',101325,'T',self.Tw_inlet+273.15,"water")
        # print("self.h_water_inlet=",self.h_water_inlet)
        # self.h_water_outlet=(-self.Qevap/(self.m_water_flow/3.6))+self.h_water_inlet
        # print("self.h_water_outlet=",self.h_water_outlet)
        # self.Tw_outlet=PropsSI('T','P',101325,'H',self.h_water_outlet,"water")-273.15
        # print("self.Tw_outlet=",self.Tw_outlet)
        
        if len(self.Qevap_i)>=20 and self.Qevap!=0: 
            #calcul descrtisation de la temp du fluide frigorigene
            for i in range(len(self.Qevap_i)):
                self.Tfluid_i.append(0)
            
            for i in range(0,len(self.Qevap_i),1):
                self.Tfluid_i[i]=PropsSI('T','H',self.Inlet.h+self.Qevap_i[i]/self.Inlet.F_kgs,'P',self.Inlet.P,self.fluid)
            #print("self.Tfluid_i=",self.Tfluid_i)
            
            #calcul descrtisation de la temp de l'eau   
            
        #     for i in range(len(self.Qevap_i)):
        #         self.Twater_i.append(0)
            
        #     for i in range(0,len(self.Qevap_i),1):
               
        #         self.Twater_i[i]=PropsSI('T','H',self.h_water_outlet+self.Qevap_i[i]/(self.m_water_flow/3.6),'P',101325,"water")
        #     print("self.Twater_i=",self.Twater_i)
            
        #     for i in range(len(self.Qevap_i)):
        #         self.pinch.append(0)
        #         self.pinch[i]=self.Twater_i[i]-self.Tfluid_i[i]
        # print("self.pinch=",self.pinch)

        # Results
        self.df = pd.DataFrame({'Evaporator': [self.fluid,self.Outlet.F_kgs,self.Inlet.P/100000,self.Tsv-273.15,self.Hsv/1000, self.Ssv/1000, self.To-273.15,self.Ho/1000,self.So/1000,self.Qevap/1000], },
                      index = ['fluid','Outlet.F_kgs','Pevap(bar)','Tsv(°C)', 'Hsv(kJ/kg)', 'Ssv(kJ/kg-K)','To(°C)', 'Ho(kJ/kg)', 'So(kJ/kg-K)','Qevap(kW)',])
       
     

        