# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 19:39:26 2020

@author: zohei
"""

from PyQt5.QtCore import *
from PyqtSimulator.calc_conf import *
from PyqtSimulator.calc_node_base import *
from NodeEditor.nodeeditor.utils import dumpException

#############les modèles d'un groupe frigorifique#################
#from AHU import FreshAir
from AHU.Coil import CoolingCoil_Expert
#from AHU.Humidification import Humidifier


from AHU.Connect import Air_connect
from AHU.AirPort.AirPort import AirPort




class CalcCoolingCoilExpertContent(QDMNodeContentWidget):
    def initUI(self):
        
        self.P_drop_lbl=QLabel("Perte de pression (bar)", self) 
        self.P_drop_edit=QLineEdit("0.001", self)
        
        self.HA_target_lbl=QLabel("poid d'eau (g/kgas)", self) 
        self.HA_target_edit=QLineEdit("5", self)
        
        
        
        self.Tsat_lbl=QLabel("Temp Eau glacée ou évap (°C)", self) 
        self.Tsat_edit=QLineEdit("8.0", self)
        
        self.Qth_lbl_title = QLabel("Qhex(kW)", self)
        self.Qth_lbl = QLabel("", self)
        
        
        self.Eff_lbl = QLabel("", self)
        self.FB_lbl = QLabel("", self)
        
        
        
        # self.Qlosses_lbl_title = QLabel("Energie dissipée (kW):", self)
        # self.Qlosses_lbl = QLabel("", self)
        
        # self.Tis_lbl_title = QLabel("Temp. isentrop. (°C)", self)
        # self.Tis_lbl = QLabel("", self)
        
        
        
        
         
        self.layout=QVBoxLayout()

        self.layout.addWidget(self.P_drop_lbl)
        self.layout.addWidget(self.P_drop_edit) 
        
        self.layout.addWidget(self.Tsat_lbl)
        self.layout.addWidget(self.Tsat_edit)
        
        self.layout.addWidget(self.HA_target_lbl)
        self.layout.addWidget(self.HA_target_edit)
        
        
        
        self.layout.addWidget(self.Qth_lbl_title)
        self.layout.addWidget(self.Qth_lbl) 
        
        self.layout.addWidget(self.Eff_lbl)  
        self.layout.addWidget(self.FB_lbl)  
        
        # self.layout.addWidget(self.Qlosses_lbl_title)
        # self.layout.addWidget(self.Qlosses_lbl) 
      
        # self.layout.addWidget(self.Tis_lbl_title)
        # self.layout.addWidget(self.Tis_lbl)
        
     
        
                         
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)
        
    def serialize(self):
        res = super().serialize()
        res['P_drop'] = self.P_drop_edit.text()
        res2 = super().serialize()
        res2['HA_target'] = self.HA_target_edit.text()
        
        res3 = super().serialize()
        res3['Tsat'] = self.Tsat_edit.text()
        
        
        
        # res4 = super().serialize()
        # res4['Tsat'] = self.F_kgs_edit.text()
        
        return res,res2,res3

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        res2 = super().deserialize(data, hashmap)
       # res3 = super().deserialize(data, hashmap)
        # res4 = super().deserialize(data, hashmap)
        # print("res=",res,res2,res3,res4)
        # print("dataaaaaaaaaa=",data)
        try:
            
            P_drop = data[0]["P_drop"]
            HA_target = data[1]['HA_target']
           # value3 = data[2]['value3']
            Tsat = data[2]['Tsat']
            
            # print("values=",value,HA_target,value3,Tsat)
            
            self.P_drop_edit.setText(P_drop)
            self.HA_target_edit.setText(HA_target)
            self.Tsat_edit.setText(Tsat)
           
            
            return True & res  & res2 & res3 #& res4
        except Exception as e:
            dumpException(e)
        return res ,res2,res3 #,res4

@register_node(OP_NODE_COOLING_COIL_EXPERT)
class CalcNode_cooling_coil_expert(CalcNode):
    icon = "icons/cooling_coil.png"
    op_code = OP_NODE_COOLING_COIL_EXPERT
    op_title = "Cooling Coil Expert"
    content_label = "/"
    content_label_objname = "calc_node_cooling_coil_expert"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()
        
    def initInnerClasses(self):
        self.content = CalcCoolingCoilExpertContent(self)
        self.grNode = CalcGraphicsNode(self)
        
        
        self.grNode.height=300
        self.grNode.width=250
        
        self.content.P_drop_edit.textChanged.connect(self.onInputChanged)
        self.content.Tsat_edit.textChanged.connect(self.onInputChanged)
        self.content.HA_target_edit.textChanged.connect(self.onInputChanged)
  
    def evalOperation(self, input1, input2):
        self.value=[]
        
        a=AirPort()
        a.HA=input1[0]
        a.F_kgs=input1[1]
        a.P=input1[2]*1e5
        a.h=input1[3]
       
        COOLING_COIL=CoolingCoil_Expert.Object()
        Air_connect(COOLING_COIL.Inlet,a)
        ################""""
        u_P_drop = self.content.P_drop_edit.text()
        s_P_drop = float(u_P_drop)
        ####################
        COOLING_COIL.P_drop=1e5*s_P_drop
        COOLING_COIL.HA_target=float(self.content.HA_target_edit.text()) 
        COOLING_COIL.T_sat=float(self.content.Tsat_edit.text())
        COOLING_COIL.calculate()
        
       
        self.value.append(COOLING_COIL.Outlet.HA) #HAe
        self.value.append(COOLING_COIL.Outlet.F_kgs) #débit
        self.value.append(COOLING_COIL.Outlet.P/1e5) #pression min
        self.value.append(COOLING_COIL.Outlet.h) #Enthalpie
        
        self.content.Qth_lbl.setText("%f" % (COOLING_COIL.Qth)) #"%d" % 
        
        self.content.Eff_lbl.setText("Efficacité="+"%f" % (COOLING_COIL.Eff)) #"%d" % 
        self.content.FB_lbl.setText("Facteur bypass="+"%f" % (COOLING_COIL.FB)) #"%d" % 
        
        
            
        return self.value