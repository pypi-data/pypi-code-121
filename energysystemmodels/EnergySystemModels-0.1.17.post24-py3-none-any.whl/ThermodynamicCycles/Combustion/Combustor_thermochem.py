#pip install thermochem
#http://garfield.chem.elte.hu/Burcat/BURCAT.THR

from thermochem import burcat, combustion
from ThermodynamicCycles.FluidPort.FluidPort import FluidPort
from CoolProp.CoolProp import PropsSI
import pandas as pd 

# from scipy import *
# from pylab import *
# #from scipy.optimize import bisect   
# from scipy.optimize import fsolve  

# import numpy as np

class Object:
    def __init__(self):
        self.Inlet=FluidPort() 
        self.Outlet=FluidPort()
        self.fuel=None
        self.burca_name=None
        self.phi=None
        self.AIR_EXCESS=None
        self.products_O2_molRatio=None
        self.fuel_Sdensity=None #in kg/m3 at 101325 Pa, 273.15+15 °C
        
        #Fuel Flow rate
        self.F_fuel_Sm3h=None
        self.F_fuel_m3h=None
        self.F_fuel_kgh=None
        self.F_fuel_kgs=None
        self.Nominal_Power_kW=None

        #Heating value
        self.LHV_kJmol=None
        self.LHV_kJkg=None
        self.LHV_kWhJkg=None
        self.LHV_kWhSm3=None

        self.HHV_kJmol=None
        self.HHV_kJkg=None
        self.HHV_kWhkg=None
        self.HHV_kWhSm3=None

        self.Ti_air=None #température d'entrée d'air
        self.Tflame=None
        self.Tflame_degC=None
        self.air_mm=None

        #output data
        self.df=[]

    def calculate (self):
        #calcul de la température d'air
        self.Ti_air=PropsSI('T','P',self.Inlet.P,'H',self.Inlet.h,self.Inlet.fluid) # K
        #print("self.Ti_air=",self.Ti_air)

        db = burcat.Elementdb()

        if self.fuel=="methane" or self.fuel=="CH4" or self.fuel=="NG" or self.fuel=="GN" or self.fuel=="Gaz Naturel":
            self.burca_name="CH4   RRHO"
        self.fuel= db.getelementdata(self.burca_name)

        #print(self.fuel.elements)
        #print(self.fuel.cp,"J/kg K at 298 K")
        #print(self.fuel.cp_(273.15+1100),"J/kg K at T in K")
        self.fuel_Sdensity=self.fuel.density(101325, 273.15+15)

        #*****************************calcul de l'excés d'air********************************************
        if self.products_O2_molRatio is not None:
            #balance  at phi=1
            bal0=combustion.balance(self.fuel, 1, 1)
            #print("bal0[0]['O2']",bal0[0]['O2'])
            self.phi=(1-self.products_O2_molRatio*(1+3.76))/(1+(self.products_O2_molRatio/bal0[0]['O2']))
            #print("self.phi = ",self.phi)
           
        if self.AIR_EXCESS is not None:
            self.phi=1/((self.AIR_EXCESS)+1)
            #print("self.phi=",self.phi)
        if self.phi is not None:
            self.AIR_EXCESS=((1/self.phi)-1)
            #print("AIR_EXCESS= ",self.AIR_EXCESS)

        #***************************Calcul du pouvoir calorifique et les propriétés de la réaction********************************************
        combustor = combustion.SimpleCombustor(self.fuel,self.phi,db)
        #print("cp product",round(combustor.products.cp, 6),'J/kg-K')
        #print("heat of combustion",round(combustor.heat_of_comb(self.Ti_air), 2),'J/kg of fuel at Ti air')
        
        self.LHV_kWhkg=round(combustor.heat_of_comb(self.Ti_air)/3600000, 2)
        self.LHV_kJmol=round(combustor.heat_of_comb(self.Ti_air)/1000*self.fuel.mm, 2)
        self.LHV_kJkg=round(combustor.heat_of_comb(self.Ti_air)/1000, 2)
        self.LHV_kWhSm3=self.LHV_kWhkg*self.fuel_Sdensity
        if self.burca_name=="CH4   RRHO":
            self.HHV_kWhkg=self.LHV_kWhkg*1.109
            self.HHV_kJmol=self.LHV_kJmol*1.109
            self.HHV_kJkg=self.LHV_kJkg*1.109
            self.HHV_kWhSm3=self.LHV_kWhSm3*1.109
        #print(combustor.reactants)
        #print(combustor.products)

        #Combustion balance
        am=1 #1 mol of fuel
        bal=combustion.balance(self.fuel, am, self.phi)
        #print(bal)
        self.products_O2_molRatio=bal[1]['O2']/(bal[0]['fuel']+bal[0]['O2']+bal[0]['N2'])
        #print("products_O2_molRatio",self.products_O2_molRatio)
        self.AIR_EXCESS=((1/self.phi)-1)
        #print("self.phi=",self.phi)
        #print("AIR_EXCESS= ",self.AIR_EXCESS)

        #Calculate Heat Power and adiabatic temperature
        self.Tflame=round(combustor.adiabatic_flame_temp(self.Ti_air)[0], 1)
        self.Tflame_degC=round(combustor.adiabatic_flame_temp(self.Ti_air)[0]-273.15,1)
     
        
        #print(combustor.reactants.mm)
        #print(combustor.products.mm)
        #print(bal[0]['fuel'])
        #print(bal[0]['O2'])

        db2 = burcat.Elementdb()
        self.air = db2.getelementdata("AIR")
        self.air_mm=self.air.mm
        print(self.air_mm)

        if self.Nominal_Power_kW is None:
            self.F_air_mols=self.Inlet.F_kgs/self.air_mm/(1+3.76)
            #print(self.F_air_mols)
            self.F_fuel_mols=self.F_air_mols*bal[0]['fuel']/bal[0]['O2']
            #print(self.F_fuel_mols)
            self.F_fuel_kgs=self.F_fuel_mols*self.fuel.mm
            self.F_fuel_Sm3s=self.F_fuel_kgs/self.fuel_Sdensity
            self.F_fuel_Sm3h=self.F_fuel_Sm3s*3600

            #print(self.F_fuel_kgs)
            #bal2=combustion.balance(self.fuel, self.F_fuel_mols, self.phi)
            #print(bal2)
            
            
            self.Q_comb_HHV=self.HHV_kJkg*self.F_fuel_kgs*1000
            #print(self.Q_comb_LHV,"W")
            #print("self.HHV_kJkg",self.LHV_kJkg)

        
        #*********************************************recalcul du débit de combustible pour une puissance données*****************************
        if self.Nominal_Power_kW is not None:
            self.Q_comb_HHV=self.Nominal_Power_kW*1000
            self.F_fuel_kgs=self.Q_comb_HHV/1000/self.HHV_kJkg
            self.F_fuel_mols=self.F_fuel_kgs/self.fuel.mm
            #recalcul du nb mol air
            self.F_air_mols=self.F_fuel_mols/(bal[0]['fuel']/bal[0]['O2'])
            #recalcul du débit d'air
            self.Inlet.F_kgs=self.F_air_mols*(self.air_mm*(1+3.76))

        self.F_fuel_Sm3s=self.F_fuel_kgs/self.fuel_Sdensity
        self.F_fuel_Sm3h=self.F_fuel_Sm3s*3600
        self.Q_comb_LHV=self.LHV_kJkg*self.F_fuel_kgs*1000

        self.F_products_kgs=self.F_fuel_kgs+self.Inlet.F_kgs
        print('self.F_products_kgs*combustor.products.cp dT(W) ',self.F_products_kgs,combustor.products.cp,(self.Tflame_degC-110))

        self.df = pd.DataFrame({'Boiler': [self.fuel,self.F_fuel_Sm3h,self.F_fuel_kgs,self.fuel.mm,self.fuel_Sdensity,self.HHV_kWhSm3,self.products_O2_molRatio,self.phi,self.AIR_EXCESS,self.Q_comb_LHV,self.Q_comb_HHV,self.Tflame_degC,self.Inlet.F_kgs], },
                      index = ['fuel','F_fuel_Sm3h','F_fuel_kgs','molar mass (kg/mol)',"fuel_Sdensity (Kg/Sm3)",'HHV_kWhSm3','products_O2_molRatio','phi','AIR_EXCESS','Q_comb_LHV(W)','Q_comb_HHV(W)','Tflame_degC','Inlet.F_kgs'])
       

        #N2 : 28,0134 g/mol
       # O2 : 32 g/mol
      # CH4 : 16,04 g/mol


        

            
            
            
            


