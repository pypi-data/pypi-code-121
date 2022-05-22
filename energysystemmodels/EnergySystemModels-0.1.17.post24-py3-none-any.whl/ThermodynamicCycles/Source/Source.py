from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI
import pandas as pd 

class Object:
    def __init__(self):
        self.Timestamp=None
        #Input and Output Connector
       # self.Inlet=FluidPort() 
        self.Outlet=FluidPort()

        #Input Data
        self.fluid=None #"air"
        self.Ti_degC=None #15 #♣°C
        self.Pi_bar=None #1.01325
        self.F_kgs=None
        
        self.F_Sm3s=None
        self.F_m3s=None
        self.F_Sm3h=None
        self.F_m3h=None
        self.F_kgh=None
        
        

        #Initial Values
        
        
        self.Q=0
        self.fluid_quality="liquid"
       
    
        
    def calculate (self):

        if self.F_Sm3h is not None:
            self.F_kgs=self.F_Sm3h/3600*PropsSI("D", "P", 100000*1.01325, "T", (15+273.15), self.fluid)
        
        if self.F_m3s is not None:
            self.F_kgs=self.F_m3s*PropsSI("D", "P", 100000*self.Pi_bar, "T", (self.Ti_degC+273.15), self.fluid)

        if self.F_m3h is not None:
            self.F_kgs=self.F_m3h/3600*PropsSI("D", "P", 100000*self.Pi_bar, "T", (self.Ti_degC+273.15), self.fluid)

        if self.F_kgh is not None:
            self.F_kgs=self.F_kgh/3600
        
        if self.F_Sm3s is not None:
            self.F_kgs=self.F_Sm3s*PropsSI("D", "P", 100000*1.01325, "T", (15+273.15), self.fluid)

        #print("self.F_kgs",self.F_kgs)
        if self.F_kgs is None:
            self.F_kgs=0


        self.Outlet.fluid=self.fluid
        self.Outlet.F_kgs=self.F_kgs
        self.Outlet.P=self.Pi_bar*100000

        #Inlet temperature calculation
        self.Outlet.h=PropsSI('H','P',self.Outlet.P,'T',self.Ti_degC+273.15,self.fluid)
        #print("sink h",self.Outlet.h)
        #calcul de l'état du fluid
        try:
            self.Ti_degC=PropsSI("T", "P", 100000*self.Pi_bar, "H", self.Outlet.h,self.fluid)-273.15
        except:
            self.Ti_degC=0-273.15

        if (100000*self.Pi_bar)<PropsSI("Pcrit",self.fluid): #comparer à la pression critique
            Hv=PropsSI("H", "P", 100000*self.Pi_bar, "Q", 1, self.fluid)
           # print("Hv=",Hv)
            Hl=PropsSI("H", "P", 100000*self.Pi_bar, "Q", 0, self.fluid)
          #  print("Hl=",Hl)
            self.Q=1-((Hv-self.Outlet.h)/(Hv-Hl))
            
            if self.Q>=1:
               # print(self.fluid+" vapeur"+"%.2f" % self.Q) #"%d" % 
                self.fluid_quality="vapor"
            elif (self.Q<1 and self.Q>0):
               # print(self.fluid+" diphasique"+"%.2f" % self.Q) #"%d" % 
                self.fluid_quality="two-phase"
            else:
                #print(self.fluid+" liquide"+"%.2f" % self.Q) #"%d" % 
                self.fluid_quality="liquid"
           # print("Qualité=",self.Q)
            
        else:
            #print(self.fluid+" supercritique") #"%d" % 
            self.fluid_quality="supercritical"
            
         
        if (100000*self.Pi_bar)<PropsSI("Pcrit",self.fluid): #comparer à la pression critique
            if self.Q>1:
                self.F_m3s=self.Outlet.F_kgs/PropsSI("D", "P", 100000*self.Pi_bar, "T", (self.Ti_degC+273.15), self.fluid)
            elif (self.Q<=1 and self.Q>=0):
                self.F_m3s=self.Q*self.Outlet.F_kgs/PropsSI("D", "P", 100000*self.Pi_bar, "Q", 1, self.fluid)+(1-self.Q)*self.Outlet.F_kgs/PropsSI("D", "P", 100000*self.Pi_bar, "Q", 0, self.fluid)
            else:
                self.F_m3s=self.Outlet.F_kgs/PropsSI("D", "P", 100000*self.Pi_bar, "T", (self.Ti_degC+273.15), self.fluid)        
        else:    
            self.F_m3s=self.Outlet.F_kgs/PropsSI("D", "P", 100000*self.Pi_bar, "T", (self.Ti_degC+273.15), self.fluid)
        
        self.F_Sm3s=self.Outlet.F_kgs/PropsSI("D", "P", 100000*1.01325, "T", (15+273.15), self.fluid)

        self.F_Sm3h=self.F_Sm3s*3600
        self.F_m3h=self.F_m3s*3600
        self.F_kgh=self.Outlet.F_kgs*3600

        self.df = pd.DataFrame({'Source': [self.Timestamp,self.Ti_degC,self.Outlet.fluid,self.F_Sm3h,self.F_m3h,self.F_kgh,self.F_kgs,self.F_m3s,self.F_Sm3s,], },
                      index = ['Timestamp','src_Ti_degC','src_fluid','src_F_Sm3h','src_F_m3h', 'src_F_kgh','src_F_kgs','src_F_m3s','src_F_Sm3s'])

        #réinitialiser les débits
        self.F_Sm3s=None
        self.F_m3s=None
        self.F_Sm3h=None
        self.F_m3h=None
        self.F_kgh=None
        
 
        