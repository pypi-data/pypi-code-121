#pip install CoolProp
#pip install -vvv --pre --trusted-host www.coolprop.dreamhosters.com --find-links http://www.coolprop.dreamhosters.com/binaries/Python/ -U --force-reinstall CoolProp
#pip install Cython
#pip install tkintertable

import os
import sys
sys.path.append("../..") # Adds higher directory to python Modules_CTA path.



from ThermodynamicCycles.Evaporator import Evaporator
from ThermodynamicCycles.Compressor import Compressor
from ThermodynamicCycles.Desuperheater import Desuperheater
from ThermodynamicCycles.Expansion_Valve import Expansion_Valve
from ThermodynamicCycles.Condenser import Condenser
from ThermodynamicCycles.Connect import Fluid_connect


from tkinter import*
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import CoolProp.CoolProp as CP
import CoolProp.Plots as CPP
import tkinter.ttk as ttk
from CoolProp.Plots import PropertyPlot

from tkintertable import TableCanvas, TableModel

class App:
    def __init__(self, master):
       
  ######################################Input#########################################################
 
        Couleur="#A6A094"
 
        LabelFrame_Input=LabelFrame(master, bg=Couleur,bd=1,text="données d'entrée")
        self.Label_FluidName=Label(LabelFrame_Input,bg=Couleur,text="Type de fluide")
        self.Label_FluidName.grid(row=1, column=1)
        self.comboFluid = ttk.Combobox(LabelFrame_Input,values=["1-Butene","Acetone"	,"Air"	,"Ammonia","Argon"	,"Benzene"	,"CarbonDioxide"	,"CarbonMonoxide","CarbonylSulfide"	,
"CycloHexane"	,"CycloPropane"	,"Cyclopentane"	,"D4"	,"D5"	,"D6"	,"Deuterium"	,"Dichloroethane"	,"DiethylEther"	,
"DimethylCarbonate"	,
"DimethylEther"	,
"Ethane"	,
"Ethanol"	,
"EthylBenzene"	,
"Ethylene"	,
"EthyleneOxide"	,
"Fluorine"	,
"HFE143m"	,
"HeavyWater"	,
"Helium"	,
"Hydrogen"	,
"HydrogenChloride"	,
"HydrogenSulfide"	,
"IsoButane"	,
"IsoButene"	,
"Isohexane"	,
"Isopentane"	,
"Krypton"	,
"MD2M"	,
"MD3M"	,
"MD4M"	,
"MDM"	,
"MM"	,
"Methane"	,
"Methanol"	,
"MethylLinoleate"	,
"MethylLinolenate"	,
"MethylOleate"	,
"MethylPalmitate"	,
"MethylStearate"	,
"Neon"	,
"Neopentane"	,
"Nitrogen"	,
"NitrousOxide"	,
"Novec649"	,
"OrthoDeuterium"	,
"OrthoHydrogen"	,
"Oxygen"	,
"ParaDeuterium"	,
"ParaHydrogen"	,
"Propylene"	,
"Propyne"	,
"R11"	,
"R113"	,
"R114"	,
"R115"	,
"R116"	,
"R12"	,
"R123"	,
"R1233zd(E)"	,
"R1234yf"	,
"R1234ze(E)"	,
"R1234ze(Z)"	,
"R124"	,
"R125"	,
"R13"	,
"R134a"	,
"R13I1"	,
"R14"	,
"R141b"	,
"R142b"	,
"R143a"	,
"R152A"	,
"R161"	,
"R21"	,
"R218"	,
"R22"	,
"R227EA"	,
"R23"	,
"R236EA"	,
"R236FA"	,
"R245ca"	,
"R245fa"	,
"R32"	,
"R365MFC"	,
"R40"	,
"R404A"	,
"R407C"	,
"R41"	,
"R410A"	,
"R507A"	,
"RC318"	,
"SES36"	,
"SulfurDioxide"	,
"SulfurHexafluoride"	,
"Toluene"	,
"Water"	,
"Xenon"	,
"cis-2-Butene"	,
"m-Xylene"	,
"n-Butane"	,
"n-Decane"	,
"n-Dodecane"	,
"n-Heptane"	,
"n-Hexane"	,
"n-Nonane"	,
"n-Octane"	,
"n-Pentane"	,
"n-Propane"	,
"n-Undecane"	,
"o-Xylene"	,
"p-Xylene"	,
"trans-2-Butene"	])
        self.fluid = self.comboFluid.get()
        self.comboFluid.grid(column=2, row=1)
        
        self.comboFluid.current(75)
        self.comboFluid.bind("<<ComboboxSelected>>", self.Afficher)

        self.Label_BP=Label(LabelFrame_Input,bg=Couleur,text="BP (bar) ")
        self.Label_BP.grid(row=2, column=1)
        # Tevap au lieu de BP
        self.Label_Tevap=Label(LabelFrame_Input,bg=Couleur,text="Tevap (°C) ")
        self.Label_Tevap.grid(row=2, column=1)

        DoubleVar_BP=DoubleVar(value=3.15)
        self.Spinbox_BP=Spinbox(LabelFrame_Input,format='%10.4f',increment=0.1,from_=0.001, to=100,textvariable=DoubleVar_BP,command=self.Afficher,wrap=True)
        self.Spinbox_BP.grid(row=2, column=2)
        #Tevap au lieu de BP
        DoubleVar_Tevap=DoubleVar(value=-0.001)
        self.Spinbox_Tevap=Spinbox(LabelFrame_Input,format='%10.4f',increment=0.1,from_=-200, to=200,textvariable=DoubleVar_Tevap,command=self.Afficher,wrap=True)
        self.Spinbox_Tevap.grid(row=2, column=2)

        # à remplacer par Tcond
        self.Label_HP=Label(LabelFrame_Input,bg=Couleur,text="HP (bar) ")
        self.Label_HP.grid(row=3, column=1)

        DoubleVar_HP=DoubleVar(value=11.6)
        self.Spinbox_HP=Spinbox(LabelFrame_Input,format='%10.4f',increment=0.1,from_=0.001, to=100, textvariable=DoubleVar_HP,command=self.Afficher,wrap=True)
        self.Spinbox_HP.grid(row=3, column=2)

        #Tcond remplace HP

        self.Label_Tcond=Label(LabelFrame_Input,bg=Couleur,text="Tcond (°C) ")
        self.Label_Tcond.grid(row=3, column=1)

        DoubleVar_Tcond=DoubleVar(value=40.0)
        self.Spinbox_Tcond=Spinbox(LabelFrame_Input,format='%10.4f',increment=0.1,from_=-100, to=300, textvariable=DoubleVar_Tcond,command=self.Afficher,wrap=True)
        self.Spinbox_Tcond.grid(row=3, column=2)


        self.Label_Surchauffe=Label(LabelFrame_Input,bg=Couleur,text="Surchauffe (°C) ")
        self.Label_Surchauffe.grid(row=4, column=1)

        self.Spinbox_Surchauffe=Spinbox(LabelFrame_Input,format='%10.4f',increment=0.1,from_=2, to=20,command=self.Afficher,wrap=True)
        self.Spinbox_Surchauffe.grid(row=4, column=2)

        self.Label_RendIs=Label(LabelFrame_Input,bg=Couleur,text="rendement isentropique (-) ")
        self.Label_RendIs.grid(row=5, column=1)
        
        self.Spinbox_RendIs=Spinbox(LabelFrame_Input,format='%10.4f',increment=0.1,from_=0.7, to=1,command=self.Afficher,wrap=True)
        self.Spinbox_RendIs.grid(row=5, column=2)

        self.Label_SSrefroid=Label(LabelFrame_Input,bg=Couleur,text="sous-refroidissement (°C) ")
        self.Label_SSrefroid.grid(row=6, column=1) 

        self.Spinbox_SSrefroid=Spinbox(LabelFrame_Input,format='%10.4f',increment=0.1,from_=2.0, to=20,command=self.Afficher,wrap=True)
        self.Spinbox_SSrefroid.grid(row=6, column=2)



        # self.ComboBoxRefComp = ttk.Combobox(LabelFrame_Input,values=["oui"	,"non"])
        # self.bool = self.ComboBoxRefComp.get()
        # self.ComboBoxRefComp.grid(column=1, row=9)
        # self.ComboBoxRefComp.current(0)
        # self.ComboBoxRefComp.bind("<<ComboboxSelected>>", self.Afficher)

        # if self.ComboBoxRefComp.get()=="oui" :
        self.Label_Tdischarge_target=Label(LabelFrame_Input,bg=Couleur,text="Tref_compresseur (°C) ")
        self.Label_Tdischarge_target.grid(row=7, column=1)
        DoubleVar_Tdischarge_target=DoubleVar(value=80)
        self.Spinbox_Tdischarge_target=Spinbox(LabelFrame_Input,format='%10.4f',increment=0.5,from_=-273.15, to=1000, textvariable=DoubleVar_Tdischarge_target,command=self.Afficher,wrap=True)
        self.Spinbox_Tdischarge_target.grid(row=7, column=2)
        
        
     

        self.Label_m=Label(LabelFrame_Input,bg=Couleur,text="débit du fluide (kg/s) ")
        self.Label_m.grid(row=8, column=1) 


        DoubleVar_m=DoubleVar(value=10.025)
        self.Spinbox_m=Spinbox(LabelFrame_Input,format='%10.4f',increment=0.01,from_=0.0001, to=400,textvariable=DoubleVar_m,command=self.Afficher,wrap=True)
        self.Spinbox_m.grid(row=8, column=2)
        
        LabelFrame_Input.grid(row=1, column=1)
