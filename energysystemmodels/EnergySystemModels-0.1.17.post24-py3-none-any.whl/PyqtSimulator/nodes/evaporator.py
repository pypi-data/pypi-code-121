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
from ThermodynamicCycles.Evaporator import Evaporator
#from Modules_GroupeFrigorifique.Compressor import Compressor
#from Modules_GroupeFrigorifique.Desuperheater import Desuperheater
#from Modules_GroupeFrigorifique.Expansion_Valve import Expansion_Valve
#from Modules_GroupeFrigorifique.Condenser import Condenser
from ThermodynamicCycles.Connect import Fluid_connect
from ThermodynamicCycles.FluidPort.FluidPort import FluidPort




class CalcEvapContent(QDMNodeContentWidget):
    def initUI(self):
        
        self.Surchauffe_lbl=QLabel("surchauffe", self) 
        self.Surchauffe_edit=QLineEdit("0.01", self)
        
        # self.IsenEff_lbl=QLabel("Rendement isentropique", self) 
        # self.IsenEff_edit=QLineEdit("0.7", self)
        
        
        
        # self.Tref_lbl=QLabel("refoidissement cible (°C)", self) 
        # self.Tref_edit=QLineEdit("80", self)
        
        self.Tevap_lbl_title = QLabel("Tevap(°C)", self)
        self.Tevap_lbl = QLabel("", self)
        
        self.Qevap_lbl_title = QLabel("Qevap (kW):", self)
        self.Qevap_lbl = QLabel("", self)
        
        # self.Tis_lbl_title = QLabel("Temp. isentrop. (°C)", self)
        # self.Tis_lbl = QLabel("", self)
        
        
        
        
         
        self.layout=QVBoxLayout()

        self.layout.addWidget(self.Surchauffe_lbl)
        self.layout.addWidget(self.Surchauffe_edit) 
        
        # self.layout.addWidget(self.Tref_lbl)
        # self.layout.addWidget(self.Tref_edit)
        
        # self.layout.addWidget(self.IsenEff_lbl)
        # self.layout.addWidget(self.IsenEff_edit)
        
        
        
        self.layout.addWidget(self.Tevap_lbl_title)
        self.layout.addWidget(self.Tevap_lbl)  
        
        self.layout.addWidget(self.Qevap_lbl_title)
        self.layout.addWidget(self.Qevap_lbl) 
      
        # self.layout.addWidget(self.Tis_lbl_title)
        # self.layout.addWidget(self.Tis_lbl)
        
     
        
                         
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)
        
    def serialize(self):
        res = super().serialize()
        res['value'] = self.Surchauffe_edit.text()
        # res2 = super().serialize()
        # res2['value2'] = self.P_edit.text()
        
        # res3 = super().serialize()
        # res3['value3'] = self.fluid.currentText()
        
        # res4 = super().serialize()
        # res4['value4'] = self.F_kgs_edit.text()
        
        return res #,res2,res3,res4

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        # res2 = super().deserialize(data, hashmap)
        # res3 = super().deserialize(data, hashmap)
        # res4 = super().deserialize(data, hashmap)
        # print("res=",res,res2,res3,res4)
        # print("dataaaaaaaaaa=",data)
        try:
            
            value = data["value"]
            # value2 = data[1]['value2']
            # value3 = data[2]['value3']
            # value4 = data[3]['value4']
            
            # print("values=",value,value2,value3,value4)
            
            self.Surchauffe_edit.setText(value)
            # self.P_edit.setText(value2)
            # self.fluid.setCurrentText(value3)
            # self.F_kgs_edit.setText(value4)
            
            return True & res # & res2 & res3 & res4
        except Exception as e:
            dumpException(e)
        return res #,res2,res3,res4

@register_node(OP_NODE_EVAP)
class CalcNode_Evap(CalcNode):
    icon = "icons/evaporator.png"
    op_code = OP_NODE_EVAP
    op_title = "Evaporateur"
    content_label = "/"
    content_label_objname = "calc_node_evap"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()
        
    def initInnerClasses(self):
        self.content = CalcEvapContent(self)
        self.grNode = CalcGraphicsNode(self)
        
        
        self.grNode.height=210
        self.grNode.width=180
        
        self.content.Surchauffe_edit.textChanged.connect(self.onInputChanged)
        # self.content.Tref_edit.textChanged.connect(self.onInputChanged)
        # self.content.IsenEff_edit.textChanged.connect(self.onInputChanged)
  
    def evalOperation(self, input1, input2):
        self.value=[]
        
        a=FluidPort()
        a.fluid=input1[0]
        a.F_kgs=input1[1]
        a.P=input1[2]*1e5
        a.h=input1[3]*1000
       

        
                #####Evaporateur
        EVAP=Evaporator.Object()
        Fluid_connect(EVAP.Inlet,a)
       
        EVAP.surchauff=float(self.content.Surchauffe_edit.text()) 
        EVAP.calculate()
        
       
        self.value.append(EVAP.Outlet.fluid) #fluide
        self.value.append(EVAP.Outlet.F_kgs) #débit
        self.value.append(EVAP.Outlet.P/1e5) #pression min
        self.value.append(EVAP.Outlet.h/1000) #Enthalpie
        
        # self.content.fluid_lbl.setText("%f" % (COMP.Qcomp/1000)) #"%d" % 
        self.content.Qevap_lbl.setText("%f" % (EVAP.Qevap/1000))
        self.content.Tevap_lbl.setText("%f" % (EVAP.Tsl-273.15))
        
        #self.content.lbl.setText("%f" % val[3])
        
        
            
        return self.value