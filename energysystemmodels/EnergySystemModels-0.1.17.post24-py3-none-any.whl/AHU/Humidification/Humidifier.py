from AHU.air_humide import air_humide
from AHU.air_humide import air_humide_NB
#from modules.FreshAir import FreshAir
from AHU.AirPort.AirPort import AirPort


from scipy import *
from pylab import *
from scipy.optimize import bisect   
from scipy.optimize import fsolve   
  
class Object:
    def __init__(self):
        self.Inlet=AirPort() 
        self.Outlet=AirPort()
        
        self.P_drop=0 #perte de charge
        
    
        #parameter
        #type d'humidification
        self.HumidType="adiabatique"
        #consigne Humidité relative
        self.HR_out_target=60
        
        self.HA_out_target=10
        
        # données air amont
        self.T_in=18
        self.HR=20
        self.h_in=24.522
        self.HA_in=10
        self.F_kgs=20000
        self.Llv=2500.8 #kJ/kg
        self.Tvap=100
        self.Cpv=1.8262 #KJ/kg-K
        self.hvap=self.Cpv*self.Tvap+self.Llv #2676 kJ/kg à 100 °C
       # print("self.hvap",self.hvap)
        
        
        # calcul sortie Coil
        self.Pvsat_out=0
        self.HR_out=0
        
        self.T_out=0
        self.m_water=0
        self.h_out=0
        self.Q_th=0
        
        self.P=0
        
        
    def calculate(self):
        
        self.HA_in=self.Inlet.HA
        self.P=self.Inlet.P
        self.h_in=self.Inlet.h
        self.F_kgs=self.Inlet.F_kgs
        
        if self.HA_out_target>self.HA_in:
            # print("self.HA_out_target>self.HA_in",self.HA_out_target,self.HA_in)
               
            if self.HumidType=="adiabatique" :
                # print("calcul Humidifier adiabatique réussi")
                #Bilan de masse
                self.h_out=self.h_in
                def syst(var): # définition du système
                    self.Pvsat_out,self.T_out, self.HR_out, = var[0], var[1], var[2] # définition des variables
                    eq1 =self.Pvsat_out-air_humide.Pvs(self.T_out)
                    eq2 =self.HA_out_target-air_humide.HA(self.Pvsat_out,self.HR_out,101325)
                    eq3 =self.h_in-air_humide.Enthalpie(self.T_out, self.HA_out_target)
                    res = [eq1, eq2, eq3]
                    return res
                #self.h_out=self.h_in
                x0, y0, z0 = 0, 0, 0 # Initialisation de la recherche des solutions numériques
                sol_ini = [x0, y0, z0]
    
                x=fsolve(syst, sol_ini)
               # print(x)
                self.m_as=(self.Inlet.F_kgs)/(1+(self.Inlet.HA/1000))
                #self.m_as=(self.Inlet.F_kgs)/air_humide_NB.Air3_Vs(self.Inlet.HA/1000,self.Inlet.P,self.Inlet.h) #[m3/s] / [m3/kg air sec]  = [kg air sec/s]
                self.m_water=self.m_as*(self.HA_out_target-self.HA_in)/1000 #débit d'eau en kgH2O/s
               # print("self.F_kgs",self.F_kgs,"\n","self.m_water",self.m_water,"\n","self.T_out",self.T_out,"\n","self.HA_out_target",self.HA_out_target,"\n","self.HR_out",self.HR_out,"\n")
            
            if self.HumidType=="vapeur" :
              #  print("hvap=",self.hvap)
                def syst(var): # définition du système
                    self.Pvsat_out,self.T_out, self.HR_out,self.h_out = var[0], var[1], var[2], var[3] # définition des variables
                    eq1 =self.Pvsat_out-air_humide.Pvs(self.T_out)
                    eq2 =self.HA_out_target-air_humide.HA(self.Pvsat_out,self.HR_out,101325)
                    eq3 =self.h_out-air_humide.Enthalpie(self.T_out, self.HA_out_target)
                    eq4 =self.h_out-self.h_in-(self.HA_out_target-self.HA_in)/1000*self.hvap
                    res = [eq1, eq2, eq3, eq4]
                    return res
                #self.h_out=self.h_in
                x0, y0, z0, t0 = 0, 0, 0, 0 # Initialisation de la recherche des solutions numériques
                sol_ini = [x0, y0, z0, t0]
    
                x=fsolve(syst, sol_ini)
               # print(x)
                self.m_as=(self.Inlet.F_kgs)/(1+(self.Inlet.HA/1000))
                #self.m_as=(self.Inlet.F_kgs)/air_humide_NB.Air3_Vs(self.Inlet.HA/1000,self.Inlet.P,self.Inlet.h) #[m3/s] / [m3/kg_air_sec]  = [kg_air_sec/s]
                self.m_water=self.m_as*(self.HA_out_target-self.HA_in)/1000 #débit d'eau en kgH2O/s = [kg_air_sec/s] * kg_H20 /kg_air_sec
                # print("self.m_water=",self.m_water)
                
              #  print("self.F_kgs",self.F_kgs,"\n","self.m_water",self.m_water,"\n","self.T_out",self.T_out,"\n","self.HA_out_target",self.HA_out_target,"\n","self.HR_out",self.HR_out,"\n")
            
                 #connecteur   
             
             #modele perte de charge
             #self.P_drop=f(self.F_kgs)
              
            self.Outlet.HA=self.HA_out_target
            self.Outlet.P=self.Inlet.P-self.P_drop
            self.Outlet.h=self.h_out
            self.m_as=(self.Inlet.F_kgs)/(1+(self.Inlet.HA/1000))
            #self.m_as=(self.Inlet.F_kgs)/air_humide_NB.Air3_Vs(self.Inlet.HA/1000,self.Inlet.P,self.Inlet.h) #[m3/s] / [m3/kg_air_sec]  = [kg_air_sec/s]
            self.Outlet.F_kgs=self.m_as*(1+(self.Outlet.HA/1000))
            #self.Outlet.F_kgs=self.m_as*air_humide_NB.Air3_Vs(self.Outlet.HA/1000,self.Outlet.P,self.Outlet.h) #[kg air sec/s] * [m3/kg air sec] =[m3/s]
           # self.m_water=self.m_as*(self.HA_out_target-self.HA_in)/1000
            self.Qth=(self.Outlet.h-self.Inlet.h)*self.m_as
        else:
            self.Outlet.HA=self.Inlet.HA
            self.Outlet.P=self.Inlet.P-self.P_drop
            self.Outlet.h=self.Inlet.h
            self.m_as=(self.Inlet.F_kgs)/(1+(self.Inlet.HA/1000))
            self.Outlet.F_kgs=self.m_as*(1+(self.Outlet.HA/1000))
            #self.m_as=(self.Inlet.F_kgs)/air_humide_NB.Air3_Vs(self.Inlet.HA/1000,self.Inlet.P,self.Inlet.h) #[m3/s] / [m3/kg_air_sec]  = [kg_air_sec/s]
            #self.Outlet.F_kgs=self.m_as*air_humide_NB.Air3_Vs(self.Outlet.HA/1000,self.Outlet.P,self.Outlet.h) #[kg air sec/s] * [m3/kg air sec] =[m3/s]
            self.m_water=0
            self.Qth=0
            # print("pas d'humidification")
            