####################################################################################################

        
        LabelFrame_CycleResults=LabelFrame(master, bg=Couleur,bd=1,text="Cycle thermodynamique")

        
##################################################################################################   
        
        #Affichage des résultats
        self.Label_T1=Label(LabelFrame_CycleResults,bg=Couleur,text="T1 (°C)")
        self.Label_T1.grid(row=8, column=1)

        self.Label_H1=Label(LabelFrame_CycleResults,bg=Couleur,text="H1 (KJ/kg)")
        self.Label_H1.grid(row=8, column=2)

        self.Label_S1=Label(LabelFrame_CycleResults,bg=Couleur,text="S1 (J/kg-K)")
        self.Label_S1.grid(row=8, column=3)    

        self.Label_P1=Label(LabelFrame_CycleResults,bg=Couleur,text="P1 (bar)")
        self.Label_P1.grid(row=8, column=4)      
        ###        
        self.Label_T2=Label(LabelFrame_CycleResults,bg=Couleur,text="T2 (°C)")
        self.Label_T2.grid(row=9, column=1)

        self.Label_H2=Label(LabelFrame_CycleResults,bg=Couleur,text="H2 (KJ/kg)")
        self.Label_H2.grid(row=9, column=2)
        
        self.Label_S2=Label(LabelFrame_CycleResults,bg=Couleur,text="S2 (J/kg-K)")
        self.Label_S2.grid(row=9, column=3)

        self.Label_P2=Label(LabelFrame_CycleResults,bg=Couleur,text="P2 (bar)")
        self.Label_P2.grid(row=9, column=4)  
        ###
       
        self.Label_T3is=Label(LabelFrame_CycleResults,bg=Couleur,text="T3is (°C)")
        self.Label_T3is.grid(row=11, column=1)

        self.Label_H3is=Label(LabelFrame_CycleResults,bg=Couleur,text="H3is (KJ/kg)")
        self.Label_H3is.grid(row=11, column=2)
            
        self.Label_S3is=Label(LabelFrame_CycleResults,bg=Couleur,text="S3is (J/kg-K)")
        self.Label_S3is.grid(row=11, column=3)

        self.Label_P3is=Label(LabelFrame_CycleResults,bg=Couleur,text="P3is (bar)")
        self.Label_P3is.grid(row=11, column=4)  
        ###

        self.Label_T3ref=Label(LabelFrame_CycleResults,bg=Couleur,text="T3ref (°C)")
        self.Label_T3ref.grid(row=12, column=1)

        self.Label_H3ref=Label(LabelFrame_CycleResults,bg=Couleur,text="H3ref (KJ/kg)")
        self.Label_H3ref.grid(row=12, column=2)
        
        self.Label_S3ref=Label(LabelFrame_CycleResults,bg=Couleur,text="S3ref (J/kg-K)")
        self.Label_S3ref.grid(row=12, column=3)

        self.Label_P3ref=Label(LabelFrame_CycleResults,bg=Couleur,text="P3ref (bar)")
        self.Label_P3ref.grid(row=12, column=4)  
        ###
        ###
        self.Label_To=Label(LabelFrame_CycleResults,bg=Couleur,text="To (°C)")
        self.Label_To.grid(row=13, column=1)

        self.Label_Ho=Label(LabelFrame_CycleResults,bg=Couleur,text="Ho (KJ/kg)")
        self.Label_Ho.grid(row=13, column=2)
        
        self.Label_So=Label(LabelFrame_CycleResults,bg=Couleur,text="So (J/kg-K)")
        self.Label_So.grid(row=13, column=3)
        
        self.Label_Po=Label(LabelFrame_CycleResults,bg=Couleur,text="Po (bar)")
        self.Label_Po.grid(row=13, column=4)  
        ###
        ###
        self.Label_T4=Label(LabelFrame_CycleResults,bg=Couleur,text="T4 (°C)")
        self.Label_T4.grid(row=14, column=1)

        self.Label_H4=Label(LabelFrame_CycleResults,bg=Couleur,text="H4 (KJ/kg)")
        self.Label_H4.grid(row=14, column=2)
        
        self.Label_S4=Label(LabelFrame_CycleResults,bg=Couleur,text="S4 (J/kg-K)")
        self.Label_S4.grid(row=14, column=3)

        self.Label_P4=Label(LabelFrame_CycleResults,bg=Couleur,text="P4 (bar)")
        self.Label_P4.grid(row=14, column=4)  
        ###
        ###
        self.Label_T5=Label(LabelFrame_CycleResults,bg=Couleur,text="T5 (°C)")
        self.Label_T5.grid(row=15, column=1)

        self.Label_H5=Label(LabelFrame_CycleResults,bg=Couleur,text="H5 (KJ/kg)")
        self.Label_H5.grid(row=15, column=2)
        
        self.Label_S5=Label(LabelFrame_CycleResults,bg=Couleur,text="S5 (J/kg-K)")
        self.Label_S5.grid(row=15, column=3) 

        self.Label_P5=Label(LabelFrame_CycleResults,bg=Couleur,text="P5 (bar)")
        self.Label_P5.grid(row=15, column=4)  
        ###
        ###
        self.Label_T6=Label(LabelFrame_CycleResults,bg=Couleur,text="T6 (°C)")
        self.Label_T6.grid(row=16, column=1)

        self.Label_H6=Label(LabelFrame_CycleResults,bg=Couleur,text="H6 (KJ/kg)")
        self.Label_H6.grid(row=16, column=2)
        
        self.Label_S6=Label(LabelFrame_CycleResults,bg=Couleur,text="S6 (J/kg-K)")
        self.Label_S6.grid(row=16, column=3) 

        self.Label_P6=Label(LabelFrame_CycleResults,bg=Couleur,text="P6 (bar)")
        self.Label_P6.grid(row=16, column=4)  
        ###

        ###

        self.Label_T7=Label(LabelFrame_CycleResults,bg=Couleur,text="T7 (°C)")
        self.Label_T7.grid(row=17, column=1)

        self.Label_H7=Label(LabelFrame_CycleResults,bg=Couleur,text="H7 (KJ/kg)")
        self.Label_H7.grid(row=17, column=2)
        
        self.Label_S7=Label(LabelFrame_CycleResults,bg=Couleur,text="S7 (J/kg-K)")
        self.Label_S7.grid(row=17, column=3)

        self.Label_P7=Label(LabelFrame_CycleResults,bg=Couleur,text="P7 (bar)")
        self.Label_P7.grid(row=17, column=4)  


        ###############################
        #Affichage des résultats##############################################""""
     
   
        LabelFrame_CycleResults.grid(row=1, column=2)

        LabelFrame_Results=LabelFrame(master, bg=Couleur,bd=1,text="résultats")
        
        self.Label_Qcomp=Label(LabelFrame_Results,bg=Couleur,text="Qcomp (kW)")
        self.Label_Qcomp.grid(row=1, column=1)

        self.Label_Qevap=Label(LabelFrame_Results,bg=Couleur,text="Qevap (kW)")
        self.Label_Qevap.grid(row=1, column=2)

        self.Label_EER=Label(LabelFrame_Results,bg=Couleur,text="EER")
        self.Label_EER.grid(row=1, column=3)

        self.Label_COP=Label(LabelFrame_Results,bg=Couleur,text="COP")
        self.Label_COP.grid(row=1, column=4)

        self.Label_Qdesurch=Label(LabelFrame_Results,bg=Couleur,text="Qdesurch")
        self.Label_Qdesurch.grid(row=2, column=1)

        self.Label_Qcond=Label(LabelFrame_Results,bg=Couleur,text="Qcond")
        self.Label_Qcond.grid(row=2, column=2)

        self.Label_QcondTot=Label(LabelFrame_Results,bg=Couleur,text="QcondTot")
        self.Label_QcondTot.grid(row=2, column=3)

        self.Label_Qlosses=Label(LabelFrame_Results,bg=Couleur,text="Qlosses")
        self.Label_Qlosses.grid(row=2, column=4)
        
        LabelFrame_Results.grid(row=2, column=1,columnspan=3)
        

