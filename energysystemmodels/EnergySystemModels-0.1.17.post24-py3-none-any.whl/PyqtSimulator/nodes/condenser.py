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
#from Modules_GroupeFrigorifique.Expansion_Valve import Expansion_Valve
from ThermodynamicCycles.Condenser import Condenser
from ThermodynamicCycles.Connect import Fluid_connect
from ThermodynamicCycles.FluidPort.FluidPort import FluidPort




class CalcCondContent(QDMNodeContentWidget):
    def initUI(self):
        
        self.subcooling_lbl=QLabel("subcooling", self) 
        self.subcooling_edit=QLineEdit("0.01", self)
        
        # self.IsenEff_lbl=QLabel("Rendement isentropique", self) 
        # self.IsenEff_edit=QLineEdit("0.7", self)
        
        
        
        # self.Tref_lbl=QLabel("refoidissement cible (°C)", self) 
        # self.Tref_edit=QLineEdit("80", self)
        
        self.Tcond_lbl_title = QLabel("Tcond(°C)", self)
        self.Tcond_lbl = QLabel("", self)
        
        self.Qcond_lbl_title = QLabel("Qcond (kW):", self)
        self.Qcond_lbl = QLabel("", self)
        
        # self.Tis_lbl_title = QLabel("Temp. isentrop. (°C)", self)
        # self.Tis_lbl = QLabel("", self)
        
        
        
        
         
        self.layout=QVBoxLayout()

        self.layout.addWidget(self.subcooling_lbl)
        self.layout.addWidget(self.subcooling_edit) 
        
        # self.layout.addWidget(self.Tref_lbl)
        # self.layout.addWidget(self.Tref_edit)
        
        # self.layout.addWidget(self.IsenEff_lbl)
        # self.layout.addWidget(self.IsenEff_edit)
        
        
        
        self.layout.addWidget(self.Tcond_lbl_title)
        self.layout.addWidget(self.Tcond_lbl)  
        
        self.layout.addWidget(self.Qcond_lbl_title)
        self.layout.addWidget(self.Qcond_lbl) 
      
        # self.layout.addWidget(self.Tis_lbl_title)
        # self.layout.addWidget(self.Tis_lbl)
        
     
        
                         
        
        self.setLayout(self.layout)
        
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setObjectName(self.node.content_label_objname)
        
        
    def serialize(self):
        res = super().serialize()
        res['value'] = self.subcooling_edit.text()
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
            
            self.subcooling_edit.setText(value)
            # self.P_edit.setText(value2)
            # self.fluid.setCurrentText(value3)
            # self.F_kgs_edit.setText(value4)
            
            return True & res # & res2 & res3 & res4
        except Exception as e:
            dumpException(e)
        return res #,res2,res3,res4


@register_node(OP_NODE_COND)
class CalcNode_Cond(CalcNode):
    icon = "icons/condenser.png"
    op_code = OP_NODE_COND
    op_title = "Condenseur"
    content_label = "/"
    content_label_objname = "calc_node_cond"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()
        
    def initInnerClasses(self):
        self.content = CalcCondContent(self)
        self.grNode = CalcGraphicsNode(self)
        
        
        self.grNode.height=210
        self.grNode.width=200
        
        self.content.subcooling_edit.textChanged.connect(self.onInputChanged)
        # self.content.Tref_edit.textChanged.connect(self.onInputChanged)
        # self.content.IsenEff_edit.textChanged.connect(self.onInputChanged)
  
    def evalOperation(self, input1, input2):
        self.value=[]
        
        a=FluidPort()
        a.fluid=input1[0]
        a.F_kgs=input1[1]
        a.P=input1[2]*1e5
        a.h=input1[3]*1000
       
        # COMP=Compressor.Compressor()
        # connect(COMP.Inlet,a)
        # ################""""
        # u_HP = self.content.HP_edit.text()
        # s_HP = float(u_HP)
        # ####################
        # COMP.HP=1e5*s_HP
        # COMP.IsenEff=float(self.content.IsenEff_edit.text()) 
        # COMP.Tdischarge_target=float(self.content.Tref_edit.text())
        # COMP.calculate()
        
                #####Condenseur    
      
        COND=Condenser.Object()
        Fluid_connect(COND.Inlet,a)
        COND.subcooling=float(self.content.subcooling_edit.text()) 
        COND.calculate()
        
       
        self.value.append(COND.Outlet.fluid) #fluide
        self.value.append(COND.Outlet.F_kgs) #débit
        self.value.append(COND.Outlet.P/1e5) #pression min
        self.value.append(COND.Outlet.h/1000) #Enthalpie
        
        # self.content.fluid_lbl.setText("%f" % (COMP.Qcomp/1000)) #"%d" % 
        self.content.Qcond_lbl.setText("%f" % (COND.Qcond/1000))
        self.content.Tcond_lbl.setText("%f" % (COND.Tsl-273.15))
        
        #self.content.lbl.setText("%f" % val[3])
        
        
            
        return self.value