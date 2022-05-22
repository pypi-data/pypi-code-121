from AHU.air_humide import air_humide
from AHU.air_humide import air_humide_NB
from AHU.AirPort.AirPort import AirPort



        

class Object:
    def __init__(self):
        
        self.Inlet1=AirPort() 
        self.Inlet2=AirPort() 
        self.Outlet=AirPort()
        self.id=1
        self.T=5
        self.HR_FreshAir = 60
        self.F_kgs = 10000
        self.Pvsat=0
        self.HA=0
        self.T_hum=0
        self.h=0
        self.P=101325
        
        self.m_as=0
        self.m_as1=0
        self.m_as2=0
        
        
    def calculate(self):
        
        # self.F_kgs = self.m_vol * air_humide.rho_ah(self.T, self.HR_FreshAir, self.P)/3600 #kg/s
        # self.F_kgs = self.F_kgs/3600 #m3/s
        #Connecteur entree
                        
        self.Pvsat=air_humide.Pvs(self.T)
       # print("Pvsat=",self.Pvsat)
        self.HA=air_humide.HA(self.Pvsat,self.HR_FreshAir,self.P)
       # print("HA=",self.HA)
        self.T_hum=air_humide.Tw(self.T,self.HR_FreshAir)
      #  print("self.T_hum=",self.T_hum)
        self.h=air_humide.Enthalpie(self.T, self.HA)
      #  print("self.h=",self.h)
        
        self.m_as1=self.Inlet1.F_kgs/(1+self.Inlet1.HA)
        self.m_as2=self.Inlet2.F_kgs/(1+self.Inlet2.HA)

        #connecteur   
      
        #self.Inlet1.HA=self.HA
        #self.Inlet.P=
        self.Outlet.HA=(self.Inlet1.HA*self.m_as1+self.Inlet2.HA*self.m_as2)/(self.m_as1+self.m_as2)
        self.Outlet.P=min(self.Inlet1.P,self.Inlet2.P)
        self.Outlet.h=(self.Inlet1.h*self.m_as1+self.Inlet2.h*self.m_as2)/(self.m_as1+self.m_as2)
        self.Outlet.F_kgs=self.Inlet1.F_kgs+self.Inlet2.F_kgs 
        self.T_outlet=air_humide_NB.Air3_Tdb(self.Outlet.HA/1000,self.Outlet.P,self.Outlet.h)
        self.m_as=(self.Outlet.F_kgs)/(1+self.Outlet.HA/1000)
    
    
    



