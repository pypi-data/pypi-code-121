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
#from Modules_GroupeFrigorifique.Desuperheater import Desuperheater
from ThermodynamicCycles.Expansion_Valve import Expansion_Valve
#from Modules_GroupeFrigorifique.Condenser import Condenser
from ThermodynamicCycles.Connect import Fluid_connect
from ThermodynamicCycles.FluidPort.FluidPort import FluidPort




class CalcDetContent(QDMNodeContentWidget):
    def initUI(self):
        
        self.LP_lbl=QLabel("basse pression (bar)", self) 
        self.LP_edit=QLineEdit("2.7", self)
        
        # self.IsenEff_lbl=QLabel("Rendement isentropique", self) 
        # self.IsenEff_edit=QLineEdit("0.7", self)
        
        
        
        # self.Tref_lbl=QLabel("refoidissement cible (°C)", self) 
        # self.Tref_edit=QLineEdit("80", self)
        
        self.Tdet_lbl_title = QLabel("Tcond(°C)", self)
        self.Tdet_lbl = QLabel("", self)
        
        self.Qdet_lbl_title = QLabel("Qdet (kW):", self)
        self.Qdet_lbl = QLabel("", self)
        
        # self.Tis_lbl_title = QLabel("Temp. isentrop. (°C)", self)
        # self.Tis_lbl = QLabel("", self)
        
        
        
        
         
        self.layout=QVBoxLayout()

        self.layout.addWidget(self.LP_lbl)
        self.layout.addWidget(self.LP_edit) 
        
        # self.layout.addWidget(self.Tref_lbl)
        # self.layout.addWidget(self.Tref_edit)
        
        # self.layout.addWidget(self.IsenEff_lbl)
        # self.layout.addWidget(self.IsenEff_edit)
        
        
        
        self.layout.addWidget(self.Tdet_lbl_title)
        self.layout.addWidget(self.Tdet_lbl)  
        
        self.layout.addWidget(self.Qdet_lbl_title)
        self.layout.addWidget(self.Qdet_lbl) 
      
        # self.layout.addWidget(self.Tis_lbl_title)
        # self.layout.addWidget(self.Tis_lbl)
        
     
        
                         
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)
        
        
    def serialize(self):
        res = super().serialize()
        res['value'] = self.LP_edit.text()
    
        
        return res #,res2,res3,res4
        
        

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        
        try:
            
            value = data["value"]
        
            
            self.LP_edit.setText(value)
           
            
            return True & res # & res2 & res3 & res4
        except Exception as e:
            dumpException(e)
        return res #,res2,res3,res4
        

@register_node(OP_NODE_DET)
class CalcNode_Det(CalcNode):
    icon = "icons/expansion_valve.png"
    op_code = OP_NODE_DET
    op_title = "Détendeur"
    content_label = "/"
    content_label_objname = "calc_node_det"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()
        
    def initInnerClasses(self):
        self.content = CalcDetContent(self)
        self.grNode = CalcGraphicsNode(self)
        
        
        self.grNode.height=210
        self.grNode.width=200
        
        self.content.LP_edit.textChanged.connect(self.onInputChanged)
        
  
    def evalOperation(self, input1, input2):
        self.value=[]
        
        a=FluidPort()
        a.fluid=input1[0]
        a.F_kgs=input1[1]
        a.P=input1[2]*1e5
        a.h=input1[3]*1000
       
             
                #####Désurchauffeur    
             
        DET=Expansion_Valve.Object()
        Fluid_connect(DET.Inlet,a)
        DET.Outlet.P=float(self.content.LP_edit.text())*100000
        DET.calculate()
       
        self.value.append(DET.Outlet.fluid) #fluide
        self.value.append(DET.Outlet.F_kgs) #débit
        self.value.append(DET.Outlet.P/1e5) #pression min
        self.value.append(DET.Outlet.h/1000) #Enthalpie
        
        # self.content.fluid_lbl.setText("%f" % (COMP.Qcomp/1000)) #"%d" % 
        self.content.Qdet_lbl.setText("%f" % (DET.Qdet/1000))
        self.content.Tdet_lbl.setText("%f" % (DET.To-273.15))
        
        #self.content.lbl.setText("%f" % val[3])
        
        
            
        return self.value