#conda install --channel cantera/label/dev cantera
#conda install --channel cantera cantera
import cantera as ct
import numpy as np

class combustor:
    def __init__(self):
        self.Tcomb=0 #Température initiale de combustion °C ?
        self.Pcomb=101325
        #parameter:
        self.EXCESS_AIR=0 #%
        self.phi=1/(1+self.EXCESS_AIR/100)
        print("self.phi",self.phi)
        
    def calculer(self):
     
        gas = ct.Solution('gri30.cti')
              
        # Set reactants state
        gas.TPX = (15+273.15),101325,{'CH4':1}
        N_rho=gas.density
        print(N_rho,"kg/Nm3")
        print(gas.density)
        gas.TPX = (self.Tcomb+273.15),self.Pcomb,{'CH4':1, 'O2':2/self.phi, 'N2':2*3.76/self.phi}
        
        print(gas.density)
        print(gas())
        
        print("gas.T_avant_combustion=",gas.T)
        gas.equilibrate('HP')
        print("gas.T=",gas.T)
        
        print(gas())
        
        r = gas.reaction(2) # get a Reaction object
        print(r.reactants)
        print(r.products)
        print(r.rate)
        
        
        # Set reactants state
        gas.TPX = 298, 101325, 'CH4:1, O2:2'
        h1 = gas.enthalpy_mass
        
        Y_CH4 = gas['CH4'].Y[0] # returns an array, of which we only want the first element
        print("Y_CH4",gas['CH4'].Y[0])
        
        # set state to complete combustion products without changing T or P
        gas.TPX = None, None, 'CO2:1, H2O:2' 
        h2 = gas.enthalpy_mass
        
        print('LHV = {:.3f} kWh/Nm3'.format(-(h2-h1)/Y_CH4/1e6/3.6*N_rho))
       # LHV = 50.026 MJ/kg
       
       

        water = ct.Water()
       # Set liquid water state, with vapor fraction x = 0
        water.TQ = 298, 0
        h_liquid = water.h
        # Set gaseous water state, with vapor fraction x = 1
        water.TQ = 298, 1
        h_gas = water.h
        
        # Calculate higher heating value
        Y_H2O = gas['H2O'].Y[0]
        print('HHV = {:.3f} kWh/kg'.format(-(h2-h1 + (h_liquid-h_gas) * Y_H2O)/Y_CH4/1e6/3.6*N_rho))


    
    # def __init__(self):
    #     
    #     self.fuel_m_flow=0.016042459999999998 #kg/s
    #     
    #     self.Tfume=200
    #     self.Heat_losses_ratio=5
    #     self.Heat_losses=0
    #     self.Q_PCS=0 #puissance de la chaudière en kW PCS
        
    #     self.Qu=0
    #     self.PCI_Eff=0
    #     self.PCS_Eff=0
    
        
    #     self.reactants="reactants" #= {'fuel': am, 'N2': 0, 'O2': 0}
    #     self.products="products" #= {'N2': 0, 'CO2': 0, 'H2O': 0, 'O2': 0}
        
    #     self.fuel_mol_flow=0 #mol/s = self.fuel_m_flow/self.fuel_mmol
    #     self.fuel_mmol=1 #masse molaire kg/mol
    #     self.fuel="méthane"
    #     self.Nfuel_density=0 #(p, T) Density in kg/Nm³.
    #     self.fuel_NV_flow=0 #Nm3/s

        
    #     self.Tflame=0 #°C
    #     self.spec_heat_of_comb=0 #KWh/kg
    #     self.PCI_kWh_Nm3=0 #"kWh/Nm³
    #     self.O2_mol_ratio=0

    # def calculer(self):
        
    #     # db = Elementdb()
    #     # fuels = db.getmixturedata([("CH4   RRHO", 0.9168),("C2H6", 0.0686),("C3H8", 0.0070),("C4H10 n-butane", 0.0011)])
        
    #     # combustor = Combustor(fuels, 1, db)
    #     # print(combustor.adiabatic_flame_temp(300)-273.15)
        
    #     db = Elementdb()
        
    #     #créer le combustible
    #     self.fuel = db.getelementdata("CH4   RRHO")
    #     #self.fuel = db.getelementdata("C4H10 n-butane")
        
        
    #     print("               propriétés thermodynamiques:     ")
    #     #masse volumique:
    #     self.Nfuel_density=self.fuel.density(101325,15+273.15)
    #     print("masse vol combustible:",round(self.Nfuel_density,3),"kg/Nm³")
    #     #masse molaire:
    #     self.fuel_mmol=self.fuel.mm
    #     print("masse mol combustible:",round(self.fuel_mmol,3),"kg/mol")
    #     #calcul du débit molaire
    #     print("débit massique combustible :",round(self.fuel_m_flow,3), "kg/s")
    #     self.fuel_mol_flow=self.fuel_m_flow/self.fuel_mmol
    #     print("débit mol combustible: ",round(self.fuel_mol_flow,3),"mol/s")
    #     #débit volumique
    #     self.fuel_NV_flow=self.fuel_m_flow/self.Nfuel_density
    #     print("débit volumique",round(self.fuel_NV_flow,3),"Nm3/s",round(self.fuel_NV_flow*3600,2),"Nm3/h")
    #     print("   ")
        
        
        
        
        
    #     ######################"combustion############################
        
    #     combustor2 = SimpleCombustor(self.fuel, self.phi, db)
       
    #     print("               propriétés thermochimiques:     ")
    #     self.spec_heat_of_comb=combustor2.heat_of_comb(self.Tcomb+273.15)/3600000
    #     self.PCI_kWh_Nm3=self.spec_heat_of_comb*self.Nfuel_density
        
        
    #     print("PCI du combustible : ",round(self.spec_heat_of_comb,3),"kWh/kg",round(self.PCI_kWh_Nm3,3),"kWh/Nm³")
    #     self.heat_of_comb=self.spec_heat_of_comb*3600*self.fuel_m_flow #(kJ/kg)*(kg/s)
    #     print("chaleur de combustion PCI:",round(self.heat_of_comb,2),"kW")
        
        
    #     self.Tflame=combustor2.adiabatic_flame_temp(self.Tcomb+273.15)[0]-273.15
    #     print("Temp de Flamme:",round(self.Tflame,1),"°C")
    #     print("      ")     
            
    #    # print("cp J/kg-K",self.fuel.cp_(self.Tcomb+273.15))
       
    #     print("               Produits de combustion:     ")
        
    #     EqEquilibre=balance(self.fuel,self.fuel_mol_flow,self.phi)
    #     self.products=EqEquilibre[1]
    #     print("produits de combustion : ",self.products)
    #     self.reactants=EqEquilibre[0]
    #     print("mélange réactif : ",self.reactants)
        
    #     print("CO2=",round(EqEquilibre[1]['CO2'],3),"mol/s")
    #     print("O2=",round(EqEquilibre[1]['O2'],3),"mol/s")
    #     print("H2O=",round(EqEquilibre[1]['H2O'],3),"mol/s")
    #     print("N2=",round(EqEquilibre[1]['N2'],3),"mol/s")
    #     products_mol_flow=(EqEquilibre[1]['O2']+EqEquilibre[1]['CO2']+EqEquilibre[1]['N2']+EqEquilibre[1]['H2O'])
    #     dry_products_mol_flow=(EqEquilibre[1]['O2']+EqEquilibre[1]['CO2']+EqEquilibre[1]['N2'])
    #     self.O2_mol_ratio=EqEquilibre[1]['O2']/products_mol_flow
        
    #     print("taux d'O2 dans les fummée:",round(self.O2_mol_ratio*100,2),"%")
        
        
        
    #     produit = db.getmixturedata([("N2  REF ELEMENT",EqEquilibre[1]['N2']),("O2 REF ELEMENT",EqEquilibre[1]['O2']),("CO2",EqEquilibre[1]['CO2']),("H2O",EqEquilibre[1]['H2O'])])
    #     print("fummée:",produit)
    #     dry_produit = db.getmixturedata([("N2  REF ELEMENT",EqEquilibre[1]['N2']),("O2 REF ELEMENT",EqEquilibre[1]['O2']),("CO2",EqEquilibre[1]['CO2'])])
    #     print(produit.cp_(self.Tflame+273.15))
    #     print(produit.cp_(self.Tcomb+273.15))
        
    #     print(produit.mm,"kg/mol")
    #     products_m_flow=produit.mm*products_mol_flow
    #     dry_products_m_flow=dry_produit.mm*dry_products_mol_flow
    #     print(products_m_flow,"kg/s")
        
    #    # self.Q_PCS=products_m_flow/1000*(produit.cp_(self.Tflame+273.15)*(self.Tflame+273.15)-produit.cp_(self.Tcomb+273.15)*(self.Tcomb+273.15))
    #    # print(self.Q_PCS,"kW")
        
        
       
    #     self.Q_PCS=(products_m_flow/1000*produit.h(self.Tflame+273.15)-dry_products_m_flow/1000*dry_produit.h(0+273.15))
    #     print("chaleur de combustion : ",round(self.Q_PCS,3),"kW PCS")
    #     print("PCI/PCS",self.heat_of_comb/self.Q_PCS)
        
    #     self.Heat_losses=(self.Heat_losses_ratio/100)*self.Q_PCS
    #     self.Qu=products_m_flow/1000*(produit.h(self.Tflame+273.15)-produit.h(self.Tfume+273.15))
    #     print("self.Qu=",self.Qu)
    #     self.PCI_Eff=self.Qu/self.heat_of_comb
    #     self.PCS_Eff=self.Qu/self.Q_PCS
    #     print("self.PCI_Eff",self.PCI_Eff)
    #     print("self.PCS_Eff",self.PCS_Eff)
        
    #     #print(Methane.elements)
    #     #Cp du méthane à en  J/kg K at 298 K (Reference T)
    #     #print(Methane.cp)
    #     # Computes the total enthalpy in J/kg
    #     #print(Methane.h(300))
        
    # def __str__(self): 
    #     return 'Qu: '+self.Qu+'\nself.PCS_Eff: '+self.PCS_Eff 

objetcombustion=combustor()
objetcombustion.calculate()


