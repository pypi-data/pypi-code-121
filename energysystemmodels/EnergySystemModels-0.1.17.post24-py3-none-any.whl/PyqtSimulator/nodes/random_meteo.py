from PyQt5.QtCore import *
from PyqtSimulator.calc_conf import *
from PyqtSimulator.calc_node_base import *
from NodeEditor.nodeeditor.utils import dumpException

#from component.API_Meteo import SQlite_API_Meteo

#from CoolProp.CoolProp import PropsSI

from AHU import FreshAir
#from API_Meteo import API_Meteo_call
from API_Meteo import API_Meteo_call_location
from AHU.air_humide import air_humide

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import numpy as np

import sched, time

hour=[]
temperature=[]


        
class CalcRandomMeteoContent(QDMNodeContentWidget):
    def initUI(self):
        
        
        
###################################Météo#######################################
        
        self.graphWidget = pg.PlotWidget()
        self.lat_lbl = QLabel("latitude", self)  
        self.lat_edit = QLineEdit("48.861341", self)
        self.lon_lbl = QLabel("longitude (°C)", self)  
        self.lon_edit = QLineEdit("2.337405", self)


###########################################################################                 
        
        self.V_flow_lbl=QLabel("Air humide (m3/h)", self) 
        self.V_flow_edit=QLineEdit("3000", self)
        
        self.T_lbl = QLabel("Température (°C)", self)  
        self.T_edit = QLineEdit("20", self)
        
        self.HR_lbl = QLabel("HR (%)", self)              
        self.HR_edit = QLineEdit("60", self)
        
        import threading
        import random
        
        import pandas as pd
        
        
        
        

        
        def printit():
            threading.Timer(10.0, printit).start()
            
           
            
            #API_T_HR=API_Meteo_call.API_call()
           # print(self.lat_edit.text(),self.lon_edit.text())
            API_T_HR=API_Meteo_call_location.API_call_location(self.lat_edit.text(),self.lon_edit.text())
            
            T=55*random.random()-15
            T=API_T_HR[0]
            HR=100*random.random()
            HR=API_T_HR[1]
            print("après 10 seconde T=",T)
         
            self.T_edit.setText("%f" % T)
            self.HR_edit.setText("%f" % HR)
            
            
                    ##############################################################
            
            temperature.append(float(self.T_edit.text()))  # [30,32,34,32,33,31,29,32,35,45]
          #  print(temperature)
            
            TimeIndex=len(temperature)
            hour.append(TimeIndex) #[1,2,3,4,5,6,7,8,9,10]
           # print(hour)

            # plot data: x, y values
            self.graphWidget.plot(hour, temperature)
        ######################################################
                                             
        printit()
        
            #hing to run
        


        
        
        
        self.P_lbl = QLabel("Pression (bar)", self)                       
        self.P_edit = QLineEdit("1.01325", self)
        
        
        
        
        self.layout=QVBoxLayout()
        
        self.layout.addWidget(self.lat_lbl)
        self.layout.addWidget(self.lat_edit)
        self.layout.addWidget(self.lon_lbl)
        self.layout.addWidget(self.lon_edit)
        
        # self.layout.addWidget(self.fluid_lbl)
        self.layout.addWidget(self.graphWidget)        
        self.layout.addWidget(self.V_flow_lbl)
        self.layout.addWidget(self.V_flow_edit)        
        self.layout.addWidget(self.T_lbl)
        self.layout.addWidget(self.T_edit)
        
        self.layout.addWidget(self.HR_lbl)
        self.layout.addWidget(self.HR_edit)
        
        self.layout.addWidget(self.P_lbl)
        self.layout.addWidget(self.P_edit)
        
        
        
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)
        

    def serialize(self):
        res = super().serialize()
        res['value'] = self.T_edit.text()
        res2 = super().serialize()
        res2['value2'] = self.P_edit.text()
        
        res3 = super().serialize()
        res3['value3'] = self.HR_edit.text()
        
        res4 = super().serialize()
        res4['value4'] = self.V_flow_edit.text()
        
        res5 = super().serialize()
        res5['lat'] = self.lat_edit.text()
        
        res6 = super().serialize()
        res6['lon'] = self.lon_edit.text()
        
        return res,res2,res3,res4,res5,res6

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        res2 = super().deserialize(data, hashmap)
        res3 = super().deserialize(data, hashmap)
        res4 = super().deserialize(data, hashmap)
        res5 = super().deserialize(data, hashmap)
        res6 = super().deserialize(data, hashmap)
        
       # print("res=",res,res2,res3,res4)
       # print("dataaaaaaaaaa=",data)
        try:
            
            value = data[0]["value"]
            value2 = data[1]['value2']
            value3 = data[2]['value3']
            value4 = data[3]['value4']
            value5 = data[4]['lat']
            value6 = data[5]['lon']
            
            
           # print("values=",value,value2,value3,value4)
            
            self.T_edit.setText(value)
            self.P_edit.setText(value2)
            self.HR_edit.setText(value3)
            self.V_flow_edit.setText(value4)
            self.lat_edit.setText(lat)
            self.lon_edit.setText(lon)
            
            
            return True & res & res2 & res3 & res4 & res5 & res6
        except Exception as e:
            dumpException(e)
        return res,res2,res3,res4


@register_node(OP_NODE_RANDOM_METEO)
class CalcNode_RandomMeteo(CalcNode):
    icon = "icons/in.png"
    op_code = OP_NODE_RANDOM_METEO
    op_title = "Météo"
    content_label_objname = "calc_node_random_meteo"
    

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcRandomMeteoContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.grNode.height=450
        self.grNode.width=200
        self.content.T_edit.textChanged.connect(self.onInputChanged)
        self.content.P_edit.textChanged.connect(self.onInputChanged)
        self.content.V_flow_edit.textChanged.connect(self.onInputChanged)
        self.content.HR_edit.textChanged.connect(self.onInputChanged)
        self.content.lon_edit.textChanged.connect(self.onInputChanged)
        self.content.lat_edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        u_T = self.content.T_edit.text()
        s_T = float(u_T)
        
        
        
        u_P = self.content.P_edit.text()
        s_P = float(u_P)
        
        s_HR = float(self.content.HR_edit.text())
        
        s_F_kgs = float(self.content.V_flow_edit.text())* air_humide.rho_ah(s_T, s_HR, s_P*10**5)/3600
        
        
        
        
        
        

        
        # fluid=self.content.fluid.currentText()
        
        self.AN=AirNeuf.objet()
        
        #lecture des données
        self.AN.F_kgs=s_F_kgs
        self.AN.T=s_T
       # print("self.AN.T",self.AN.T)
        self.AN.HR_AirNeuf=s_HR
      #  print("self.AN.HR_AirNeuf",self.AN.HR_AirNeuf)

        #Calculer les propriétés d'air neuf
        self.AN.calculate()
        
      #  print(self.AN.Inlet.propriete())
      #  print(self.AN.Outlet.propriete())
        
        
        self.h=self.AN.h
        
        
        
        self.value = [self.AN.HA,s_F_kgs,s_P,self.h]
       # print("air humide",self.value)
        
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("")

        self.evalChildren()
       # print("données entrée = ",self.value)
        return self.value
   

       
            


        
    def propriete(self,Pro,I1,ValI1,I2,ValI2):
        result=PropsSI(Pro, I1, ValI1, I2, ValI2, self.fluid)
        return result