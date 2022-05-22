from AHU.air_humide import air_humide



class AirPort:
    def __init__(self):
        self.F_kgs=0 # d'air d'air
        self.P = 101325 # pression
        self.h = 10000 # enthalpie spéc
        self.HA = 0 # Humidité absolue
        
    def propriete(self):
        self.result="HR,Pvs,T="
        self.T=air_humide.Temperature(self.h, self.HA)
        self.Pvs=air_humide.Pvs(self.T)
        self.HR=air_humide.HR(self.Pvs, self.HA, self.P)
        return self.result,self.HR,self.Pvs,self.T
    

