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
#from Modules_GroupeFrigorifique.Evaporator import Evaporator
#from Modules_GroupeFrigorifique.Compressor import Compressor
from ThermodynamicCycles.Desuperheater import Desuperheater
#from Modules_GroupeFrigorifique.Expansion_Valve import Expansion_Valve
#from Modules_GroupeFrigorifique.Condenser import Condenser
from ThermodynamicCycles.Connect import Fluid_connect
from ThermodynamicCycles.FluidPort.FluidPort import FluidPort




class CalcDesuContent(QDMNodeContentWidget):
    def initUI(self):
        
        # self.subcooling_lbl=QLabel("subcooling", self) 
        # self.subcooling_edit=QLineEdit("0.01", self)
        
        # self.IsenEff_lbl=QLabel("Rendement isentropique", self) 
        # self.IsenEff_edit=QLineEdit("0.7", self)
        
        
        
        # self.Tref_lbl=QLabel("refoidissement cible (°C)", self) 
        # self.Tref_edit=QLineEdit("80", self)
        
        self.Tdesu_lbl_title = QLabel("Tcond(°C)", self)
        self.Tdesu_lbl = QLabel("", self)
        
        self.Qdesu_lbl_title = QLabel("Qdesu (kW):", self)
        self.Qdesu_lbl = QLabel("", self)
        
        # self.Tis_lbl_title = QLabel("Temp. isentrop. (°C)", self)
        # self.Tis_lbl = QLabel("", self)
        
        
        
        
         
        self.layout=QVBoxLayout()

        # self.layout.addWidget(self.subcooling_lbl)
        # self.layout.addWidget(self.subcooling_edit) 
        
        # self.layout.addWidget(self.Tref_lbl)
        # self.layout.addWidget(self.Tref_edit)
        
        # self.layout.addWidget(self.IsenEff_lbl)
        # self.layout.addWidget(self.IsenEff_edit)
        
        
        
        self.layout.addWidget(self.Tdesu_lbl_title)
        self.layout.addWidget(self.Tdesu_lbl)  
        
        self.layout.addWidget(self.Qdesu_lbl_title)
        self.layout.addWidget(self.Qdesu_lbl) 
      
        # self.layout.addWidget(self.Tis_lbl_title)
        # self.layout.addWidget(self.Tis_lbl)
        
     
        
                         
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)
        
        
    def serialize(self):
        # res = super().serialize()
        # res['value'] = self.subcooling_edit.text()
    
        
        # return res #,res2,res3,res4
        
        pass

    def deserialize(self, data, hashmap={}):
        # res = super().deserialize(data, hashmap)
        
        # try:
            
        #     value = data["value"]
        
            
        #     self.subcooling_edit.setText(value)
           
            
        #     return True & res # & res2 & res3 & res4
        # except Exception as e:
        #     dumpException(e)
        # return res #,res2,res3,res4
        pass

@register_node(OP_NODE_DESU)
class CalcNode_Desu(CalcNode):
    icon = "icons/desuperheater.png"
    op_code = OP_NODE_DESU
    op_title = "Désurchauffeur"
    content_label = "/"
    content_label_objname = "calc_node_desu"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()
        
    def initInnerClasses(self):
        self.content = CalcDesuContent(self)
        self.grNode = CalcGraphicsNode(self)
        
        
        self.grNode.height=150
        self.grNode.width=200
        
        # self.content.subcooling_edit.textChanged.connect(self.onInputChanged)
        
  
    def evalOperation(self, input1, input2):
        self.value=[]
        
        a=FluidPort()
        a.fluid=input1[0]
        a.F_kgs=input1[1]
        a.P=input1[2]*1e5
        a.h=input1[3]*1000
       
             
                #####Désurchauffeur    
             
        DESU=Desuperheater.Object()
        Fluid_connect(DESU.Inlet,a)
        DESU.calculate()
       
        self.value.append(DESU.Outlet.fluid) #fluide
        self.value.append(DESU.Outlet.F_kgs) #débit
        self.value.append(DESU.Outlet.P/1e5) #pression min
        self.value.append(DESU.Outlet.h/1000) #Enthalpie
        
        # self.content.fluid_lbl.setText("%f" % (COMP.Qcomp/1000)) #"%d" % 
        self.content.Qdesu_lbl.setText("%f" % (DESU.Qdesurch/1000))
        self.content.Tdesu_lbl.setText("%f" % (DESU.Tsv-273.15))
        
        #self.content.lbl.setText("%f" % val[3])
        
        
            
        return self.value