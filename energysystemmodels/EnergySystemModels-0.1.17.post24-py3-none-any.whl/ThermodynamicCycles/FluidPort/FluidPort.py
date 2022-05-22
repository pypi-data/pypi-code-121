from CoolProp.CoolProp import PropsSI

class FluidPort:
    def __init__(self):
        self.F_kgs=None #0
        self.P = None # 101325
        self.h = None #10000
        self.fluid = None #"ammonia"
        
    def propriete(self,Pro,I1,ValI1,I2,ValI2):
        result=PropsSI(Pro, I1, ValI1, I2, ValI2, self.fluid)
        return result