##############################

        #ph_plot = CPP.PropertyPlot('Water','Ph')
        #ph_plot.savefig('enthalpy_pressure_graph_for_Water.png')


        ################"""

          # Create a container#######################################################################################"
        Frame_DiagAirHum = Frame(master,height=50)


# tracer les isoHumidité relaive...........................

        self.fluid=self.comboFluid.get()
        #print(self.fluid)

        self.Tcrit=CP.PropsSI("Tcrit",self.fluid)
        #print("Tcri")
        #print(self.Tcrit-273.15)

      
        
        print("print(self.comboFluid.get())",self.fluid)
        self.T_triple=CP.PropsSI("T_triple",self.fluid)
        #afficher la temp critique
        
        
        #print("Ttriple")
        #print(self.T_triple-273.15)
        
        #self.T=np.arange(self.T_triple-273.15,self.Tcrit-273.15,5)
   
        #self.isoS0 = []
        #for i in range(len(self.T)):
        #    self.isoS0.append(0)

        #self.isoS1 = []
        #for i in range(len(self.T)):
          #   self.isoS1.append(0)


            
        fig = Figure(figsize=(8, 5))#, dpi=96
        self.ax = fig.add_subplot(111)
    
        self.point1, = self.ax.plot(0,0,'H')
        self.point2, = self.ax.plot(0,0,'H')
        
        self.courbe_cycle, = self.ax.plot(0,0,'b:o')

     
        
        self.point3is, = self.ax.plot(0,0,'bo')
        self.point3ref, = self.ax.plot(0,0,'bo')
        self.pointo, = self.ax.plot(0,0,'H')
        self.point4, = self.ax.plot(0,0,'H')
        self.point5, = self.ax.plot(0,0,'H')

        #self.courbeTS0, = self.ax.plot(self.isoS0,self.T)
        #self.courbeTS1, = self.ax.plot(self.isoS1,self.T)
        self.courbeTS0, = self.ax.plot(1,1)
        self.courbeTS1, = self.ax.plot(1,1)
        
        #self.ax.legend()
        
        self.ax.set_xlim(0,41000)
        self.ax.set_ylim(self.T_triple-273.15,200)
        self.ax.set(xlabel='Etropie (J/kg-K)', ylabel='Température (°C)',title='diagramme TS')

        self.canvas = FigureCanvasTkAgg(fig,Frame_DiagAirHum)#master=master
        
        self.canvas.get_tk_widget().grid(row=1, column=1)
      
        Frame_DiagAirHum.grid(row=3, column=1,columnspan=3)


        
    def Afficher(self, event=None):
        

        #récupérer les données d'entrée
        self.fluid=self.comboFluid.get()

        #Afficher la Tcritique
        self.Tcrit=CP.PropsSI("Tcrit",self.fluid)
        self.T_triple=CP.PropsSI("T_triple",self.fluid)
        self.Label_FluidName.config(text="Type de fluide, Tcrit/Ttriple="+str(round(self.Tcrit-273.15,2))+"/"+str(round(self.T_triple-273.15,2))+" °C")

        
 
