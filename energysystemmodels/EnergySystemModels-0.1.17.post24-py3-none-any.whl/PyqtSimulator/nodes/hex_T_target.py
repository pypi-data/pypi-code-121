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
from ThermodynamicCycles.HEX import HEX_T_target

#from Modules_GroupeFrigorifique.Turbine import Turbine
#from Modules_GroupeFrigorifique.Desuperheater import Desuperheater
#from Modules_GroupeFrigorifique.Expansion_Valve import Expansion_Valve
#from Modules_GroupeFrigorifique.Condenser import Condenser
from ThermodynamicCycles.Connect import Fluid_connect
from ThermodynamicCycles.FluidPort.FluidPort import FluidPort




class CalcHextContent(QDMNodeContentWidget):
    def initUI(self):
        
        self.P_drop_lbl=QLabel("Perte de pression (bar)", self) 
        self.P_drop_edit=QLineEdit("0.001", self)
        
        self.T_target_lbl=QLabel("Temp. cible (°C)", self) 
        self.T_target_edit=QLineEdit("20", self)
        
        
        
        # self.Tref_lbl=QLabel("refoidissement cible (°C)", self) 
        # self.Tref_edit=QLineEdit("80", self)
        
        self.fluid_lbl_title = QLabel("Qhex(kW)", self)
        self.fluid_lbl = QLabel("", self)
        
        # self.Qlosses_lbl_title = QLabel("Energie dissipée (kW):", self)
        # self.Qlosses_lbl = QLabel("", self)
        
        # self.Tis_lbl_title = QLabel("Temp. isentrop. (°C)", self)
        # self.Tis_lbl = QLabel("", self)
        
        
        
        
         
        self.layout=QVBoxLayout()

        self.layout.addWidget(self.P_drop_lbl)
        self.layout.addWidget(self.P_drop_edit) 
        
        # self.layout.addWidget(self.Tref_lbl)
        # self.layout.addWidget(self.Tref_edit)
        
        self.layout.addWidget(self.T_target_lbl)
        self.layout.addWidget(self.T_target_edit)
        
        
        
        self.layout.addWidget(self.fluid_lbl_title)
        self.layout.addWidget(self.fluid_lbl)  
        
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
        res2['value2'] = self.T_target_edit.text()
        
        res3 = super().serialize()
       # res3['value3'] = self.Tref_edit.text()
        
        
        
        # res4 = super().serialize()
        # res4['value4'] = self.F_kgs_edit.text()
        
        return res,res2 #,res3 #,res4

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        res2 = super().deserialize(data, hashmap)
       # res3 = super().deserialize(data, hashmap)
        # res4 = super().deserialize(data, hashmap)
        # print("res=",res,res2,res3,res4)
        # print("dataaaaaaaaaa=",data)
        try:
            
            value = data[0]["value"]
            value2 = data[1]['value2']
           # value3 = data[2]['value3']
           # value4 = data[3]['value4']
            
            # print("values=",value,value2,value3,value4)
            
            self.P_drop_edit.setText(value)
            self.T_target_edit.setText(value2)
            #self.Tref_edit.setText(value3)
            # self.F_kgs_edit.setText(value4)
            
            return True & res  & res2 #& res3 #& res4
        except Exception as e:
            dumpException(e)
        return res ,res2,res3 #,res4

@register_node(OP_NODE_HEXT)
class CalcNode_Hext(CalcNode):
    icon = "icons/hex.png"
    op_code = OP_NODE_HEXT
    op_title = "Heater_Cooler"
    content_label = "/"
    content_label_objname = "calc_node_hext"
    
    def __init__(self, scene):
        super().__init__(scene, inputs=[2], outputs=[1])
        self.eval()
        
    def initInnerClasses(self):
        self.content = CalcHextContent(self)
        self.grNode = CalcGraphicsNode(self)
        
        
        self.grNode.height=280
        self.grNode.width=200
        
        self.content.P_drop_edit.textChanged.connect(self.onInputChanged)
#        self.content.Tref_edit.textChanged.connect(self.onInputChanged)
        self.content.T_target_edit.textChanged.connect(self.onInputChanged)
  
    def evalOperation(self, input1, input2):
        self.value=[]
        
        a=FluidPort()
        a.fluid=input1[0]
        a.F_kgs=input1[1]
        a.P=input1[2]*1e5
        a.h=input1[3]*1000
       
        HEXT=HEX_T_target.HEX_T_target()
        Fluid_connect(HEXT.Inlet,a)
        ################""""
        u_P_drop = self.content.P_drop_edit.text()
        s_P_drop = float(u_P_drop)
        ####################
        HEXT.P_drop=1e5*s_P_drop
        HEXT.T_target=float(self.content.T_target_edit.text()) 
        #HEXT.Tdischarge_target=float(self.content.Tref_edit.text())
        HEXT.calculate()
        
       
        self.value.append(HEXT.Outlet.fluid) #fluide
        self.value.append(HEXT.Outlet.F_kgs) #débit
        self.value.append(HEXT.Outlet.P/1e5) #pression min
        self.value.append(HEXT.Outlet.h/1000) #Enthalpie
        
        self.content.fluid_lbl.setText("%f" % (HEXT.Qhex/1000)) #"%d" % 
        #self.content.Qlosses_lbl.setText("%f" % (COMP.Qlosses/1000))
        #self.content.Tis_lbl.setText("%f" % (HEXT.Tis-273.15))
        #self.content.lbl.setText("%f" % val[3])
        
        
            
        return self.value