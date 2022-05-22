from AHU.air_humide import air_humide
from AHU.air_humide import air_humide_NB

from AHU.AirPort.AirPort import AirPort

class Object:
    def __init__(self):
        self.Inlet=AirPort() 
        self.Outlet=AirPort()
        self.P=0
        self.P_drop=0
        self.id=2
        # données air neuf
        self.T_in=0
        self.h_in=0
        self.HA_in=12
        self.F_kgs=0
        self.m_as=0
        
        #consigne
        self.T_out_target=20
        # calcul sortie Coil
        self.h_out=0
        self.Qth=12
        self.HR_out=0
       
        
    def calculate(self):
        
          #connecteur  
        self.Outlet.P=self.Inlet.P-self.P_drop
      
        self.HA_in=self.Inlet.HA
        self.P=self.Inlet.P
        self.h_in=self.Inlet.h
        self.F_kgs=self.Inlet.F_kgs
        # print("cond self.F_kgs",self.F_kgs)
        self.T_in=air_humide_NB.Air3_Tdb(self.HA_in/1000,self.Inlet.P,self.h_in)
        self.m_as=(self.F_kgs)/(1+self.HA_in/1000) #[kg air sec/s]
        ''' Témpérature fluide entré Coil < Température consigne -> Rechauffement sensible'''
        if self.T_out_target>self.T_in:
            
            self.h_out=air_humide.Enthalpie(self.T_out_target,self.HA_in)
            # self.h_out=air_humide_NB.Air2_Hs(self.T_out_target, air_humide_NB.Air4_RH(self.T_out_target,self.Outlet.P, self.HA_in/1000), self.Outlet.P) 
          #  print("h_out=",self.h_out)
            self.m_as=(self.F_kgs)/(1+self.HA_in/1000) # [kg air sec/s]
           # print("self.m_as=",self.m_as,"self.Inlet.P=",self.Inlet.P,"self.F_kgs=",self.F_kgs)
            self.Qth=(self.h_out-self.h_in)*self.m_as
           # print("self.Qth=",self.Qth)
            self.HR_out=air_humide.HR(air_humide.Pvs(self.T_out_target),self.HA_in,self.Outlet.P) #parametrer la pression
           # print("self.HR_out=",self.HR_out)
        
            ''' Température fluide entrée Coil > température de consigne -> Aucune action'''    
        else:
            self.h_out=self.h_in
            self.Qth=0
 
              
       
        #connecteur   
      
          
        self.Outlet.HA=self.Inlet.HA
        
        self.Outlet.h=self.h_out
        
        self.Outlet.F_kgs=self.m_as*(1+self.Outlet.HA/1000)  #[kg air sec/s] * [m3/kg air sec] =[m3/s]
#
        # print(self.Outlet.HA/1000, self.Outlet.P, self.Outlet.h)       
        # self.Twb_out=air_humide_NB.Air3_Twb(self.Outlet.HA/1000, self.Outlet.P, self.Outlet.h)