# Same for saturated vapor
        #####Evaporateur
        EVAP=Evaporator.Object()
        EVAP.fluid=self.fluid
        print("EVAP.fluid=",self.fluid)
        EVAP.Inlet.F_kgs=float(self.Spinbox_m.get())
        #EVAP.Inlet.P=1e5*float(self.Spinbox_BP.get()) remplacé par Tevap
        EVAP.Ti_degC=float(self.Spinbox_Tevap.get())
        EVAP.surchauff=float(self.Spinbox_Surchauffe.get())
        EVAP.Inlet.h= CP.PropsSI('H','P',1.5*1e5,'T',40+273.15,self.fluid)   #initialisation pour le calcul en boucle
        EVAP.calculate()

        self.Label_T1.config(text="EVAP.Tsv="+str(round(EVAP.Tsv-273.15,1))+" °C")           
        self.Label_H1.config(text="EVAP.Hsv="+str(round(EVAP.Hsv/1000,1))+" kJ/kg")
        self.Label_S1.config(text="EVAP.Ssv="+str(round(EVAP.Ssv/1000,1))+" kJ/kg-K")
        self.Label_P1.config(text="EVAP.Psv="+str(round(EVAP.Inlet.P/100000,2))+" bar")

        

        self.Label_T2.config(text="EVAP.To="+str(round(EVAP.To-273.15,1))+" °C")
        self.Label_H2.config(text="EVAP.Ho="+str(round(EVAP.Ho/1000,1))+" kJ/kg-K")        
        self.Label_S2.config(text="EVAP.So="+str(round(EVAP.So/1000,1))+" kJ/kg-K")
        self.Label_P2.config(text="EVAP.Po="+str(round(EVAP.Outlet.P/100000,2))+" bar")
        
        ######compresseur
     
        COMP=Compressor.Object()
        Fluid_connect(COMP.Inlet,EVAP.Outlet)
        #COMP.HP=1e5*float(self.Spinbox_HP.get())
        COMP.Tcond_degC=float(self.Spinbox_Tcond.get())
        COMP.IsenEff=float(self.Spinbox_RendIs.get())
        COMP.To=float(self.Spinbox_Tdischarge_target.get())
        COMP.Tdischarge_target=float(self.Spinbox_Tdischarge_target.get())
        COMP.calculate()

        print(COMP.F_kgs)
        
        
        
        self.Label_S3is.config(text="COMP.S3is="+str(round(COMP.S3is,1))+"J/kg-K")
        self.Label_T3is.config(text="COMP.T3is="+str(round(COMP.T3is-273.15,1))+" °C")
        self.Label_H3is.config(text="COMP.H3is="+str(round(COMP.H3is/1000,1))+" kJ/kg-K")  
        self.Label_P3is.config(text="COMP.P3is="+str(round(COMP.Outlet.P/100000,2))+" bar")       
        
        self.Label_H3ref.config(text="COMP.H3ref="+str(round(COMP.H3ref/1000,1))+" kJ/kg-K")
        self.Label_T3ref.config(text="COMP.T3ref="+str(round(COMP.T3ref-273.15,1))+" °C")
        self.Label_S3ref.config(text="COMP.S3ref"+str(round(COMP.S3ref/1000,1))+" kJ/kg-K")
        self.Label_P3ref.config(text="COMP.P3ref="+str(round(COMP.Outlet.P/100000,2))+" bar") 

        self.Label_To.config(text="COMP.To="+str(round(COMP.To-273.15,1))+" °C")
        self.Label_Ho.config(text="COMP.Ho="+str(round(COMP.Ho/1000,1))+" kJ/kg-K")
        self.Label_So.config(text="COMP.So="+str(round(COMP.So/1000,1))+" kJ/kg-K")
        self.Label_Po.config(text="COMP.Po="+str(round(COMP.Outlet.P/100000,2))+" bar") 


        ##################Desurchauffeur
        
        DESURCH=Desuperheater.Object()
        Fluid_connect(DESURCH.Inlet,COMP.Outlet)
      #  print(DESURCH.Inlet.P)
        DESURCH.calculate()

        self.Label_T4.config(text="DESURCH.Tsv="+str(round(DESURCH.Tsv-273.15,1))+" °C")
        self.Label_H4.config(text="DESURCH.Hsv="+str(round(DESURCH.Hsv/1000,1))+" kJ/kg-K")
        self.Label_S4.config(text="DESURCH.Ssv="+str(round(DESURCH.Ssv/1000,1))+" kJ/kg-K")
        self.Label_P4.config(text="DESURCH.Psv="+str(round(DESURCH.Inlet.P/100000,2))+" bar") 

                ##################condender
        COND=Condenser.Object()
        Fluid_connect(COND.Inlet, DESURCH.Outlet)
        COND.subcooling=float(self.Spinbox_SSrefroid.get())
        COND.calculate()

        self.Label_T5.config(text="COND.Tsl="+str(round(COND.Tsl-273.15,1))+" °C")
        self.Label_H5.config(text="COND.Hsl="+str(round(COND.Hsl/1000,1))+" kJ/kg-K")
        self.Label_S5.config(text="COND.Ssl="+str(round(COND.Ssl/1000,1))+" kJ/kg-K")
        self.Label_P5.config(text="COND.Psl="+str(round(COND.Inlet.P/100000,2))+" bar") 

        self.Label_T6.config(text="COND.To="+str(round(COND.To-273.15,1))+" °C")
        self.Label_H6.config(text="COND.Ho="+str(round(COND.Ho/1000,1))+" kJ/kg-K")    
        self.Label_S6.config(text="COND.So="+str(round(COND.So/1000,1))+" kJ/kg-K")
        self.Label_P6.config(text="COND.Po="+str(round(COND.Outlet.P/100000,2))+" bar") 

        ########détendeur
        
        DET=Expansion_Valve.Object()
        Fluid_connect(DET.Inlet,COND.Outlet)
        Fluid_connect(DET.Outlet,EVAP.Inlet)
        
        
        DET.calculate()
        Fluid_connect(EVAP.Inlet,DET.Outlet)
        EVAP.calculate()
        
       # print("BP=",DET.Outlet.P,EVAP.Inlet.P)
        
    

        H7 = COND.Ho
        self.Label_H7.config(text="DET.Ho="+str(round(DET.Outlet.h/1000,1))+" kJ/kg-K")

        # T7=CP.PropsSI('T','P',1e5*float(self.Spinbox_BP.get()),'H',H7,self.fluid)
        self.Label_T7.config(text="DET.To="+str(round(DET.To-273.15,1))+" °C")
        self.Label_S7.config(text="DET.So="+str(round(DET.So/1000,1))+" kJ/kg-K")
        self.Label_P7.config(text="DET.Po="+str(round(DET.Outlet.P/100000,2))+" bar") 

        #######Bilan thermique##############################"
        self.Label_Qcomp.config(text="Qcomp="+str(round(COMP.Qcomp/1000,1))+" kW")
        Qevap=-float(self.Spinbox_m.get())*(DET.Outlet.h-EVAP.Hsv)
        self.Label_Qevap.config(text="Qevap="+str(round(Qevap/1000,1))+" kW")
        
        if COMP.Qcomp!=0:
           EER=Qevap/COMP.Qcomp
        else:
           EER=0


        self.Label_EER.config(text="EER="+str(round(EER,1))+" ")

        Qdesurch=float(self.Spinbox_m.get())*(COMP.Ho-DESURCH.Hsv)
        self.Label_Qdesurch.config(text="Qdesurch="+str(round(Qdesurch/1000,1))+" kW")

        Qcond=float(self.Spinbox_m.get())*(DESURCH.Hsv-COND.Hsl)
        self.Label_Qcond.config(text="Qcond="+str(round(Qcond/1000,1))+" kW")

        QcondTot=float(self.Spinbox_m.get())*(COMP.Ho-COND.Hsl)
        self.Label_QcondTot.config(text="QcondTot="+str(round(QcondTot/1000,1))+" kW")

        if COMP.Qcomp!=0:
           COP=QcondTot/COMP.Qcomp
        else:
           COP=0

        
        self.Label_COP.config(text="COP="+str(round(COP,1))+" ")

        
        self.Label_Qlosses.config(text="Qlosses="+str(round(COMP.Qlosses/1000,1))+" kW")
        
        ##################################################"


        self.T=np.arange(self.T_triple-273.15,self.Tcrit-273.15,1) #éviter le point critique
        
        print("Tcrit=",self.Tcrit)
        
        print("self.T (k)=",self.T+273.15)
        


        
        #print(self.T)

        self.isoS0 = []
        for i in range(len(self.T)):
            self.isoS0.append(0)

        self.isoS1 = []
        for i in range(len(self.T)):
            self.isoS1.append(0)
         
        for i in range(0,len(self.T),1):
            self.isoS0[i]=CP.PropsSI('S','T',self.T[i]+273.15,'Q',0,self.fluid)
          
        for i in range(0,len(self.T),1):
            self.isoS1[i]=CP.PropsSI('S','T',self.T[i]+273.15,'Q',1,self.fluid)    

        #print(self.isoS0)
        
        self.Tcrit=CP.PropsSI("Tcrit",self.fluid)
        print('*************************************************self.Tcrit',self.Tcrit)
        
        
        self.ax.set_xlim(0,CP.PropsSI('S','Q',1,'T',self.T_triple,self.fluid)*1.5)
        self.ax.set_ylim(self.T_triple-273.15,(self.Tcrit-273.15)*2)
        
        self.courbeTS0.set_data(self.isoS0,self.T)
        self.courbeTS1.set_data(self.isoS1,self.T)
        
        self.point1.set_data(EVAP.Ssv,EVAP.Tsv-273.15)
       # print("EVAP.T1",EVAP.T1)
        self.point2.set_data(EVAP.Ssv,EVAP.Tsv-273.15)
        self.point3is.set_data(COMP.S3is,COMP.T3is-273.15)
        self.point3ref.set_data(COMP.S3ref,COMP.T3ref-273.15)
        self.pointo.set_data(COMP.So,COMP.To-273.15)
        self.point4.set_data(DESURCH.Ssv,DESURCH.Tsv-273.15)
        self.point5.set_data(COND.Ssl,COND.Tsl-273.15)

        self.courbe_cycle.remove()
        x = [EVAP.Ssv,EVAP.So, COMP.So,DESURCH.Ssv,COND.Ssl,COND.So,DET.So,EVAP.Ssv]
        print("x=",x)
        
        y = [EVAP.Tsv-273.15,EVAP.Tsv-273.15, COMP.To-273.15,DESURCH.Tsv-273.15,COND.Tsl-273.15,COND.To-273.15,DET.To-273.15,EVAP.Tsv-273.15]
        print("y=",y)
        self.courbe_cycle, = self.ax.plot( x,y,'b:o')

        
        
        self.canvas.draw()
      
w = Tk()
app = App(w)
#personaliser la fenetre
w.title("Calculs GF © Zoheir HADID")
w.geometry("900x600")
w.minsize(200,200)
#w.iconbitmap("CTA.ico")
w.config(background="#322D31")
#pip install pyinstaller
#pyinstaller --onefile <your_script_name>.py

w.mainloop()
