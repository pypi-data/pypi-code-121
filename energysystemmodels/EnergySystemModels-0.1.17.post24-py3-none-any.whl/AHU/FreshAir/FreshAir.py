from AHU.air_humide import air_humide
from AHU.air_humide import air_humide_NB
from AHU.AirPort.AirPort import AirPort



        

class Object:
    def __init__(self):
        
        self.Inlet=AirPort() 
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
        self.m_vol=0 #Débit volumique "m3/h
        self.m_as=0
        
    def calculate(self):
        
        self.F_kgs = self.m_vol * air_humide.rho_ah(self.T, self.HR_FreshAir, self.P)/3600 #kg/s
        # self.F_kgs = self.F_kgs/3600 #m3/s
        #Connecteur entree
        self.P=self.Inlet.P
                 
        self.Pvsat=air_humide.Pvs(self.T)
       # print("Pvsat=",self.Pvsat)
        self.HA=air_humide.HA(self.Pvsat,self.HR_FreshAir,self.P)
       # print("HA=",self.HA)
        self.T_hum=air_humide.Tw(self.T,self.HR_FreshAir)
      #  print("self.T_hum=",self.T_hum)
        self.h=air_humide.Enthalpie(self.T, self.HA)
      #  print("self.h=",self.h)
        self.m_as=(self.F_kgs)/(1+(self.HA/1000))
      
      #connecteur   
      
        self.Inlet.HA=self.HA
        #self.Inlet.P=
        self.Inlet.h=self.h
        self.Inlet.F_kgs=self.F_kgs
        
        self.Outlet.HA=self.Inlet.HA
        self.Outlet.P=self.Inlet.P
        self.Outlet.h=self.Inlet.h
        self.Outlet.F_kgs=self.Inlet.F_kgs
        self.T_outlet=air_humide_NB.Air3_Tdb(self.Outlet.HA/1000,self.Outlet.P,self.Outlet.h)
        
    
    
    



