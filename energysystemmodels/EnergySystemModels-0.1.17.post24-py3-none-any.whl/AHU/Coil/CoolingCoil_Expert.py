from AHU.air_humide import air_humide
from AHU.air_humide import air_humide_NB
from AHU.AirPort.AirPort import AirPort


from scipy import *
from pylab import *
from scipy.optimize import bisect   
from scipy.optimize import fsolve   


class Object:
    def __init__(self):
        self.Inlet=AirPort() 
        self.Outlet=AirPort()
        
        #parameter :
        self.P_drop=0
        
        '''Point de consignes'''
        self.HA_target=8 
        self.T_target=15
        self.Outlet_HR=90
        
        
        
        '''Température point de rosée de l air au contact de la Coil froide '''
        self.T_sat=7  
        '''Températures inlet et outlet'''
        self.T_inlet=0
        self.T_Outlet=12
        self.Outlet_Pvsat=100# initialisation
        self.Inlet_HR=0
        
       
                
        """facteur de bypass"""
        self.FB=0.2
        self.HA_sat=0
        self.h_sat=0
        # calcul sortie Coil
       
        self.Qth=12      
        self.Eff=0.8 #efficacité de la Coil froide
        
        self.F_kgs=0
        self.m_vol=0
        self.m_as=0 #Débit d'air sec
        
    def calculate(self):
        #print("self.Inlet.P=",self.Inlet.P,"air_humide.Pvs(self.T_sat)=",air_humide.Pvs(self.T_sat),"self.T_sat=",self.T_sat)
        self.HA_sat=air_humide.HA(air_humide.Pvs(self.T_sat), 100, self.Inlet.P)
        self.h_sat=air_humide.Enthalpie(self.T_sat,self.HA_sat)
        
        self.T_inlet=air_humide_NB.Air3_Tdb(self.Inlet.HA/1000, self.Inlet.P, self.Inlet.h)
        self.F_kgs=self.Inlet.F_kgs
        #print("self.HA_sat=",self.HA_sat,"self.HA_target=",self.HA_target)
        
        
      #  Test du calcul de point de sortie à 90% d'humidité 7.5 g/kg, 12°C
        self.Outlet.HA=self.HA_target
        # print("CC.Outlet.HA consigne",self.Outlet.HA)
        self.Inlet_HR=air_humide.HR(air_humide.Pvs(self.T_inlet),self.Inlet.HA,self.Inlet.P)
        
      
        if self.Inlet.HA>=self.HA_target and self.HA_target>=self.HA_sat: 
            
            if self.Inlet_HR<=90 :
        
                def syst(var): # définition du système
                    self.Outlet_Pvsat,self.T_Outlet, = var[0], var[1] # définition des variables
                    eq1 =self.Outlet_HR-air_humide.HR(self.Outlet_Pvsat,self.HA_target,self.Inlet.P)  #calcul de Pvsat
                    eq2 =self.Outlet_Pvsat-air_humide.Pvs(self.T_Outlet) #calcul de T      
                    #eq2=self.T_Outlet-12          
                    #eq3 =self.Outlet.HA-air_humide.HA(self.Outlet_Pvsat, self.Outlet_HR, self.Inlet.P) #recalcul de HA
                    res = [eq1,eq2]
                    return res
                        #self.h_out=self.h_in
                x0,y0 = 1341,12 # Initialisation de la recherche des solutions numériques
                sol_ini = [x0,y0]
                
                
                # print(self.Outlet_Pvsat)
        
                x=fsolve(syst, sol_ini)
                # print("Résultats x=",x)
          
                # #self.T_Outlet=12
            
            
                # print("CC.Outlet.HA recalculée",self.Outlet.HA)
             
                               
                # print("self.Outlet_HR=",self.Outlet_HR)
                # print("self.Outlet.HA=",self.Outlet.HA)
                
                # print("self.T_Outlet=",self.T_Outlet)
                # # self.Outlet.h=air_humide_NB.Air4_Hs(self.T_Outlet, self.Inlet.P, self.Outlet.HA/1000)
                # print("self.Outlet.h NB=",self.Outlet.HA)
                self.Outlet.h=air_humide.Enthalpie(self.T_Outlet, self.Outlet.HA)
                # print("self.Outlet.h ZHA=",self.Outlet.h)   
        
            else:
                def syst(var): # définition du système
                    self.Outlet_Pvsat,self.T_Outlet, = var[0], var[1] # définition des variables
                    eq1 =100-air_humide.HR(self.Outlet_Pvsat,self.HA_target,self.Inlet.P)  #calcul de Pvsat
                    eq2 =self.Outlet_Pvsat-air_humide.Pvs(self.T_Outlet) #calcul de T      
                    #eq2=self.T_Outlet-12          
                    #eq3 =self.Outlet.HA-air_humide.HA(self.Outlet_Pvsat, self.Outlet_HR, self.Inlet.P) #recalcul de HA
                    res = [eq1,eq2]
                    return res
                        #self.h_out=self.h_in
                x0,y0 = 1341,12 # Initialisation de la recherche des solutions numériques
                sol_ini = [x0,y0]
                
                
                # print(self.Outlet_Pvsat)
        
                x=fsolve(syst, sol_ini)
                # print("Résultats x=",x)
          
                # #self.T_Outlet=12
            
            
                # print("CC.Outlet.HA recalculée",self.Outlet.HA)
             
                               
                # print("self.Outlet_HR=",self.Outlet_HR)
                # print("self.Outlet.HA=",self.Outlet.HA)
                
                # print("self.T_Outlet=",self.T_Outlet)
                # # self.Outlet.h=air_humide_NB.Air4_Hs(self.T_Outlet, self.Inlet.P, self.Outlet.HA/1000)
                # print("self.Outlet.h NB=",self.Outlet.HA)
                self.Outlet.h=air_humide.Enthalpie(self.T_Outlet, self.Outlet.HA)
                # print("self.Outlet.h ZHA=",self.Outlet.h) 
            
        
        # '''Cas où l'HA de l'air à traiter est inférieure l'HA de consigne'''
        #         ''' Avec refroidissement sensible sans déshu '''
        elif self.Inlet.HA<=self.HA_target and self.T_inlet>=self.T_target:
            self.Eff=(self.T_sat-self.T_target)/(self.T_inlet-self.T_sat)
            self.FB=1-self.Eff
            self.Outlet.h=air_humide_NB.Air4_Hs(self.T_target, self.Inlet.P, self.Inlet.HA/1000)
            self.Outlet.HA=self.Inlet.HA
        
        
         # ''' sans aucune action de la Coil froide (Pas de traitement à faire) '''
        else:
            self.Outlet.h=self.Inlet.h
            self.Outlet.HA=self.Inlet.HA
            self.Eff=0
            self.FB=1-self.Eff
            # print('CAS 5')
            
              
       
        # '''Test que la consigne de déshu est située entre HA de l'air humide et HA_sat à la surface de la Coil froide'''
        # # if self.Déshutype="Droite_sat":
        # if self.Inlet.HA>=self.HA_target and self.HA_target>=self.HA_sat:
          
        #     self.Eff=(self.Inlet.HA-self.Outlet.HA)/(self.Inlet.HA-self.HA_sat)
        #     self.FB=1-self.Eff
        #     self.Outlet.h=self.Inlet.h-self.Eff*(self.Inlet.h-self.h_sat)
        #     self.T_Outlet=air_humide_NB.Air3_Tdb(self.HA_target/1000, self.Inlet.P, self.Outlet.h)
            
        #     # print('CAS 1')
            
        #     #'''cas où après la transormation, la température de l'air traité est supérieure à la température de consigne'''
           
        #     # if self.T_Outlet>=self.T_target:
        #     #     self.Inlet.h=self.Outlet.h
        #     #     self.T_inlet=self.T_Outlet
        #     #     self.Eff=(self.T_target-self.T_sat)/(self.T_inlet-self.T_sat)
        #     #     self.FB=1-self.Eff
        #     #     self.Outlet.h=self.h_sat+self.Eff*(self.Inlet.h-self.h_sat)
        #     #     self.Outlet.HA=self.HA_sat+self.Eff*(self.HA_target-self.HA_sat)
              
        #         # print('CAS 2')
                
                
        #      #Air exterieur compris entre HA_sat et HA_Target et T_air extérieur > T_target   
       
        # elif self.Inlet.HA>self.HA_sat and self.Inlet.HA<=self.HA_target and self.T_inlet>=self.T_target:
        #     self.Eff=(self.T_target-self.T_sat)/(self.T_inlet-self.T_sat)
        #     self.FB=1-self.Eff
        #     self.Outlet.h=self.h_sat+self.Eff*(self.Inlet.h-self.h_sat)
        #     self.Outlet.HA=self.HA_sat+self.Eff*(self.HA_target-self.HA_sat)
        #     #self.Outlet.h=air_humide_NB.Air4_Hs(self.T_target, self.Inlet.P, self.Inlet.HA/1000)
        #     #self.Outlet.HA=self.Inlet.HA
        #     # print('CAS 3')
            
        # # '''Cas où l'HA de l'air à traiter est inférieure à l'HA_sat à la surface de la Coil'''
        # #         ''' Avec refroidissement sensible sans déshu '''
        # elif self.Inlet.HA<=self.HA_sat and self.T_inlet>=self.T_target:
        #     self.Eff=(self.T_sat-self.T_target)/(self.T_inlet-self.T_sat)
        #     self.FB=1-self.Eff
        #     self.Outlet.h=air_humide_NB.Air4_Hs(self.T_target, self.Inlet.P, self.Inlet.HA/1000)
        #     self.Outlet.HA=self.Inlet.HA
        #     #print('CAS 4')
            
        #     ''' sans aucune action de la Coil froide (Pas de traitement à faire) '''
        # else:
        #     self.Outlet.h=self.Inlet.h
        #     self.Outlet.HA=self.Inlet.HA
        #     self.Eff=0
        #     self.FB=1-self.Eff
        #     # print('CAS 5') 
        
        
        
        
        
        self.Outlet.P=self.Inlet.P-self.P_drop
        # print("self.Outlet.P",self.Outlet.P)  
         
         
        #self.m_as=(self.Inlet.F_kgs)/air_humide_NB.Air3_Vs(self.Inlet.HA/1000,self.Inlet.P,self.Inlet.h) #[m3/s] / [m3/kg air sec]  = [kg air sec/s]
        self.m_as=(self.Inlet.F_kgs)/(1+(self.Inlet.HA/1000))
        #print("self.m_as=",self.m_as)
        self.Qth=(self.Outlet.h-self.Inlet.h)*self.m_as       
        #self.Outlet.F_kgs=self.m_as*air_humide_NB.Air3_Vs(self.Outlet.HA/1000,self.Outlet.P,self.Outlet.h) #[kg air sec/s] * [m3/kg air sec] =[m3/s]
        self.Outlet.F_kgs=self.m_as*(1+(self.Outlet.HA/1000))
        #print("self.Inlet.F_kgs=",self.Inlet.F_kgs)
        #print("self.Outlet.F_kgs=",self.Outlet.F_kgs)
        
        
 
           
            
            


