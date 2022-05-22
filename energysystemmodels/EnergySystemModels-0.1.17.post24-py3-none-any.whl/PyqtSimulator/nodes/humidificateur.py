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
#from AHU import Coil
#from AHU.Humidification import Humidifier
from AHU.Humidification import Humidifier


from AHU.Connect import Air_connect
from AHU.AirPort.AirPort import AirPort




class CalcHMDContent(QDMNodeContentWidget):
    def initUI(self):
        
        self.HumidType_lbl = QLabel("Type d'humidification", self)
        self.HumidType=QComboBox(self)
        self.HumidType.addItem("adiabatique")
        self.HumidType.addItem("vapeur")
        self.HumidType.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) 
        
        
        self.P_drop_lbl=QLabel("Perte de pression (bar)", self) 
        self.P_drop_edit=QLineEdit("0.001", self)
        
        self.HA_target_lbl=QLabel("HA cible (g/kgas)", self) 
        self.HA_target_edit=QLineEdit("12", self)
        
        
        
        # self.Tref_lbl=QLabel("refoidissement cible (°C)", self) 
        # self.Tref_edit=QLineEdit("80", self)
        
        self.m_water_lbl_title = QLabel("débit d'eau g/s", self)
        self.m_water_lbl = QLabel("", self)
        
        # self.Qlosses_lbl_title = QLabel("Energie dissipée (kW):", self)
        # self.Qlosses_lbl = QLabel("", self)
        
        # self.Tis_lbl_title = QLabel("Temp. isentrop. (°C)", self)
        # self.Tis_lbl = QLabel("", self)
        
        
        
        
         
        self.layout=QVBoxLayout()

        self.layout.addWidget(self.HumidType_lbl)
        self.layout.addWidget(self.HumidType)
        
        self.layout.addWidget(self.P_drop_lbl)
        self.layout.addWidget(self.P_drop_edit) 
        
        # self.layout.addWidget(self.Tref_lbl)
        # self.layout.addWidget(self.Tref_edit)
        
        self.layout.addWidget(self.HA_target_lbl)
        self.layout.addWidget(self.HA_target_edit)
        
        
        
        self.layout.addWidget(self.m_water_lbl_title)
        self.layout.addWidget(self.m_water_lbl)  
        
        # self.layout.addWidget(self.Qlosses_lbl_title)
        # self.layout.addWidget(self.Qlosses_lbl) 
      
        # self.layout.addWidget(self.Tis_lbl_title)
        # self.layout.addWidget(self.Tis_lbl)
        
     
        
                         
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)
        
    def serialize(self):
        res = super().serialize()
        res['value'] = self.P_drop_edit.text()
        res2 = super().serialize()
        res2['value2'] = self.HA_target_edit.text()
        
        res3 = super().serialize()
        res3['value3'] = self.HumidType.currentText()
        
        
        
        # res4 = super().serialize()
        # res4['value4'] = self.F_kgs_edit.text()
        
        return res,res2,res3 #,res4

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        res2 = super().deserialize(data, hashmap)
        res3 = super().deserialize(data, hashmap)
        # res4 = super().deserialize(data, hashmap)
        # print("res=",res,res2,res3,res4)
        # print("dataaaaaaaaaa=",data)
        try:
            
            value = data[0]["value"]
            value2 = data[1]['value2']
            value3 = data[2]['value3']
           # value4 = data[3]['value4']
            
            # print("values=",value,value2,value3,value4)
            
            self.P_drop_edit.setText(value)
            self.HA_target_edit.setText(value2)
            self.HumidType.setCurrentText(value3)
            # self.F_kgs_edit.setText(value4)
            
            return True & res  & res2 & res3 #& res4
        except Exception as e:
            dumpException(e)
        return res ,res2,res3 #,res4

@register_node(OP_NODE_HMD)
class CalcNode_HMD(CalcNode):
    icon = "icons/HMD.png"
    op_code = OP_NODE_HMD
    op_title = "Humidifier"
    content_label = "/"
    content_label_objname = "calc_node_HMD"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()
        
    def initInnerClasses(self):
        self.content = CalcHMDContent(self)
        self.grNode = CalcGraphicsNode(self)
        
        
        self.grNode.height=250
        self.grNode.width=200
        
        self.content.P_drop_edit.textChanged.connect(self.onInputChanged)
#        self.content.Tref_edit.textChanged.connect(self.onInputChanged)
        self.content.HA_target_edit.textChanged.connect(self.onInputChanged)
        self.content.HumidType.currentIndexChanged.connect(self.onInputChanged)
  
    def evalOperation(self, input1, input2):
        self.value=[]
        
        a=AirPort()
        a.HA=input1[0]
        a.F_kgs=input1[1]
        a.P=input1[2]*1e5
        a.h=input1[3]
       
        HMD=Humidifier.objet()
        
        
        connect(HMD.Inlet,a)
        HumidType=self.content.HumidType.currentText()
       # print("HumidType=",HumidType)
        
        HMD.HA_out_target=float(self.content.HA_target_edit.text())
        print("HMD.HA_out_target",HMD.HA_out_target)
        HMD.HumidType=HumidType
        HMD.calculate()
        
        
       
        ####################
        HMD.P_drop=1e5*float(self.content.P_drop_edit.text())
       
        #HMD.Tdischarge_target=float(self.content.Tref_edit.text())
        HMD.calculate()
        
       
        self.value.append(HMD.Outlet.HA) #HAe
        self.value.append(HMD.Outlet.F_kgs) #débit
        self.value.append(HMD.Outlet.P/1e5) #pression min
        self.value.append(HMD.Outlet.h) #Enthalpie
        
        self.content.m_water_lbl.setText("%.2f" % (HMD.m_water*1000)) #"%d" % 
        # #self.content.Qlosses_lbl.setText("%f" % (COMP.Qlosses/1000))
        # #self.content.Tis_lbl.setText("%f" % (HMD.Tis-273.15))
        # #self.content.lbl.setText("%f" % val[3])
        
        
            
        return self.value